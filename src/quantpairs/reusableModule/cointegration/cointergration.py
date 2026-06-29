"""Cointegration analysis library — pure operators (data in, data out). No plots, no I/O."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint


def adf_pvalue(series: pd.Series) -> float:
    """Aggregate: ADF p-value (low => stationary)."""
    return adfuller(series.dropna())[1]


def coint_pvalue(y: pd.Series, x: pd.Series) -> float:
    """Aggregate: Engle-Granger p-value for y on x (direction-sensitive)."""
    return coint(y, x)[1]


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """Aggregate: OLS slope beta from regressing y on x (with intercept)."""
    model = sm.OLS(y, sm.add_constant(x)).fit()
    return model.params.iloc[1]


def compute_spread(y: pd.Series, x: pd.Series, beta: float) -> pd.Series:
    """Transform: spread = y - beta * x."""
    return y - beta * x


def zscore(spread: pd.Series) -> pd.Series:
    """Transform: standardise spread to (spread - mean) / std."""
    return (spread - spread.mean()) / spread.std()


def half_life(spread: pd.Series) -> float:
    """Aggregate: mean-reversion half-life in days (AR(1) on the spread)."""
    lag = spread.shift(1)
    delta = (spread - lag).dropna()
    lag = lag.dropna().loc[delta.index]
    lam = sm.OLS(delta, sm.add_constant(lag)).fit().params.iloc[1]
    if lam >= 0:                      # not mean-reverting
        return np.inf
    return -np.log(2) / lam
