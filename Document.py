from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = "Generic"

    def __str__(self):
        return f"{self.titre}"

    def afficher(self):
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Date :", self.date)
        print("URL :", self.url)
        print("Texte :", self.texte[:200], "...")
    
    def getType(self):
        return self.type
    
    def get_author(self):
        return self.auteur

    def get_title(self):
        return self.titre

    def get_date(self):
        return self.date

    def get_url(self):
        return self.url

    def get_text(self):
        return self.texte

class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_comments):
        super().__init__(titre, auteur, date, url, texte)
        self.nb_comments = nb_comments
        self.type = "Reddit"

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.nb_comments} comments)"


class ArxivDocument(Document):
    def __init__(self, titre, auteurs, date, url, texte):
        super().__init__(titre, ", ".join(auteurs), date, url, texte)
        self.co_auteurs = auteurs
        self.type = "Arxiv"
    
    def __str__(self):
        return f"[Arxiv] {self.titre} ({len(self.co_auteurs)} auteurs)"
