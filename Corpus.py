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

    # TD6 – Chaîne globale
    def build_global_text(self):
        if not hasattr(self, "global_text"):
            self.global_text = " ".join(
                doc.texte for doc in self.documents.values()
            ).lower()
        return self.global_text

      # TD6 – Recherche regex
    def search(self, keyword):
        text = self.build_global_text()
        pattern = re.compile(keyword.lower())
        return [m.group() for m in pattern.finditer(text)]

    # TD6 – Concordancier
    def concorde(self, keyword, context=30):
        text = self.build_global_text()
        results = []

        for match in re.finditer(keyword.lower(), text):
            start = max(match.start() - context, 0)
            end = min(match.end() + context, len(text))

            results.append({
                "contexte_gauche": text[start:match.start()],
                "mot": match.group(),
                "contexte_droit": text[match.end():end]
            })

        return pd.DataFrame(results)

    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = re.sub(r"[0-9]", "", texte)
        texte = re.sub(r"[^\w\s]", "", texte)
        return texte

    def stats(self, n=10):
        mots = []

        for doc in self.documents.values():
            clean = self.nettoyer_texte(doc.texte)
            mots.extend(clean.split())

        counter = Counter(mots)
        vocab_size = len(counter)

        freq_df = pd.DataFrame(
            counter.items(), columns=["mot", "frequence"]
        ).sort_values("frequence", ascending=False)

        print("Nombre de mots différents :", vocab_size)
        print(f"Top {n} mots les plus fréquents :")
        print(freq_df.head(n))

        return freq_df
    
    def search_regex(self, motif, max_res=10):
        """
        Recherche un motif regex dans tous les documents du corpus.
        Retourne un DataFrame avec les occurrences trouvées.
        """
        results = []
        pattern = re.compile(motif, re.IGNORECASE)

        for doc_id, doc in self.documents.items():
            matches = pattern.findall(doc.texte)

            if matches:
                results.append({
                    "document": doc.titre,
                    "auteur": getattr(doc, "auteur", "—"),
                    "nb_occurrences": len(matches),
                    "extrait": doc.texte[:120] + "..."
                })

            if len(results) >= max_res:
                break

        return pd.DataFrame(results)

    def vocabulaire(self):
        """
        Construit le vocabulaire du corpus avec TF et DF.
        Retourne un dictionnaire :
        {
            mot: {"tf": valeur, "df": valeur}
        }
        """
        tf = defaultdict(int)
        df = defaultdict(int)

        for doc in self.documents.values():
            mots_doc = set()

            for mot in doc.texte.lower().split():
                tf[mot] += 1
                mots_doc.add(mot)

            for mot in mots_doc:
                df[mot] += 1

        vocab = {}
        for mot in tf:
            vocab[mot] = {
                "tf": tf[mot],
                "df": df[mot]
            }

        return vocab


    def __repr__(self):
        return f"Corpus {self.nom} - {self.taille()} documents"
