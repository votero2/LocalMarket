from pathlib import Path

import joblib

from features import build_features


MODEL_DIR = Path(__file__).resolve().parent / "models"


def predict_stock(ticker, frame):
    model_path = MODEL_DIR / f"{ticker}.joblib"

    if not model_path.exists():
        return {
            "up_probability": None,
            "model_status": "not_trained",
        }

    bundle = joblib.load(model_path)

    latest_features = build_features(frame).iloc[[-1]]
    latest_features = latest_features[bundle["feature_columns"]]

    if latest_features.isna().any().any():
        return {
            "up_probability": None,
            "model_status": "insufficient_data",
        }

    model = bundle["model"]
    up_index = list(model.classes_).index(1)
    probability = model.predict_proba(latest_features)[0, up_index]

    return {
        "up_probability": float(probability),
        "model_status": "experimental",
        "model_name": "Logistic regression",
        "prediction_as_of": frame.index[-1].strftime("%Y-%m-%d"),
        "prediction_target": "next_session_close_higher",
        "model_metrics": bundle["metrics"],
    }