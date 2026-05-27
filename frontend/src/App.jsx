import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

function badgeClass(model) {
  if (!model) return 'trace-badge trace-badge-default'
  const m = model.toLowerCase()
  if (m === 'tavily') return 'trace-badge trace-badge-tavily'
  if (m.includes('haiku')) return 'trace-badge trace-badge-haiku'
  if (m.includes('sonnet')) return 'trace-badge trace-badge-sonnet'
  return 'trace-badge trace-badge-default'
}

function Trace({ steps }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="trace">
      <button className="trace-toggle" onClick={() => setOpen(o => !o)}>
        {open ? '▼' : '▶'} Execution Trace ({steps.length} steps)
      </button>
      {open && (
        <div className="trace-steps">
          {steps.map((s, i) => (
            <span key={i} className={badgeClass(s.model)}>
              {s.step}{s.model ? ` · ${s.model}` : ''}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [company, setCompany] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleResearch() {
    if (!company.trim() || loading) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const r = await fetch('https://dispatch-backend-vwgu.onrender.com/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: company.trim() }),
      })
      if (!r.ok) {
        const err = await r.json()
        throw new Error(err.detail || 'Research failed')
      }
      const data = await r.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1 className="header-title">Dispatch</h1>
        <p className="header-subtitle">AI-powered company research</p>
      </header>

      <div className="search-bar">
        <input
          className="search-input"
          type="text"
          placeholder="Enter a company name…"
          value={company}
          onChange={e => setCompany(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleResearch()}
          disabled={loading}
        />
        <button
          className="search-btn"
          onClick={handleResearch}
          disabled={loading || !company.trim()}
        >
          Research →
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="dots">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
          <p className="loading-text">Researching {company.trim()}…</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          <h2 className="result-company">{result.company}</h2>
          <div className="report">
            <ReactMarkdown>{result.report}</ReactMarkdown>
          </div>
          {result.trace?.length > 0 && <Trace steps={result.trace} />}
        </div>
      )}
    </div>
  )
}
