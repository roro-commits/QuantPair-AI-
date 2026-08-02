"""Sentiment library — pure operators (data in, data out). No plots, no I/O.

Display-only: nothing outside the dashboard reads this module's output.
Never imported by features/, model/, strategy/, or lean_app/.
"""
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_ANALYZER = SentimentIntensityAnalyzer()


def score_headline(text: str) -> float:
    """Aggregate: headline -> compound sentiment in [-1, 1]."""
    return _ANALYZER.polarity_scores(text)["compound"]


def score_headlines(headlines: pd.DataFrame) -> pd.DataFrame:
    """Transform: add a score column (headlines needs a 'title' column)."""
    out = headlines.copy()
    out["score"] = out["title"].apply(score_headline)
    return out


def sentiment_label(score: float) -> str:
    """Transform: compound score -> label (VADER conventional thresholds)."""
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


def summarise_ticker(scored: pd.DataFrame, ticker: str) -> dict:
    """Aggregate: scored headlines for one ticker -> one summary row."""
    mean = scored["score"].mean()
    return {
        "ticker": ticker,
        "n_headlines": len(scored),
        "mean_score": mean,
        "label": sentiment_label(mean),
    }
