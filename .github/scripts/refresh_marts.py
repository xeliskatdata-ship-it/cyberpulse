# refresh_marts.py -- Recreate stg_articles view + mart tables on Neon
# Called by GitHub Actions after load_to_db.py

import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

SQL_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "db", "neon_stg_marts.sql")

def main():
    conn = psycopg2.connect(
        host=os.environ["NEON_HOST"],
        dbname=os.environ["NEON_DBNAME"],
        user=os.environ["NEON_USER"],
        password=os.environ["NEON_PASSWORD"],
        sslmode="require",
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Lire et executer le fichier SQL complet
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    # Executer chaque statement separement
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            log.warning("Statement skip: %s", str(e)[:100])

    # Verification
    for table in ["stg_articles", "mart_k1", "mart_k2", "mart_k3", "mart_k4", "mart_k5", "mart_k6"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            n = cur.fetchone()[0]
            log.info("%-20s : %d lignes", table, n)
        except Exception:
            log.warning("%-20s : introuvable", table)

    cur.close()
    conn.close()
    log.info("Marts refreshed.")


if __name__ == "__main__":
    main()