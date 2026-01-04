import numpy as np
import pandas as pd
from math import log, sqrt
from tqdm.notebook import tqdm

class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus
        self.build_vocab()
        self.build_matrices()

    # Vocabulaire
    def build_vocab(self):
        self.vocab = {}
        idx = 0

        for doc in self.corpus.documents.values():
            words = set(doc.texte.lower().split())
            for w in words:
                if w not in self.vocab:
                    self.vocab[w] = {"id": idx, "tf": 0, "df": 0}
                    idx += 1

    # Matrices TF et TF-IDF
    def build_matrices(self):
        nb_docs = len(self.corpus.documents)
        nb_words = len(self.vocab)

        self.mat_tf = np.zeros((nb_docs, nb_words))

        for i, doc in enumerate(self.corpus.documents.values()):
            words = doc.texte.lower().split()
            for w in words:
                if w in self.vocab:
                    j = self.vocab[w]["id"]
                    self.mat_tf[i][j] += 1

        for w, info in self.vocab.items():
            j = info["id"]
            info["tf"] = self.mat_tf[:, j].sum()
            info["df"] = np.count_nonzero(self.mat_tf[:, j])

        self.mat_tfidf = np.zeros_like(self.mat_tf)

        for w, info in self.vocab.items():
            j = info["id"]
            idf = log(nb_docs / (1 + info["df"]))
            self.mat_tfidf[:, j] = self.mat_tf[:, j] * idf

    def cosine(self, v1, v2):
        num = np.dot(v1, v2)
        den = sqrt(np.dot(v1, v1)) * sqrt(np.dot(v2, v2))
        return num / den if den != 0 else 0

    # Recherche
    def search(self, query, top_n=5):
        q_vec = np.zeros(len(self.vocab))
        for w in query.lower().split():
            if w in self.vocab:
                q_vec[self.vocab[w]["id"]] += 1

        scores = []
        
        for i in range(len(self.corpus.documents)):
            score = self.cosine(q_vec, self.mat_tfidf[i])
            scores.append(score) 


        results = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        data = []
        docs = list(self.corpus.documents.values())

        for i, score in results:
            data.append({
                "document": docs[i].titre,
                "type": docs[i].getType(),
                "score": score
            })

        return pd.DataFrame(data)

    def vocab_dataframe(self):
        data = []
        for mot, info in self.vocab.items():
            data.append({
                "mot": mot,
                "tf": info["tf"],
                "df": info["df"]
            })
        return pd.DataFrame(data).sort_values("tf", ascending=False)

