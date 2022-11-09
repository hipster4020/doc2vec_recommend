import numpy as np
from pshmodule.utils import filemanager as fm

import config
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def main():
    # data load
    df = fm.load(config.df_vec_path)
    df = df[["ass_no", "user_no", "noun_token"]]
    df["keywords"] = df["noun_token"].apply(lambda x: " ".join(x))
    print(df.head())
    print(df.shape)
    print(
        "------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    )

    # tf-idf
    df = df[:50000]
    tfidf_vec = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = tfidf_vec.fit_transform(df["keywords"])

    # similimarity
    content_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    similar_index = np.argsort(-content_similarity)
    print(f"content_similarity : {content_similarity}")
    print(f"similar_index : {similar_index}")

    # predict


if __name__ == "__main__":
    main()
