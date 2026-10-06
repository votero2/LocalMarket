# MarketMind

Local stock research dashboard built with React and FastAPI.

## Current features
- Select AAPL, MSFT, NVDA, JPM, or XOM
- Fetch stock details from the Python API
- Display sample prices and daily changes
- Responsive dark dashboard

Prices are sample data. The prediction model is not trained yet.

## Run locally

Open two terminals from the project folder.

### Backend
```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Frontend
```powershell
cd frontend
npm run dev
```

Open http://localhost:5173.

## Planned features
- Historical market data
- Price charts
- Prediction model with evaluation on unseen data