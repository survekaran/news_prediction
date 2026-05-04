# src/utils/watchlist_loader.py

import json
from loguru import logger


def load_watchlist(path: str = "data/watchlist.json"):
    """
    Supports BOTH formats:
    1. List of dicts
    2. {"stocks": [...]}
    """

    try:
        with open(path, "r") as f:
            data = json.load(f)

        # ✅ HANDLE BOTH FORMATS
        if isinstance(data, list):
            stocks = data
        elif isinstance(data, dict):
            stocks = data.get("stocks", [])
        else:
            logger.error("[Watchlist] Invalid format")
            return []

        if not stocks:
            logger.warning("[Watchlist] Empty stock list")

        symbols = [s.get("symbol") for s in stocks if isinstance(s, dict)]
        logger.info(f"[Watchlist] Loaded stocks: {symbols}")

        return stocks

    except FileNotFoundError:
        logger.error(f"[Watchlist] File not found: {path}")
        return []

    except Exception as e:
        logger.exception(f"[Watchlist] Error loading file: {e}")
        return []