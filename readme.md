# 🧠 Model 1 — News + Exchange Announcement Sentiment Engine

This module is part of a **Stock Prediction System**.

👉 Its job:

Convert **real-time news + NSE/BSE corporate announcements** into a **numerical trading signal**.

---

# 🚀 WHAT THIS MODEL DOES (IN SIMPLE TERMS)

Every **3 minutes during market hours**, this system:

- Reads selected stocks from watchlist
- Fetches latest **news + exchange announcements**
- Filters relevant & recent data
- Uses AI (FinBERT) to analyze sentiment
- Aggregates everything into **one final score per stock**
- Stores results in a database.
---

# 🧠 WHY THIS IS IMPORTANT

Stock prices are driven by:

- News 📰
- Corporate announcements 📢
- Earnings 📊
- Board decisions ⚡

👉 This model answers:

**“Is current information pushing the stock UP or DOWN?”**

---

# ⚙️ SETUP

## Create virtual environment

python3 -m venv venv  
source venv/bin/activate

## Install dependencies

pip install -r requirements.txt

---

# ▶️ HOW TO RUN

python -m src.model1_news.pipeline

---

# 🧾 WATCHLIST (UPDATED FORMAT)

📁 data/watchlist.json

```json
[
  {
    "symbol": "RELIANCE",
    "nse_symbol": "RELIANCE",
    "bse_code": 500325
  },
  {
    "symbol": "ITC",
    "nse_symbol": "ITC",
    "bse_code": 500875
  },
  {
    "symbol": "NTPC",
    "nse_symbol": "NTPC",
    "bse_code": 532555
  },
  {
    "symbol": "COALINDIA",
    "nse_symbol": "COALINDIA",
    "bse_code": 533278
  },
  {
    "symbol": "INDUSINDBK",
    "nse_symbol": "INDUSINDBK",
    "bse_code": 532187
  }
]
```

---

# 🔄 FULL WORKFLOW

## Step 1 — Load Watchlist

- Loaded once per cycle (fixed)
- Returns structured stock objects

---

## Step 2 — Fetch Data (MULTI-SOURCE)

### 📰 News Sources

- Google News
- RSS feeds

### 📢 Exchange Announcements (NEW)

- NSE corporate announcements
- BSE corporate announcements

👉 These are **high-impact real market signals**

---

## Step 3 — Preprocessing (MAJOR FIX)

### Before ❌

- NSE/BSE announcements were filtered out
- System behaved like a basic news scraper

### After ✅

- Source-aware filtering introduced

| Source       | Logic                           |
| ------------ | ------------------------------- |
| Google / RSS | strict relevance (symbol match) |
| NSE / BSE    | always relevant                 |

---

## Step 4 — Sentiment Analysis

Uses **FinBERT**

Example:
"Reliance reports strong earnings" → +0.6  
"Company reports losses" → -0.5

---

## Step 5 — Aggregation

Combines signals using:

- Recency weighting
- Source importance
- Sentiment strength

### Source Weights

| Source | Weight |
| ------ | ------ |
