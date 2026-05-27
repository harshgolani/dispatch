# Design Decisions

## Problem framing — why company research

The demo use case had to meet three criteria: immediately useful to a recruiter opening the app, output quality self-evident (they can judge it without domain knowledge), and technically non-trivial enough to be worth building an agent for.

Company research hits all three. A recruiter types their own company name and immediately sees whether the output is accurate and useful. It requires live web retrieval (Claude's training data is stale), multi-step execution, and synthesis across heterogeneous sources — enough complexity to justify the agentic architecture.

A chatbot wrapper around Claude would not work here. The model doesn't know what happened at a company last week.

## Why an agent instead of a single prompt

A single prompt — "research Anthropic" — would produce hallucinated or stale output. Claude's knowledge cuts off at training time. The agent pattern separates concerns cleanly:

- **Tavily** handles retrieval — it knows how to find and extract current web content
- **Claude Haiku** handles classification — cheap binary decisions
- **Claude Sonnet** handles synthesis — complex reasoning over structured context

Each component does what it's best at. This is the core principle behind production AI systems: don't ask one model to do everything.

## Cost-aware model routing — Haiku for classification, Sonnet for synthesis

The most important architectural decision. Classification is a binary yes/no question: "does this search result contain useful information about this company?" Haiku answers this correctly at roughly 1/20th the cost of Sonnet. There is no reason to spend Sonnet tokens on a task that doesn't require deep reasoning.

Sonnet runs exactly once — for the final synthesis step where it reads all three search results and writes the structured report. This is the step that actually requires intelligence.

Result: ~60% token cost reduction compared to routing everything through Sonnet. In production at scale this compounds significantly.

## Retry logic on irrelevant classification

If Haiku classifies a search result as irrelevant, the agent doesn't fail — it retries with a simpler, broader query. This handles the case where a specific query returns off-topic results (common for smaller or ambiguous company names).

Current implementation: one retry. Production improvement would be: multiple retry strategies with query reformulation, and graceful degradation — if all retries fail, the section is marked "insufficient data found" rather than passing bad context to Sonnet. Passing irrelevant context to Sonnet is worse than passing nothing — it increases hallucination risk.

## Tavily over direct web scraping

Direct scraping requires handling HTML parsing, JavaScript rendering, bot detection, per-site rate limits, and content extraction heuristics. Each website is different. Maintaining scrapers at scale is a full-time job.

Tavily abstracts all of that. It returns clean, extracted text from the top results in one API call. For a system where retrieval quality matters more than retrieval cost, this is the right trade-off. It also keeps the codebase focused on the agent logic rather than infrastructure.

## Three targeted searches instead of one broad search

Running one search — "Anthropic" — returns homepage content, Wikipedia, and whatever Google decides is most relevant. It doesn't reliably surface recent news or engineering culture specifics.

Three targeted searches with explicit intent signals (overview, news, engineering) produce higher-quality, more structured context. The classification layer then verifies each one is actually relevant before synthesis. More targeted retrieval = less noise for Sonnet to reason over.

## Execution trace in the response

Every step is logged: which model ran, which query was used, what verdict was reached. This serves two purposes:

1. **Transparency** — the user can see exactly how the report was generated
2. **Debuggability** — when output is wrong, the trace shows where the pipeline broke down

In production AI systems, observability is not optional. You cannot improve what you cannot inspect. The trace is the minimal viable observability layer.

## Rate limiting — 10 research requests/hour per IP

Each research request costs real money: 3 Tavily searches + 3 Haiku classification calls + 1 Sonnet synthesis call. 10 requests/hour gives a recruiter plenty of room to test the product (type 5-6 companies, that's still within limit) while preventing systematic abuse. Using slowapi with in-memory tracking — no Redis required at this scale.

## No streaming

Claude supports streaming token-by-token output. Streaming would improve perceived performance — the user sees text appearing instead of a blank screen for 5-8 seconds.

Decision: skip streaming in Phase 1. Streaming adds frontend complexity (EventSource or streaming fetch, incremental markdown rendering, partial state management) that isn't justified for a portfolio demo where the full report is the deliverable. Phase 2 improvement with a clear implementation path.

## Session-based results, no persistence

Results live in React state. Lost on refresh. No database.

The use case is single-session: type a company, read the report, done. There is no expectation of saving research or returning to previous results. Adding a database for this would be premature — it adds deployment complexity, cost, and a new failure mode without solving a problem the user actually has.

If the product evolved toward "save and compare research across companies over time," persistence would become necessary. That's a different product.
