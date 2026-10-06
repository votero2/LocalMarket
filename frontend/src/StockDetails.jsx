import { useEffect, useState } from "react";

function StockDetails({ ticker }) {
  const [details, setDetails] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    setError("");
    setDetails(null);

    async function loadDetails() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/stocks/${ticker}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Could not load stock details.");
        }

        const data = await response.json();
        setDetails(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      }
    }

    loadDetails();

    return () => controller.abort();
  }, [ticker]);

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (!details || details.ticker !== ticker) {
    return <p>Loading stock details...</p>;
  }

  return (
    <div>
      <p className="demo-label">
         Yahoo Finance · Daily data as of {details.as_of} · Not live
     </p>
      

      <div className="quote-grid">
        <article className="quote-card">
          <p>Latest daily close</p>
          <strong>
            {details.price.toLocaleString("en-US", {
              style: "currency",
              currency: details.currency
            })}
          </strong>
        </article>

        <article className="quote-card">
          <p>Change from previous close</p>
          <strong
            className={
              details.change_percent >= 0
                ? "positive"
                : "negative"
            }
          >
            {details.change_percent >= 0 ? "+" : ""}
            {details.change_percent.toFixed(2)}%
          </strong>
        </article>
      </div>

      <p>Prediction model: not trained yet.</p>
    </div>
  );
}

export default StockDetails;