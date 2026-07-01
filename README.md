# MarketMind Agent

MarketMind Agent is an AI investment research workflow project built for AI Agent engineering portfolio and interview use. It focuses on production-style Agent workflow implementation rather than stock price prediction.

The project demonstrates how an Agent system can parse a research task, plan required data, call tools, generate a structured report, review output quality, persist execution artifacts, and expose the whole process through a web UI.

## Highlights

- LangGraph-based research workflow with 8 explicit nodes
- FastAPI backend with SQLite persistence
- React + Vite frontend with Chinese workflow UI
- Tool calling trace for market data, indicators, backtesting, report writing, and report review
- Provider abstraction for market data and LLM calls
- Graceful fallback when external market data or LLM providers fail
- Deterministic mock mode for stable public demos
- Report quality guardrails with structured review checks
- Task history with filtering and audit metadata
- Runtime capability panel showing which parts are real, configured, or mocked
- Provider diagnostics for online market data and LLM smoke testing

## Current Status

The MVP core loop is complete.

```text
Task input
  -> LangGraph workflow
  -> Tool calls
  -> SQLite persistence
  -> Report generation
  -> Quality review
  -> Frontend trace and task history
```

The public demo defaults to mock market data and mock LLM report writing so it can run reliably without paid APIs or user-provided keys. External providers can be enabled through environment variables.

## Tech Stack

- Backend: FastAPI, Pydantic
- Workflow: LangGraph
- Database: SQLite
- Frontend: React, Vite
- UI icons: lucide-react
- Markdown rendering: marked
- Market data: mock provider by default, Twelve Data demo provider and Alpha Vantage provider prepared
- LLM: mock provider by default, OpenAI-compatible provider prepared

## Workflow Nodes

Workflow mode runs these nodes:

1. `TaskParser`
2. `DataPlanner`
3. `MarketDataFetcher`
4. `IndicatorCalculator`
5. `NewsResearcher`
6. `BacktestRunner`
7. `ReportWriter`
8. `ReportReviewer`

Each run persists:

- task metadata
- workflow steps
- tool calls
- report JSON and Markdown
- quality review result

## Feature Overview

### Run Modes

- Demo mode: stable sample artifacts for public presentation
- Workflow mode: executes the LangGraph workflow and persists a new task

### Local Tools

- `MockMarketDataProvider`: deterministic OHLCV generation
- `IndicatorTool`: MA20, MA60, return, volatility, max drawdown
- `BacktestTool`: buy-and-hold return and drawdown
- `MockLLMProvider`: deterministic report commentary
- `ReportQualityReviewer`: deterministic guardrail checks

### Provider Abstractions

Market data:

- `MockMarketDataProvider`
- `TwelveDataMarketDataProvider`
- `AlphaVantageMarketDataProvider`

LLM:

- `MockLLMProvider`
- `OpenAICompatibleLLMProvider`

If an external provider fails, the workflow records the failed tool call and falls back to the mock provider.

### Provider Diagnostics

The system capability panel includes a provider diagnostics action. It runs a lightweight smoke test against the configured market data provider and LLM provider, then reports:

- provider implementation
- configuration status
- success, failure, or skipped state
- latency
- normalized error message

This helps verify online deployments after changing environment variables, without guessing whether a real API key or model endpoint is working.

### Report Quality Review

`ReportReviewer` checks:

- required section coverage
- disclaimer presence
- unsupported prediction or guaranteed-return language
- successful evidence tool calls
- source traceability

The frontend displays quality score and every check result.

### Task History

The history panel supports:

- symbol filtering
- run mode filtering
- status filtering
- manual refresh
- task detail restore

Task history includes audit metadata:

- `run_mode`
- `quality_score`
- `failed_tool_calls`
- `has_fallback`
- `market_data_provider`
- `llm_provider`

## Project Structure

```text
marketmind-agent/
  backend/
    app/
      agent/       # LangGraph nodes and workflow
      api/         # FastAPI routes
      core/        # settings
      db/          # SQLite connection and repository
      models/      # Pydantic schemas
      services/    # task executors and demo service
      tools/       # providers and local tools
    requirements.txt
    .env.example
  frontend/
    src/
      api/
      App.jsx
      styles.css
    package.json
  docs/
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173/
```

## Environment Variables

Backend variables are documented in `backend/.env.example`.

Frontend variables are documented in `frontend/.env.example`.

Default mode requires no external key.

## API Overview

```text
GET  /health
GET  /api/system/capabilities
POST /api/system/provider-diagnostics
POST /api/analysis-tasks
POST /api/analysis-tasks/workflow
GET  /api/analysis-tasks?limit=20&symbol=AAPL&run_mode=workflow&status=SUCCESS
GET  /api/analysis-tasks/{task_id}
GET  /api/analysis-tasks/{task_id}/steps
GET  /api/analysis-tasks/{task_id}/tool-calls
GET  /api/analysis-tasks/{task_id}/report
```

## Verification

Common checks:

```bash
python -m compileall backend\app
cd frontend
npm run build
```

Manual acceptance checklist:

```text
docs/ACCEPTANCE_CHECKLIST.md
```

Deployment and online trial:

```text
docs/DEPLOYMENT.md
docs/REAL_WORLD_TRIAL.md
```

## Portfolio Talking Points

This project is designed to show:

- Agent workflow orchestration with explicit state transitions
- Tool calling with persisted inputs, outputs, status, and duration
- Provider abstraction for external dependencies
- Graceful degradation and fallback observability
- Guardrail-style report review
- SQLite-backed task history and audit metadata
- Frontend workflow visualization for debugging and demo use

See:

```text
docs/INTERVIEW_NOTES.md
```

## Roadmap

- Real Alpha Vantage key verification
- Real Twelve Data market data trial
- Real OpenAI-compatible LLM verification
- Task detail route and shareable URLs
- Public website deployment
- Optional PostgreSQL migration
- Optional Redis/RQ async executor
