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
