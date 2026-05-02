import requests
from src.utils.watchlist_loader import load_watchlist


def fetch_nse_announcements(symbol: str):
    watchlist = load_watchlist()

    stock = next((s for s in watchlist if s["symbol"] == symbol), None)
    if not stock:
        return []

    nse_symbol = stock.get("nse_symbol")
    if not nse_symbol:
        return []

    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers)

        data = response.json()

        results = []

        for item in data:
            if item.get("symbol") == nse_symbol:
                results.append({
                    "title": item.get("desc"),
                    "content": item.get("attchmntText"),
                    "published": item.get("an_dt"),
                    "source": "nse",
                    "symbol": symbol
                })

        return results

    except Exception as e:
        print("NSE error:", e)
        return []