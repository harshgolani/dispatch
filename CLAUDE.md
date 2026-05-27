# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dispatch is a company research tool. A user submits a company name; the backend runs a multi-step AI agent that searches the web and returns a structured research brief. The frontend is a React/Vite SPA (currently scaffolded); the backend is a Python FastAPI service.

## Repository Layout

```
dispatch/
  backend/   # FastAPI app + AI agent
  frontend/  # React 19 + Vite SPA
```

## Backend

### Setup & Running

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and TAVILY_API_KEY
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Single endpoint: `POST /research` with body `{"company": "<name>"}`. Rate-limited to 10 requests/hour per IP via `slowapi`.

### Agent Architecture (`agent.py`)

The agent uses a two-model cost routing pattern:

1. **Tavily** performs three web searches (overview, news, engineering/culture).
2. **Claude Haiku** (`claude-haiku-4-5`) classifies each search result for relevance — cheap, fast, binary yes/no.
3. If a result is irrelevant, Tavily retries with a broader query.
4. **Claude Sonnet** (`claude-sonnet-4-5`) runs once at the end to synthesize all results into a structured markdown brief.

The response includes a `trace` array logging every step (model used, query, verdict) for debugging.

## Frontend

### Setup & Running

```bash
cd frontend
npm install
npm run dev      # dev server at http://localhost:5173
npm run build    # production build to dist/
npm run lint     # ESLint
npm run preview  # preview production build
```

The frontend (`src/App.jsx`) is currently the default Vite scaffold and has not yet been wired to the backend API.

## Key Environment Variables

| Variable | Where set | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | `backend/.env` | Anthropic API access |
| `TAVILY_API_KEY` | `backend/.env` | Web search via Tavily |
