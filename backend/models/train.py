"""
train.py
--------
Trains three ML models on each available dataset:
    1. Logistic Regression
    2. Random Forest
    3. XGBoost  (falls back to LightGBM if XGBoost unavailable)

After training, each model is saved to  models/<dataset>/<model_name>.pkl
and a comprehensive metrics report is written to  metrics.json.

Run from the project root:
    py backend/models/train.py
"""

import os
import sys
import json
import time
import joblib
import numpy as np
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    average_precision_score,
)

# ── Gradient boosting - try XGBoost first, fall back to LightGBM ────────────
try:
    from xgboost import XGBClassifier
    GB_NAME = "xgboost"
    def make_gb(scale_pos_weight=1.0):
        return XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            use_label_encoder=False,
            random_state=42,
            scale_pos_weight=scale_pos_weight,
            tree_method="hist",
            verbosity=0,
        )
except ImportError:
    try:
        from lightgbm import LGBMClassifier
        GB_NAME = "lightgbm"
        def make_gb(scale_pos_weight=1.0):
            return LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=63,
                random_state=42,
                class_weight="balanced",
                verbosity=-1,
            )
    except ImportError:
        GB_NAME = None
        make_gb = None

# ── Project path setup ───────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]      # project root
sys.path.insert(0, str(ROOT))

from backend.data_loader import get_split, DATASET_CONFIG

MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_PATH = ROOT / "metrics.json"


# ═══════════════════════════════════════════════════════════════════════════════
def evaluate(model, X, y, threshold: float = 0.5) -> dict:
    """Compute a comprehensive set of classification metrics."""
    proba = model.predict_proba(X)[:, 1]
    preds = (proba >= threshold).astype(int)

    cm = confusion_matrix(y, preds).tolist()
    report = classification_report(y, preds, output_dict=True, zero_division=0)

    return {
        "precision":         float(precision_score(y, preds, zero_division=0)),
        "recall":            float(recall_score(y, preds, zero_division=0)),
        "f1":                float(f1_score(y, preds, zero_division=0)),
        "roc_auc":           float(roc_auc_score(y, proba)),
        "avg_precision":     float(average_precision_score(y, proba)),
        "confusion_matrix":  cm,
        "classification_report": report,
        # fraud-class specific (row 1 of confusion matrix)
        "fraud_precision":   report.get("1", {}).get("precision", 0.0),
        "fraud_recall":      report.get("1", {}).get("recall",    0.0),
        "fraud_f1":          report.get("1", {}).get("f1-score",  0.0),
    }


def train_on_dataset(dataset_key: str, all_metrics: dict):
    """Train all three models on one dataset and save results."""
    print(f"\n{'='*60}")
    print(f"  Training on dataset: {dataset_key}")
    print(f"{'='*60}")

    # ── Load data ────────────────────────────────────────────────────
    # Use a sample for very large datasets to keep training time reasonable
    nrows = None
    sample_frac = None
    if dataset_key == "paysim":
        sample_frac = 0.20          # ~1.2M rows -> use 20 % (~240k)
    if dataset_key == "base":
        sample_frac = 0.30

    try:
        X_train, X_val, X_test, y_train, y_val, y_test = get_split(
            dataset_key=dataset_key,
            nrows=nrows,
            sample_frac=sample_frac,
        )
    except (FileNotFoundError, KeyError) as exc:
        print(f"  [SKIP] {exc}")
        return

    n_fraud   = int(y_train.sum())
    n_legit   = int(len(y_train) - n_fraud)
    ratio     = n_legit / max(n_fraud, 1)

    print(f"  Train size : {len(X_train):,}  (fraud={n_fraud:,}, ratio={ratio:.1f}:1)")
    print(f"  Val size   : {len(X_val):,}")
    print(f"  Test size  : {len(X_test):,}")
    print(f"  Features   : {X_train.shape[1]}")

    # ── Output directory ─────────────────────────────────────────────
    ds_dir = MODELS_DIR / dataset_key
    ds_dir.mkdir(parents=True, exist_ok=True)

    dataset_metrics = {}

    # ────────────────────────────────────────────────────────────────────
    # 1. Logistic Regression  (with StandardScaler in a Pipeline)
    # ────────────────────────────────────────────────────────────────────
    print("\n  [1/3] Logistic Regression ...", end=" ", flush=True)
    t0 = time.time()
    lr = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="saga",
            random_state=42,
        )),
    ])
    lr.fit(X_train, y_train)
    elapsed = time.time() - t0
    m = evaluate(lr, X_test, y_test)
    m["training_time_sec"] = round(elapsed, 2)
    dataset_metrics["logistic_regression"] = m
    joblib.dump(lr, ds_dir / "logistic_regression.pkl")
    print(f"done ({elapsed:.1f}s)  Recall={m['fraud_recall']:.3f}  ROC-AUC={m['roc_auc']:.3f}")

    # ────────────────────────────────────────────────────────────────────
    # 2. Random Forest
    # ────────────────────────────────────────────────────────────────────
    print("  [2/3] Random Forest ...", end=" ", flush=True)
    t0 = time.time()
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=42,
    )
    rf.fit(X_train, y_train)
    elapsed = time.time() - t0
    m = evaluate(rf, X_test, y_test)
    m["training_time_sec"] = round(elapsed, 2)
    dataset_metrics["random_forest"] = m
    joblib.dump(rf, ds_dir / "random_forest.pkl")
    print(f"done ({elapsed:.1f}s)  Recall={m['fraud_recall']:.3f}  ROC-AUC={m['roc_auc']:.3f}")

    # ────────────────────────────────────────────────────────────────────
    # 3. XGBoost / LightGBM
    # ────────────────────────────────────────────────────────────────────
    if make_gb is not None:
        print(f"  [3/3] {GB_NAME.title()} ...", end=" ", flush=True)
        t0 = time.time()
        gb = make_gb(scale_pos_weight=ratio)
        gb.fit(X_train, y_train)
        elapsed = time.time() - t0
        m = evaluate(gb, X_test, y_test)
        m["training_time_sec"] = round(elapsed, 2)
        dataset_metrics[GB_NAME] = m
        joblib.dump(gb, ds_dir / f"{GB_NAME}.pkl")
        print(f"done ({elapsed:.1f}s)  Recall={m['fraud_recall']:.3f}  ROC-AUC={m['roc_auc']:.3f}")
    else:
        print("  [3/3] SKIP - neither XGBoost nor LightGBM installed.")

    all_metrics[dataset_key] = dataset_metrics


# ═══════════════════════════════════════════════════════════════════════════════
def main():
    all_metrics: dict = {}

    for dataset_key in DATASET_CONFIG:
        train_on_dataset(dataset_key, all_metrics)

    # ── Save combined metrics JSON ────────────────────────────────────
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Metrics saved -> {METRICS_PATH}")
    print("[OK] Training complete - launch the dashboard with:")
    print("   py -m streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()
