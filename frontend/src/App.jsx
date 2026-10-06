import { useState, useEffect } from 'react'
import './App.css'
import StockDetails from './StockDetails'
import PriceChart from './PriceChart'

function App() {
  const [stocks, setStocks] = useState([])
  const [selectedTicker, setSelectedTicker] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const controller = new AbortController();

    async function loadStocks() {
      try{
        const response = await fetch(
          "http://127.0.0.1:8000/stocks",
          {signal: controller.signal}
        );

        if(!response.ok){
          throw new Error("Could not retrieve stocks.")
        }

        const data = await response.json();
        setStocks(data.stocks)
        setSelectedTicker(data.stocks[0]?.ticker ?? "");
      } catch(err){
        if (err.name !== "AbortError"){
          setError("Could not connect. Check that the Python API is running.")
        }
      } finally{
        if(!controller.signal.aborted){
          setLoading(false)
        }
      }
    }

    loadStocks()

    return () => controller.abort()
  }, [])

  return (
    <main>
     <h1>MarketMind</h1>
     <p>Local stock research dashboard</p>

     {loading && <p>Loading stocks...</p>}
     {error && <p role="alert">{error}</p>}

     <div>
      {stocks.map((stock) =>(
        <button
        key={stock.ticker}
        onClick={() => setSelectedTicker(stock.ticker)}
        aria-pressed={selectedTicker === stock.ticker}
        >
            {stock.ticker}
        </button>
      ))}
     </div>

     {selectedTicker && (
      <section>
        <h2>{selectedTicker}</h2>
        <p>
          {stocks.find(
            (stock) => stock.ticker === selectedTicker
          )?.name}
        </p>
        <StockDetails ticker={selectedTicker}/>
        <PriceChart ticker={selectedTicker}/>
      </section>
     )}
    </main>
  )
}

export default App
