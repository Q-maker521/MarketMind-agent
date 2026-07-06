# 真实环境测试结果

日期：2026-07-06

公开访问地址：

```text
http://8.139.5.187:8080/
```

## 运行时能力

线上运行时检查：

```text
GET /health -> {"status":"ok"}
app_env=production
workflow_engine=LangGraph
persistence=SQLite
effective_market_data_provider=twelve_data
external_market_data_ready=true
uses_mock_market_data=false
effective_llm_provider=openai_compatible
external_llm_ready=true
llm_model=qwen3.7-plus
```

Provider 诊断结果：

```text
Market data:
  provider=TwelveDataMarketDataProvider
  status=success
  source=twelve_data
  symbol=AAPL
  candles=21
  latency_ms=4740

LLM:
  provider=OpenAICompatibleLLMProvider
  status=success
  source=openai_compatible
  model=qwen3.7-plus
  latency_ms=35676
```

## 测试运行记录

### 测试 1

```text
task_id=task-aapl-1mo-003faa68
symbol=AAPL
time_range=1mo
run_mode=workflow
status=SUCCESS
steps_count=8
quality_score=1.0
review_passed=true
stance=neutral
confidence=0.60
```

工具调用：

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

报告摘要：

```text
AAPL 在 1 个月窗口内整体接近持平，期间出现过明显回撤，后续在关键均线之上企稳。报告认为动量偏混合，AI 和服务业务增长构成支撑，设备需求和监管压力是主要风险。
```

### 测试 2

```text
task_id=task-aapl-3mo-a8b24f03
symbol=AAPL
time_range=3mo
run_mode=workflow
status=SUCCESS
steps_count=8
quality_score=1.0
review_passed=true
stance=bullish
confidence=0.85
```

工具调用：

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

报告摘要：

```text
AAPL 在 3 个月窗口内上涨约 20.6%。报告描述了较积极的技术形态，设备需求、AI 功能和服务业务增长构成支撑，同时仍提示监管压力。
```

### 测试 3

```text
task_id=task-aapl-6mo-2cc76b9c
symbol=AAPL
time_range=6mo
run_mode=workflow
status=SUCCESS
steps_count=8
quality_score=1.0
review_passed=true
stance=bullish
confidence=0.75
```

工具调用：

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

报告摘要：

```text
AAPL 在 6 个月窗口内上涨约 13.53%，并保持在 20 日和 60 日均线之上。报告认为 AI 功能发布和服务业务增长支撑了正向动量，同时将监管压力列为风险因素。
```

## 这些结果证明了什么

这些运行记录验证了线上部署可以：

- 接收公开工作流请求
- 通过 provider 抽象获取真实历史行情数据
- 计算指标和回测指标
- 调用真实 OpenAI-compatible LLM endpoint
- 持久化任务、步骤、工具调用和报告产物
- 执行确定性的报告质量检查
- 通过 API 和前端暴露执行证据

这不是对股票预测准确性的声明。已经验证的价值是：可复现、可检查、接近生产形态的 Agent 工作流执行能力。

## 面试讲解点

```text
我在真实线上环境中验证了 MarketMind Agent。部署后的工作流使用 Twelve Data 获取真实行情数据，并使用 OpenAI-compatible 的 Qwen 模型生成报告。每次运行都会持久化任务、工作流步骤、provider 工具调用、生成报告和确定性质量评审。我也在早期测试过 provider fallback 行为，因此外部依赖失败时系统仍可以保持可用。
```
