#CyberPulse — Veille automatique & analyse des actualités cyber

Mon projet solo — Formation Data Analyst   
L'idée sera d'automatiser la veille cyber et détecter les menaces émergentes via un dashboard Streamlit.
Problématique : Comment automatiser la veille cyber et détecter les sujets émergents avant qu'ils deviennent des crises ?

#Utilisateurs cibles

Analyste SOC / RSSI · Consultant cyber · DSI / CTO · Étudiant / Chercheur · Citoyen passionné

#KPIs

| K1 | Articles collectés par jour / par source | Barres groupées |
| K2 | Top 10 mots-clés (7 jours glissants) | Histogramme horizontal |
| K3 | Répartition par type de menace | Camembert / Treemap |
| K4 | Évolution des mentions d'une menace | Courbe temporelle + filtre |
| K5 | Alertes critiques par semaine | Barres + seuil d'alerte |
| K6 | Top CVE les plus mentionnées | Tableau classé + histogramme |

#Sources de données

| NewsAPI | API REST 
| The Hacker News | Flux RSS 
| BleepingComputer | Flux RSS 
| Zataz | Flux RSS 
| CISA Alerts | Flux RSS 

#Architecture

Collecte    →    Nettoyage    →    ETL / PostgreSQL    →    Dashboard    →    NLP bonus
Python           Pandas            raw_articles              Streamlit        TF-IDF
NewsAPI                            stg_articles              Plotly           VADER
RSS Feeds                          mart_kpis                                  LDA
                                   Airflow · dbt
                                   Docker

#Structure du projet

cyberpulse/
├── data/
│   ├── raw/                    <- articles bruts (NewsAPI + RSS)
│   └── cleaned/                <- données nettoyées
├── src/
│   ├── acquisition.py          <- collecte 5 sources          
│   ├── cleaning.py             <- nettoyage pandas            
│   ├── etl.py                  <- pipeline ETL
│   ├── nlp.py                  <- TF-IDF / VADER / LDA (BONUS / OPTIONNEL)       
│   └── utils.py                <- fonctions utilitaires
├── app/
│   ├── app.py                  <- dashboard Streamlit — 6 KPIs
│   └── pages/                  <- une page par KPI
├── db/
│   ├── schema.sql              <- tables PostgreSQL
│   ├── load_to_db.py           <- chargement SQLAlchemy
│   └── queries.sql             <- requêtes KPIs
├── dbt/
│   └── models/
│       ├── staging/            <- stg_articles.sql
│       └── mart/               <- mart_kpis.sql
├── pipelines/
│   └── dag_cyberpulse.py       <- DAG Airflow quotidien
├── notebooks/
├── docker-compose.yml          <- PostgreSQL + Airflow + Streamlit
├── .env                       
├── requirements.txt
└── README.md

#Règles de nettoyage 

Script : `src/cleaning.py`  
Entrée : `data/raw/articles_YYYY-MM-DD.csv` — 184 articles · 6 colonnes  
Sortie : `data/cleaned/articles_cleaned_YYYY-MM-DD.csv` — 174 articles · 9 colonnes

| 1 | Suppression doublons | Sur `url` puis sur `title` | 10 supprimés |
| 2 | Valeurs manquantes | `description` NaN → `''` · `title` NaN → `'Sans titre'` | 10 NaN → 0 |
| 3 | Normalisation dates | `2026-03-12T15:40:00Z` → `2026-03-12 15:40:00` | 174 OK |
| 4 | Nettoyage texte | Suppression HTML · entités · caractères de contrôle · espaces multiples · troncature 500 chars | 174 traités |
| 5 | Colonne `published_date` | Date seule `YYYY-MM-DD` extraite de `published_at` | Créée |
| 6 | Colonne `content_length` | Longueur de la description en caractères | Créée |
| 7 | Colonne `category` | Type de menace détecté par mots-clés | Créée |

#Catégories de menaces (colonne créée pour les mots-clés)

| `ransomware` | ransomware, ransom, lockbit, blackcat, ryuk, conti |
| `phishing` | phishing, spear-phishing, credential, spoofing, smishing |
| `vulnerability` | vulnerability, cve, patch, exploit, zero-day, rce |
| `malware` | malware, trojan, backdoor, spyware, rootkit, botnet, worm |
| `apt` | apt, nation-state, threat actor, campaign, espionage |
| `ddos` | ddos, denial of service, flood |
| `data_breach` | data breach, leak, exposed, stolen data, exfiltration |
| `supply_chain` | supply chain, third-party, dependency |
| `general` | Aucun mot-clé trouvé |

#Distribution des articles par menaces

general        : 83 articles
vulnerability  : 46 articles
malware        : 13 articles
phishing       : 12 articles
ransomware     :  8 articles
supply_chain   :  5 articles
data_breach    :  4 articles
apt            :  3 articles


#Etat d'avancement du projet :
| Semaine 1 → 16 mars | Cadrage & Architecture (fait)
| Semaine 2 | 17 → 23 mars | Collecte réelle & Nettoyage : en cours

