import pandas as pd
import csv
from chain import GenBILLMChain
import time
import traceback
import time


def load_data(dataset_location):
    return pd.read_json(dataset_location)

if __name__ == '__main__':
    GEN_BI_DATASET = "gen_bi_dev.json"
    OUTPUT_FILE = "benchmark.csv"
    benchmark_queries = load_data(GEN_BI_DATASET)

    gen_bi_chain = GenBILLMChain("", mock_data=True)

    benchmark_items = []
    for index, row in benchmark_queries.iterrows():
        print(f"index is {index}")
        print(row['question'])
        start = time.time()
        try:
            result = gen_bi_chain.run(row['question'])
            end = time.time()
            benchmark_items.append([row['question'], result['sql_query'], result['output'], end - start])
        except Exception as e:
            traceback.print_exc()
            end = time.time()
            time.sleep(3)
            benchmark_items.append([row['question'], "", end - start])
            pass
    df = pd.DataFrame(benchmark_items, columns=['NLQ', 'PREDICTED SQL', 'PREDICTED ANSWER', 'PREDICTION_TIME'])
    df.to_csv(index=False,quoting=csv.QUOTE_ALL)
    df.to_csv(OUTPUT_FILE, index=False, quoting=csv.QUOTE_ALL)

        
            

