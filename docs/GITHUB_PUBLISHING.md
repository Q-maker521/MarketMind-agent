# GitHub Publishing Notes

## Repository Name

Recommended:

```text
marketmind-agent
```

## Short Description

```text
AI investment research Agent workflow with LangGraph, FastAPI, React, tool-call tracing, provider fallback, and report quality guardrails.
```

## Topics

```text
ai-agent
langgraph
fastapi
react
tool-calling
rag-ready
agent-workflow
llmops
investment-research
portfolio-project
```

## Suggested GitHub About Text

MarketMind Agent is a portfolio project demonstrating production-style AI Agent engineering: workflow orchestration, tool calling, provider abstraction, graceful fallback, persisted execution traces, quality guardrails, and a React-based inspection UI.

## First Push

Create an empty GitHub repository first, then run:

```bash
git remote add origin https://github.com/<your-name>/marketmind-agent.git
git push -u origin main
```

## Before Pushing

Run:

```bash
git status --short --ignored
```

Expected ignored local files may include:

```text
backend/marketmind.db
backend/server.log
backend/server.err.log
frontend/node_modules/
frontend/dist/
frontend/server.log
frontend/server.err.log
```

Do not commit real `.env` files or API keys.

## Resume Project Name

```text
MarketMind Agent - AI 投研工作流 Agent
```

## Resume One-Liner

基于 FastAPI、LangGraph 和 React 构建 AI 投研工作流 Agent，实现任务解析、工具调用、Provider 抽象、失败降级、链路可视化、报告质量检查与历史任务审计。
