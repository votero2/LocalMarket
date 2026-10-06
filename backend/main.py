from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


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
    symbol = ticker.upper()

    if symbol not in DEMO_QUOTES:
        raise HTTPException(
            status_code=404,
            detail="Stock not supported"
        )

    quote = DEMO_QUOTES[symbol]

    return {
        "ticker": symbol,
        "source": "demo",
        "currency": "USD",
        "price": quote["price"],
        "change_percent": quote["change_percent"],
        "up_probability": None,
        "model_status": "not_trained"
    }