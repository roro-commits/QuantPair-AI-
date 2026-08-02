"""Phase 4 — unilateral pairs trading backtest on the locked pair. Composes strategy.py operators."""

import pandas as pd

from quantpairs.reusableModule.eda.eda import (
    select_columns,
    volatility,
    cumulative_returns,
)
from quantpairs.reusableModule.cointegration.cointergration import adf_pvalue, half_life
from quantpairs.reusableModule.strategy.strategy import (
    price_ratio,
    moving_average,
    ratio_difference,
    rolling_zscore,
    daily_change,
    generate_positions,
    strategy_returns,
    sharpe_ratio,
    max_drawdown,
    trade_count,
)

DATA = "/home/rotimi/_developement/QuantPair-AI-/data_files/masterData"
TABLES = "strategy_output"
PAIR = ("QCOM", "AMD")  # locked pair from Phase 3 (provisional)
WINDOW = 20  # MA + rolling std window (Altucher)
ENTRY_Z = 1.5
EXIT_Z = 0.5
MOVE_PCT = 2.0  # same-day P1 move filter
TRAIN_END = "2023-12-31"  # train/test boundary for reporting


def strip_prefix(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the Close_ prefix so columns match ticker names."""
    return df.rename(columns=lambda s: s.replace("Close_", ""))


def assign_legs(close: pd.DataFrame, a: str, b: str) -> tuple:
    """P1 = the more volatile leg (by daily return std), P2 = the more stable."""
    vols = volatility(close[[a, b]].apply(daily_change))
    return (a, b) if vols[a] >= vols[b] else (b, a)


def performance(returns: pd.Series, positions: pd.Series, label: str) -> dict:
    """Metrics row for one window slice."""
    growth = cumulative_returns(returns.fillna(0).to_frame("strategy"))["strategy"]
    return {
        "window": label,
        "cumulative_return_pct": (growth.iloc[-1] - 1) * 100,
        "sharpe": sharpe_ratio(returns),
        "max_drawdown_pct": max_drawdown(returns) * 100,
        "trades": trade_count(positions),
        "days_in_market_pct": (positions != 0).mean() * 100,
    }


def main()-> None:
    import os

    os.makedirs(TABLES, exist_ok=True)

    master = pd.read_csv(f"{DATA}/master_data.csv", index_col="Date", parse_dates=True)
    close = strip_prefix(select_columns(master, "Close_"))

    p1_name, p2_name = assign_legs(close, *PAIR)
    p1, p2 = close[p1_name], close[p2_name]
    print(f"P1 (volatile) = {p1_name}, P2 (stable) = {p2_name}")

    # steps 1-5: operator chain
    ratio = price_ratio(p1, p2)
    ma = moving_average(ratio, WINDOW)
    diff = ratio_difference(ratio, ma)
    z = rolling_zscore(diff, WINDOW)

    # sanity checks on the traded series (reuses cointegration operators)
    print(
        f"diff ADF p = {adf_pvalue(diff):.4f}, diff half-life = {half_life(diff.dropna()):.1f}d"
    )

    # steps 6-8: signals and returns
    p1_change = daily_change(p1)
    positions = generate_positions(z, p1_change, ENTRY_Z, EXIT_Z, MOVE_PCT)
    returns = strategy_returns(positions, p1_change)

    signals = pd.DataFrame(
        {
            "ratio": ratio,
            "ma": ma,
            "diff": diff,
            "z": z,
            "p1_change": p1_change,
            "position": positions,
            "strategy_return": returns,
        }
    )
    signals.to_csv(f"{TABLES}/signals.csv")

    # train/test reporting (rolling stats -> no fitted params, no refit needed)
    train = signals.loc[:TRAIN_END]
    test = signals.loc[TRAIN_END:].iloc[1:]
    results = pd.DataFrame(
        [
            performance(
                train["strategy_return"], train["position"], f"train (<= {TRAIN_END})"
            ),
            performance(
                test["strategy_return"], test["position"], f"test (> {TRAIN_END})"
            ),
            performance(signals["strategy_return"], signals["position"], "full"),
        ]
    )
    print("\n=== Strategy performance ===\n", results.round(2))
    results.to_csv(f"{TABLES}/performance.csv", index=False)
    print(f"\nSaved -> {TABLES}/")


if __name__ == "__main__":
    main()
