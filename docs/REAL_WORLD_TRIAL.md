# 真实环境测试计划

线上测试的目标是证明产品价值和工程价值，而不是宣称股票预测准确率。

## 本项目应该证明什么

MarketMind Agent 应该证明它可以：

- 从用户问题到最终报告，跑完完整研究工作流
- 通过 provider 接口采集或生成行情数据
- 计算指标和回测指标
- 生成结构化报告
- 使用确定性护栏评审报告质量
- 持久化每个步骤、工具调用、报告和评审结果
- 让用户检查历史任务并调试工作流

## 推荐测试配置

先使用稳定公开模式：

```text
MARKETMIND_MARKET_DATA_PROVIDER=mock
MARKETMIND_LLM_PROVIDER=mock
```

再运行受控的真实 provider 测试：

```text
MARKETMIND_MARKET_DATA_PROVIDER=twelve_data
MARKETMIND_TWELVE_DATA_API_KEY=demo
MARKETMIND_LLM_PROVIDER=openai_compatible
```

`twelve_data` 适合作为第一次线上测试的数据源，因为它可以通过 public demo key 获取真实历史行情。`alpha_vantage` 可以在后续需要测试个人 API Key 的行情 provider 时使用。

如果 provider 失败，系统价值依然可见：失败的工具调用会被记录，工作流会回退到 fallback。

## 测试用例

至少运行 5 个任务：

| Symbol | Time Range | Question |
| --- | --- | --- |
| AAPL | 6mo | 分析 AAPL 最近 6 个月走势，重点关注趋势、波动和主要风险。 |
| MSFT | 6mo | 分析 MSFT 最近 6 个月走势，并总结技术指标和风险。 |
| NVDA | 3mo | 分析 NVDA 最近 3 个月走势，关注回撤和波动率。 |
| AAPL | 1y | 分析 AAPL 最近 1 年表现，并给出非投资建议式研究摘要。 |
| MSFT | 1mo | 快速分析 MSFT 最近 1 个月走势，验证短周期报告能力。 |

## 需要记录的证据

每次运行记录：

- 公开 URL
- task id
- symbol
- time range
- run mode
- market data provider
- LLM provider
- 是否发生 fallback
- quality score
- failed tool count
- report 截图
- trace 截图
- tool call 截图
- history card 截图
- 切换真实/模拟 provider 配置后的 provider diagnostics 截图

## 成功标准

测试成功需要满足：

- 至少 5 个 workflow 任务成功完成
- 每份报告都能看到 quality score
- 工具调用可见且容易理解
- 历史筛选可以恢复之前的任务
- 系统能力里能看到 provider 状态
- 故意错误配置时能看到 fallback 行为
- 前端没有暴露 API Key
- 修改配置后，provider diagnostics 可以验证行情数据和 LLM 连通性

## 故意失败测试

正常测试成功后，可以故意配置一个错误 provider：

```text
MARKETMIND_MARKET_DATA_PROVIDER=alpha_vantage
MARKETMIND_ALPHA_VANTAGE_API_KEY=bad_key
```

预期结果：

- 工作流仍然完成
- 失败的 provider 调用出现在工具调用列表中
- fallback 提示出现
- 历史任务显示 `has_fallback=true`

然后恢复正确配置。

## 测试记录模板

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

## 如何描述测试价值

推荐说法：

```text
我在真实线上环境中验证了该项目：运行多次研究工作流，检查持久化的工具链路、provider 状态、质量分、fallback 行为和历史任务恢复。
```

避免说法：

```text
这个 Agent 可以准确预测股价。
```

更好的说法：

```text
这个 Agent 的价值在于把数据采集、指标计算、报告生成、质量评审和链路检查变成可复现、可审计的研究工作流。
```
