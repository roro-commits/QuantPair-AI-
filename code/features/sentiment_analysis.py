"""Sentiment analysis — display-only. Composes sentiment.py. Output read ONLY by the dashboard."""

import urllib.request
import xml.etree.ElementTree as ET

import pandas as pd

from quantpairs.reusableModule.sentiment.sentiment import score_headlines, summarise_ticker

OUT = "sentiment_output"
TICKERS = ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL", "CRM", "ADBE", "AMD", "QCOM"]
MAX_HEADLINES = 20
RSS = "https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en"


def fetch_headlines(ticker: str, limit: int = MAX_HEADLINES) -> pd.DataFrame:
    """Google News RSS -> DataFrame of (title, published). Free, no key."""
    with urllib.request.urlopen(RSS.format(query=ticker), timeout=10) as r:
        root = ET.fromstring(r.read())
    items = root.findall(".//item")[:limit]
    return pd.DataFrame({
        "title": [i.findtext("title") for i in items],
        "published": [i.findtext("pubDate") for i in items],
    })


def main()-> None:
    import os
    os.makedirs(OUT, exist_ok=True)

    rows, all_scored = [], []
    for t in TICKERS:
        headlines = fetch_headlines(t)
        if headlines.empty:
            print(f"{t}: no headlines")
            continue
        scored = score_headlines(headlines)
        scored.insert(0, "ticker", t)
        all_scored.append(scored)
        rows.append(summarise_ticker(scored, t))

    summary = pd.DataFrame(rows)
    summary["as_of"] = pd.Timestamp.now().isoformat(timespec="seconds")
    print("\n=== Sentiment summary ===\n", summary.round(3))
    summary.to_csv(f"{OUT}/sentiment.csv", index=False)
    pd.concat(all_scored).to_csv(f"{OUT}/headlines_scored.csv", index=False)
    print(f"\nSaved -> {OUT}/")


if __name__ == "__main__":
    main()
