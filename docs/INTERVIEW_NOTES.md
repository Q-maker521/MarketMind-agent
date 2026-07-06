# 面试讲解稿

## 一句话项目介绍

MarketMind Agent 是一个 AI 投研工作流系统，用于展示生产化 Agent 工程能力：工作流编排、工具调用、Provider 抽象、失败降级、持久化、链路可视化和报告质量评审。

## 项目要解决的问题

很多 Agent Demo 只展示“生成了一个答案”。这个项目更关注 Agent 背后的工程生命周期：

- 任务如何被解析
- 数据需求如何被规划
- 工具如何被调用
- 中间产物如何被持久化
- 失败如何被观测和恢复
- 最终输出如何被评审
- 用户如何检查历史运行记录

## 架构

```text
React frontend
  -> FastAPI API
  -> LangGraph workflow
  -> local tools and provider abstractions
  -> SQLite persistence
  -> report and quality review
```

中文解释：

```text
React 前端
  -> FastAPI 接口层
  -> LangGraph 工作流
  -> 本地工具与 provider 抽象
  -> SQLite 持久化
  -> 报告生成与质量评审
```

## Agent 工作流

工作流包含 8 个节点：

1. `TaskParser`
2. `DataPlanner`
3. `MarketDataFetcher`
4. `IndicatorCalculator`
5. `NewsResearcher`
6. `BacktestRunner`
7. `ReportWriter`
8. `ReportReviewer`

每个节点都会写入一条 step 记录。工具调用会单独保存，包括状态、输入摘要、输出摘要、耗时和错误信息。

## 工程亮点

### Provider 抽象

行情数据和 LLM 调用都隐藏在 provider 接口之后。

这样做可以：

- 使用 mock provider 运行稳定的公开演示
- 通过环境变量启用真实 provider
- 避免把供应商相关逻辑硬编码到工作流节点里
- 确定性地测试 fallback 行为

### 优雅降级

当 provider 失败时，工作流会：

1. 记录失败的工具调用
2. 保存错误信息
3. 回退到 mock provider
4. 继续执行工作流
5. 在前端展示 fallback 状态

这比直接抛异常或隐藏失败更接近生产项目的处理方式。

### 质量护栏

`ReportReviewer` 会做确定性的检查：

- 必要章节是否完整
- 是否包含免责声明
- 是否出现不合理的预测或收益保证语言
- 是否有工具证据
- 是否具备来源可追溯性

前端会展示质量分和每一项检查结果。

### 持久化与可审计性

SQLite 保存：

- 任务
- 工作流步骤
- 工具调用
- 报告
- 质量分
- 审计元数据

任务历史支持按股票代码、运行模式和状态筛选。

## 为什么默认使用 Mock

公开演示应该稳定、低成本、可重复。默认使用 Mock 可以避免：

- 收集 API Key
- provider 限流
- 第三方数据不稳定
- LLM 输出不可控
- 演示成本

真实 provider 仍然可以通过配置启用。

## 简历描述备选

- 构建 FastAPI + LangGraph AI 投研 Agent，实现显式工作流节点、工具调用持久化和前端链路可视化。
- 设计行情数据和 OpenAI-compatible LLM 的 provider 抽象，支持 fallback、运行时能力报告和线上诊断。
- 实现确定性的报告质量护栏，并在 UI 中展示结构化评审结果。
- 基于 SQLite 实现任务历史、筛选、审计元数据、provider 跟踪和质量分记录。

## 面试中可以主动展开的问题

- 为什么先做顺序工作流，而不是一开始做复杂多 Agent？
- LangGraph 在项目中负责什么？状态如何在节点之间传递？
- Tool Calling 的输入输出如何记录，如何用于排查问题？
- provider 抽象解决了哪些工程问题？
- fallback 如何证明系统在外部依赖失败时仍可用？
- 报告质量评审为什么用确定性规则，而不是完全交给 LLM？
- 如果要接入 RAG 或多 Agent，现有架构如何演进？

## 后续改进

- 使用真实 Alpha Vantage API Key 验证备用行情 provider
- 增加更多 OpenAI-compatible LLM 的兼容性验证
- 增加可分享的任务详情 URL
- 补充更完整的公开网站部署说明
- 增加 PostgreSQL 迁移路径
- 使用 Redis/RQ 或其他队列实现异步执行
