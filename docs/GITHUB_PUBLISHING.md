# GitHub 发布说明

## 仓库名称

推荐：

```text
marketmind-agent
```

## 简短描述

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

## GitHub About 推荐文案

MarketMind Agent 是一个 AI Agent 工程作品集项目，用于展示生产化 Agent 落地能力：工作流编排、工具调用、Provider 抽象、失败降级、执行链路持久化、质量护栏，以及基于 React 的可视化检查界面。

## 首次推送

先在 GitHub 创建一个空仓库，然后执行：

```bash
git remote add origin https://github.com/<your-name>/marketmind-agent.git
git push -u origin main
```

## 推送前检查

执行：

```bash
git status --short --ignored
```

预期被忽略的本地文件可能包括：

```text
backend/marketmind.db
backend/server.log
backend/server.err.log
frontend/node_modules/
frontend/dist/
frontend/server.log
frontend/server.err.log
```

不要提交真实 `.env` 文件或 API Key。

## 简历项目名称

```text
MarketMind Agent - AI 投研工作流 Agent
```

## 简历一句话

基于 FastAPI、LangGraph 和 React 构建 AI 投研工作流 Agent，实现任务解析、工具调用、Provider 抽象、失败降级、链路可视化、报告质量检查与历史任务审计。
