from time import monotonic
from datetime import datetime
from zoneinfo import ZoneInfo

from predict_model import predict_stock

import yfinance as yf
from fastapi import HTTPException

SUPPORTED_TICKERS = {"AAPL", "MSFT", "NVDA", "JPM", "XOM"}
CACHE = {}


def load_market_data(ticker: str):
    symbol = ticker.upper()

    if symbol not in SUPPORTED_TICKERS:
        raise HTTPException(404, "Stock not supported")

    cached = CACHE.get(symbol)

    if cached and monotonic() - cached["saved_at"] < 300:
        return cached["data"]

    today = datetime.now(ZoneInfo("America/New_York")).date()
    try:
        frame = yf.Ticker(symbol).history(
            period="3mo",
            interval="1d",
            auto_adjust=False,
            end= today.isoformat(),
            timeout=15
        )
        frame = frame.dropna(subset=["Close"])
    except Exception:
        raise HTTPException(502, "Market data provider unavailable")

    if len(frame) < 2:
        raise HTTPException(502, "Not enough market data returned")

    latest = float(frame["Close"].iloc[-1])
    previous = float(frame["Close"].iloc[-2])

    data = {
        "ticker": symbol,
        "source": "yahoo_finance",
        "currency": "USD",
        "as_of": frame.index[-1].strftime("%Y-%m-%d"),
        "price": round(latest, 2),
        "change_percent": round(
            (latest / previous - 1) * 100, 2
        ),
        "up_probability": None,
        "model_status": "not_trained",
        "history": [
            {
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2)
            }
            for date, row in frame.iterrows()
        ]
    }

    data.update(predict_stock(symbol,frame))
    CACHE[symbol] = {"saved_at": monotonic(), "data": data}
    return data