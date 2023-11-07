"""Toolkit for interacting with an SQL database."""
from typing import List

from pydantic import Field

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools import BaseTool
from nerve_langchain.tools.nerve_sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
    ChartDecisionTool
)
from langchain.utilities.sql_database import SQLDatabase
from langchain.tools.python.tool import PythonREPLTool


class SQLDatabaseToolkit(BaseToolkit):
    """Toolkit for interacting with SQL databases."""

    db: SQLDatabase = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)
    top_k: int = Field(default=10)

    @property
    def dialect(self) -> str:
        """Return string representation of SQL dialect to use."""
        return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        list_sql_database_tool = ListSQLDatabaseTool(db=self.db)
        info_sql_database_tool_description = (
            "Input to this tool is a comma-separated list of tables, output is the "
            "schema and sample rows for those tables. "
            "Be sure that the tables actually exist by calling "
            f"{list_sql_database_tool.name} first! "
            "Example Input: table1, table2, table3"
        )
        info_sql_database_tool = InfoSQLDatabaseTool(
            db=self.db, description=info_sql_database_tool_description
        )
        query_sql_database_tool_description = (
            "Input to this tool is a detailed and correct SQL query, output is a "
            "result from the database in csv format along with the headers. If the query is not correct, an error message "
            "will be returned. If an error is returned, rewrite the query, check the "
            "query, and try again. If you encounter an issue with Unknown column "
            f"'xxxx' in 'field list', using {info_sql_database_tool.name} "
            "to query the correct table fields."
        )
        query_sql_database_tool = QuerySQLDataBaseTool(
            db=self.db, description=query_sql_database_tool_description
        )

        python_repl_tool_description: str = (
            "A Python shell. Use this to execute python commands in order to generate charts. "
            "Input should be a valid python command in triple quotation. "
            "Use this to generate charts images stored locally using pandas dataframe. "
            "Use plain format for the y-axis using matplotlib's ticklabel_format. "
            "Use different colours to make the chart interesting. "
            "Use bbox_inches='tight' when using matplotlib's savefig. "
            "Use the format uuid-v4 for the file name. "
            "Print the file name using python function print() after generating the chart. "
        )
        python_repl_tool = PythonREPLTool(description=python_repl_tool_description)

        return [
            query_sql_database_tool,
            info_sql_database_tool,
            list_sql_database_tool,
            python_repl_tool,
        ]