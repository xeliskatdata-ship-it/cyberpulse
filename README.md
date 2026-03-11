# CyberPulse — Veille automatique & analyse NLP des actualités cyber

## Problématique
Comment automatiser la veille cyber et détecter les sujets émergents
avant qu'ils deviennent des crises ?

## Utilisateur cible
Analystes SOC, consultants cybersécurité, DSI — toute personne qui
surveille les menaces sans vouloir lire 50 sites par jour et 
tout passionné s'intéressant à l'actualité cyber...

## KPIs principaux
- **K1** — Nombre d'articles collectés par jour / par source
- **K2** — Top 10 mots-clés les plus fréquents (7 jours glissants)
- **K3** — Répartition des articles par type de menace

## Architecture technique
Extract → Transform → Load → Visualize

| Phase | Outils |
|---|---|
| Acquisition | Python · Requests · BeautifulSoup · NewsAPI · PRAW |
| Nettoyage | Python · Pandas |
| ETL & Stockage | Airflow · PostgreSQL · SQLAlchemy · dbt |
| Visualisation | Streamlit · Plotly |
| NLP (bonus S5) | Scikit-learn · TF-IDF · LDA · VADER |


## Pipeline — Architecture technique
```mermaid
flowchart LR
    subgraph COLLECTE["🔵 Phase 1 — Collecte"]
        A1[NewsAPI] 
        A2[RSS Feeds\nHackerNews\nBleeping\nZataz\nCISA]
    end

    subgraph TRAITEMENT["🟢 Phase 2 — Nettoyage"]
        B1[Pandas\nSuppr. doublons\nNaN → vide\nNorm. texte]
    end

    subgraph ETL["🟡 Phase 3 — ETL"]
        C1[PostgreSQL\nSQLAlchemy\ndbt\nAirflow DAG]
    end

    subgraph VIZ["🔴 Phase 4 — Visualisation"]
        D1[Streamlit\nPlotly\nFiltres + CSV]
    end

    subgraph NLP["🩵 Phase 5 — NLP"]
        E1[TF-IDF\nLDA\nVADER]
    end

    COLLECTE --> TRAITEMENT --> ETL --> VIZ --> NLP
```

## Structure du projet
```
cyberpulse/
├── data/          # raw/ et cleaned/
├── src/           # scripts Python
├── app/           # application Streamlit
├── db/            # SQL et ETL
├── notebooks/     # exploration
├── pipelines/     # DAGs Airflow
└── README.md
```

## Lancement (à compléter plus tard...)
```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Période de construction du projet à la Wild code School :
10 mars → 23 avril 2026 · Projet solo · Formation Data Analyst

