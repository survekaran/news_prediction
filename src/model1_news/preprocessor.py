# src/model1_news/preprocessor.py

from typing import List, Dict
from datetime import datetime, timedelta, timezone, time
import dateutil.parser
import re
from loguru import logger


# ==============================
# CLEANING
# ==============================

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


# ==============================
# TIME WINDOW
# ==============================

def get_dynamic_window() -> int:
    now = datetime.now().time()
    return 90 if time(9, 30) <= now <= time(15, 0) else 240


def is_recent(published_str: str) -> bool:
    try:
        published_time = dateutil.parser.parse(published_str)

        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        return (now - published_time) <= timedelta(minutes=get_dynamic_window())

    except Exception:
        logger.warning(f"[Preprocessor] Bad date: {published_str}")
        return False


# ==============================
# RELEVANCE
# ==============================

def is_relevant(text: str, symbol: str, source: str) -> bool:
    text = text.lower()

    # ✅ NSE/BSE always relevant
    if source in ["nse", "bse"]:
        return True

    # ✅ For news → only symbol match (simple & robust)
    return symbol.lower() in text


# ==============================
# MAIN FUNCTION
# ==============================

def preprocess_news(news_list: List[Dict]) -> List[Dict]:
    results = []
    seen_titles = set()  # 🔥 deduplication

    for news in news_list:
        title = clean_text(news.get("title", ""))
        summary = clean_text(news.get("summary", ""))

        if not title:
            continue

        source = news.get("source", "").lower()
        published = news.get("published", "")

        combined_text = f"{title} {summary}".strip()

        # ==============================
        # FILTER
        # ==============================

        if not is_recent(published):
            continue

        if not is_relevant(combined_text, news["symbol"], source):
            continue

        # ==============================
        # DEDUPLICATION
        # ==============================

        if title in seen_titles:
            continue

        seen_titles.add(title)

        results.append({
            **news,
            "title": title,
            "summary": summary,
            "analysis_text": combined_text
        })

    logger.info(f"[Preprocessor] Final → {len(results)} articles")

    return results