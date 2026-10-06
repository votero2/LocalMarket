import { useEffect, useState } from "react";

function PriceChart({ ticker }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError("");

    async function loadHistory() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/stocks/${ticker}/history`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Could not load price history.");
        }

        const result = await response.json();

        if (!controller.signal.aborted) {
          setData(result);
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      }
    }

    loadHistory();
    return () => controller.abort();
  }, [ticker]);

  if (error) return <p role="alert">{error}</p>;

  if (!data || data.ticker !== ticker) {
    return <p>Loading chart...</p>;
  }

  const history = data.history;

  if (history.length < 2) {
    return <p>Not enough history to draw a chart.</p>;
  }

  const prices = history.map((point) => point.close);
  const minimum = Math.min(...prices);
  const maximum = Math.max(...prices);
  const padding = Math.max((maximum - minimum) * 0.15, 1);
  const lower = minimum - padding;
  const upper = maximum + padding;

  const points = prices.map((price, index) => {
    const x = 70 + (index / (prices.length - 1)) * 700;
    const y = 230 - ((price - lower) / (upper - lower)) * 200;
    return `${x},${y}`;
  }).join(" ");

  const color = prices[prices.length - 1] >= prices[0]
    ? "#6ee7b7"
    : "#fca5a5";

  return (
    <div className="price-chart">
      <h3>Price history</h3>
      <p>
        Yahoo Finance · 3 months · USD · Daily closes
     </p>

      <svg
        viewBox="0 0 800 280"
        role="img"
        aria-label={`${ticker} daily closing price history`}
      >
        <line x1="70" y1="30" x2="70" y2="230" />
        <line x1="70" y1="230" x2="770" y2="230" />

        <text x="8" y="40">${upper.toFixed(0)}</text>
        <text x="8" y="230">${lower.toFixed(0)}</text>
        <text x="70" y="260">{history[0].date}</text>
        <text x="770" y="260" textAnchor="end">{history[history.length -1].date}</text>

        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

export default PriceChart;