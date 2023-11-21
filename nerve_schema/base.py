from nerve_schema.schema import schema as nerve_schema
import pandas as pd
import sqlparse

class NerveSchema:

    schema_dataframe: pd.DataFrame = None
    primary_key_dataframe: pd.DataFrame = None
    secondary_key_dataframe: pd.DataFrame = None
    sample_query_dataframe: pd.DataFrame = None

 
    # init method or constructor
    def __init__(self):
        raw_schema_df = pd.DataFrame.from_dict(nerve_schema)
        schema = []
        f_keys = []
        p_keys = []
        sample_qas = []
        for index, row in raw_schema_df.iterrows():
            table_name = row['table_name']
            col_names = row['columns']
            col_types = row['column_types']
            foreign_keys = row.get('foreign_keys', [])
            description = row.get('description', '')
            primary_keys = row.get('primary_keys', [])
            sample_queries = row.get('sample_queries', [])
            #Transpose col_samples from array of sample row to array of sample columns values
            for col_name, col_type in zip(col_names, col_types):
                schema.append([table_name, col_name, col_type, description])
            for primary_key in primary_keys:
                p_keys.append([table_name, primary_key])
            for foreign_key in foreign_keys:
                first, second = foreign_key.split("=")
                first_table, first_column = first.strip().split(".")
                second_table, second_column = second.strip().split(".")
                f_keys.append([first_table, second_table, first_column, second_column])
            for sample_query in sample_queries:
                sample_qas.append([table_name, sample_query["question"], sample_query["answer"]])
        self.schema_dataframe = pd.DataFrame(schema, columns=['table_name', 'column_name', 'type', 'table_description'])
        self.primary_key_dataframe = pd.DataFrame(p_keys, columns=['table_name','primary_key'])
        self.foreign_key_dataframe = pd.DataFrame(f_keys, columns=['first_table_name', 'second_table_name', 'first_table_foreign_key', 'second_table_foreign_key'])
        self.sample_query_dataframe = pd.DataFrame(sample_qas, columns=['table_name', 'question', 'answer'])
            

    def get_table_names(self):
        return list(self.schema_dataframe['table_name'].unique())

    def get_table_info(self, table_name):
        table_info = ""
        table_found = False
        columns = []
        table_comment = ""
        table_constraints = []
        primary_keys = []
        sample_queries_and_answers = []
        
        filtered_schema_df = self.schema_dataframe[self.schema_dataframe['table_name'] == table_name]
        for index, row in filtered_schema_df.iterrows():
            table_found = True
            table_name = row['table_name']
            table_comment = row['table_description']
            columns.append(f"{row['column_name']} {row['type']}")
        
        
        filtered_primary_df = self.primary_key_dataframe[self.primary_key_dataframe['table_name'] == table_name]
        for index, row in filtered_primary_df.iterrows():
            primary_keys.append(row['primary_key'])
        if primary_keys:
            table_constraints.append(f"CONSTRAINT pk_{table_name} PRIMARY KEY ({','.join(primary_keys)})")
        
        filtered_secondary_df = self.foreign_key_dataframe[self.foreign_key_dataframe['first_table_name'] == table_name]
        for index, row in filtered_secondary_df.iterrows():
            table_constraints.append(f"CONSTRAINT fk_{row['first_table_foreign_key']} FOREIGN KEY ({row['first_table_foreign_key']}) REFERENCES {row['second_table_name']}({row['second_table_foreign_key']})")

        filtered_sample_query_df = self.sample_query_dataframe[self.sample_query_dataframe['table_name'] == table_name]
        for index,row in filtered_sample_query_df.iterrows():
            sample_queries_and_answers.append(f"QUESTION: {row['question']}\nANSWER: {row['answer']}\n")

        if table_found:
            table_info = f"CREATE TABLE {table_name} (\n"
            table_info += ",\n".join(columns)
            if table_constraints:
                table_info += ",\n" + ",\n".join(table_constraints)
            table_info += "\n)"
            if table_comment:
                table_info += f"\nCOMMENT '{table_comment}'\n"
            table_info = sqlparse.format(table_info, keyword_case='upper')
            
            # if sample_df is not None:
            #     table_info += "\n\n/*\n"
            #     table_info += f"Sample row(s) from {table_name} table:\n"
            #     table_info += sample_df.replace(r'^\s*$', "None", regex=True).to_csv(sep='\t', index=False)
            #     table_info += "*/\n"

            if sample_queries_and_answers:
                table_info += "\n\n/*\n"
                table_info += f"Sample queries from {table_name} table:\n"
                table_info += "\n\n".join(sample_queries_and_answers)
                table_info += "*/\n"

                
        return table_info

