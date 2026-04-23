# test_google_news.py

import asyncio
import aiohttp
from src.model1_news.sources.google_news import fetch_google_news
from src.model1_news.preprocessor import preprocess_news


async def main():
    async with aiohttp.ClientSession() as session:
        news = await fetch_google_news(session, "RELIANCE")
        for n in news[:5]:
            print(n)
            for n in news[:5]:
             print(n["published"])
        
        news = await fetch_google_news(session, "RELIANCE")

        filtered_news = preprocess_news(news)

        print(f"Before: {len(news)}")
        print(f"After: {len(filtered_news)}")

        for n in filtered_news:
         print(n["published"], n["title"])
  


asyncio.run(main())