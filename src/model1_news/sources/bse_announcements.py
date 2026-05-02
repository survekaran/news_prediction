import requests
import time
from src.utils.watchlist_loader import load_watchlist


def fetch_bse_announcements(symbol: str):
    watchlist = load_watchlist()

    # find matching stock
    stock = next((s for s in watchlist if s["symbol"] == symbol), None)
    if not stock:
        return []

    bse_code = stock.get("bse_code")
    if not bse_code:
        return []

    url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bseindia.com/"
    }

    results = []

    try:
        for page in range(1, 4):
            params = {
                "pageno": page,
                "strCat": "-1",
                "strPrevDate": "",
                "strScrip": "",
                "strSearch": "P",
                "strToDate": "",
                "strType": "C",
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            table = data.get("Table", [])

            for item in table:
                if item.get("SCRIP_CD") == bse_code:
                    results.append({
                        "title": item.get("HEADLINE"),
                        "content": item.get("NEWSSUB"),
                        "published": item.get("DT_TM"),
                        "source": "bse",
                        "symbol": symbol
                    })

            if not table:
                break

            time.sleep(0.3)

    except Exception as e:
        print("BSE error:", e)

    return results