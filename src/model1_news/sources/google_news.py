# src/model1_news/sources/google_news.py

from typing import List, Dict
import asyncio
import aiohttp
import feedparser
from loguru import logger

GOOGLE_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


async def fetch_google_news(
    session: aiohttp.ClientSession,
    symbol: str,
    max_items: int = 20
) -> List[Dict]:
    """
    Fetch news articles for a given stock symbol from Google News RSS.

    Args:
        session (aiohttp.ClientSession): Shared async HTTP session
        symbol (str): Stock symbol (e.g., RELIANCE, TCS)
        max_items (int): Max number of articles to return

    Returns:
        List[Dict]: List of news articles with structured fields
    """

    query = f"{symbol} NSE stock"
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
                "link": entry.get("link", "").strip(),
                "published": entry.get("published", ""),
                "source": "google"
            }

            # Basic validation
            if article["title"] and article["link"]:
                articles.append(article)

        logger.info(f"[GoogleNews] {symbol} → {len(articles)} articles fetched")

        return articles

    except Exception as e:
        logger.exception(f"[GoogleNews] Parsing error for {symbol}: {e}")
        return []