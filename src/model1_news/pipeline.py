# src/model1_news/pipeline.py

import asyncio
from typing import List, Dict
from datetime import datetime, time

import aiohttp
import sqlite3

from loguru import logger

# Sources
from src.model1_news.sources.google_news import fetch_google_news
from src.model1_news.sources.rss_sources import fetch_all_rss
from src.model1_news.sources.nse_announcements import fetch_nse_announcements
from src.model1_news.sources.bse_announcements import fetch_bse_announcements

# Core
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
# MEMORY
# ==============================

last_states: Dict[str, Dict] = {}


# ==============================
# PROCESS SINGLE STOCK
# ==============================

async def process_stock(session, symbol, scorer):
    try:
        # 🔥 PARALLEL FETCH
        google_task = fetch_google_news(session, symbol)
        rss_task = fetch_all_rss(session, symbol)

        nse_task = asyncio.to_thread(fetch_nse_announcements, symbol)
        bse_task = asyncio.to_thread(fetch_bse_announcements, symbol)

        google_news, rss_news, nse_news, bse_news = await asyncio.gather(
            google_task,
            rss_task,
            nse_task,
            bse_task,
            return_exceptions=True
        )

        raw_news = []

        for source_data in [google_news, rss_news, nse_news, bse_news]:
            if isinstance(source_data, Exception):
                logger.warning(f"[Pipeline] Source failed: {source_data}")
                continue

            if source_data:
                raw_news.extend(source_data)

        logger.info(f"[DEBUG] {symbol} → Raw News: {len(raw_news)}")

        # ==============================
        # PROCESS
        # ==============================

        processed_news = preprocess_news(raw_news)

        if not processed_news:
            logger.warning(f"[Pipeline] No processed news for {symbol}")

        texts = [n.get("analysis_text") or n["title"] for n in processed_news]
        sentiments = scorer.score_batch(texts)

        result = aggregate_news(
            symbol=symbol,
            news_list=processed_news,
            sentiment_list=sentiments,
            last_state=last_states.get(symbol)
        )

        # SAVE
        last_states[symbol] = result
        save_to_db(result)

        return result

    except Exception as e:
        logger.exception(f"[Pipeline] Error processing {symbol}: {e}")
        return None


# ==============================
# RUN ONE CYCLE
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
        # ✅ LOAD WATCHLIST ONLY ONCE
        watchlist = load_watchlist()

        symbols = [stock["symbol"] for stock in watchlist if isinstance(stock, dict)]

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
# ENTRY
# ==============================

if __name__ == "__main__":
    asyncio.run(run_intraday())
