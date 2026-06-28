"""EDA analysis library — pure operators (data in, data out). No plots, no I/O."""

import pandas as pd


def select_columns(master: pd.DataFrame, prefix: str = "Return_") -> pd.DataFrame:
    """Subset: keep columns starting with prefix."""
    return master[[c for c in master.columns if c.startswith(prefix)]]


def mean_returns(returns: pd.DataFrame) -> pd.Series:
    """Aggregate: mean daily return per stock."""
    return returns.mean()


def volatility(returns: pd.DataFrame) -> pd.Series:
    """Aggregate: daily volatility (std) per stock."""
    return returns.std()


def annualise_volatility(daily_vol: pd.Series) -> pd.Series:
    """Transform: daily vol -> annual (x sqrt 252)."""
    return daily_vol * (252**0.5)


def cumulative_returns(returns: pd.DataFrame) -> pd.DataFrame:
    """Transform: % returns -> running growth factor."""
    return (1 + returns / 100).cumprod()


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Aggregate: pairwise correlation matrix."""
    return returns.corr()


def rank_pairs(corr: pd.DataFrame) -> pd.DataFrame:
    """Reshape: matrix -> unique pairs ranked by |corr|."""
    long = corr.stack().reset_index()
    long.columns = ["stock_a", "stock_b", "corr"]
    long = long[long["stock_a"] < long["stock_b"]]
    order = long["corr"].abs().sort_values(ascending=False).index
    return long.loc[order].reset_index(drop=True)


def beta(returns: pd.DataFrame, market_col: str = "Return_SP500") -> pd.Series:
    """Aggregate: beta per stock vs benchmark = cov(r, mkt)/var(mkt)."""
    market = returns[market_col]
    var_market = market.var()
    stocks = returns.drop(columns=[market_col])
    return stocks.apply(lambda col: col.cov(market) / var_market)


def rolling_correlation(
    returns: pd.DataFrame, col_a: str, col_b: str, window: int = 63
) -> pd.Series:
    """Transform: rolling-window correlation between two columns."""
    return returns[col_a].rolling(window).corr(returns[col_b])
