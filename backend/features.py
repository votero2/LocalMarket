import numpy as np
import pandas as pd

# Keep these for the existing saved model.
FEATURE_COLUMNS = [
    "return_1d",
    "return_5d",
    "return_10d",
    "distance_ma10",
    "distance_ma20",
    "volatility_10d",
]

EXPERIMENT_FEATURE_COLUMNS = FEATURE_COLUMNS + [
    "intraday_return",
    "range_pct",
    "relative_volume20",
]


def build_features(frame):
    close = frame["Close"].astype(float)
    opening = frame["Open"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    volume = frame["Volume"].astype(float)

    daily_return = close.pct_change(fill_method=None)
    features = pd.DataFrame(index=frame.index)

    features["return_1d"] = daily_return
    features["return_5d"] = close.pct_change(5, fill_method=None)
    features["return_10d"] = close.pct_change(10, fill_method=None)

    features["distance_ma10"] = close / close.rolling(10).mean() - 1
    features["distance_ma20"] = close / close.rolling(20).mean() - 1
    features["volatility_10d"] = daily_return.rolling(10).std()

    features["intraday_return"] = close / opening.replace(0, np.nan) - 1
    features["range_pct"] = (high - low) / close
    features["relative_volume20"] = (
        volume / volume.rolling(20).mean().replace(0, np.nan) - 1
    )

    return features.replace([np.inf, -np.inf], np.nan)