from datetime import datetime, timezone

DEMO_TASK_ID = "demo-aapl-6mo"
DEMO_CREATED_AT = datetime(2026, 6, 29, 12, 0, tzinfo=timezone.utc)

DEMO_MARKDOWN = """# AAPL 近 6 个月投研简报

## 核心观点

基于历史行情和公开信息，AAPL 当前呈现“中性偏积极”的趋势特征。大型科技股质量、生态黏性和服务收入仍是支撑因素，但估值敏感性、产品周期预期和 AI 功能落地节奏是主要风险。

## 行情走势

近 6 个月样例数据呈现温和上行，同时在财报窗口和科技板块情绪变化时出现阶段性波动。近期走势只能作为历史背景，不应被理解为确定性预测。

## 技术指标快照

- 均线趋势：价格接近中期均线区间
- 近 6 个月收益：样例数据中为正
- 波动水平：相对大型科技股处于中等水平

## 新闻与事件

近期公开讨论集中在设备需求、AI 功能发布、服务业务增长和监管压力等主题。这些事件即使不改变基本面，也可能影响短期市场情绪。

## 基准回测

第一阶段采用“买入并持有”作为基准回测，因为它透明、易验证，适合演示工作流。后续阶段可扩展均线交叉等策略。

## 主要风险

- 市场对 AI 功能的预期较高
- 硬件换机周期存在不确定性
- 监管与平台费用压力
- 大型科技股估值倍数变化带来的敏感性

## 免责声明

本报告仅用于投研工作流演示，基于历史数据和公开信息生成，不构成任何投资建议。
"""

DEMO_TASK = {
    "id": DEMO_TASK_ID,
    "symbol": "AAPL",
    "market": "US",
    "question": "分析 AAPL 最近 6 个月走势，并总结未来一个月的主要风险。",
    "time_range": "6mo",
    "status": "SUCCESS",
    "created_at": DEMO_CREATED_AT,
    "updated_at": DEMO_CREATED_AT,
    "error_message": None,
}

DEMO_STEPS = [
    {
        "id": "step-1",
        "task_id": DEMO_TASK_ID,
        "node_name": "TaskParser",
        "title": "解析研究任务",
        "status": "SUCCESS",
        "input_summary": "用户提交 AAPL、美股市场、6 个月周期和风险分析问题。",
        "output_summary": "解析得到 symbol=AAPL、market=US、time_range=6mo、intent=trend_and_risk_analysis。",
        "duration_ms": 186,
        "error_message": None,
    },
    {
        "id": "step-2",
        "task_id": DEMO_TASK_ID,
        "node_name": "DataPlanner",
        "title": "规划数据需求",
        "status": "SUCCESS",
        "input_summary": "已解析出趋势分析和风险分析意图。",
        "output_summary": "需要行情数据、基础指标、新闻事件和买入持有基准回测。",
        "duration_ms": 322,
        "error_message": None,
    },
    {
        "id": "step-3",
        "task_id": DEMO_TASK_ID,
        "node_name": "MarketDataFetcher",
        "title": "获取行情数据",
        "status": "SUCCESS",
        "input_summary": "AAPL 近 6 个月日线 OHLCV。",
        "output_summary": "加载样例行情序列，并完成日期覆盖范围校验。",
        "duration_ms": 913,
        "error_message": None,
    },
    {
        "id": "step-4",
        "task_id": DEMO_TASK_ID,
        "node_name": "IndicatorCalculator",
        "title": "计算技术指标",
        "status": "SUCCESS",
        "input_summary": "已校验的历史价格序列。",
        "output_summary": "计算均线、近 6 个月收益和波动率摘要。",
        "duration_ms": 247,
        "error_message": None,
    },
    {
        "id": "step-5",
        "task_id": DEMO_TASK_ID,
        "node_name": "NewsResearcher",
        "title": "整理公开事件",
        "status": "SUCCESS",
        "input_summary": "AAPL 风险导向研究请求。",
        "output_summary": "整理产品周期、AI 功能发布、服务业务和监管主题。",
        "duration_ms": 1210,
        "error_message": None,
    },
    {
        "id": "step-6",
        "task_id": DEMO_TASK_ID,
        "node_name": "BacktestRunner",
        "title": "运行基准回测",
        "status": "SUCCESS",
        "input_summary": "AAPL 近 6 个月历史价格。",
        "output_summary": "计算所选区间内买入并持有的基准收益。",
        "duration_ms": 201,
        "error_message": None,
    },
    {
        "id": "step-7",
        "task_id": DEMO_TASK_ID,
        "node_name": "ReportWriter",
        "title": "生成投研报告",
        "status": "SUCCESS",
        "input_summary": "指标、事件和回测摘要。",
        "output_summary": "生成中等详细度的结构化投研简报。",
        "duration_ms": 1568,
        "error_message": None,
    },
    {
        "id": "step-8",
        "task_id": DEMO_TASK_ID,
        "node_name": "ReportReviewer",
        "title": "审核报告质量",
        "status": "SUCCESS",
        "input_summary": "已生成的报告 JSON 和 Markdown。",
        "output_summary": "检查必需章节、免责声明和缺少依据的预测性表述。",
        "duration_ms": 433,
        "error_message": None,
    },
]

DEMO_TOOL_CALLS = [
    {
        "id": "tool-1",
        "task_id": DEMO_TASK_ID,
        "step_id": "step-3",
        "tool_name": "MarketDataProvider.get_daily_prices",
        "status": "SUCCESS",
        "input_summary": "symbol=AAPL, market=US, range=6mo",
        "output_summary": "从样例数据中加载 126 条日线数据。",
        "duration_ms": 870,
        "error_message": None,
    },
    {
        "id": "tool-2",
        "task_id": DEMO_TASK_ID,
        "step_id": "step-4",
        "tool_name": "IndicatorTool.calculate_basic_snapshot",
        "status": "SUCCESS",
        "input_summary": "OHLCV 日线数据。",
        "output_summary": "生成 MA、收益率和波动率摘要。",
        "duration_ms": 219,
        "error_message": None,
    },
    {
        "id": "tool-3",
        "task_id": DEMO_TASK_ID,
        "step_id": "step-6",
        "tool_name": "BacktestTool.buy_and_hold",
        "status": "SUCCESS",
        "input_summary": "区间起止复权收盘价。",
        "output_summary": "完成基准收益计算。",
        "duration_ms": 166,
        "error_message": None,
    },
]

DEMO_REPORT = {
    "id": "report-demo-aapl-6mo",
    "task_id": DEMO_TASK_ID,
    "title": "AAPL 近 6 个月投研简报",
    "summary": "趋势中性偏积极，但仍需关注产品周期、AI 落地、监管压力和估值敏感性。",
    "stance": "neutral",
    "confidence": 0.72,
    "sections": [
        {
            "title": "行情走势",
            "body": "近 6 个月样例区间呈现温和上行，并在财报和科技板块情绪变化时出现波动。",
        },
        {
            "title": "技术指标快照",
            "body": "样例指标集包含均线位置、区间收益和已实现波动率。",
        },
        {
            "title": "新闻与事件",
            "body": "公开讨论主要集中在设备需求、AI 功能发布、服务业务增长和监管压力。",
        },
        {
            "title": "基准回测",
            "body": "第一阶段采用买入并持有作为基准策略，因为它透明且易于验证。",
        },
        {
            "title": "主要风险",
            "body": "主要风险包括估值敏感性、产品周期预期、监管压力和 AI 执行不确定性。",
        },
    ],
    "sources": [
        {
            "title": "Alpha Vantage API 文档",
            "url": "https://www.alphavantage.co/documentation/",
            "type": "data_source_reference",
        },
        {
            "title": "本地样例数据",
            "url": "local://demo/aapl-6mo",
            "type": "demo_data",
        },
    ],
    "disclaimer": "本报告仅用于投研工作流演示，不构成任何投资建议。",
    "markdown": DEMO_MARKDOWN,
    "created_at": DEMO_CREATED_AT,
}
