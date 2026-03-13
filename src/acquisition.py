"""
CyberPulse -- acquisition.py
Sprint 2 : Collecte reelle des articles cyber

Sources :
  - NewsAPI          (API REST)
  - The Hacker News  (RSS)
  - BleepingComputer (RSS)
  - Zataz            (RSS)
  - CISA Alerts      (RSS)

Sortie : data/raw/articles_YYYY-MM-DD.csv
"""

import requests
import feedparser
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)

RSS_FEEDS = {
    "The Hacker News" : "https://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "Zataz"           : "https://www.zataz.com/feed/",
    "CISA Alerts"     : "https://www.cisa.gov/news.xml",
}

# ---------------------------------------------------
# 1. COLLECTE NEWSAPI
# ---------------------------------------------------
def collect_newsapi():
    """Collecte les articles depuis NewsAPI et retourne une liste de dicts."""
    print("\nCollecte NewsAPI...")
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        print("  ERREUR : Cle NEWSAPI_KEY manquante dans .env")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q"       : "cybersecurity OR ransomware OR phishing OR malware OR CVE",
        "language": "en",
        "pageSize": 100,
        "sortBy"  : "publishedAt",
        "apiKey"  : key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            print(f"  ERREUR NewsAPI : {data.get('message')}")
            return []

        articles = []
        for a in data.get("articles", []):
            articles.append({
                "source"      : "NewsAPI",
                "title"       : a.get("title", ""),
                "description" : a.get("description", ""),
                "url"         : a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
                "collected_at": datetime.now().isoformat(),
            })

        print(f"  OK -- {len(articles)} articles collectes")
        return articles

    except Exception as e:
        print(f"  ERREUR -- {e}")
        return []


# ---------------------------------------------------
# 2. COLLECTE RSS FEEDS
# ---------------------------------------------------
def collect_rss():
    """Collecte les articles depuis les 4 flux RSS et retourne une liste de dicts."""
    print("\nCollecte flux RSS...")
    articles = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            count = 0
            for entry in feed.entries:
                articles.append({
                    "source"      : source_name,
                    "title"       : entry.get("title", ""),
                    "description" : entry.get("summary", ""),
                    "url"         : entry.get("link", ""),
                    "published_at": entry.get("published", ""),
                    "collected_at": datetime.now().isoformat(),
                })
                count += 1
            print(f"  OK -- {source_name} -- {count} articles")

        except Exception as e:
            print(f"  ERREUR -- {source_name} -- {e}")

    return articles


# ---------------------------------------------------
# 3. SAUVEGARDE CSV
# ---------------------------------------------------
def save_to_csv(articles):
    """Sauvegarde la liste d'articles dans data/raw/articles_YYYY-MM-DD.csv"""
    if not articles:
        print("\nATTENTION : Aucun article a sauvegarder.")
        return None

    today    = datetime.now().strftime("%Y-%m-%d")
    filename = f"articles_{today}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    df = pd.DataFrame(articles)

    # Si le fichier existe deja aujourd'hui, on ajoute sans dupliquer l'en-tete
    if os.path.exists(filepath):
        df.to_csv(filepath, mode='a', header=False, index=False, encoding='utf-8')
        print(f"\nArticles ajoutes dans : {filepath}")
    else:
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"\nFichier cree : {filepath}")

    print(f"  > {len(df)} articles sauvegardes")
    print(f"  > Colonnes : {list(df.columns)}")
    return filepath


# ---------------------------------------------------
# 4. FONCTION PRINCIPALE
# ---------------------------------------------------
def collect_all():
    """Lance la collecte complete et sauvegarde en CSV."""
    print("=" * 55)
    print("CyberPulse -- Collecte reelle S2")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    all_articles = []

    all_articles += collect_newsapi()
    all_articles += collect_rss()

    print(f"\nTotal collecte : {len(all_articles)} articles")
    print(f"   Sources : {set(a['source'] for a in all_articles)}")

    filepath = save_to_csv(all_articles)

    print("\nCollecte terminee !")
    return filepath


# ---------------------------------------------------
# LANCEMENT DIRECT
# ---------------------------------------------------
if __name__ == "__main__":
    collect_all()
