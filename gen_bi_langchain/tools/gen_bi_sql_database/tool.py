# flake8: noqa
"""Tools for interacting with a SQL database."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Extra, Field, root_validator

from langchain.schema.language_model import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from gen_bi_langchain.utilities.sql_database import GenBISQLDatabase
from langchain.tools.base import BaseTool
from gen_bi_langchain.tools.gen_bi_sql_database.prompt import QUERY_CHECKER, CHART_DECISION
import pandas as pd
import csv

class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with a SQL database."""

    db: GenBISQLDatabase = Field(exclude=True)

    # Override BaseTool.Config to appease mypy
    # See https://github.com/pydantic/pydantic/issues/4173
    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = Extra.forbid

class ChartDecisionTool(BaseTool):
    """Use an to decide which tool is the most suitable based on the query."""

    template: str = CHART_DECISION
    llm: BaseLanguageModel
    llm_chain: LLMChain = Field(init=False)
    name = "chart_decision_tool"
    description = """
    Use this tool to decide which chart is the most appropriate for the input. Input is a question and the data represented by an array of tuple
    """

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "llm_chain" not in values:
            values["llm_chain"] = LLMChain(
                llm=values.get("llm"),
                prompt=PromptTemplate(
                    template=CHART_DECISION, input_variables=["query"]
                ),
            )

        if values["llm_chain"].prompt.input_variables != ["query"]:
            raise ValueError(
                "LLM chain for ChartDecisionTool must have input variables ['query']"
            )

        return values

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the LLM to check the query."""
        result = self.llm_chain.predict(
            query=query,
            callbacks=run_manager.get_child() if run_manager else None,
        )
        return result.replace("Answer: ", "").strip()

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        result = await self.llm_chain.apredict(
            query=query,
            callbacks=run_manager.get_child() if run_manager else None,
        )
        return result.replace("Answer: ", "").strip()

class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_db_query"
    description = """
    Input to this tool is a detailed and correct SQL query, output is a result in csv format along with the headers from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.db.run_no_throw(query)


class InfoSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name = "sql_db_schema"
    description = """
    Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.    

    Example Input: "table1, table2, table3"
    """

    def _run(
        self,
        table_names: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        tables = table_names.split(",")
        tables = list(map(lambda x: x.strip(), tables))
        return self.db.get_table_info_no_throw(tables)


class ListSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting tables names."""

    name = "sql_db_list_tables"
    description = "Input is an empty string, output is a csv formatted list of tables and their description"

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for a specific table."""
        table_and_description_dict = self.db.get_usable_table_names_and_description()
        table_and_description_array = [{"table": table, "description": description} for table,description in table_and_description_dict.items()]
        return pd.DataFrame.from_dict(table_and_description_array).to_csv(index=False, quoting=csv.QUOTE_MINIMAL)


class QuerySQLCheckerTool(BaseSQLDatabaseTool, BaseTool):
    """Use an LLM to check if a query is correct.
    Adapted from https://www.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt/"""

    template: str = QUERY_CHECKER
    llm: BaseLanguageModel
    llm_chain: LLMChain = Field(init=False)
    name = "sql_db_query_checker"
    description = """
    Use this tool to double check if your query is correct before executing it.
    Always use this tool before executing a query with query_sql_db!
    """

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "llm_chain" not in values:
            values["llm_chain"] = LLMChain(
                llm=values.get("llm"),
                prompt=PromptTemplate(
                    template=QUERY_CHECKER, input_variables=["query", "dialect"]
                ),
            )

        if values["llm_chain"].prompt.input_variables != ["query", "dialect"]:
            raise ValueError(
                "LLM chain for QueryCheckerTool must have input variables ['query', 'dialect']"
            )

        return values

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the LLM to check the query."""
        return self.llm_chain.predict(
            query=query,
            dialect=self.db.dialect,
            callbacks=run_manager.get_child() if run_manager else None,
        )

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await self.llm_chain.apredict(
            query=query,
            dialect=self.db.dialect,
            callbacks=run_manager.get_child() if run_manager else None,
        )