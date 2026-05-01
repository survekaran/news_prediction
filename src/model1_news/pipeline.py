# src/model1_news/pipeline.py

import asyncio
from typing import List, Dict
from datetime import datetime, time

import aiohttp
import sqlite3

from loguru import logger

# 🔥 Sources
from src.model1_news.sources.google_news import fetch_google_news
from src.model1_news.sources.et_news import fetch_et_news
from src.model1_news.sources.moneycontrol import fetch_moneycontrol_news
from src.model1_news.sources.rss_sources import fetch_all_rss

# 🔥 Core modules
from src.model1_news.preprocessor import preprocess_news
from src.model1_news.finbert_scorer import FinBERTScorer
from src.model1_news.aggregator import aggregate_news
from src.utils.watchlist_loader import load_watchlist


# ==============================
# CONFIG
# ==============================

MARKET_START = time(9, 30)
MARKET_END = time(15, 0)

DB_PATH = "data/signals.db"


# ==============================
# DB SETUP
# ==============================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        timestamp TEXT,
        news_score REAL,
        direction TEXT,
        confidence REAL,
        headline_count INTEGER,
        top_headline TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_to_db(result: Dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO news_signals (
        symbol, timestamp, news_score, direction,
        confidence, headline_count, top_headline
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        result["symbol"],
        result["timestamp"],
        result["news_score"],
        result["direction"],
        result["confidence"],
        result["headline_count"],
        result["top_headline"]
    ))

    conn.commit()
    conn.close()


# ==============================
# MEMORY (carry-forward)
# ==============================

last_states: Dict[str, Dict] = {}


# ==============================
# SINGLE STOCK PROCESSING
# ==============================

async def process_stock(session, symbol, scorer):
    """
    Process one stock: fetch → preprocess → score → aggregate
    """
    try:
        # 🔥 PARALLEL FETCH (IMPORTANT CHANGE)
        # 🔥 Multi-source fetch
        google_task = fetch_google_news(session, symbol)
        rss_task = fetch_all_rss(session, symbol)

        google_news, rss_news = await asyncio.gather(
            google_task,
            rss_task,
            return_exceptions=True
        )

        raw_news = []

        for source_data in [google_news, rss_news]:
            if isinstance(source_data, Exception):
                logger.warning(f"[Pipeline] Source failed: {source_data}")
                continue
            raw_news.extend(source_data)

        # 🔥 CONTINUE PIPELINE
        processed_news = preprocess_news(raw_news)

        texts = [n["title"] for n in processed_news]
        sentiments = scorer.score_batch(texts)

        result = aggregate_news(
            symbol=symbol,
            news_list=processed_news,
            sentiment_list=sentiments,
            last_state=last_states.get(symbol)
        )

        # 🔥 MEMORY + DB
        last_states[symbol] = result
        save_to_db(result)

        return result

    except Exception as e:
        logger.exception(f"[Pipeline] Error processing {symbol}: {e}")
        return None


# ==============================
# SINGLE CYCLE
# ==============================

async def run_cycle(symbols: List[str], scorer: FinBERTScorer):
    async with aiohttp.ClientSession() as session:
        tasks = [
            process_stock(session, symbol, scorer)
            for symbol in symbols
        ]

        results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]


# ==============================
# MAIN LOOP
# ==============================

async def run_intraday():
    logger.info("🚀 Starting Model 1 News Pipeline")

    init_db()
    scorer = FinBERTScorer()

    while True:
        symbols = load_watchlist()

        if not symbols:
            logger.warning("⚠️ Watchlist empty")
            await asyncio.sleep(60)
            continue

        now = datetime.now().time()

        if MARKET_START <= now <= MARKET_END:
            logger.info(f"⏱ Running cycle for: {symbols}")

            results = await run_cycle(symbols, scorer)

            for r in results:
                logger.info(f"📊 {r}")

            await asyncio.sleep(180)

        else:
            logger.info("⏸ Market closed")
            await asyncio.sleep(60)


# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    asyncio.run(run_intraday())