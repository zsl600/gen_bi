import pandas as pd
import csv
from chain import NerveLLMChain
from langchain.chat_models import AzureChatOpenAI
import time
import os
import traceback
import time


def load_data(dataset_location):
    return pd.read_json(dataset_location)

if __name__ == '__main__':
    NERVE_DATASET = "nerve_dev.json"
    OUTPUT_FILE = "benchmark.csv"
    benchmark_queries = load_data(NERVE_DATASET)

    nerve_chain = NerveLLMChain("", mock_data=True)

    benchmark_items = []
    for index, row in benchmark_queries.iterrows():
        print(f"index is {index}")
        print(row['question'])
        start = time.time()
        try:
            result = nerve_chain.run(row['question'])
            end = time.time()
            benchmark_items.append([row['question'], result['sql_query'], end - start])
        except Exception as e:
            traceback.print_exc()
            end = time.time()
            time.sleep(3)
            benchmark_items.append([row['question'], "", end - start])
            pass
    df = pd.DataFrame(benchmark_items, columns=['NLQ', 'PREDICTED SQL', 'PREDICTION_TIME'])
    df.to_csv(index=False,quoting=csv.QUOTE_ALL)
    df.to_csv(OUTPUT_FILE, index=False, quoting=csv.QUOTE_ALL)

        
            

