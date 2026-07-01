# Acceptance Checklist

Use this checklist before pushing the project to GitHub or showing it in an interview.

## Local Services

- [ ] Backend starts on `http://127.0.0.1:8000`
- [ ] Frontend starts on `http://127.0.0.1:5173`
- [ ] `GET /health` returns `{"status":"ok"}`
- [ ] `GET /api/system/capabilities` returns runtime metadata
- [ ] Provider diagnostics can run from the frontend system capability panel

## Frontend Workflow

- [ ] Demo mode can create and load a stable sample report
- [ ] Workflow mode can run a new LangGraph task
- [ ] Report tab shows summary, Markdown report, and quality review
- [ ] Trace tab shows workflow nodes and durations
- [ ] Tool calls tab shows tool name, status, input, output, and duration
- [ ] Failed tool calls are visually distinct
- [ ] Fallback banner appears when a provider fails
- [ ] Provider diagnostics shows market data and LLM provider status, latency, and error details

## Task History

- [ ] Recent tasks appear in the left history panel
- [ ] Clicking a historical task restores report, trace, tools, and review
- [ ] Symbol filter works
- [ ] Run mode filter works
- [ ] Status filter works
- [ ] Refresh button reloads history
- [ ] History cards show run mode, quality score, fallback status, market provider, and LLM provider

## Backend API

- [ ] `POST /api/analysis-tasks`
- [ ] `POST /api/analysis-tasks/workflow`
- [ ] `POST /api/system/provider-diagnostics`
- [ ] `GET /api/analysis-tasks`
- [ ] `GET /api/analysis-tasks/{task_id}`
- [ ] `GET /api/analysis-tasks/{task_id}/steps`
- [ ] `GET /api/analysis-tasks/{task_id}/tool-calls`
- [ ] `GET /api/analysis-tasks/{task_id}/report`

## Verification Commands

```bash
python -m compileall backend\app
cd frontend
npm run build
```

## GitHub Hygiene

- [ ] `backend/marketmind.db` is not committed
- [ ] `backend/server.log` and `backend/server.err.log` are not committed
- [ ] `frontend/node_modules` is not committed
- [ ] `frontend/dist` is not committed
- [ ] Real `.env` files are not committed
- [ ] `.env.example` files are committed

## Demo Script

1. Open the frontend.
2. Point out the system capability panel.
3. Run provider diagnostics and explain real/mock provider observability.
4. Run workflow mode for `AAPL`.
5. Open the trace tab and explain each Agent node.
6. Open tool calls and explain provider/tool observability.
7. Open the report tab and explain quality review.
8. Use history filters to reload a previous workflow task.
