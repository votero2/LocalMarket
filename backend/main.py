from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from market_data import load_market_data


app = FastAPI(title = "MarketMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["GET"],
    allow_headers=["*"]
)

@app.get("/health")
def health_check():
    return{
        "status": "ok",
        "project": "MarketMind"
    }
    

@app.get("/stocks")
def get_stocks():
    return {
        "stocks":[
             {"ticker": "AAPL", "name": "Apple"},
            {"ticker": "MSFT", "name": "Microsoft"},
            {"ticker": "NVDA", "name": "NVIDIA"},
            {"ticker": "JPM", "name": "JPMorgan Chase"},
            {"ticker": "XOM", "name": "Exxon Mobil"}
        ]
    }
    
DEMO_QUOTES = {
    "AAPL": {"price": 200.00, "change_percent": 1.20},
    "MSFT": {"price": 420.00, "change_percent": 0.75},
    "NVDA": {"price": 130.00, "change_percent": -1.40},
    "JPM": {"price": 240.00, "change_percent": 0.35},
    "XOM": {"price": 110.00, "change_percent": -0.60}
}


@app.get("/stocks/{ticker}")
def get_stock_details(ticker: str):
    data = load_market_data(ticker)
    return {
        key: value
        for key, value in data.items()
        if key != "history"
    }
    
    
  
DEMO_HISTORY = {
    "AAPL": [192, 194, 193, 196, 195, 198, 197, 199, 198, 200],
    "MSFT": [405, 408, 406, 412, 410, 415, 413, 418, 417, 420],
    "NVDA": [138, 140, 137, 135, 136, 133, 134, 132, 131, 130],
    "JPM": [230, 232, 231, 234, 233, 236, 235, 238, 237, 240],
    "XOM": [115, 114, 116, 113, 114, 112, 113, 111, 112, 110]
}


@app.get("/stocks/{ticker}/history")
def get_stock_history(ticker: str):
    data = load_market_data(ticker)
    return {
        "ticker": data["ticker"],
        "source": data["source"],
        "currency": data["currency"],
        "as_of": data["as_of"],
        "history": data["history"]
    }