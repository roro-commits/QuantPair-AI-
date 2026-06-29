"""Phase 3 — cointegration testing on the EDA shortlist. Composes cointegration.py operators."""

from typing import Dict
import pandas as pd

from quantpairs.reusableModule.eda.eda import select_columns
from quantpairs.reusableModule.cointegration.cointergration import (
    coint_pvalue,
    hedge_ratio,
    compute_spread,
    adf_pvalue,
    half_life,
)

DATA = "/home/rotimi/_developement/QuantPair-AI-/data_files/masterData"
SHORT_LIST = "/home/rotimi/_developement/QuantPair-AI-/eda_output/tables"
TABLES = "cointegration_output"
TOP_N = 36  # shortlist pairs to test (head(N) automation knob)
ALPHA = 0.05  # cointegration significance threshold
MAX_HALF_LIFE = 126  # tradeable gate: <= ~6 months reversion


def strip_prefix(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the Close_ prefix so columns match the shortlist ticker names."""
    return df.rename(columns=lambda s: s.replace("Close_", ""))


def test_pair(close: pd.DataFrame, a: str, b: str) -> Dict:
    """Run both directions, keep the stronger; derive beta, spread, half-life."""
    pair = close[[a, b]].dropna()
    sa, sb = pair[a], pair[b]
    p_ab, p_ba = coint_pvalue(sa, sb), coint_pvalue(sb, sa)
    if p_ab <= p_ba:
        y, x, yname, xname, pval = sa, sb, a, b, p_ab
    else:
        y, x, yname, xname, pval = sb, sa, b, a, p_ba
    beta = hedge_ratio(y, x)
    spread = compute_spread(y, x, beta)
    hl = half_life(spread)
    tradeable = (pval < ALPHA) and (0 < hl <= MAX_HALF_LIFE)
    return {
        "y": yname, "x": xname,
        "coint_p": pval,
        "beta": beta,
        "spread_adf_p": adf_pvalue(spread),
        "half_life": hl,
        "tradeable": tradeable,
    }

def main():
    import os
    os.makedirs(TABLES, exist_ok=True)

    master = pd.read_csv(f"{DATA}/master_data.csv", index_col="Date", parse_dates=True)
    close = strip_prefix(select_columns(master, "Close_"))

    BENCHMARKS = {"GSPC", "VIX", "^GSPC", "^VIX", "SP500"}
    shortlist = pd.read_csv(f"{SHORT_LIST}/pair_shortlist.csv")

    rows = []
    for _, p in shortlist.head(TOP_N).iterrows():
        a, b = p["stock_a"], p["stock_b"]
        if a in BENCHMARKS or b in BENCHMARKS:
            continue
        if a not in close.columns or b not in close.columns:
            continue
        rows.append(test_pair(close, a, b))

    results = pd.DataFrame(rows).sort_values("coint_p").reset_index(drop=True)
    print("\n=== Cointegration results ===\n", results.round(4))
    results.to_csv(f"{TABLES}/cointegration_results.csv", index=False)

    locked = results[results["tradeable"]]
    print(f"\n=== Locked pairs (p < {ALPHA} and half-life <= {MAX_HALF_LIFE}d) ===")
    print(locked[["y", "x", "coint_p", "beta", "half_life"]].round(4)
          if not locked.empty else "  none passed both gates")
    locked.to_csv(f"{TABLES}/locked_pairs.csv", index=False)
    print(f"\nSaved -> {TABLES}/")


if __name__ == "__main__":
    main()
