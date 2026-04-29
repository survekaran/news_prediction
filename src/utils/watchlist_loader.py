# src/utils/watchlist_loader.py

import json
from loguru import logger


def load_watchlist(path: str = "data/watchlist.json"):
    """
    Load stock symbols from watchlist JSON file
    """

    try:
        with open(path, "r") as f:
            data = json.load(f)

        stocks = data.get("stocks", [])

        if not stocks:
            logger.warning("[Watchlist] Empty stock list")

        logger.info(f"[Watchlist] Loaded stocks: {stocks}")

        return stocks

    except FileNotFoundError:
        logger.error(f"[Watchlist] File not found: {path}")
        return []

    except Exception as e:
        logger.exception(f"[Watchlist] Error loading file: {e}")
        return []