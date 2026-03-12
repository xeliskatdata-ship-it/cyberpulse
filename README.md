# CyberPulse — Veille automatique & analyse NLP des actualités cyber

Je suis en formation data analyst et créé un projet en solo afin de me challenger sur un sujet qui me passionne.
Par la même occasion, je souhaitais contribuée à ma petite échelle contribuer pour la communauté des professionnels en cybersécurité.

## Problématique
Comment automatiser la veille cyber et détecter les sujets émergents avant qu'ils deviennent des crises ?

CyberPulse serait une plateforme qui automatiserait une veille en collectant, nettoyant et analysant les actualités cyber en
temps quasi-réel, puis en détectant les tendances émergentes grâce au NLP.

## Utilisateurs cibles

RSSI, analyste SOC : surveiller les menaces sans lire 50 sites/jour
Consultants en cyber : préparer des briefs client avec les tendances récentes
DSI et ses équipes : suivre les vulnérabilités de son secteur
Etudiants cyber – journalistes : explorer les données réelles
Tout citoyen passionné : comme moi envie de s’informer sur les menaces

## KPI visiblent sur la plateforme :

KPI 1 : Nombre d’articles collectés par jour/par source
KPI 2 : Top 10 mots-clés fréquents (7 jours glissants)
KPI 3 : Répartition par type de menace (ransomware, phishing, etc…) 
KPI 4 : Evolution des mentions d’une menace dans le temps
KPI 5 : Nombre d’alertes critiques détectées par semaine
KPI 6 : Top des vulnérabilités les plus mentionnées (CVE -> officiels)

## Sources de données

NewsAPI : Presse cyber agrégée - API REST 
The Hacker News : Articles sécurité - Flux RSS 
BleepingComputer : Incidents & vulnérabilités - Flux RSS 
Zataz : Actualités cyber FR - Flux RSS passionnée par son actualité !
CISA Alerts : Alertes gouvernementales - Flux RSS 


## Architecture technique

A FAIRE VALIDER PAR MA FORMATRICE

Collecte : Python · Requests · BeautifulSoup · NewsAPI · RSS Feeds 
Nettoyage : Python · Pandas 
ETL & Stockage : Airflow · PostgreSQL · SQLAlchemy · dbt 
Visualisation : Streamlit · Plotly 
NLP (Sprint 5) : Scikit-learn · TF-IDF · LDA · VADER (à découvrir..)

## Structure du projet

cyberpulse/
├── data/
│   ├── raw/          # données brutes collectées
│   └── cleaned/      # données nettoyées
├── src/
│   ├── acquisition.py  # collecte NewsAPI + RSS
│   ├── cleaning.py     # nettoyage pandas
│   ├── etl.py          # pipeline ETL
│   ├── nlp.py          # modèles NLP
│   └── utils.py        # fonctions utilitaires
├── app/
│   ├── app.py          # application Streamlit
│   └── pages/          # pages du dashboard
├── db/
│   ├── schema.sql      # structure de la base
│   ├── load_to_db.py   # chargement PostgreSQL
│   └── queries.sql     # requêtes KPIs
├── notebooks/          # exploration & tests
├── pipelines/          # DAGs Airflow
├── docs/
│   └── architecture.png  # schéma visuel
├── requirements.txt
├── .gitignore
└── README.md

## Lancement (à compléter en S4)
en bash : 
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app/app.py

## Planning du projet en 6 sprints ou moins :

S1 : 10 → 16 mars  Cadrage & Architecture 
S2 : 17 → 23 mars  Collecte & Nettoyage 
S3 : 24 → 30 mars  Cloud & Modélisation 
S4 : 31 mars → 6 avril  ETL & Dashboard 
S5 : 7 → 13 avril  NLP & Orchestration 
S6 : 14 → 22 avril  Stabilisation & Démo 
Présentation finale du projet : 23 avril 

