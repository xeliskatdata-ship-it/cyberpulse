# load_to_db.py -- Charge les CSV raw dans PostgreSQL (mode batch, low egress)
# Usage : python db/load_to_db.py
# Seule raw_articles est alimentee ici -- stg + mart sont geres par dbt

import glob
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# -- Connexion PostgreSQL --
DB_USER     = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME     = os.getenv("POSTGRES_DB")
DB_HOST     = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT     = os.getenv("POSTGRES_PORT", "5432")

_MISSING = [k for k, v in {
    "POSTGRES_USER": DB_USER, "POSTGRES_PASSWORD": DB_PASSWORD, "POSTGRES_DB": DB_NAME,
}.items() if not v]

if _MISSING:
    raise EnvironmentError(
        f"Variables manquantes : {', '.join(_MISSING)}\n"
        "Ajoutez-les dans les secrets GitHub Actions + Streamlit."
    )

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

RAW_COLS = ["source", "title", "description", "url", "published_at", "collected_at"]


def _get_engine():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    log.info("Connexion PostgreSQL OK (%s:%s/%s)", DB_HOST, DB_PORT, DB_NAME)
    return engine


# ---------------------------------------------------
# 1. LECTURE + DEDUP INTRA-BATCH (pas de network)
# ---------------------------------------------------
def _read_all_csv():
    files = sorted(glob.glob("data/raw/articles_*.csv"))
    if not files:
        log.warning("Aucun fichier dans data/raw/")
        return pd.DataFrame(columns=RAW_COLS)

    # Concat de tous les CSV en 1 seul DataFrame -> on evite les boucles
    dfs = []
    for fp in files:
        d = pd.read_csv(fp, usecols=lambda c: c in RAW_COLS)
        for col in RAW_COLS:
            if col not in d.columns:
                d[col] = None
        dfs.append(d[RAW_COLS])
        log.info("read | %s : %d lignes", os.path.basename(fp), len(d))

    df = pd.concat(dfs, ignore_index=True)

    # Ransomware.live envoie NaN sur url -> obligatoire avant INSERT (m'a bloque sur Streamlit)
    df = df.fillna('')

    # Dedup intra-batch : URL si presente, sinon (source, title)
    df['_key'] = df['url'].where(df['url'].str.strip() != '', df['source'] + '||' + df['title'])
    df = df.drop_duplicates(subset=['_key'], keep='first').drop(columns=['_key'])

    log.info("concat + dedup intra-batch : %d lignes candidates", len(df))
    return df


# ---------------------------------------------------
# 2. BULK INSERT avec ON CONFLICT DO NOTHING
#    -> Postgres gere la dedup cote serveur (via index uniques partiels)
#    -> 1 seule requete par chunk au lieu de N
# ---------------------------------------------------
def _bulk_insert(df, engine, chunk_size=500):
    if df.empty:
        log.info("Rien a inserer.")
        return 0

    # Convertit le DF en liste de tuples (format execute_values)
    rows = list(df[RAW_COLS].itertuples(index=False, name=None))

    sql = """
        INSERT INTO raw_articles (source, title, description, url, published_at, collected_at)
        VALUES %s
        ON CONFLICT DO NOTHING
    """

    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        # execute_values groupe les lignes en 1 INSERT multi-values par page
        # page_size = taille du batch, compromis memoire / taille requete
        execute_values(cur, sql, rows, page_size=chunk_size)
        inserted = cur.rowcount  # nb de lignes reellement inserees (hors conflits)
        raw.commit()
        cur.close()
    finally:
        raw.close()

    log.info("bulk insert : %d nouvelles / %d ignorees (ON CONFLICT)", inserted, len(rows) - inserted)
    return inserted


# ---------------------------------------------------
# 3. VERIFICATION (1 seul SELECT COUNT par table)
# ---------------------------------------------------
def _check_counts(engine):
    log.info("-" * 40)
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM raw_articles")).scalar()
        log.info("  %-20s : %d lignes", "raw_articles", n)

        for name in ("stg_articles", "mart_k1", "mart_k3", "mart_k6"):
            try:
                n = conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
                log.info("  %-20s : %d lignes", name, n)
            except Exception:
                log.info("  %-20s : pas encore cree (lance dbt run)", name)
    log.info("-" * 40)


# ---------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------
def main():
    log.info("=" * 40)
    log.info("CyberPulse -- Chargement en base (batch mode, low egress)")
    log.info("=" * 40)

    engine = _get_engine()
    df = _read_all_csv()
    if df.empty:
        log.info("Rien a charger. Fin.")
        return

    _bulk_insert(df, engine)
    _check_counts(engine)

    log.info("Chargement termine.")


if __name__ == "__main__":
    main()