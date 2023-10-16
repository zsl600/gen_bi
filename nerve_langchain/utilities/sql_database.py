from langchain.sql_database import SQLDatabase
from typing import Any, Iterable, List, Optional, Sequence, Dict
import re
import pandas as pd
import csv
from sqlalchemy import MetaData, Table, create_engine, inspect, select, text
import re
from sqlalchemy.engine import Engine

def truncate_word(content: Any, *, length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a certain number of words, based on the max string
    length.
    """

    if not isinstance(content, str) or length <= 0:
        return content

    if len(content) <= length:
        return content

    return content[: length - len(suffix)].rsplit(" ", 1)[0] + suffix


class NerveSQLDatabase(SQLDatabase):

    def __init__(
        self,
        engine: Engine,
        schema: Optional[str] = None,
        metadata: Optional[MetaData] = None,
        ignore_tables: Optional[List[str]] = None,
        include_tables: Optional[List[str]] = None,
        sample_rows_in_table_info: int = 3,
        indexes_in_table_info: bool = False,
        custom_table_info: Optional[dict] = None,
        view_support: bool = False,
        max_string_length: int = 300,
        max_result_length: int = 1000
    ):
        
        super(NerveSQLDatabase,self).__init__(
            engine=engine, 
            schema=schema, 
            metadata=metadata, 
            ignore_tables=ignore_tables, 
            include_tables=include_tables,
            sample_rows_in_table_info=sample_rows_in_table_info,
            indexes_in_table_info=indexes_in_table_info,
            custom_table_info=custom_table_info,
            view_support=view_support,
            max_string_length=max_string_length)
        self._max_result_length = max_result_length

    def run(self, command: str, fetch: str = "all") -> str:
        """Execute a SQL command and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        result, columns = self._execute(command, fetch)
        # Convert columns values to string to avoid issues with sqlalchemy
        # truncating text
        if isinstance(result, list):
            res: Sequence = [
                                {key:truncate_word(value, length=self._max_string_length) for key, value in row.items()}
                                for row in result
                            ]
        else:
            res = [{key:truncate_word(value, length=self._max_string_length) for key, value in result.items()}]

        if res:
            result = str(pd.DataFrame.from_dict(res).to_csv(index=False, quoting=csv.QUOTE_MINIMAL))
            string_length = len(re.findall(r'\w+', result))
            if string_length > self._max_result_length:
                return "Result size is too large, use LIMIT to reduce the size"
            else:
                return result
        else:
            return "No results found"
        
    
    def _execute(self, command: str, fetch: Optional[str] = "all") -> (Sequence, List[str]):
        """
        Executes SQL command through underlying engine.

        If the statement returns no rows, an empty list is returned.
        """
        with self._engine.begin() as connection:
            if self._schema is not None:
                if self.dialect == "snowflake":
                    connection.exec_driver_sql(
                        f"ALTER SESSION SET search_path='{self._schema}'"
                    )
                elif self.dialect == "bigquery":
                    connection.exec_driver_sql(f"SET @@dataset_id='{self._schema}'")
                elif self.dialect == "mssql":
                    pass
                else:  # postgresql and compatible dialects
                    connection.exec_driver_sql(f"SET search_path TO {self._schema}")
            cursor = connection.execute(text(command))
            if cursor.returns_rows:
                if fetch == "all":
                    result = cursor.fetchall()
                elif fetch == "one":
                    result = cursor.fetchone()  # type: ignore
                else:
                    raise ValueError("Fetch parameter must be either 'one' or 'all'")
                return result,list(cursor.keys())
        return [],[]
    
    def get_usable_table_names_and_description(self) -> Dict[str,str]:
        """Get names of tables available."""
        list_of_tables = []
        if self._include_tables:
            list_of_tables = sorted(self._include_tables)
        else: 
            list_of_tables = sorted(self._all_tables - self._ignore_tables)

        return {
            table: ((re.compile("COMMENT.*\n").findall(self._custom_table_info[table])[:1] or [""])[0]).replace("COMMENT","").strip() for table in list_of_tables
        }
        


