# src/model1_news/sources/moneycontrol.py

from typing import List, Dict
import aiohttp
import feedparser
import asyncio
from loguru import logger

MC_RSS_URL = "https://www.moneycontrol.com/rss/MCtopnews.xml"


async def fetch_moneycontrol_news(
    session: aiohttp.ClientSession,
    symbol: str,
    max_items: int = 30
) -> List[Dict]:
    """
    Fetch MoneyControl news and filter by stock symbol
    """

    try:
        async with session.get(MC_RSS_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                logger.warning(f"[MoneyControl] Failed | Status: {response.status}")
                return []

            xml_text = await response.text()

    except asyncio.TimeoutError:
        logger.error(f"[MoneyControl] Timeout")
        return []

    except Exception as e:
        logger.exception(f"[MoneyControl] Error fetching: {e}")
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
                "source": "moneycontrol"
            }

            if article["title"] and article["link"]:
                articles.append(article)

        logger.info(f"[MoneyControl] {symbol} → {len(articles)} articles")

        return articles

    except Exception as e:
        logger.exception(f"[MoneyControl] Parsing error: {e}")
        return []