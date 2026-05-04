# src/model1_news/preprocessor.py

from typing import List, Dict
from datetime import datetime, timedelta, timezone, time
import dateutil.parser
import re
from loguru import logger


# ==============================
# STOCK METADATA
# ==============================

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


# ==============================
# CLEANING
# ==============================

def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# ==============================
# TIME WINDOW
# ==============================

def get_dynamic_window() -> int:
    now = datetime.now().time()

    if time(9, 30) <= now <= time(15, 0):
        return 90   # strict during market
    else:
        return 240  # relaxed outside market


def is_recent(published_str: str) -> bool:
    try:
        published_time = dateutil.parser.parse(published_str)

        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        max_age_minutes = get_dynamic_window()

        return (now - published_time) <= timedelta(minutes=max_age_minutes)

    except Exception:
        logger.warning(f"[Preprocessor] Failed to parse date: {published_str}")
        return False


# ==============================
# RELEVANCE LOGIC
# ==============================

def is_relevant(title: str, summary: str, symbol: str, source: str) -> bool:
    """
    Different logic for:
    - News sources (Google, RSS)
    - NSE/BSE announcements
    """

    combined_text = f"{title} {summary}".lower()

    # 🔥 NSE/BSE → ALWAYS RELEVANT (already filtered upstream)
    if source in ["nse", "bse"]:
        return True

    # 🔥 News sources → strict match
    company_name = STOCK_METADATA.get(symbol, symbol)

    return (
        symbol.lower() in combined_text or
        company_name.lower() in combined_text
    )


# ==============================
# MAIN PREPROCESS FUNCTION
# ==============================

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
        summary = clean_text(news.get("summary", ""))

        if not title:
            continue

        source = news.get("source", "").lower()

        if (
            is_recent(news.get("published", "")) and
            is_relevant(title, summary, news["symbol"], source)
        ):
            strict_results.append({
                **news,
                "title": title,
                "summary": summary,
                "analysis_text": clean_text(f"{title}. {summary}") if summary else title
            })

    # ==============================
    # STRICT SUCCESS
    # ==============================

    if strict_results:
        logger.info(f"[Preprocessor] Strict → {len(strict_results)} articles")
        return strict_results

    # ==============================
    # FALLBACK MODE
    # ==============================

    logger.warning("[Preprocessor] No strict matches → using relaxed filter")

    relaxed_results = []

    for news in news_list:
        title = clean_text(news.get("title", ""))
        summary = clean_text(news.get("summary", ""))

        if not title:
            continue

        if is_recent(news.get("published", "")):
            relaxed_results.append({
                **news,
                "title": title,
                "summary": summary,
                "analysis_text": clean_text(f"{title}. {summary}") if summary else title
            })

    logger.info(f"[Preprocessor] Relaxed → {len(relaxed_results)} articles")

    return relaxed_results
