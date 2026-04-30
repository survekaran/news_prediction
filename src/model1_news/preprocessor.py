# src/model1_news/preprocessor.py

from typing import List, Dict
from datetime import datetime, timedelta, timezone, time
import dateutil.parser
import re
from loguru import logger


# 🔥 Add company mapping (same as google_news.py)
STOCK_METADATA = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank"
}


def clean_text(text: str) -> str:
    """
    Basic text cleaning for headlines
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# 🔥 Dynamic time window
def get_dynamic_window() -> int:
    now = datetime.now().time()

    if time(9, 30) <= now <= time(15, 0):
        return 90   # strict during market
    else:
        return 240  # relaxed outside market


def is_recent(published_str: str) -> bool:
    """
    Check if news is within allowed time window (dynamic)
    """
    try:
        published_time = dateutil.parser.parse(published_str)

        # Ensure timezone-aware
        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        max_age_minutes = get_dynamic_window()

        return (now - published_time) <= timedelta(minutes=max_age_minutes)

    except Exception:
        logger.warning(f"[Preprocessor] Failed to parse date: {published_str}")
        return False


# 🔥 Strict relevance check
def is_relevant(title: str, symbol: str) -> bool:
    company_name = STOCK_METADATA.get(symbol, symbol)

    title = title.lower()

    return (
        symbol.lower() in title or
        company_name.lower() in title
    )


def preprocess_news(news_list: List[Dict]) -> List[Dict]:
    """
    Clean and filter news articles

    Strategy:
    1. STRICT → (time + relevance)
    2. FALLBACK → (time only)
    """

    strict_results = []

    for news in news_list:
        title = clean_text(news.get("title", ""))

        if not title:
            continue

        if is_recent(news.get("published", "")) and is_relevant(title, news["symbol"]):
            strict_results.append({
                **news,
                "title": title
            })

    # ✅ If strict gives results → return
    if strict_results:
        logger.info(f"[Preprocessor] Strict → {len(strict_results)} articles")
        return strict_results

    # 🔥 Fallback mode
    logger.warning("[Preprocessor] No strict matches → using relaxed filter")

    relaxed_results = []

    for news in news_list:
        title = clean_text(news.get("title", ""))

        if not title:
            continue

        if is_recent(news.get("published", "")):
            relaxed_results.append({
                **news,
                "title": title
            })

    logger.info(f"[Preprocessor] Relaxed → {len(relaxed_results)} articles")

    return relaxed_results