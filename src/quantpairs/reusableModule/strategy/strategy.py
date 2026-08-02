"""Unilateral pairs trading library — pure operators (data in, data out). No plots, no I/O.

System: Altucher, Trade Like a Hedge Fund (2004) — see trading_strategy_doc/trading_strategy.md
"""
import pandas as pd


def price_ratio(p1: pd.Series, p2: pd.Series) -> pd.Series:
    """Transform: step 1 — ratio = p1 / p2."""
    return p1 / p2


def moving_average(series: pd.Series, window: int = 20) -> pd.Series:
    """Transform: steps 2 & 4 — rolling mean over window days."""
    return series.rolling(window).mean()


def ratio_difference(ratio: pd.Series, ma: pd.Series) -> pd.Series:
    """Transform: step 3 — difference between ratio and its moving average."""
    return ratio - ma


def rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """Transform: step 5 — (series - rolling mean) / rolling std.

    NOTE: 'prior 20 days' read as rolling(20) including today —
    shift(1) variant pending step-5 verification against the source.
    """
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std


def daily_change(series: pd.Series) -> pd.Series:
    """Transform: day-over-day % change (same formula as master data returns)."""
    return series.pct_change() * 100


def generate_positions(
    z: pd.Series,
    p1_change: pd.Series,
    entry_z: float = 1.5,
    exit_z: float = 0.5,
    move_pct: float = 2.0,
) -> pd.Series:
    """Transform: steps 6-8 — z + daily change -> position series.

    Position state: -1 short, 0 flat, +1 long. Entry needs BOTH the
    z-threshold and the same-day 2% move; exit needs only reversion.
    """
    pos = 0
    out = []
    for zi, chg in zip(z, p1_change):
        if pd.isna(zi) or pd.isna(chg):          # warm-up rows
            out.append(0)
            continue
        if pos == 0:
            if zi > entry_z and chg >= move_pct:      # step 6: short entry
                pos = -1
            elif zi < -entry_z and chg <= -move_pct:  # step 7: long entry
                pos = 1
        elif pos == -1 and zi < exit_z:               # step 8: cover
            pos = 0
        elif pos == 1 and zi > -exit_z:               # step 8: sell
            pos = 0
        out.append(pos)
    return pd.Series(out, index=z.index, name="position")


def strategy_returns(positions: pd.Series, p1_returns: pd.Series) -> pd.Series:
    """Transform: position held at close t earns day t+1's P1 return (no same-day lookahead)."""
    return positions.shift(1) * p1_returns


def sharpe_ratio(returns: pd.Series) -> float:
    """Aggregate: annualised Sharpe (rf = 0) from daily % returns."""
    r = returns.dropna()
    if r.std() == 0:
        return 0.0
    return r.mean() / r.std() * (252**0.5)


def max_drawdown(returns: pd.Series) -> float:
    """Aggregate: worst peak-to-trough drawdown of the growth curve (negative fraction)."""
    growth = (1 + returns.fillna(0) / 100).cumprod()
    return (growth / growth.cummax() - 1).min()


def trade_count(positions: pd.Series) -> int:
    """Aggregate: number of entries (flat -> long/short transitions)."""
    return int(((positions != positions.shift(1)) & (positions != 0)).sum())
