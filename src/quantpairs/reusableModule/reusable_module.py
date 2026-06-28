import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    recall_score,
    roc_auc_score,
    roc_curve,
    classification_report,
    confusion_matrix,
)
from typing import Tuple, List, Union


# ============================================
# SUBSET — DataFrame -> DataFrame
# ============================================


def drop_columns(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Remove specified columns from a DataFrame."""
    return data.drop(columns=columns)


# ============================================
# TRANSFORM — DataFrame -> DataFrame
# ============================================


def encode_categorical(data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Encode categorical columns using OneHotEncoder."""
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(data[columns])
    encoded_df = pd.DataFrame(
        encoded, columns=encoder.get_feature_names_out(columns), index=data.index
    )
    return data.drop(columns=columns).join(encoded_df)


def scale_features(
    X_train: pd.DataFrame, X_test: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Scale features using StandardScaler. Fit on train, transform both."""
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=X_test.columns, index=X_test.index
    )
    return X_train_scaled, X_test_scaled


def strip_characters(data: pd.DataFrame, column: str, chars: str) -> pd.DataFrame:
    """Remove specific characters from a string column and convert to numeric."""
    df = data.copy()
    df[column] = df[column].str.replace(chars, "", regex=False).astype(int)
    return df


def rename_column(
    data: pd.DataFrame, column_name: str, new_column_name: str
) -> pd.DataFrame:
    """Remove a column"""
    df = data.rename(columns={column_name: new_column_name})
    return df


# ============================================
# EXTRACT — DataFrame -> Series / DataFrame
# ============================================


def extract_target(data: pd.DataFrame, column: str) -> pd.Series:
    """Extract a single target variable as a Series."""
    return data[column]


def extract_features(data: pd.DataFrame, targets: List[str]) -> pd.DataFrame:
    """Extract feature columns by dropping target column(s)."""
    return data.drop(columns=targets)


# ============================================
# SPLIT — DataFrame -> DataFrame + DataFrame
# ============================================


def split_data(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.3, random_state: int = 42
) -> List[Union[pd.DataFrame, pd.Series]]:
    """Split features and target into train/test sets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


# ============================================
# MODEL — Fit and predict
# ============================================


def fit_decision_tree(X_train, y_train, **kwargs) -> DecisionTreeClassifier:
    """Fit a Decision Tree classifier."""
    model = DecisionTreeClassifier(**kwargs)
    model.fit(X_train, y_train)
    return model


def fit_random_forest(X_train, y_train, **kwargs) -> RandomForestClassifier:
    """Fit a Random Forest classifier."""
    model = RandomForestClassifier(**kwargs)
    model.fit(X_train, y_train)
    return model


def fit_neural_network(X_train, y_train, **kwargs) -> MLPClassifier:
    """Fit a Neural Network (MLP) classifier."""
    model = MLPClassifier(**kwargs)
    model.fit(X_train, y_train)
    return model


def predict_probabilities(model, X) -> pd.Series:
    """Get predicted probabilities for the positive class."""
    return model.predict_proba(X)[:, 1]


def predict_classes(probabilities, cutoff: float = 0.5) -> pd.Series:
    """Convert probabilities to class labels using a cutoff."""
    return (probabilities >= cutoff).astype(int)


# ============================================
# AGGREGATE — Evaluate model performance
# ============================================


def get_recall(y_true, y_pred) -> float:
    """Calculate sensitivity/recall."""
    return recall_score(y_true, y_pred)


def get_auc(y_true, y_prob) -> float:
    """Calculate area under the ROC curve."""
    return roc_auc_score(y_true, y_prob)


def get_roc_curve(y_true, y_prob) -> Tuple:
    """Get false positive rate, true positive rate for ROC plot."""
    return roc_curve(y_true, y_prob)


def get_confusion_matrix(y_true, y_pred):
    """Return confusion matrix."""
    return confusion_matrix(y_true, y_pred)


def get_classification_report(y_true, y_pred) -> str:
    """Return full classification report."""
    return classification_report(y_true, y_pred)


# ============================================
# COMBINE — Series -> DataFrame
# ============================================
def combine_columns(columns: dict) -> pd.DataFrame:
    """Join named Series side by side, aligned on a shared index."""
    return pd.concat(columns, axis=1, join="inner")


# ============================================
# CLEAN — DataFrame -> DataFrame
# ============================================
def drop_missing(data: pd.DataFrame) -> pd.DataFrame:
    """Drop rows containing missing values."""
    return data.dropna()


if __name__ == "__main__":
    pass
