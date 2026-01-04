import streamlit as st
import pandas as pd
import re
from math import log
from datetime import datetime
import praw
import urllib.request
import xmltodict
from Corpus import Corpus
from Document import RedditDocument, ArxivDocument

# Configuration Streamlit
st.set_page_config(
    page_title="Analyse de corpus",
    layout="wide"
)

st.title("📚 Interface d’analyse de corpus")
st.caption(
    "L'Application couvre TD6, TD7 et TD8 : "
    "et exploration thématique Reddit / ArXiv (TF, DF, TF-IDF)."
)

# Session state
if "corpus_ext" not in st.session_state:
    st.session_state.corpus_ext = None

# Sidebar
st.sidebar.markdown("## 🎛️ Module")

mode = st.sidebar.radio(
    "Choisir le module :",
    [
        "🗳️ Discours politiques",
        "🌐 Reddit / ArXiv (thématique)"
    ]
)

# MODULE DISCOURS POLITIQUES
if mode == "🗳️ Discours politiques":

    # Chargement CSV 
    @st.cache_data
    def load_data():
        return pd.read_csv(
            "discours_US.csv",
            sep="\t",
            engine="python",
            quotechar='"',
            on_bad_lines="skip"
        )

    df = load_data()

    # Nettoyage
    def nettoyer_texte(texte):
        texte = texte.lower()
        texte = re.sub(r"\n", " ", texte)
        texte = re.sub(r"[0-9]", "", texte)
        texte = re.sub(r"[^\w\s]", "", texte)
        return texte

    def construire_tf(df):
        tf = {}
        for texte in df["text"]:
            mots = nettoyer_texte(str(texte)).split()
            for mot in mots:
                tf[mot] = tf.get(mot, 0) + 1
        return tf

    def calcul_tfidf(tf, tf_autre):
        data = {}
        N = 2
        for mot, tf_val in tf.items():
            df_val = 1 + (1 if mot in tf_autre else 0)
            idf = log(1 + N / df_val)
            data[mot] = {
                "TF": tf_val,
                "DF": df_val,
                "TF-IDF": tf_val * idf
            }
        return data

    def top_mots(data, n):
        return (
            pd.DataFrame.from_dict(data, orient="index")
            .reset_index()
            .rename(columns={"index": "mot"})
            .sort_values("TF-IDF", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )

    # Sidebar paramètres 
    st.sidebar.markdown("## ⚙️ Paramètres discours")

    speakers = df["speaker"].dropna().unique()

    speaker_A = st.sidebar.selectbox("Speaker A", speakers)
    speaker_B = st.sidebar.selectbox(
        "Speaker B", speakers,
        index=1 if len(speakers) > 1 else 0
    )

    top_n = st.sidebar.slider(
        "Nombre de mots affichés",
        5, 30, 10
    )

    df_A = df[df["speaker"] == speaker_A]
    df_B = df[df["speaker"] == speaker_B]

    tf_A = construire_tf(df_A)
    tf_B = construire_tf(df_B)

    tfidf_A = calcul_tfidf(tf_A, tf_B)
    tfidf_B = calcul_tfidf(tf_B, tf_A)

    # Affichage
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"{speaker_A}")
        dfA = top_mots(tfidf_A, top_n)
        st.dataframe(dfA)
        st.subheader(f"Scores des mots utilisés par {speaker_A}")
        st.bar_chart(dfA.set_index("mot")["TF-IDF"])

    with col2:
        st.subheader(f"{speaker_B}")
        dfB = top_mots(tfidf_B, top_n)
        st.dataframe(dfB)
        st.subheader(f"Scores des mots utilisés par {speaker_B}")
        st.bar_chart(dfB.set_index("mot")["TF-IDF"])


# MODULE REDDIT / ARXIV

else:
    # Sidebar paramètres 
    st.sidebar.markdown("## 🌐 Reddit / ArXiv")

    theme = st.sidebar.text_input("Thème :", "climate")
    source = st.sidebar.radio("Source :", ["Reddit", "ArXiv"])
    charger = st.sidebar.button("Charger le corpus")
    mot_sidebar = st.sidebar.text_input("Mot à analyser :", "climate")

    st.sidebar.markdown("## 🧭 Navigation")
    st.sidebar.markdown("## 🔢 Affichage")

    max_results = st.sidebar.slider(
        "Nombre maximum d’éléments affichés",
        min_value=5,
        max_value=100,
        value=30,
        step=5
    )

    vue = st.sidebar.radio(
        "Choisir une vue :",
        [
            "Aperçu du corpus",
            "Recherche texte (regex)",
            "Concordancier",
            "Statistiques lexicales (TF/DF)",
            "Recherche TF-IDF"
        ]
    )

    # Chargement Reddit
    def load_reddit_corpus(theme, limit=20):
        reddit = praw.Reddit(
        client_id='d1Tw8tp5olTmdil0VRXG7g',
        client_secret='RtB3x3GBthG57qgUQrnI0Al6bKkWkw',
        user_agent='Firdaouss Scrapping'
    )

        corpus = Corpus(f"Reddit_{theme}")
        subreddit = reddit.subreddit(theme)

        for post in subreddit.hot(limit=limit):
            if not post.selftext or len(post.selftext) < 100:
                continue

            doc = RedditDocument(
                titre=post.title,
                auteur=str(post.author),
                date=datetime.fromtimestamp(post.created),
                url=post.url,
                texte=post.selftext.replace("\n", " "),
                nb_comments=post.num_comments
            )
            corpus.add_document(doc)

        return corpus

    # Chargement ArXiv
    def load_arxiv_corpus(theme, limit=10):
        corpus = Corpus(f"Arxiv_{theme}")

        url = (
            "http://export.arxiv.org/api/query?"
            f"search_query=all:{theme}&start=0&max_results={limit}"
        )

        with urllib.request.urlopen(url) as response:
            data = xmltodict.parse(response.read())

        for entry in data["feed"]["entry"]:
            auteurs = (
                [a["name"] for a in entry["author"]]
                if isinstance(entry["author"], list)
                else [entry["author"]["name"]]
            )

            doc = ArxivDocument(
                titre=entry["title"],
                auteurs=auteurs,
                date=datetime.fromisoformat(entry["published"].replace("Z", "")),
                url=entry["id"],
                texte=entry["summary"].replace("\n", " ")
            )
            corpus.add_document(doc)

        return corpus

    if charger and theme.strip():
        with st.spinner("Chargement du corpus..."):
            if source == "Reddit":
                st.session_state.corpus_ext = load_reddit_corpus(theme)
            else:
                st.session_state.corpus_ext = load_arxiv_corpus(theme)

        st.success(f"{st.session_state.corpus_ext.taille()} documents chargés")

    if not st.session_state.corpus_ext:
        st.info("⬅️ Charge un corpus depuis la barre latérale.")
        st.stop()

    corpus = st.session_state.corpus_ext

    nb_reddit = sum(isinstance(d, RedditDocument) for d in corpus.documents.values())
    nb_arxiv = sum(isinstance(d, ArxivDocument) for d in corpus.documents.values())

    st.sidebar.markdown("## ℹ️ Infos corpus")
    st.sidebar.write(f"{corpus.nom}")
    st.sidebar.write(f"Total : {corpus.taille()}")
    st.sidebar.write(f"Reddit : {nb_reddit}")
    st.sidebar.write(f"ArXiv : {nb_arxiv}")

    # TF-IDF par document 
    def analyser_documents(corpus, mot):
        docs = list(corpus.documents.values())
        data = []

        df_val = sum(1 for d in docs if mot.lower() in d.texte.lower())

        for doc in docs:
            tf = doc.texte.lower().split().count(mot.lower())
            if tf == 0:
                continue

            idf = log(1 + len(docs) / (1 + df_val))
            tfidf = tf * idf

            data.append({
                "titre": doc.titre,
                "auteur": getattr(doc, "auteur", "—"),
                "TF": tf,
                "DF": df_val,
                "TF-IDF": round(tfidf, 4),
                "url": doc.url
            })

        return pd.DataFrame(data)

    # Vues
    if vue == "Aperçu du corpus":
        rows = []
        for i, d in corpus.documents.items():
            rows.append({
                "id": i,
                "titre": d.titre,
                "auteur": getattr(d, "auteur", "—"),
                "type": d.getType(),
                "url": d.url,
                "extrait": d.texte[:120] + "..."
            })
        st.dataframe(pd.DataFrame(rows).head(max_results))

    elif vue == "Recherche texte (regex)":
        motif = st.text_input("Motif regex :", "climate")
        st.dataframe(corpus.search_regex(motif, max_results))

    elif vue == "Concordancier":
        df_conc = corpus.concorde(mot_sidebar, context=40)
        st.dataframe(df_conc.head(max_results))

    elif vue == "Statistiques lexicales (TF/DF)":
        vocab = corpus.vocabulaire()
        df_stats = pd.DataFrame([
            {"mot": m, "TF": v["tf"], "DF": v["df"]}
            for m, v in vocab.items()
        ]).sort_values("TF", ascending=False)
        #st.dataframe(df_stats.head(50))
        st.dataframe(df_stats.head(max_results))

    elif vue == "Recherche TF-IDF":
        st.dataframe(analyser_documents(corpus, mot_sidebar).head(max_results))


