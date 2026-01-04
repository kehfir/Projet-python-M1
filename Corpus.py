import pandas as pd
import re
from collections import Counter , defaultdict

class Corpus:
    _instance = None  

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
        return cls._instance

    def __init__(self, nom):
        self.nom = nom
        self.documents = {}
        self.authors = {}
        self.id_document = 0

    def add_document(self, doc):
        self.documents[self.id_document] = doc

        if doc.auteur not in self.authors:
            from Author import Author
            self.authors[doc.auteur] = Author(doc.auteur)

        self.authors[doc.auteur].add(self.id_document, doc)
        self.id_document += 1

    def get_author(self, doc_id):
        if doc_id in self.documents:
            return getattr(self.documents[doc_id], "auteur", None)
        return None

    
    def taille(self):
        return len(self.documents)

    def trier_par_date(self, n=5):
        docs = sorted(self.documents.values(), key=lambda d: d.date, reverse=True)
        return docs[:n]

    def trier_par_titre(self, n=5):
        docs = sorted(self.documents.values(), key=lambda d: d.titre)
        return docs[:n]

    def save_csv(self, path):
        data = []
        for i, doc in self.documents.items():
            data.append([i, doc.texte, doc.getType()])
        df = pd.DataFrame(data, columns=["id", "texte", "origine"])
        df.to_csv(path, sep="\t", index=False)

    def load_csv(self, path):
        df = pd.read_csv(path, sep="\t")
        return df
