#!/usr/bin/env python3
"""Fetch stock news using yfinance."""

import argparse
import json
import time
import yfinance as yf


def yf_retry(fn, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"Retry {attempt + 1}/{retries}: {e}")
            time.sleep(delay)


def get_news(ticker: str, count: int = 10):
    stock = yf.Ticker(ticker)
    news = yf_retry(lambda: stock.get_news(count=count))
    return news


def main():
    parser = argparse.ArgumentParser(description="Fetch stock news via yfinance")
    parser.add_argument("ticker", help="Stock symbol (e.g. AAPL, TSLA)")
    parser.add_argument(
        "-n", "--count", type=int, default=10, help="Number of articles (default: 10)"
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output as JSON"
    )
    args = parser.parse_args()

    news = get_news(args.ticker, args.count)

    if not news:
        print("No news found.")
        return

    if args.json:
        print(json.dumps(news, indent=2, default=str))
        return

    for i, article in enumerate(news, 1):
        content = article.get("content", {})
        print(f"--- [{i}] ---")
        print(f"Title:    {content.get('title', 'N/A')}")
        print(f"Date:     {content.get('pubDate', 'N/A')}")
        print(f"Summary:  {content.get('summary', 'N/A')[:200]}...")
        print(f"URL:      {content.get('canonicalUrl', {}).get('url', 'N/A')}")
        print()


if __name__ == "__main__":
    main()
