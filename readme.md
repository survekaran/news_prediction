MODEL 1 — NEWS SENTIMENT ENGINE (README)

============================================================

OVERVIEW

This module is part of the Stock Prediction System.
It fetches real-time news and converts it into sentiment signals for stocks.

Pipeline Flow:

1. Fetch news from Google News RSS
2. Filter outdated news
3. Clean headlines
4. Run sentiment analysis using FinBERT
5. Output sentiment scores per headline

============================================================

PROJECT STRUCTURE

src/
│
├── model1_news/
│ ├── sources/
│ │ ├── google_news.py
│ │ └── test_google_news.py
│ │
│ ├── preprocessor.py
│ ├── finbert_scorer.py
│ ├── aggregator.py (next step)
│ ├── pipeline.py (next step)
│ └── config.py
│
└── utils/

============================================================

SETUP

1. Create virtual environment

python3 -m venv venv
source venv/bin/activate (Mac/Linux)

---

2. Install dependencies

pip install -r requirements.txt

---

Main Libraries Used:

- aiohttp
- feedparser
- transformers
- torch
- loguru
- python-dateutil
- pandas, numpy

============================================================

HOW TO RUN

Correct command:

python -m src.model1_news.sources.test_google_news

---

Wrong command (will fail):

python test_google_news.py

============================================================

WHY "-m" IS REQUIRED

Python needs to treat "src" as a package.

Using:
python -m src.module.file

ensures imports like:
from src.model1_news.sources.google_news import fetch_google_news

work correctly.

============================================================

DATA SOURCE

Using Google News RSS (free, real-time-like feed)

Example:
https://news.google.com/rss/search?q=RELIANCE+NSE&hl=en-IN&gl=IN&ceid=IN:en

============================================================

FEATURES IMPLEMENTED

1. Async News Fetching

- Uses aiohttp
- Parallel fetching for multiple stocks
- Fast execution (<2 seconds)

---

2. Preprocessing

- Removes old news (> 90 minutes)
- Cleans text
- Handles timestamp parsing

---

3. Sentiment Analysis

Using FinBERT model

- Converts headlines into sentiment scores
- Score range: -1.0 to +1.0

Labels:

- Positive
- Negative
- Neutral

============================================================

SAMPLE OUTPUT

{
"title": "Reliance stock rises after earnings",
"score": 0.42,
"label": "positive"
}

============================================================

IMPORTANT OBSERVATIONS

1. Google RSS is NOT strictly real-time

- Returns both old and new news
- Requires filtering (handled in preprocessor)

---

2. Night-time behavior

At night (e.g., 3 AM IST):
Filtered news = 0

This is expected.

Interpretation:
news_score = 0 (neutral)

---

3. First FinBERT run

- Downloads model (~400MB)
- Happens only once

============================================================

CURRENT STATUS

Project Structure : DONE
Async Fetching : DONE
Google RSS : DONE
Preprocessing : DONE
FinBERT Scoring : DONE
Aggregation : PENDING
Pipeline : PENDING

============================================================

NEXT STEPS

1. Build aggregator.py

   - Combine multiple headlines per stock
   - Generate final news_score

2. Build pipeline.py

   - Orchestrate full flow

3. Add more sources:

   - Economic Times RSS
   - MoneyControl RSS
   - NSE announcements

============================================================

KEY DESIGN PRINCIPLES

- Async-first architecture
- Modular design
- Clean data pipeline
- Real-time filtering
- Production-ready logging

============================================================

COMMON ERRORS

ERROR:
ModuleNotFoundError: No module named 'src'

FIX:
Run using:
python -m src.model1_news.sources.test_google_news

============================================================

AUTHOR NOTES

This module is designed for:

- Intraday trading systems
- Real-time decision making
- Zero-cost infrastructure (RSS-based)

============================================================
