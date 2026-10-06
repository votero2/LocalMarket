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

      {details.model_status === "experimental" &&
 typeof details.up_probability === "number" ? (
  <div className="quote-card">
    <h3>Experimental prediction</h3>

    <p>Estimated probability of a higher next-session close</p>
    <strong>
      {(details.up_probability * 100).toFixed(2)}%
    </strong>

    <p>
      Based on the close dated {details.prediction_as_of}
      {" · "}{details.model_name}
    </p>

    {details.model_metrics && (
      <>
        <p>
          Test accuracy:{" "}
          {(details.model_metrics.accuracy * 100).toFixed(2)}%
          {" · "}Baseline:{" "}
          {(details.model_metrics.baseline_accuracy * 100).toFixed(2)}%
        </p>

        <p>
          Probability error (Brier, lower is better):{" "}
          {details.model_metrics.brier_score.toFixed(4)}
          {" · "}Baseline:{" "}
          {details.model_metrics.baseline_brier_score.toFixed(4)}
        </p>

        <p>
          Evaluated on {details.model_metrics.test_rows} sessions
          {" · "}{details.model_metrics.test_start}
          {" to "}{details.model_metrics.test_end}
        </p>
      </>
    )}

    <p className="demo-label">
      Research prototype · Predictive advantage not established
    </p>
  </div>
) : (
  <p>
    {details.model_status === "insufficient_data"
      ? "Not enough recent data for a prediction."
      : "Prediction model: not trained for this stock yet."}
  </p>
)}
    </div>
  );
}

export default StockDetails;