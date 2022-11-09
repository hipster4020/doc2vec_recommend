import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from konlpy.tag import Mecab
from pshmodule.utils import filemanager as fm

import config

m = Mecab("/usr/local/lib/mecab/dic/mecab-ko-dic")


def noun_token(x):
    noun = m.nouns(x)
    result = ",".join(noun)
    return result


def doc2vec(tagged_data):
    model = Doc2Vec(tagged_data, vector_size=128, window=3, min_count=1, workers=4)
    model.save(config.model_path)
    print("Model Saved")


def main():
    # data load
    df = fm.load(config.df_final_pickle_path)

    # mecab
    df["noun_token"] = df.content.apply(noun_token)

    tagged_data = [
        TaggedDocument(words=_d, tags=[str(i)]) for i, _d in enumerate(df.noun_token)
    ]

    # doc2vec train & save
    doc2vec(tagged_data)

    # model load
    model = Doc2Vec.load(config.model_path)
    print(model)

    # vectorizing
    df = df[["content", "ass_no", "user_no", "noun_token"]]
    df["noun_token"] = df.noun_token.apply(lambda x: x.split(","))

    def sim(content):
        similar_doc = list(model.infer_vector(content))
        return similar_doc

    df["vec"] = df.noun_token.apply(sim)
    df["research_yn"] = 1

    print(df.head())
    fm.save(config.df_vec_path, df)


if __name__ == "__main__":
    main()
