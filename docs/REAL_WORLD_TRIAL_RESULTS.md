# Real-World Trial Results

Date: 2026-07-06

Public URL:

```text
http://8.139.5.187:8080/
```

## Runtime Capability

Online runtime check:

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

Provider diagnostics:

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

## Trial Runs

### Trial 1

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

Tool calls:

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

Report summary:

```text
AAPL was nearly flat over the 1-month window, with meaningful drawdown during the period and a later stabilization above key moving averages. The report described mixed momentum, with AI and services growth as support factors and device demand plus regulatory pressure as risks.
```

### Trial 2

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

Tool calls:

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

Report summary:

```text
AAPL gained about 20.6% over the 3-month window. The report described a constructive technical setup, supported by device demand, AI features, and services growth, while still noting regulatory pressure.
```

### Trial 3

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

Tool calls:

```text
TwelveDataMarketDataProvider.get_daily_prices -> SUCCESS
IndicatorTool.calculate_basic_indicators -> SUCCESS
BacktestTool.run_buy_and_hold_backtest -> SUCCESS
OpenAICompatibleLLMProvider.generate_report_commentary -> SUCCESS
ReportQualityReviewer.evaluate_report_quality -> SUCCESS
```

Report summary:

```text
AAPL gained about 13.53% over the 6-month window and remained above the 20-day and 60-day moving averages. The report described positive momentum supported by AI feature releases and services growth, with regulatory pressure as a risk factor.
```

## What This Proves

These runs verify that the online deployment can:

- accept public workflow requests,
- fetch real historical market data through the provider abstraction,
- calculate indicators and backtest metrics,
- call a real OpenAI-compatible LLM endpoint,
- persist task, step, tool-call, and report artifacts,
- run deterministic report quality checks,
- expose execution evidence through the API and frontend.

This is not a claim of stock prediction accuracy. The validated value is reproducible, inspectable, production-style Agent workflow execution.

## Interview Talking Point

```text
I validated MarketMind Agent in a real online environment. The deployed workflow used Twelve Data for real market data and an OpenAI-compatible Qwen model for report generation. Each run persisted the task, workflow steps, provider tool calls, generated report, and deterministic quality review. I also tested provider fallback behavior earlier, so the system can remain usable even when an external dependency fails.
```

