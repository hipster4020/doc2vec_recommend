import config
import swifter
import json
from pshmodule.utils import filemanager as fm
from gensim.models.doc2vec import Doc2Vec

def main():
    # data load
    df = fm.load(config.df_mecab_morphs_path)
    df.rename(columns={'vec2':'noun2', 'vec5':'noun5'}, inplace=True)

    # model load
    model2 = Doc2Vec.load(config.doc2vec_morphs+"d2v_2_1024.model")
    model5 = Doc2Vec.load(config.doc2vec_morphs+"d2v_5_1024.model")

    # infer vector
    df['vec2'] = df.noun2.swifter.apply(lambda x: list(model2.infer_vector(x)))
    df['vec5'] = df.noun5.swifter.apply(lambda x: list(model5.infer_vector(x)))

    # save
    print("save start")
    # fm.save(config.df_doc2vec_1024, df)
    temp_dict = [{"year": row['year'], "ass_no": row['ass_no'], "user_no": row['user_no'], "vec2": [float(i) for i in row['vec2']], "vec5": [float(i) for i in row['vec5']]} for _, row in df.iterrows()]
    with open(config.df_doc2vec_morphs_1024, 'w', encoding='utf-8') as f:
        for line in temp_dict:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + '\n')
    print("save end")

if __name__ == "__main__":
    main()