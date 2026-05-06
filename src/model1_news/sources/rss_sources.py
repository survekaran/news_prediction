# src/model1_news/sources/rss_sources.py

from typing import List, Dict
import aiohttp
import feedparser
import asyncio
from loguru import logger


RSS_SOURCES = {
    "et": "https://economictimes.indiatimes.com/markets/stocks/rss.cms",
    "moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
    "business_standard": "https://www.business-standard.com/rss/markets-106.rss",
    "mint": "https://www.livemint.com/rss/markets",
    # "reuters": "https://feeds.reuters.com/reuters/INbusinessNews",  -- Can't fetch the news from this source, it blocks the request (403 Forbidden)
}

STOCK_METADATA = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank",
    "ITC": "ITC",
    "NTPC": "NTPC",
    "COALINDIA": "Coal India",
    "INDUSINDBK": "IndusInd Bank"
}


async def fetch_rss_source(session, url: str, source_name: str, symbol: str, max_items: int = 30) -> List[Dict]:
    """
    Generic RSS fetcher for all sources
    """

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                logger.warning(f"[{source_name}] Failed | Status: {response.status}")
                return []

            xml_text = await response.text()

    except asyncio.TimeoutError:
        logger.error(f"[{source_name}] Timeout")
        return []

    except Exception as e:
        logger.warning(f"[{source_name}] Fetch error: {e}")
        return []

    try:
        feed = feedparser.parse(xml_text)
        company_name = STOCK_METADATA.get(symbol, symbol)

        articles: List[Dict] = []

        for entry in feed.entries[:max_items]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()

            if not title:
                continue

            # 🔥 LIGHT relevance (title + summary)
            combined_text = f"{title} {summary}".lower()
            if symbol.lower() not in combined_text and company_name.lower() not in combined_text:
                continue

            article = {
                "symbol": symbol,
                "title": title,
                "summary": summary,
                "link": entry.get("link", "").strip(),
                "published": entry.get("published", ""),
                "source": source_name
            }

            articles.append(article)

        logger.info(f"[{source_name.upper()}] {symbol} → {len(articles)} articles")

        return articles

    except Exception as e:
        logger.exception(f"[{source_name}] Parse error: {e}")
        return []


async def fetch_all_rss(session, symbol: str) -> List[Dict]:
    """
    Fetch all RSS sources in parallel
    """

    tasks = [
        fetch_rss_source(session, url, name, symbol)
        for name, url in RSS_SOURCES.items()
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_articles = []

    for res in results:
        if isinstance(res, Exception):
            logger.warning(f"[RSS] Source failed: {res}")
            continue
        all_articles.extend(res)

    return all_articles
