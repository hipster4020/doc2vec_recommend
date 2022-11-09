import re
import json
import config
from tqdm import tqdm
import pandas as pd
import numpy as np
import swifter
from collections import defaultdict, deque

def main():
    # data load
    print("data load")
    data = []
    with open(config.df_doc2vec_morphs_1024, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.rstrip('\n|\r')))
    df = pd.DataFrame(data)
    print(df.head())
    
    # creating input data form
    print("creating input data form")
    df.sort_values(by=["user_no", "ass_no"], inplace=True) 
    df.reset_index(inplace=True)
    del df['index']
    print(df.head())
    
    user_dict = defaultdict(list)
    for k, v in tqdm(enumerate(df.iterrows())):
        user_dict[v[1]['user_no']].append(v[1]['vec2'])
    
    # input form
    print("input form")
    result = defaultdict(list)

    for k, v in tqdm(user_dict.items()):
        data = []
        data = deque(data)

        for kk, vv in enumerate(v):
            temp = []
            if len(data) > 0:
                # padding 채우기
                if len(data) < 5:
                    for _ in range(5 - len(data)):
                        data.appendleft([0 for _ in range(1024)])

                temp.append(list(data))
                temp.append(vv)

                result[f"{k}_{kk}"].append(temp)
                data.popleft()

            data.append(vv) 
            
    df = pd.DataFrame.from_dict(result, orient='index')
    df.reset_index(inplace=True)
    
    # make user_no
    print("make user_no")
    df.rename(columns={0:'data'}, inplace=True)
    df.rename(columns={'index':'origin_user_no'}, inplace=True)
    
    def make_user_no(x):
        result = ""
        try:
            result = x[:x.index('_')]
        except Exception as e:
            print(x)
            print(e)
        return result
    
    df['user_no'] = df.origin_user_no.apply(make_user_no)
    del df['origin_user_no']
    print(df.head())
    
    # checkpoints save
    print("checkpoints save")
    df.to_json(config.train_morphs_ckp, orient='records')
    
    df = pd.read_json(config.train_morphs_ckp, orient='records')
    df.rename(columns={'data':'content'}, inplace=True)
    print(df.head())
    print(df.shape)
    
    # label 만들기
    df['label'] = df.content.apply(lambda x: x[-1])
    df['data'] = df.content.apply(lambda x: x[:-1])
    df['data2'] = df.data.apply(lambda x: np.squeeze(np.array(x)).tolist())
    df = df[['data2', 'label', 'user_no']]
    df.rename(columns={'data2':'content'}, inplace=True)

    print(df.head(10))
    print(f"content : {np.array(df.content[2]).shape}")
    print(f"label : {np.array(df.label[2]).shape}")
    
    df = df[['content', 'label']]
    
    # json save
    print("json save")
    temp_dict = [{"input": row['content'], "target": row['label']} for _, row in df.iterrows()]
    with open(config.train_data, 'w', encoding='utf-8') as f:
        for line in temp_dict:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + '\n')
    print(df.head())
    
    
    
if __name__ == "__main__":
    main()