import React, { useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_ASNE_API_URL || 'http://localhost:8000/query';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`API error ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>ASNE Query Router</h1>
        <p>Ask a question, then inspect the route, confidence, latency, and cost.</p>
      </header>

      <main>
        <form className="query-form" onSubmit={handleSubmit}>
          <textarea
            rows="4"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query here"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Querying...' : 'Submit'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result-card">
            <h2>Answer</h2>
            <p>{result.answer}</p>
            <div className="metadata-grid">
              <div>
                <strong>Route</strong>
                <div>{result.route}</div>
              </div>
              <div>
                <strong>Confidence</strong>
                <div>{result.confidence}%</div>
              </div>
              <div>
                <strong>Latency</strong>
                <div>{result.latency_seconds}s</div>
              </div>
              <div>
                <strong>Cost</strong>
                <div>${result.cost_usd}</div>
              </div>
            </div>
            <div className="reason-box">
              <strong>Reason</strong>
              <p>{result.reason}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
