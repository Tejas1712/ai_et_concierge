"""
ET Catalog RSS Scraper — uses Google News RSS (free, no blocking)
Fetches latest news and appends to et_catalog.json

Usage:
    python rss_scraper.py
"""

import feedparser
import json
import os
import re
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def strip_html(text: str) -> str:
    """Remove HTML tags and decode common HTML entities."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = (
        clean.replace("&nbsp;", " ")
             .replace("&amp;", "&")
             .replace("&lt;", "<")
             .replace("&gt;", ">")
             .replace("&quot;", '"')
             .replace("&#39;", "'")
    )
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

# ── Google News RSS feeds (free, no blocking) ──────────────────────────────
RSS_FEEDS = {
    "Wealth": "https://news.google.com/rss/search?q=ET+wealth+mutual+funds+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Markets": "https://news.google.com/rss/search?q=economic+times+markets+nifty+sensex&hl=en-IN&gl=IN&ceid=IN:en",
    "IPO": "https://news.google.com/rss/search?q=IPO+india+stock+market&hl=en-IN&gl=IN&ceid=IN:en",
    "Politics": "https://news.google.com/rss/search?q=india+politics+economy+policy&hl=en-IN&gl=IN&ceid=IN:en",
    "Prime": "https://news.google.com/rss/search?q=ET+prime+business+india+analysis&hl=en-IN&gl=IN&ceid=IN:en",
    "Masterclass": "https://news.google.com/rss/search?q=india+career+upskill+courses+jobs&hl=en-IN&gl=IN&ceid=IN:en",
    "Enterprise": "https://news.google.com/rss/search?q=india+startup+SME+business+growth&hl=en-IN&gl=IN&ceid=IN:en",
}

# ── Metadata per section ───────────────────────────────────────────────────
METADATA = {
    "Wealth": {
        "target_audience": ["Long-term Investors", "Salaried Employees", "Retirees"],
        "categories": ["Wealth", "MF", "Personal Finance"],
        "risk_profile": ["conservative", "moderate"],
        "trigger_keywords": ["saving", "taxes", "mutual funds", "retirement", "wealth"],
        "core_benefit": "Guidance on personal finance, tax saving, and long-term wealth creation.",
        "discovery_weight": 8,
        "cta_text": "Explore wealth tools",
        "url": "https://economictimes.com/wealth",
    },
    "Markets": {
        "target_audience": ["Active Traders", "Day Traders", "Market Watchers"],
        "categories": ["Markets", "Market Data", "Stocks"],
        "risk_profile": ["moderate", "aggressive"],
        "trigger_keywords": ["stocks", "trading", "live price", "nifty", "sensex"],
        "core_benefit": "Live data, stock analysis, and market insights for active participants.",
        "discovery_weight": 5,
        "cta_text": "View live markets",
        "url": "https://economictimes.com/markets",
    },
    "IPO": {
        "target_audience": ["Growth Investors", "Stock Traders"],
        "categories": ["Markets", "IPO", "Equities"],
        "risk_profile": ["aggressive"],
        "trigger_keywords": ["IPO", "listing", "subscription", "grey market"],
        "core_benefit": "Latest IPO news, GMP, and subscription status for growth investors.",
        "discovery_weight": 6,
        "cta_text": "Track IPOs",
        "url": "https://economictimes.com/markets/ipos",
    },
    "Politics": {
        "target_audience": ["General Public", "Policy Analysts", "Business Owners"],
        "categories": ["News", "Politics", "Governance"],
        "risk_profile": ["conservative", "moderate"],
        "trigger_keywords": ["government", "policy", "election", "budget", "regulation"],
        "core_benefit": "Policy and governance news affecting business and the economy.",
        "discovery_weight": 6,
        "cta_text": "Read policy news",
        "url": "https://economictimes.com/news/politics-and-nation",
    },
    "Prime": {
        "target_audience": ["Professionals", "Executives", "Tech Enthusiasts"],
        "categories": ["ETPrime", "Tech", "AI", "Opinion"],
        "risk_profile": ["conservative", "moderate", "aggressive"],
        "trigger_keywords": ["reading", "deep dive", "tech trends", "ad-free", "premium"],
        "core_benefit": "Ad-free, deep-dive analytical articles on business, tech, and policy.",
        "discovery_weight": 6,
        "cta_text": "Start free trial",
        "url": "https://economictimes.com/prime",
    },
    "Masterclass": {
        "target_audience": ["Students", "Early Career", "Upskillers"],
        "categories": ["Masterclass", "Careers", "Learning"],
        "risk_profile": ["conservative", "moderate", "aggressive"],
        "trigger_keywords": ["learn", "course", "job", "upskill", "career growth"],
        "core_benefit": "Expert-led courses and job market insights to accelerate your career.",
        "discovery_weight": 9,
        "cta_text": "Browse masterclasses",
        "url": "https://economictimes.com/masterclass",
    },
    "Enterprise": {
        "target_audience": ["Business Owners", "Founders", "B2B Professionals"],
        "categories": ["Industry", "SME", "Startup"],
        "risk_profile": ["moderate", "aggressive"],
        "trigger_keywords": ["my business", "startup", "sector", "government policy", "SME"],
        "core_benefit": "Macro-economic trends, sector-specific news, and SME growth strategies.",
        "discovery_weight": 9,
        "cta_text": "Explore enterprise tools",
        "url": "https://economictimes.com/industry",
    },
}

# ── Catalog path ───────────────────────────────────────────────────────────
CATALOG_PATH = Path(__file__).parent.parent / "data" / "et_catalog.json"


def load_catalog() -> list:
    """Load existing catalog from JSON."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("products", [])
    return []


def save_catalog(products: list) -> None:
    """Save catalog back to JSON wrapped in products key."""
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump({"products": products}, f, indent=2, ensure_ascii=False)


def fetch_and_update_catalog():
    print(" Starting RSS scraper...\n")

    # Load existing catalog
    catalog = load_catalog()
    existing_titles = {item["name"] for item in catalog}
    print(f" Loaded {len(catalog)} existing products\n")

    total_new = 0

    for section, url in RSS_FEEDS.items():
        print(f" Fetching {section}...")
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f" No entries found for {section}\n")
            continue

        meta = METADATA[section]
        section_count = 0

        for entry in feed.entries[:5]:  # Latest 5 per section
            title = strip_html(entry.get("title", "")).strip()
            if not title or title in existing_titles:
                continue

            description = strip_html(entry.get("summary", "No description available."))

            new_item = {
                "product_id": str(uuid.uuid4())[:8],
                "product_name": title,
                "id": str(uuid.uuid4())[:8],
                "name": title,
                "description": description,
                "core_benefit": meta["core_benefit"],
                "target_audience": meta["target_audience"],
                "categories": meta["categories"],
                "trigger_keywords": meta["trigger_keywords"],
                "risk_profile": meta["risk_profile"],
                "discovery_weight": meta["discovery_weight"],
                "cta_text": meta["cta_text"],
                "url": entry.get("link", meta["url"]),
                "includes": meta["categories"],
            }

            catalog.append(new_item)
            existing_titles.add(title)
            section_count += 1

        total_new += section_count
        print(f"    Added {section_count} new items from {section}\n")

    # Save updated catalog
    save_catalog(catalog)

    print(f" Done! {total_new} new items added.")
    print(f" Total products in catalog: {len(catalog)}")
    print(f"\n Now run: python ingest.py  to update FAISS with new data!")


if __name__ == "__main__":
    fetch_and_update_catalog()
