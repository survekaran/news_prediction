# src/model1_news/aggregator.py

from typing import List, Dict, Optional
from datetime import datetime, timezone
import math
from loguru import logger
import dateutil.parser  # 🔥 IMPORTANT FIX


SOURCE_WEIGHTS = {
    "google": 0.6,
    "et": 0.8,
    "moneycontrol": 0.7,
    "nse": 1.0,
    "bse": 0.95   # 👈 ADD THIS
}


def compute_recency_weight(published_time: datetime) -> float:
    now = datetime.now(timezone.utc)
    minutes_old = (now - published_time).total_seconds() / 60
    return math.exp(-minutes_old / 60)


def aggregate_news(
    symbol: str,
    news_list: List[Dict],
    sentiment_list: List[Dict],
    last_state: Optional[Dict] = None
) -> Dict:

    # ==============================
    # NO NEWS → CARRY FORWARD
    # ==============================

    if not news_list or not sentiment_list:
        logger.warning(f"[Aggregator] No news for {symbol}")

        if last_state:
            return {
                **last_state,
                "confidence": round(last_state["confidence"] * 0.9, 3),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "headline_count": 0,
                "top_headline": None
            }

        return {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "news_score": 0.0,
            "direction": "neutral",
            "confidence": 0.0,
            "headline_count": 0,
            "top_headline": None,
            "source_breakdown": {}
        }

    weighted_scores = []
    weights = []
    source_count = {}

    top_headline = None
    max_abs_score = 0

    # ==============================
    # MAIN LOOP
    # ==============================

    for news, sentiment in zip(news_list, sentiment_list):
        try:
            score = sentiment["score"]

            # 🔥 FIXED DATE PARSING
            published_time = dateutil.parser.parse(news["published"])

            recency_weight = compute_recency_weight(published_time)
            source_weight = SOURCE_WEIGHTS.get(news["source"], 0.5)

            final_weight = recency_weight * source_weight

            weighted_scores.append(score * final_weight)
            weights.append(final_weight)

            # track sources
            source = news["source"]
            source_count[source] = source_count.get(source, 0) + 1

            # strongest headline
            if abs(score) > max_abs_score:
                max_abs_score = abs(score)
                top_headline = news["title"]

        except Exception as e:
            logger.warning(f"[Aggregator] Skipping entry: {e}")
            continue

    # ==============================
    # EDGE CASE
    # ==============================

    if not weights:
        logger.warning(f"[Aggregator] No valid weights for {symbol}")
        return {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "news_score": 0.0,
            "direction": "neutral",
            "confidence": 0.0,
            "headline_count": 0,
            "top_headline": None,
            "source_breakdown": {}
        }

    # ==============================
    # FINAL SCORE
    # ==============================

    news_score = sum(weighted_scores) / sum(weights)

    if news_score > 0.2:
        direction = "bullish"
    elif news_score < -0.2:
        direction = "bearish"
    else:
        direction = "neutral"

    headline_count = len(weights)
    confidence = min(1.0, abs(news_score) + 0.2 * math.log(1 + headline_count))

    result = {
        "symbol": symbol,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "news_score": round(news_score, 4),
        "direction": direction,
        "confidence": round(confidence, 4),
        "headline_count": headline_count,
        "top_headline": top_headline,
        "source_breakdown": source_count
    }

    logger.info(f"[Aggregator] {symbol} → {result}")

    return result