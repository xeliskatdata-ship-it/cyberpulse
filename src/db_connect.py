# db_connect.py -- Connexion PostgreSQL partagee entre toutes les pages KPI
# Cache TTL 3600s (1h) aligne sur le cron GitHub Actions -- force_refresh() vide tout
# Dual mode : st.secrets (Streamlit Cloud) ou .env (Docker local)

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Fenetres glissantes -- source de verite unique pour toutes les pages
WINDOW_MAP_DAYS = 90   # Carte des menaces (patterns geopolitiques)
WINDOW_KPI_DAYS = 30   # Pages KPI (indicateurs operationnels)

# Fenetre de chargement SQL -- borne l'egress des marts temporelles
# Aucun KPI ne regarde au-dela de 90j -> on coupe la remontee a la source
LOAD_WINDOW_DAYS  = 90
LOAD_WINDOW_WEEKS = 13   # mart_k5 est agrege en semaines

# TTL cache aligne sur le cron horaire (marts refresh max 1x/h)
# Etait a 120s -> 30 rechargements inutiles par heure -> quota Neon exploser
CACHE_TTL = 3600

# -- Connexion dual Cloud / Local --
if "postgres" in st.secrets:
    s = st.secrets["postgres"]
    DATABASE_URL = (
        f"postgresql+psycopg2://{s['user']}:{s['password']}"
        f"@{s['host']}:{s.get('port', 5432)}/{s['dbname']}"
        f"?sslmode={s.get('sslmode', 'require')}"
    )
else:
    DB_USER     = os.getenv("POSTGRES_USER",     "cyberpulse")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cyberpulse123")
    DB_NAME     = os.getenv("POSTGRES_DB",       "cyberpulse_db")
    DB_HOST     = os.getenv("POSTGRES_HOST",     "localhost")
    DB_PORT     = os.getenv("POSTGRES_PORT",     "5432")
    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


# -- Helper pour eviter la repetition query -> df -> cast date --
def _query(sql, params=None, date_cols=None):
    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params or {})
    for col in (date_cols or []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k1():
    # Fenetre glissante 90j -> evite de tirer 1 an d'historique a chaque refresh
    return _query("""
        SELECT published_date, source, nb_articles
        FROM mart_k1
        WHERE published_date IS NOT NULL
          AND published_date >= CURRENT_DATE - INTERVAL '1 day' * :days
        ORDER BY published_date DESC
    """, params={"days": LOAD_WINDOW_DAYS}, date_cols=["published_date"])


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k2():
    return _query("""
        SELECT keyword, category, sub_category,
               period_days, occurrences, article_count, source_count
        FROM mart_k2
        ORDER BY period_days, occurrences DESC
    """)


# Bug corrige : le double @st.cache_data d'origine a ete supprime
@st.cache_data(ttl=CACHE_TTL)
def get_stg_articles(keyword=None, limit=5000, window_days=None):
    # window_days : fenetre glissante en jours (None = pas de filtre temporel)
    # Utilise WINDOW_MAP_DAYS pour la carte, WINDOW_KPI_DAYS pour les KPI
    base = """
        SELECT source, title, description, url,
               published_date, category, content_length
        FROM stg_articles
        WHERE published_date IS NOT NULL
    """

    # Filtre fenetre glissante optionnel
    window_clause = " AND published_date >= CURRENT_DATE - INTERVAL '1 day' * :window" if window_days else ""

    if keyword:
        sql = base + window_clause + """
              AND (LOWER(title) LIKE :kw OR LOWER(description) LIKE :kw)
            ORDER BY published_date DESC LIMIT :limit
        """
        params = {"kw": f"%{keyword.lower()}%", "limit": limit}
    else:
        sql = base + window_clause + " ORDER BY published_date DESC LIMIT :limit"
        params = {"limit": limit}

    if window_days:
        params["window"] = window_days

    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    df["published_date"] = pd.to_datetime(df["published_date"])
    return df


@st.cache_data(ttl=CACHE_TTL)
def get_articles_by_keyword(keyword, period_days=7):
    # Utilisee par KPI2 au clic sur une bulle du scatter
    sql = """
        SELECT title, source, url, published_date, category
        FROM stg_articles
        WHERE published_date >= NOW() - INTERVAL '1 day' * :days
          AND (LOWER(title) LIKE :kw OR LOWER(description) LIKE :kw)
        ORDER BY published_date DESC
        LIMIT 50
    """
    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn, params={
            "days": period_days, "kw": f"%{keyword.lower()}%",
        })
    df["published_date"] = pd.to_datetime(df["published_date"])
    return df


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k3():
    # Pas de colonne date dans mart_k3 -> pas de fenetre, mais table petite par construction
    return _query("""
        SELECT category, source, nb_articles
        FROM mart_k3
        ORDER BY category, nb_articles DESC
    """)


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k4():
    # Fenetre 90j idem K1
    return _query("""
        SELECT published_date, category, nb_mentions
        FROM mart_k4
        WHERE published_date >= CURRENT_DATE - INTERVAL '1 day' * :days
        ORDER BY published_date DESC, nb_mentions DESC
    """, params={"days": LOAD_WINDOW_DAYS}, date_cols=["published_date"])


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k5():
    # Fenetre 13 semaines (~90j) - agrege hebdomadaire
    return _query("""
        SELECT semaine, category, nb_alertes
        FROM mart_k5
        WHERE semaine >= CURRENT_DATE - INTERVAL '1 week' * :weeks
        ORDER BY semaine DESC, nb_alertes DESC
    """, params={"weeks": LOAD_WINDOW_WEEKS}, date_cols=["semaine"])


@st.cache_data(ttl=CACHE_TTL)
def get_mart_k6():
    # Petite table (liste de CVE + compteurs) -> pas de fenetre necessaire
    return _query("""
        SELECT cve, nb_mentions
        FROM mart_k6
        ORDER BY nb_mentions DESC
    """)


@st.cache_data(ttl=CACHE_TTL)
def get_sidebar_counts():
    # Mutualise en 1 seule requete -> 1 round-trip au lieu de 5 par session x page
    sql = """
        SELECT
            (SELECT COALESCE(SUM(nb_articles), 0) FROM mart_k1) AS k1,
            (SELECT COUNT(*) FROM mart_k2 WHERE period_days = 7 AND occurrences > 0) AS k2,
            (SELECT COUNT(DISTINCT category) FROM mart_k3) AS k3,
            (SELECT COALESCE(SUM(nb_alertes), 0) FROM mart_k5) AS k5,
            (SELECT COUNT(*) FROM mart_k6) AS k6
    """
    try:
        with get_engine().connect() as conn:
            row = conn.execute(text(sql)).mappings().first()
        return dict(row) if row else {}
    except Exception:
        # Fallback : si une table manque (dbt pas encore lance), on retourne ce qui a marche
        return {}


def force_refresh():
    # Vide le cache Streamlit -- force rechargement depuis PostgreSQL
    for fn in (get_mart_k1, get_mart_k2, get_mart_k3, get_mart_k4,
               get_mart_k5, get_mart_k6, get_stg_articles,
               get_articles_by_keyword, get_sidebar_counts):
        fn.clear()