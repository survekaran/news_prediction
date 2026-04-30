# src/model1_news/sources/et_news.py

from typing import List, Dict
import aiohttp
import feedparser
import asyncio
from loguru import logger

ET_RSS_URL = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"


async def fetch_et_news(
    session: aiohttp.ClientSession,
    symbol: str,
    max_items: int = 30
) -> List[Dict]:
    """
    Fetch Economic Times market news and filter by stock symbol
    """

    try:
        async with session.get(ET_RSS_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                logger.warning(f"[ET] Failed | Status: {response.status}")
                return []

            xml_text = await response.text()

    except asyncio.TimeoutError:
        logger.error(f"[ET] Timeout")
        return []

    except Exception as e:
        logger.exception(f"[ET] Error fetching: {e}")
        return []

    try:
        feed = feedparser.parse(xml_text)

        articles: List[Dict] = []

        for entry in feed.entries[:max_items]:
            title = entry.get("title", "").strip()

            # 🔥 basic relevance filtering
            if symbol.lower() not in title.lower():
                continue

            article = {
                "symbol": symbol,
                "title": title,
                "link": entry.get("link", "").strip(),
                "published": entry.get("published", ""),
                "source": "et"
            }

            if article["title"] and article["link"]:
                articles.append(article)

        logger.info(f"[ET] {symbol} → {len(articles)} articles")

        return articles

    except Exception as e:
        logger.exception(f"[ET] Parsing error: {e}")
        return []