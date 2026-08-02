"""Phase 5 — train pair classifiers + voting ensemble on strategy features. Composes build_features.py."""

import pickle

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from quantpairs.reusableModule.eda.eda import select_columns
from quantpairs.reusableModule.features.build_features import build_features, build_labels
from quantpairs.reusableModule.strategy.strategy import (
    price_ratio, moving_average, ratio_difference, rolling_zscore,
)

DATA = "/home/rotimi/_developement/QuantPair-AI-/data_files/masterData"
OUT = "model_output"
PAIR = ("QCOM", "AMD")   # locked pair (provisional)
WINDOW = 20
K = 5                    # label horizon (half-life ~9d)
DEAD_ZONE = 0.25
TRAIN_END = "2023-12-31"

MODELS = {
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "forest": RandomForestClassifier(n_estimators=200, random_state=42),
    "gboost": GradientBoostingClassifier(random_state=42),
}


def strip_prefix(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the Close_ prefix so columns match ticker names."""
    return df.rename(columns=lambda s: s.replace("Close_", ""))


def main():
    import os
    os.makedirs(OUT, exist_ok=True)

    master = pd.read_csv(f"{DATA}/master_data.csv", index_col="Date", parse_dates=True)
    close = strip_prefix(select_columns(master, "Close_"))
    p1, p2 = close[PAIR[0]], close[PAIR[1]]

    X = build_features(p1, p2, WINDOW)
    ratio = price_ratio(p1, p2)
    z = rolling_zscore(ratio_difference(ratio, moving_average(ratio, WINDOW)), WINDOW)
    y = build_labels(z, K, DEAD_ZONE)

    data = X.join(y.rename("label")).dropna()
    train = data.loc[:TRAIN_END].iloc[:-K]           # purge: no train label overlaps test
    test = data.loc[TRAIN_END:].iloc[1:]
    X_train, y_train = train.drop(columns="label"), train["label"]
    X_test, y_test = test.drop(columns="label"), test["label"]

    # baselines every model must beat
    rule = pd.Series("diverge", index=test.index)
    rule[test["z"].abs() > 1] = "revert"
    print(f"train {len(train)} rows, test {len(test)} rows")
    print(f"baseline always-revert: {(y_test == 'revert').mean():.2%}")
    print(f"baseline one-rule (|z|>1): {(rule == y_test).mean():.2%}\n")

    # individual models
    rows = []
    for name, model in MODELS.items():
        model.fit(X_train, y_train)
        rows.append({"model": name, "test_accuracy": accuracy_score(y_test, model.predict(X_test))})

    # soft-voting ensemble of the model families
    ensemble = VotingClassifier([(n, m) for n, m in MODELS.items()], voting="soft")
    ensemble.fit(X_train, y_train)
    rows.append({"model": "ensemble", "test_accuracy": accuracy_score(y_test, ensemble.predict(X_test))})

    results = pd.DataFrame(rows)
    print(results.round(4).to_string(index=False))
    print("\n=== Ensemble ===\n", classification_report(y_test, ensemble.predict(X_test)))
    results.to_csv(f"{OUT}/model_comparison.csv", index=False)

    with open(f"{OUT}/model.pkl", "wb") as f:
        pickle.dump(ensemble, f)
    print(f"Saved -> {OUT}/model.pkl (ensemble)")


if __name__ == "__main__":
    main()
