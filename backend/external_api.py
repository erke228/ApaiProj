"""
backend/external_api.py
-----------------------
Minimal HTTP server to accept transaction data from a partner bank.
Run with:  py backend/external_api.py

Requires: pip install flask

Stores incoming payloads to external_data/ and scores them with
the trained models.
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Flask not installed. Run: pip install flask")
    sys.exit(1)

import joblib
import pandas as pd

EXT_DIR = ROOT / "external_data"
EXT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "models"

app = Flask(__name__)

# ── Lazy model cache ────────────────────────────────────────────────────────────
_model_cache: dict = {}

def get_models(dataset_key: str = "creditcard") -> dict:
    if dataset_key not in _model_cache:
        ds_dir = MODEL_DIR / dataset_key
        models = {}
        if ds_dir.exists():
            for pkl in ds_dir.glob("*.pkl"):
                models[pkl.stem] = joblib.load(pkl)
        _model_cache[dataset_key] = models
    return _model_cache[dataset_key]


def score_record(record: dict, models: dict, feature_names: list) -> dict:
    row = {f: float(record.get(f, 0)) for f in feature_names}
    X = pd.DataFrame([row])
    probs = {}
    for name, model in models.items():
        try:
            probs[name] = float(model.predict_proba(X)[:, 1][0])
        except Exception:
            probs[name] = 0.0
    avg_prob = sum(probs.values()) / max(len(probs), 1)
    return {
        "transaction_id": record.get("transaction_id", str(uuid.uuid4())[:8]),
        "ml_probabilities": probs,
        "ml_avg_prob": avg_prob,
        "verdict": "FRAUD" if avg_prob >= 0.5 else "LEGIT",
    }


@app.route("/external/transactions", methods=["POST"])
def receive_transactions():
    """Accept a JSON array of transaction objects from the partner bank."""
    payload = request.get_json(force=True)
    if not isinstance(payload, list):
        payload = [payload]

    dataset_key = request.args.get("dataset", "creditcard")
    models = get_models(dataset_key)

    if not models:
        return jsonify({"error": f"No models found for dataset '{dataset_key}'"}), 400

    # Infer feature names from the first model
    sample = next(iter(models.values()))
    if hasattr(sample, "feature_names_in_"):
        feature_names = list(sample.feature_names_in_)
    elif hasattr(sample, "steps"):
        last = sample.steps[-1][1]
        feature_names = list(getattr(last, "feature_names_in_", []))
    else:
        feature_names = []

    results = [score_record(rec, models, feature_names) for rec in payload]

    # Persist raw payload
    day = datetime.utcnow().strftime("%Y-%m-%d")
    raw_file = EXT_DIR / f"raw_{day}.jsonl"
    with open(raw_file, "a", encoding="utf-8") as f:
        for rec in payload:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Persist scored results
    scored_file = EXT_DIR / f"scored_{day}.jsonl"
    with open(scored_file, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return jsonify({"scored": len(results), "results": results}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Defender External API"}), 200


if __name__ == "__main__":
    print("Starting Defender External API on http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
