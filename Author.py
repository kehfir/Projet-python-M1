class Author:
    def __init__(self, name):
        self.name = name
        self.nb_docs = 0
        self.production = {}

    def add(self, doc_id, document):
        self.production[doc_id] = document
        self.nb_docs += 1

    def taille_moyenne(self):
        if self.nb_docs == 0:
            return 0
        return sum(len(d.texte) for d in self.production.values()) / self.nb_docs

    def __str__(self):
        return f"{self.name} ({self.nb_docs} documents)"
