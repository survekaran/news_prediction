 🧠 Model 1 — News Sentiment Engine

This module is part of a **Stock Prediction System**.

👉 Its job is simple:

Take stock news → understand sentiment → convert it into a number  
so the trading system can make decisions.

---

# 🚀 WHAT THIS MODEL DOES (IN SIMPLE TERMS)

Every **3 minutes during market hours**, this system:

- Reads a list of 5 stocks
- Fetches latest news about them
- Filters useful & recent news
- Uses AI to understand sentiment
- Converts everything into **one final score per stock**
- Stores the result in a database

---

# 🧠 WHY THIS IS IMPORTANT

Stock prices move because of:

- News 📰
- Events ⚡
- Announcements 📢

This model helps answer:

👉 “Is the news pushing the stock UP or DOWN right now?”

---

# ⚙️ SETUP

Create virtual environment:

python3 -m venv venv  
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

---

# ▶️ HOW TO RUN

python -m src.model1_news.pipeline

---

# 🧾 WATCHLIST (VERY IMPORTANT):

File location:

data/watchlist.json

Example:

{
"date": "2026-04-30",
"stocks": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
}

👉 This file tells the system which 5 stocks to track.

---

# 🔄 FULL WORKFLOW

Step 1 — Morning (8:30 AM)

- AI (Claude) selects 5 stocks
- Updates watchlist.json

---

Step 2 — Market Starts

Pipeline starts running

---

Step 3 — Every 3 Minutes

For each stock:

1. Fetch News

   - Uses Google News RSS
   - Gets latest headlines

2. Filter News

   - Removes old news (> 90 minutes)
   - Removes irrelevant news

3. Analyze Sentiment

   - Uses FinBERT (AI model trained on financial data)
   - Converts text into score

   Example:  
   "Reliance stock jumps after earnings" → +0.6 (positive)

4. Aggregate Results

   - Combines multiple headlines
   - Gives ONE final score

5. Handle No News

   - Uses previous score (carry-forward)
   - Slightly reduces confidence

6. Store Output
   - Saved in database (signals.db)

---

# 📊 FINAL OUTPUT

Each stock produces:

{
"symbol": "RELIANCE",
"news_score": 0.38,
"direction": "bullish",
"confidence": 0.72
}

---

# 🧠 WHAT THESE VALUES MEAN

news_score → Range from -1 to +1  
direction → bullish / bearish / neutral  
confidence → Strength of signal

---

# ⚡ TECHNIQUES USED

1. Async Programming

   - Fetch multiple stocks at once
   - Fast execution

2. AI Sentiment Analysis

   - Uses FinBERT
   - Specialized for financial news

3. Smart Filtering

   - Removes noise
   - Keeps only relevant news

4. Weighted Scoring

   - Newer news matters more
   - Strong sentiment has more impact

5. Carry Forward Logic

   - If no news → don’t reset signal
   - Keeps system stable

6. Database Storage
   - Stores every 3-minute signal
   - Used later by trading models

---

# 🧠 HOW THIS FITS INTO FULL SYSTEM

This is only Model 1.

Full system includes:

Model 1 → News Sentiment  
Model 2 → Candlestick Patterns  
Model 3 → Technical Indicators  
Model 4 → Final Decision Engine

---

# 💀 IMPORTANT NOTES

Google News is not perfectly real-time  
→ That’s why filtering is required

Night-time behavior:  
No news → neutral signal

First run:  
FinBERT downloads (~400MB, one-time)

---

# 🚀 FUTURE IMPROVEMENTS

- Add Economic Times + MoneyControl
- Improve filtering using company names
- Add alerts
- Integrate trading APIs

---

# 🎯 FINAL SUMMARY

This model:

✔ Reads news  
✔ Understands sentiment  
✔ Converts it into numbers  
✔ Runs every 3 minutes  
✔ Feeds trading system

---

# 👨‍💻 TL;DR

Stock news → AI → trading signal
