import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import yfinance as yf
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import FEATURE_COLUMNS, build_features

TICKER = "NVDA"
MODEL_DIR = Path(__file__).resolve().parent / "models"


def train():
    #Exclude today's session so we only complete daily bars.
    today = datetime.now(ZoneInfo("America/New_York")).date()
    
    frame = yf.Ticker(TICKER).history(
        period = "5y",
        interval = "1d",
        auto_adjust = False,
        end=today.isoformat(),
        timeout=30,
    )
    frame = frame.sort_index().dropna(subset=["Close"])
    frame = frame.loc[frame["Close"] > 0].copy()
    
    if len(frame) < 300:
        raise ValueError("Not enough historical data to train")
    
    features = build_features(frame)
    
    #Tomorrow's close is the answer we lear to predict.
    next_close = frame["Close"].shift(-1)
    target = (next_close > frame["Close"]).astype(float)
    
    #The newest row has no known next close yet
    target = target.where(next_close.notna())
    
    dataset = features.copy()
    dataset["target"] = target
    dataset = dataset.dropna()
    
    split = int(len(dataset) * 0.8)
    
    # Leave one row out at the boundary to separate target dates.
    training = dataset.iloc[:split - 1]
    testing = dataset.iloc[split:]
    
    X_train = training[FEATURE_COLUMNS]
    y_train = training["target"].astype(int)
    X_test = testing[FEATURE_COLUMNS]
    y_test = testing["target"].astype(int)
    
    if y_train.nunique() != 2:
        raise ValueError("Training requires both up and down examples.")
    
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000),
    )
    model.fit(X_train, y_train)
    
    baseline = DummyClassifier(strategy="prior")
    baseline.fit(X_train, y_train)
    
    probabilities = model.predict_proba(X_test)[:, 1]
    baseline_probabilities = baseline.predict_proba(X_test)[:, 1]
    
    metrics = {
         "accuracy": float(
            accuracy_score(y_test, model.predict(X_test))
        ),
        "baseline_accuracy": float(
            accuracy_score(y_test, baseline.predict(X_test))
        ),
        "brier_score": float(
            brier_score_loss(y_test, probabilities)
        ),
        "baseline_brier_score": float(
            brier_score_loss(y_test, baseline_probabilities)
        ),
        "train_rows": len(training),
        "test_rows": len(testing),
        "train_start": training.index[0].strftime("%Y-%m-%d"),
        "train_end": training.index[-1].strftime("%Y-%m-%d"),
        "test_start": testing.index[0].strftime("%Y-%m-%d"),
        "test_end": testing.index[-1].strftime("%Y-%m-%d"),
    }
    
    bundle = {
        "ticker": TICKER,
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics,
        "price_basis": "Close_auto_adjust_false",
        "target": "next_session_close_higher" 
    }
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    
    joblib.dump(bundle, MODEL_DIR / f"{TICKER}.joblib")
    
    report = MODEL_DIR / f"{TICKER}_metrics.json"
    report.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    
    print(f"\n{TICKER} evaluation:")
    print(json.dumps(metrics, indent=2))
    print(f"\nSaved model to {MODEL_DIR / f'{TICKER}.joblib'}")
    
    if __name__ == "__main__":
        train()
        