# Real-World Trial Plan

The goal of the online trial is to prove product and engineering value, not to claim stock prediction accuracy.

## What This Project Should Prove

MarketMind Agent should prove that it can:

- run a complete research workflow from question to report
- collect or generate market data through a provider interface
- calculate indicators and backtest metrics
- generate a structured report
- review report quality with deterministic guardrails
- persist every step, tool call, report, and review result
- let users inspect history and debug the workflow

## Recommended Trial Setup

Start with stable public mode:

```text
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_LLM_PROVIDER=mock
```

Then run a controlled real-provider trial:

```text
MARKETMIND_MARKET_DATA_PROVIDER=yahoo_finance
MARKETMIND_LLM_PROVIDER=openai_compatible
```

`yahoo_finance` is useful for the first online trial because it provides real historical market data without requiring a key. `alpha_vantage` can be used later when you want to test a keyed market data provider.

If a provider fails, the value is still visible because the system records the failed tool call and falls back.

## Trial Cases

Run at least 5 tasks:

| Symbol | Time Range | Question |
| --- | --- | --- |
| AAPL | 6mo | 分析 AAPL 最近 6 个月走势，重点关注趋势、波动和主要风险。 |
| MSFT | 6mo | 分析 MSFT 最近 6 个月走势，并总结技术指标和风险。 |
| NVDA | 3mo | 分析 NVDA 最近 3 个月走势，关注回撤和波动率。 |
| AAPL | 1y | 分析 AAPL 最近 1 年表现，并给出非投资建议式研究摘要。 |
| MSFT | 1mo | 快速分析 MSFT 最近 1 个月走势，验证短周期报告能力。 |

## Evidence To Capture

For each run, record:

- public URL
- task id
- symbol
- time range
- run mode
- market data provider
- LLM provider
- whether fallback happened
- quality score
- failed tool count
- report screenshot
- trace screenshot
- tool call screenshot
- history card screenshot
- provider diagnostics screenshot after changing real/mock provider config

## Success Criteria

The trial is successful if:

- at least 5 workflow tasks finish successfully
- quality score is visible for every report
- tool calls are visible and understandable
- history filters can recover previous tasks
- provider status is visible in system capabilities
- fallback behavior is visible when intentionally misconfigured
- no API key is exposed in the frontend
- provider diagnostics can verify market data and LLM connectivity after config changes

## Intentional Failure Test

After successful normal trials, intentionally test a bad provider config:

```text
MARKETMIND_MARKET_DATA_PROVIDER=alpha_vantage
MARKETMIND_ALPHA_VANTAGE_API_KEY=bad_key
```

Expected result:

- workflow still completes
- failed provider call appears in tool calls
- fallback banner appears
- history task shows `has_fallback=true`

Then restore the correct config.

## Trial Notes Template

```text
Date:
Public URL:
Backend capability:
Provider diagnostics:

Task ID:
Symbol:
Time range:
Question:

Market provider:
LLM provider:
Fallback:
Quality score:
Failed tool calls:

Useful output:

Observed issue:

Screenshot files:
```

## How To Talk About Trial Value

Good statement:

```text
I validated the project in an online environment by running multiple research workflows, checking persisted tool traces, provider status, quality scores, fallback behavior, and task history recovery.
```

Avoid:

```text
This Agent predicts stock prices accurately.
```

Better:

```text
This Agent improves the research workflow by making data collection, indicator calculation, report generation, quality review, and trace inspection reproducible and auditable.
```
