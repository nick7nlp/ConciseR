import json
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def load_jsonl(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    return data

def convert_parquent(datas, out_path):
    save_data = []
    for idx, js in enumerate(datas):
        
        system_prompt = """<|startoftext|>A conversation between User and Assistant. The User asks a question, and the Assistant solves it. \
The Assistant first thinks about the reasoning process in the mind and then provides the User with the answer. \
The reasoning process is enclosed within <think> </think> and answer is enclosed within <answer> </answer> tags, respectively, \
i.e., <think> reasoning process here </think> <answer> answer here </answer>. \
Please reason step by step, and put your final answer within \\boxed{}.

User:
{query}

Assistant:
"""
        prompt = system_prompt.replace("{query}", js['query'])
        ojs = {
            "data_source": js['critic_method'],
            "prompt": [{
                "role": "user",
                "content": prompt
                }],
            "ability": "math",
            "reward_model": {
                "style": "rule",
                "ground_truth": str(js['ans_box'])
            },
            "extra_info": {
                'split': 0,
                'index': idx,
                'answer': str(js['ans_box']),
                "question": js['query']
            }
        }
        save_data.append(ojs)
    df = pd.DataFrame(save_data)
    # write to parquet
    pq.write_table(pa.Table.from_pandas(df), out_path)


if __name__ == '__main__':
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='')
    parser.add_argument('--out_path', type=str, default='')
    args = parser.parse_args()
    datas = load_jsonl(args.data_path)
    convert_parquent(datas, args.out_path)
