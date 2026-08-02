"""Shared feature library — pure operators (data in, data out). No plots, no I/O.

Single source of truth: build_features runs in training AND LEAN.
build_labels touches the future — training only, never in LEAN.
"""
import pandas as pd

from quantpairs.reusableModule.strategy.strategy import (
    price_ratio,
    moving_average,
    ratio_difference,
    rolling_zscore,
    daily_change,
)


def build_features(p1: pd.Series, p2: pd.Series, window: int = 20) -> pd.DataFrame:
    """Combine: two price series -> feature matrix (one row per day, computable at close t)."""
    ratio = price_ratio(p1, p2)
    diff = ratio_difference(ratio, moving_average(ratio, window))
    z = rolling_zscore(diff, window)
    return pd.DataFrame({
        "z": z,
        "z_change_1d": z.diff(1),
        "z_change_5d": z.diff(5),
        "p1_change": daily_change(p1),
        "vol_p1": daily_change(p1).rolling(window).std(),
        "vol_p2": daily_change(p2).rolling(window).std(),
    })


def build_labels(z: pd.Series, k: int = 5, dead_zone: float = 0.25) -> pd.Series:
    """Transform: z -> label per day. TRAINING ONLY (looks k days ahead).

    revert  : |z| shrinks by more than dead_zone over k days
    diverge : |z| grows by more than dead_zone
    flat    : otherwise. Last k days undefined (NaN).
    """
    dz = z.abs().shift(-k) - z.abs()
    labels = pd.Series("flat", index=z.index)
    labels[dz < -dead_zone] = "revert"
    labels[dz > dead_zone] = "diverge"
    labels[dz.isna()] = None
    return labels
