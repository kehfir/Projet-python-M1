from datetime import datetime
import praw
import urllib.request
import xmltodict

from Corpus import Corpus
from Document import RedditDocument, ArxivDocument
from SearchEngine import SearchEngine


# ======================
# Reddit credentials
# ======================
reddit = praw.Reddit(
    client_id='d1Tw8tp5olTmdil0VRXG7g',
    client_secret='RtB3x3GBthG57qgUQrnI0Al6bKkWkw',
    user_agent='Firdaouss Scrapping'
)

BASE_URL = "http://export.arxiv.org/api/query?"

def build_corpus(theme):
    corpus = Corpus(f"Corpus_{theme}")

    # -------- Reddit --------
    subreddit = reddit.subreddit(theme)
    for post in subreddit.hot(limit=10):
        texte = post.selftext.replace("\n", " ")
        doc = RedditDocument(
            titre=post.title,
            auteur=str(post.author),
            date=datetime.fromtimestamp(post.created),
            url=post.url,
            texte=texte,
            nb_comments=post.num_comments
        )
        corpus.add_document(doc)

    # -------- Arxiv --------
    query = f"{BASE_URL}search_query=all:{theme}&start=0&max_results=5"
    with urllib.request.urlopen(query) as url:
        data = xmltodict.parse(url.read())

    for entry in data["feed"]["entry"]:

        if isinstance(entry["author"], list):
            auteurs = [a["name"] for a in entry["author"]]
        else:
            auteurs = [entry["author"]["name"]]

        doc = ArxivDocument(
            titre=entry["title"],
            auteurs=auteurs,
            date=datetime.fromisoformat(entry["published"].replace("Z", "")),
            url=entry["id"],
            texte=entry["summary"].replace("\n", " ")
        )
        corpus.add_document(doc)


    return corpus


if __name__ == "__main__":
    corpus = build_corpus("football")

    print(corpus)
    print("Taille du corpus :", corpus.taille())

    print("\n=== TEST : tri par date ===")
    for doc in corpus.trier_par_date(3):
        print(doc.date, "-", doc)

    print("\n=== TEST : tri par titre ===")
    for doc in corpus.trier_par_titre(3):
        print("titre du document " ,doc.titre)

    print("\n=== TEST : auteurs ===")
    for name, author in corpus.authors.items():
        print(author)
        print("  Taille moyenne :", author.taille_moyenne())

    # Tests statistiques (TD3)
    for doc in corpus.documents.values():
        mots = len(doc.texte.split(" "))
        phrases = len(doc.texte.split("."))
        print(doc.getType(), "| mots:", mots, "| phrases:", phrases)

    # Suppression docs < 100 caractères
    corpus.documents = {
        k: v for k, v in corpus.documents.items() if len(v.texte) >= 100
    }

    # Chaîne globale
    chaine = " ".join(doc.texte for doc in corpus.documents.values())
    print("Longueur chaîne globale :", len(chaine))

    # Sauvegarde
    corpus.save_csv("data/corpus.csv")

print("\n=== TEST : chargement CSV ===")
df = corpus.load_csv("data/corpus.csv")
print(df.head())


print("\n=== TD6 : SEARCH ===")
print(corpus.search("football")[:5])

print("\n=== TD6 : CONCORDE ===")
print(corpus.concorde("football", 20).head())

print("\n=== TD6 : STATS ===")
freq_df = corpus.stats(10)


print("\n=== TD7 : SEARCH ENGINE ===")
engine = SearchEngine(corpus)

resultats = engine.search("football analytics", 5)
print(resultats)

print("\n=== TF / DF pour quelques mots  terme frequency et docuement freauency ===")

'''for mot in ["football", "team", "match","maroc"]:
    if mot in engine.vocab:
        info = engine.vocab[mot]
        print(f"{mot:10s} | TF={info['tf']:6.2f} | DF={info['df']:6.2f}")

'''

print("\n=== VOCABULAIRE TF / DF ===")
print(engine.vocab_dataframe().head(10))


