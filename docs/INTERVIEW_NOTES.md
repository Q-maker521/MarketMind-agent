# Interview Notes

## One-Line Project Pitch

MarketMind Agent is an AI investment research workflow system that demonstrates production-style Agent engineering: workflow orchestration, tool calling, provider abstraction, fallback handling, persistence, trace visualization, and report quality review.

## Problem

Many Agent demos only show a single generated answer. This project focuses on the engineering lifecycle behind an Agent:

- how the task is parsed
- how data requirements are planned
- how tools are called
- how intermediate artifacts are persisted
- how failures are observed and recovered
- how final output is reviewed
- how users can inspect historical runs

## Architecture

```text
React frontend
  -> FastAPI API
  -> LangGraph workflow
  -> local tools and provider abstractions
  -> SQLite persistence
  -> report and quality review
```

## Agent Workflow

The workflow contains 8 nodes:

1. `TaskParser`
2. `DataPlanner`
3. `MarketDataFetcher`
4. `IndicatorCalculator`
5. `NewsResearcher`
6. `BacktestRunner`
7. `ReportWriter`
8. `ReportReviewer`

Each node writes a step record. Tool calls are stored separately with status, input summary, output summary, duration, and error message.

## Engineering Highlights

### Provider Abstraction

Market data and LLM calls are hidden behind provider interfaces.

This makes it possible to:

- run a stable public demo with mock providers
- enable real providers through environment variables
- avoid hard-coding vendor-specific logic into workflow nodes
- test fallback behavior deterministically

### Graceful Degradation

When a provider fails, the workflow:

1. records a failed tool call
2. stores the error message
3. falls back to a mock provider
4. continues the workflow
5. exposes fallback status in the frontend

This is closer to production than simply throwing an exception or hiding the failure.

### Guardrails

`ReportReviewer` performs deterministic checks:

- required sections
- disclaimer
- unsupported prediction language
- tool evidence
- source traceability

The frontend shows the quality score and each check result.

### Persistence And Auditability

SQLite stores:

- tasks
- workflow steps
- tool calls
- reports
- quality score
- audit metadata

Task history supports filtering by symbol, run mode, and status.

## Why The Project Uses Mock Defaults

The public demo should be stable and free to run. Mock defaults avoid:

- API key collection
- provider rate limits
- unstable third-party data
- unpredictable LLM output
- demo cost

Real providers are still supported through configuration.

## Resume Bullet Ideas

- Built a FastAPI + LangGraph AI research Agent with explicit workflow nodes, persisted tool calls, and frontend trace visualization.
- Designed provider abstractions for market data and OpenAI-compatible LLM calls with fallback handling and runtime capability reporting.
- Implemented deterministic report quality guardrails and surfaced structured review results in the UI.
- Added SQLite-backed task history with filtering, audit metadata, provider tracking, and quality scores.

## Follow-Up Improvements

- Verify Alpha Vantage with a real API key
- Verify an OpenAI-compatible LLM endpoint
- Add shareable task detail URLs
- Add deployment notes for a public website
- Add PostgreSQL migration path
- Add async execution with Redis/RQ
