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

from features import (
    FEATURE_COLUMNS,
    EXPERIMENT_FEATURE_COLUMNS,
    build_features,
)
from sklearn.model_selection import TimeSeriesSplit

TICKER = "NVDA"
MODEL_DIR = Path(__file__).resolve().parent / "models"


def evaluate_windows(dataset, columns=FEATURE_COLUMNS, report_name="windows"):
    # Use the earlier 80%; keep the existing latest-period test separate.
    split = int(len(dataset) * 0.8)
    development = dataset.iloc[:split - 1]

    if len(development) < 700:
        raise ValueError("Not enough data for four evaluation windows.")

    splitter = TimeSeriesSplit(
        n_splits=4,
        test_size=126,
        gap=1,
    )

    results = []

    for window, (train_index, test_index) in enumerate(
        splitter.split(development), start=1
    ):
        training = development.iloc[train_index]
        testing = development.iloc[test_index]

        X_train = training[columns]
        y_train = training["target"].astype(int)
        X_test = testing[columns]
        y_test = testing["target"].astype(int)

        if y_train.nunique() != 2:
            raise ValueError(f"Window {window} needs both classes.")

        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000),
        )
        model.fit(X_train, y_train)

        baseline = DummyClassifier(strategy="prior")
        baseline.fit(X_train, y_train)

        probabilities = model.predict_proba(X_test)[:, 1]
        baseline_probabilities = baseline.predict_proba(X_test)[:, 1]

        result = {
            "window": window,
            "train_rows": len(training),
            "test_rows": len(testing),
            "train_end": training.index[-1].strftime("%Y-%m-%d"),
            "test_start": testing.index[0].strftime("%Y-%m-%d"),
            "test_end": testing.index[-1].strftime("%Y-%m-%d"),
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
        }

        results.append(result)
        print(f"\nWindow {window}:")
        print(json.dumps(result, indent=2))

    score_names = [
        "accuracy",
        "baseline_accuracy",
        "brier_score",
        "baseline_brier_score",
    ]
    averages = {
        name: sum(result[name] for result in results) / len(results)
        for name in score_names
    }

    report = {
    "ticker": TICKER,
    "feature_columns": columns,
    "windows": results,
    "average_scores": averages,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    report_path = MODEL_DIR / f"{TICKER}_{report_name}.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nAverage scores across four windows:")
    print(json.dumps(averages, indent=2))


def train(evaluate_only=False):
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
    if evaluate_only:
        print("\n=== ORIGINAL SIX FEATURES ===")
        evaluate_windows(
            dataset,
            columns=FEATURE_COLUMNS,
            report_name="windows",
        )

        print("\n=== EXPANDED NINE FEATURES ===")
        evaluate_windows(
            dataset,
            columns=EXPERIMENT_FEATURE_COLUMNS,
            report_name="windows_expanded",
        )
        return
    
    evaluate_windows(dataset)
    
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
        