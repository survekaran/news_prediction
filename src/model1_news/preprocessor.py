# src/model1_news/preprocessor.py

from typing import List, Dict
from datetime import datetime, timedelta, timezone
import dateutil.parser
import re
from loguru import logger


def clean_text(text: str) -> str:
    """
    Basic text cleaning for headlines
    """
    text = text.strip()

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text


def is_recent(published_str: str, max_age_minutes: int = 90) -> bool:
    """
    Check if news is within allowed time window
    """
    try:
        published_time = dateutil.parser.parse(published_str)

        # Ensure timezone-aware
        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        return (now - published_time) <= timedelta(minutes=max_age_minutes)

    except Exception as e:
        logger.warning(f"[Preprocessor] Failed to parse date: {published_str}")
        return False


def preprocess_news(news_list: List[Dict]) -> List[Dict]:
    """
    Clean and filter news articles

    Steps:
    1. Remove old news (>90 min)
    2. Clean text
    3. Remove empty entries
    """

    processed = []

    for news in news_list:
        # Filter by recency
        if not is_recent(news.get("published", "")):
            continue

        title = clean_text(news.get("title", ""))

        if not title:
            continue

        processed.append({
            **news,
            "title": title
        })

    logger.info(f"[Preprocessor] {len(processed)} articles after filtering")

    return processed