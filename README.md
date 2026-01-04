# 📚 Analyse et Exploration de Corpus Textuels

**Kehailou Firdaouss** -- Master 1 Informatique

---

## Objectif du projet

Ce projet a pour objectif de développer une application interactive d’analyse de corpus textuels couvrant plusieurs travaux dirigés (TD6 à TD10).

Il permet notamment :

- l’analyse de discours politiques américains  
- l’exploration de corpus thématiques issus de **Reddit** et **ArXiv**  
- le calcul et la visualisation de statistiques lexicales (**TF**, **DF**, **TF-IDF**)  
- la recherche textuelle et la visualisation contextuelle (**concordancier**)  

L’interface est réalisée avec **Streamlit**, afin de proposer une visualisation claire et interactive.

## Contenu fonctionnel

### Module 1 — Discours politiques

- Chargement d’un fichier CSV (`discours_US.csv`)
- Sélection de deux *speakers*
- Calculs comparatifs :
  - **TF** (Term Frequency)
  - **DF** (Document Frequency)
  - **TF-IDF**
- Visualisations :
  - tableaux de mots discriminants
  - graphiques TF-IDF

### Module 2 — Reddit / ArXiv

- Chargement dynamique de corpus thématiques
- Exploration à travers plusieurs vues :
  - aperçu du corpus
  - recherche textuelle (expressions régulières)
  - concordancier
  - statistiques lexicales (**TF / DF**)
  - recherche **TF-IDF** par document

- Affichage d’informations globales :
  - nombre total de documents
  - répartition entre **Reddit** et **ArXiv**

## Concepts abordés

- Programmation Orientée Objet (**POO**)
- Pattern **Singleton** (classe `Corpus`)
- Nettoyage et normalisation de texte
- Recherche par expressions régulières
- Concordancier
- Statistiques lexicales
- Calculs **TF / DF / TF-IDF**
- API **Reddit** (PRAW)
- API **ArXiv**
- Visualisation interactive avec **Streamlit**

