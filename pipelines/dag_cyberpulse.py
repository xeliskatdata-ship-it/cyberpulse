"""
CyberPulse — DAG Airflow
Collecte automatique quotidienne des articles cyber

Pipeline :
  1. Collecte  →  NewsAPI + 4 flux RSS
  2. Nettoyage →  pandas
  3. Chargement →  PostgreSQL
  4. Transformation → dbt
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Ajouter src/ au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ─────────────────────────────────────────────
# Configuration du DAG
# ─────────────────────────────────────────────
default_args = {
    'owner': 'cyberpulse',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 17),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

dag = DAG(
    dag_id='cyberpulse_daily_pipeline',
    default_args=default_args,
    description='Collecte quotidienne des articles cyber + ETL + dbt',
    schedule_interval='0 6 * * *',  # Tous les jours à 6h00
    catchup=False,
    tags=['cyberpulse', 'collecte', 'etl'],
)

# ─────────────────────────────────────────────
# Fonctions Python (à compléter en S2/S3)
# ─────────────────────────────────────────────

def task_collect():
    """Étape 1 — Collecte des articles depuis NewsAPI + 4 flux RSS"""
    # TODO S2 : importer et lancer acquisition.py
    print("Collecte en cours — NewsAPI + The Hacker News + BleepingComputer + Zataz + CISA")
    # from acquisition import collect_all
    # collect_all()

def task_clean():
    """Étape 2 — Nettoyage pandas des données brutes"""
    # TODO S2 : importer et lancer cleaning.py
    print("Nettoyage en cours — suppression doublons, NaN, normalisation texte")
    # from cleaning import clean_all
    # clean_all()

def task_load():
    """Étape 3 — Chargement des données nettoyées dans PostgreSQL"""
    # TODO S3 : importer et lancer load_to_db.py
    print("Chargement en cours — PostgreSQL via SQLAlchemy")
    # from etl import load_to_db
    # load_to_db()

# ─────────────────────────────────────────────
# Tâches du DAG
# ─────────────────────────────────────────────

t1_collect = PythonOperator(
    task_id='collecte_articles',
    python_callable=task_collect,
    dag=dag,
)

t2_clean = PythonOperator(
    task_id='nettoyage_donnees',
    python_callable=task_clean,
    dag=dag,
)

t3_load = PythonOperator(
    task_id='chargement_postgres',
    python_callable=task_load,
    dag=dag,
)

t4_dbt = BashOperator(
    task_id='transformations_dbt',
    bash_command='cd /app && dbt run --project-dir dbt/ --profiles-dir dbt/',
    dag=dag,
)

# ─────────────────────────────────────────────
# Ordre d'exécution
# ─────────────────────────────────────────────
# Collecte → Nettoyage → Chargement → dbt
t1_collect >> t2_clean >> t3_load >> t4_dbt
