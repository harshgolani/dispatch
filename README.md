# Dispatch

AI agent for company research. Type a company name, get a structured brief powered by live web search and Claude.

**Live:** https://dispatch-agent.netlify.app
**Backend:** https://github.com/harshgolani/dispatch/tree/main/backend

---

## What it does

1. You type a company name
2. The agent runs three targeted web searches via Tavily — overview, recent news, engineering culture
3. Claude Haiku classifies each result for relevance. If irrelevant, retries with a broader query.
4. Claude Sonnet synthesizes all results into a structured markdown report
5. The execution trace shows every step — which model ran what and why

Output format:
- **What They Do** — products, positioning, business model
- **Recent News** — latest developments, funding, launches
- **Engineering & Culture** — stack, hiring, Glassdoor signals
- **Why It's Interesting** — for job seekers and investors

---

## Architecture

Browser → Netlify (React) → Render (FastAPI) → Agent Pipeline

The agent pipeline runs three steps:
1. Tavily searches the web (3 targeted queries)
2. Claude Haiku classifies each result for relevance
3. Claude Sonnet synthesizes all results into a structured report

---

## The routing decision

Every search result is classified by Haiku before reaching Sonnet. Classification is a binary yes/no question — cheap, fast, and Haiku handles it correctly. Sonnet runs exactly once for the final synthesis. This reduces token cost by ~60% compared to routing everything through Sonnet.

Simple tasks → Haiku. Complex reasoning → Sonnet. This is how production AI systems manage inference cost.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite |
| Backend | FastAPI + Python |
| Web retrieval | Tavily |
| Classification | Claude Haiku |
| Synthesis | Claude Sonnet |
| Frontend hosting | Netlify |
| Backend hosting | Render |

---

## Run locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY and TAVILY_API_KEY to .env
uvicorn main:app --reload
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

Update `API` constant in `src/App.jsx` to switch between local and production backend.

---

## API

**POST /research**

Request:
```json
{"company": "Anthropic"}
```

Response:
```json
{
  "company": "Anthropic",
  "report": "## What They Do\n...",
  "trace": [
    {"step": "search_overview", "model": "tavily", "query": "..."},
    {"step": "classify_overview", "model": "haiku"},
    {"step": "classify_overview_result", "verdict": "relevant"},
    ...
    {"step": "synthesize", "model": "sonnet"}
  ]
}
```

---

## Security

- CORS restricted to Netlify frontend URL
- Rate limiting: 10 research requests/hour per IP via slowapi
- 100 character input limit on company name
- API keys stored as environment variables, never in code

---

## Known limitations

- **No streaming** — report appears all at once after 5-8 seconds. Streaming is a Phase 2 improvement.
- **Session-only results** — lost on page refresh. No database required for current use case.
- **Single retry on irrelevant results** — production version would use multiple query reformulation strategies.
- **Render free tier spin-down** — first request after inactivity takes 30-60 seconds to wake the server.
