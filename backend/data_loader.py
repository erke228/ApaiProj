"""
data_loader.py
--------------
Unified data loader for all three datasets in the DataSets/ folder:
 - creditcard.csv        (credit card fraud, target: 'Class')
 - Base.csv              (bank fraud, target detected automatically)
 - PS_20174392719_...csv (PaySim synthetic, target: 'isFraud')

The loader normalises the target column to 'fraud' (0 / 1),
drops non-numeric or identifier columns that cannot be used as
features, and returns a train / validation / test split.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# ──────────────────────────────────────────────────────────────────────
# Resolve the DataSets directory relative to this file's location
# ──────────────────────────────────────────────────────────────────────
DATASETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "DataSets")
)

# ──────────────────────────────────────────────────────────────────────
# Per-dataset configuration
# ──────────────────────────────────────────────────────────────────────
DATASET_CONFIG = {
    "creditcard": {
        "file": "creditcard.csv",
        "target": "Class",
        # these columns are dropped before training
        "drop_cols": [],
    },
    "paysim": {
        "file": "PS_20174392719_1491204439457_log.csv",
        "target": "isFraud",
        # nameOrig / nameDest are string IDs; isFlaggedFraud leaks the label
        "drop_cols": ["nameOrig", "nameDest", "isFlaggedFraud"],
        # one-hot-encode the 'type' column
        "categorical_cols": ["type"],
    },
    "base": {
        "file": "Base.csv",
        "target": None,          # auto-detected below
        "drop_cols": [],
    },
}


def _detect_target_column(df: pd.DataFrame) -> str:
    """Return the most likely binary target column (0 / 1 or False / True)."""
    candidates = [
        c for c in df.columns
        if c.lower() in ("fraud", "isfraud", "class", "label", "target", "isFraud")
    ]
    if candidates:
        return candidates[0]
    # fall back: the first binary integer column
    for c in df.columns:
        if df[c].dropna().isin([0, 1]).all() and df[c].nunique() == 2:
            return c
    raise ValueError(
        "Could not detect a binary target column. "
        "Please add a 'fraud' column to your CSV."
    )


def load_dataset(
    dataset_key: str = "creditcard",
    nrows: int | None = None,
    sample_frac: float | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Load one of the known datasets and return (X, y).

    Parameters
    ----------
    dataset_key : str
        One of 'creditcard', 'paysim', 'base'.
    nrows : int or None
        If set, read only this many rows (useful for quick tests).
    sample_frac : float or None
        If set, randomly sample this fraction of rows after loading.

    Returns
    -------
    X : pd.DataFrame
        Feature matrix (all-numeric, NaN-free).
    y : pd.Series
        Binary target (0 = legitimate, 1 = fraud).
    """
    cfg = DATASET_CONFIG[dataset_key]
    csv_path = os.path.join(DATASETS_DIR, cfg["file"])

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    df = pd.read_csv(csv_path, nrows=nrows, low_memory=False)

    if sample_frac is not None:
        df = df.sample(frac=sample_frac, random_state=42).reset_index(drop=True)

    # ── Determine target column ────────────────────────────────────────
    target_col = cfg.get("target") or _detect_target_column(df)
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in {cfg['file']}.")

    y = df[target_col].astype(int).rename("fraud")

    # ── Drop identifier / leaky columns ───────────────────────────────
    drop_cols = list(cfg.get("drop_cols", []))
    drop_cols.append(target_col)
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # ── One-hot encode requested categorical columns ───────────────────
    cat_cols = cfg.get("categorical_cols", [])
    if cat_cols:
        df = pd.get_dummies(df, columns=[c for c in cat_cols if c in df.columns])

    # ── Drop remaining non-numeric columns ────────────────────────────
    non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        df = df.drop(columns=non_numeric)

    # ── Fill any remaining NaNs ───────────────────────────────────────
    df = df.fillna(0)

    return df, y


def get_split(
    dataset_key: str = "creditcard",
    nrows: int | None = None,
    sample_frac: float | None = None,
    test_size: float = 0.15,
    val_size: float = 0.10,
    random_state: int = 42,
):
    """Return stratified train / validation / test splits.

    Returns
    -------
    X_train, X_val, X_test, y_train, y_val, y_test
    """
    X, y = load_dataset(dataset_key=dataset_key, nrows=nrows, sample_frac=sample_frac)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=test_size + val_size,
        random_state=random_state, stratify=y
    )
    relative_val = val_size / (test_size + val_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=1 - relative_val,
        random_state=random_state, stratify=y_temp
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


if __name__ == "__main__":
    for key in DATASET_CONFIG:
        print(f"\n── {key} ──")
        try:
            X, y = load_dataset(key, nrows=5000)
            print(f"  Shape : {X.shape}")
            print(f"  Fraud : {y.sum()} / {len(y)} ({100*y.mean():.2f}%)")
        except FileNotFoundError as e:
            print(f"  SKIP  : {e}")
