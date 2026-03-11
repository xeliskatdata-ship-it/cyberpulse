import requests
import feedparser
from dotenv import load_dotenv
import os

load_dotenv()

# ── TEST NEWSAPI ─────────────────────────────────────
def test_newsapi():
    key = os.getenv("NEWSAPI_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "cybersecurity",
        "language": "en",
        "pageSize": 3,
        "apiKey": key
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "ok":
        print(f"✅ NewsAPI OK — {data['totalResults']} articles trouvés")
        for article in data["articles"]:
            print(f"   → {article['title']}")
    else:
        print(f"❌ NewsAPI erreur : {data}")

# ── TEST RSS FEEDS ───────────────────────────────────
def test_rss():
    feeds = {
        "The Hacker News" : "https://feeds.feedburner.com/TheHackersNews",
        "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
        "Zataz"           : "https://www.zataz.com/feed/",
        "CISA Alerts"     : "https://www.cisa.gov/news.xml",
    }

    for source, url in feeds.items():
        feed = feedparser.parse(url)
        print(f"\n✅ {source} — {len(feed.entries)} articles")
        for entry in feed.entries[:2]:
            print(f"   → {entry.title}")

# ── LANCEMENT ────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST APIs CyberPulse ===\n")
    test_newsapi()
    test_rss()