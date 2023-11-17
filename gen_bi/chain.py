import os
from sqlalchemy import create_engine
from langchain.chat_models import AzureChatOpenAI
from nerve_schema import NerveSchema
from nerve_langchain.sql_database import NerveSQLDatabase
from langchain.sql_database import SQLDatabase
from typing import Any, Dict, List, Optional
from nerve_langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent import AgentExecutor
import pandas as pd
from io import BytesIO
from nerve_langchain.agents.agent_toolkits.nerve_sql.prompt import (
    SQL_FUNCTIONS_SUFFIX,
    SQL_PREFIX,
    SQL_SUFFIX,
)
import ast
import traceback
import io
from langchain.callbacks.base import BaseCallbackManager,BaseCallbackHandler
import streamlit as st
from datetime import date
from langchain.llms import VertexAI
import json
from google.oauth2.service_account import Credentials
from langchain.llms.base import LLM
import duckdb

class NerveLLMChain():
    def mock_data_into_database(_self, _nerve_schema: NerveSchema):
        tables: List[str] = _nerve_schema.get_table_names()
        conn = duckdb.connect(database="nerve.db")
        for table in tables:
            conn.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('demo_dataset/{table}.csv', HEADER=true);")


    @st.cache_resource
    def init_database(_self, databricks_token: str, databricks_sql_hostname: str, databricks_sql_http_path: str, tables:List[str], custom_table_info:Dict[str,str], mock_data: bool = False) -> NerveSQLDatabase:

        if mock_data:
            return NerveSQLDatabase.from_uri("duckdb:///nerve.db", include_tables=tables, custom_table_info=custom_table_info)
        else:
            return NerveSQLDatabase.from_uri("databricks://token:{token}@{host}?http_path={http_path}&catalog={catalog}&schema={schema}".format(
                token=databricks_token,
                host=databricks_sql_hostname,
                http_path=databricks_sql_http_path,
                catalog="nerve",
                schema="genbi"
            ), include_tables=tables, custom_table_info=custom_table_info, max_string_length=100, max_result_length=1000, engine_args={"pool_pre_ping":True})
        
    @st.cache_resource
    def init_llm(_self, llm_provider="openai", openai_endpoint="", openai_token="") -> LLM:

        if llm_provider == "vertexai":
            service_account_key_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', "")
            service_account_key = json.loads(service_account_key_json,strict=False)
            creds = Credentials.from_service_account_info(info=service_account_key)
            return VertexAI(
                temperature=0,
                top_p=1,
                top_k=1,
                max_output_tokens=1024,
                credentials=creds,
                project=service_account_key["project_id"],
                model="code-bison"
            )
        else:
            os.environ["OPENAI_API_TYPE"] = "azure"
            os.environ["OPENAI_API_VERSION"] = "2023-08-01-preview"
            os.environ["OPENAI_API_BASE"] = openai_endpoint
            os.environ["OPENAI_API_KEY"] = openai_token

            return AzureChatOpenAI(
                temperature=0, 
                deployment_name="gpt-4-32k",
            )





    def __init__(
            self, 
            starting_message_for_context:str,
            mock_data:bool = False
        ):
        openai_endpoint:str = os.environ.get("OPENAI_ENDPOINT", "")
        openai_token:str = os.environ.get("OPENAI_TOKEN","")
        databricks_token:str = os.environ.get("DATABRICKS_TOKEN","")
        databricks_sql_hostname:str = os.environ.get("DATABRICKS_SQL_HOSTNAME","")
        databricks_sql_http_path:str = os.environ.get("DATABRICKS_SQL_HTTP_PATH","")

        schema:NerveSchema = NerveSchema()
        tables:List[str] = schema.get_table_names()
        custom_table_info:Dict[str,str] = {}
        for table in tables:
            custom_table_info[table] = schema.get_table_info(table_name=table)
        
        if mock_data:
            self.mock_data_into_database(schema)

        db:NerveSQLDatabase = self.init_database(databricks_token, databricks_sql_hostname, databricks_sql_http_path, tables, custom_table_info, mock_data=mock_data)

        self.llm:LLM = self.init_llm(llm_provider="openai", openai_endpoint=openai_endpoint, openai_token=openai_token)

        toolkit:SQLDatabaseToolkit = SQLDatabaseToolkit(db=db, llm=self.llm, top_k=20)

        self.agent_executor:AgentExecutor = create_sql_agent(
            llm=self.llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prefix=SQL_PREFIX.format(dialect=toolkit.dialect, top_k=20, date=date.today()),
            suffix=SQL_SUFFIX,
            top_k=20,
            agent_executor_kwargs={"return_intermediate_steps":True,"handle_parsing_errors": True},
            trim_intermediate_steps=7
        )

        self.memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(llm=self.llm, max_token_limit=500)



        self.starting_message_for_context:str = starting_message_for_context
        self.clear_memory()


    def clear_memory(self) -> None:
        self.memory.clear()
        if self.starting_message_for_context:
            self.memory.chat_memory.add_ai_message(self.starting_message_for_context)

    def get_memory(self) -> str:
        return self.memory.load_memory_variables({})["history"]

    def run(self, query:str, callbacks:List[BaseCallbackHandler]=None) -> Dict[str, str]:
        self.memory.chat_memory.add_user_message(query)
        history = self.memory.load_memory_variables({})
        result = self.agent_executor({"input": history["history"]},callbacks=callbacks)
        output = result["output"]
        chart_decision_result = "table"
        chart_decision_input = None
        file_buf = None
        sql_query = ""
        result_length = 0
        sql_db_queries = list(filter(lambda step: step[0].tool == "sql_db_query", result["intermediate_steps"])) 
        if sql_db_queries:
            last_sql_db_query_step = sql_db_queries.pop()
            sql_query = last_sql_db_query_step[0].tool_input
            #Save this to last sql query result so that in the event we did not requery the table, we reuse the result
            self.last_sql_query_result = last_sql_db_query_step[1]
            result_length = len(pd.read_csv(io.StringIO(last_sql_db_query_step[1])).index)
        chart_decision = list(filter(lambda step: step[0].tool == "Python_REPL", result["intermediate_steps"]))
        if chart_decision:
            last_chart_generation_step = chart_decision.pop()
            try:
                last_chart_generation_file = last_chart_generation_step[1].strip()
                with open(last_chart_generation_file, "rb") as fh:
                    file_buf = BytesIO(fh.read())
                    os.remove(last_chart_generation_file)
                if self.last_sql_query_result is not None:
                    df = pd.read_csv(io.StringIO(self.last_sql_query_result))
                    output = df.to_markdown(index=False,floatfmt=".2f")
            except:
                traceback.print_exc()
                pass

        self.memory.chat_memory.add_ai_message(output + "\n\n" + sql_query)
        return {
            "output": output,
            "sql_query": sql_query,
            "image": file_buf,
            "result_length": result_length
        }