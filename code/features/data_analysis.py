"""Phase 2 EDA — composes eda.py operators, saves tables (CSV) and plots (PNG)."""
import math
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from quantpairs.reusableModule.eda.eda import (
    select_columns,
    mean_returns,
    volatility,
    annualise_volatility,
    cumulative_returns,
    correlation_matrix,
    rank_pairs,
    beta,
    rolling_correlation,
)

DATA = "/home/rotimi/_developement/QuantPair-AI-/data_files/masterData"
FIGS = "eda_output/figures"
TABLES = "eda_output/tables"
MARKET = "Return_SP500"
TOP_N = 6  # how many top pairs to scatter / roll


def strip_prefix(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the Return_ prefix from column names for readable output."""
    return df.rename(columns=lambda s: s.replace("Return_", ""))


def save(fig_name: str) -> None:
    """Save current figure then show."""
    plt.tight_layout()
    plt.savefig(f"{FIGS}/{fig_name}", dpi=150)
    plt.show()


def main() -> None:
    os.makedirs(FIGS, exist_ok=True)
    os.makedirs(TABLES, exist_ok=True)

    # Load + subset
    master = pd.read_csv(f"{DATA}/master_data.csv", index_col="Date", parse_dates=True)
    returns = select_columns(master)  # all Return_* (incl SP500)
    stocks = strip_prefix(returns.drop(columns=[MARKET]))  # stock-only, clean names

    # Summary table: mean, daily vol, annual vol, beta
    b = beta(returns, MARKET)
    b.index = b.index.str.replace("Return_", "")
    summary = pd.DataFrame(
        {
            "mean_return": mean_returns(stocks),
            "daily_vol": volatility(stocks),
            "annual_vol": annualise_volatility(volatility(stocks)),
            "beta": b,
        }
    )
    print("\n=== Summary ===\n", summary.round(4))
    summary.to_csv(f"{TABLES}/summary.csv")

    # Volatility bar (calm -> jumpy)
    vol = annualise_volatility(volatility(stocks)).sort_values()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=vol.values, y=vol.index, orient="h", color="steelblue")
    plt.title("Annualised Volatility (calm -> jumpy)")
    plt.xlabel("annual vol")
    save("volatility_bar.png")

    # Beta bar (market sensitivity, 1.0 = moves with market)
    bs = b.sort_values()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=bs.values, y=bs.index, orient="h", color="indianred")
    plt.axvline(1.0, ls="--", c="grey", label="market beta = 1")
    plt.title("S&P 500 Beta")
    plt.xlabel("beta")
    plt.legend()
    save("beta_bar.png")

    # Correlation matrix + heatmap
    corr = correlation_matrix(stocks)
    plt.figure(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
    plt.title("Return Correlation — S&P 500 Tech")
    save("correlation_heatmap.png")

    # Ranked pair shortlist
    pairs = rank_pairs(corr)
    print("\n=== Top pairs ===\n", pairs.head(10).round(4))
    pairs.to_csv(f"{TABLES}/pair_shortlist.csv", index=False)

    # Cumulative growth curves
    growth = cumulative_returns(stocks)
    plt.figure(figsize=(11, 6))
    growth.plot(ax=plt.gca())
    plt.title("Cumulative Growth (1.0 = flat)")
    plt.ylabel("growth factor")
    save("cumulative_returns.png")

    # Pairwise scatter for top candidates
    top = pairs.head(TOP_N)
    rows = math.ceil(len(top) / 2)
    fig, axes = plt.subplots(rows, 2, figsize=(11, 4 * rows))
    for ax, (_, p) in zip(axes.flat, top.iterrows()):
        sns.regplot(
            x=stocks[p.stock_a],
            y=stocks[p.stock_b],
            ax=ax,
            scatter_kws={"s": 8, "alpha": 0.4},
        )
        ax.set_title(f"{p.stock_a} vs {p.stock_b} (r={p['corr']:.2f})")
    for ax in axes.flat[len(top) :]:
        ax.axis("off")
    save("pair_scatter.png")

    # Rolling correlation — top N pairs (stability)
    plt.figure(figsize=(11, 5))
    for _, p in top.iterrows():
        rc = rolling_correlation(stocks, p.stock_a, p.stock_b, window=63)
        rc.plot(ax=plt.gca(), label=f"{p.stock_a}/{p.stock_b}")
    plt.title("63-day Rolling Correlation — top pairs")
    plt.ylabel("correlation")
    plt.legend()
    save("rolling_corr_top_pairs.png")

    print(f"\nSaved tables -> {TABLES}/  figures -> {FIGS}/")


if __name__ == "__main__":
    main()
