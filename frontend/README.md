# Dispatch — Frontend

React 19 + Vite frontend for Dispatch.

**Live:** https://dispatch-agent.netlify.app
**Backend:** https://github.com/harshgolani/dispatch/tree/main/backend

## Stack

- React 19
- Vite
- react-markdown (report rendering)
- Pure CSS (no component library)

## Run locally

```bash
npm install
npm run dev
```

Requires backend running at `http://localhost:8000`. Update `API` constant in `src/App.jsx` to switch between local and production backend.

## Structure

src/
├── App.jsx          # Root component — all state, fetch logic, Trace component
├── App.css          # All styles
└── index.css        # Minimal reset only


## Key components

**App** — owns all state (company, loading, result, error), handles POST /research, renders search bar, loading dots, report, and trace

**Trace** — collapsible execution trace showing each agent step as a color-coded badge (blue=Tavily, green=Haiku, rose gold=Sonnet)
