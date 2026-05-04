# src/model1_news/sources/google_news.py

from typing import List, Dict
import aiohttp
import feedparser
import asyncio
from loguru import logger

# 🔥 Add company mapping (important for better search)
STOCK_METADATA = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank"
}

GOOGLE_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


async def fetch_google_news(
    session: aiohttp.ClientSession,
    symbol: str,
    max_items: int = 50  # 🔥 increased from 20 → 50
) -> List[Dict]:

    company_name = STOCK_METADATA.get(symbol, symbol)

    # 🔥 improved query
    query = f'"{company_name}" OR {symbol} stock India'
    url = GOOGLE_RSS_URL.format(query=query.replace(" ", "+"))

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                logger.warning(f"[GoogleNews] Failed {symbol} | Status: {response.status}")
                return []

            xml_text = await response.text()

    except asyncio.TimeoutError:
        logger.error(f"[GoogleNews] Timeout for {symbol}")
        return []

    except Exception as e:
        logger.exception(f"[GoogleNews] Error fetching {symbol}: {e}")
        return []

    try:
        feed = feedparser.parse(xml_text)

        articles: List[Dict] = []

        for entry in feed.entries[:max_items]:
            article = {
                "symbol": symbol,
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": entry.get("published", ""),
                "source": "google"
            }

            if article["title"] and article["link"]:
                articles.append(article)

        logger.info(f"[GoogleNews] {symbol} → {len(articles)} articles fetched")

        return articles

    except Exception as e:
        logger.exception(f"[GoogleNews] Parsing error for {symbol}: {e}")
        return []
