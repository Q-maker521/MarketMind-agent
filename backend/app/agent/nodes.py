from datetime import datetime, timezone
from typing import Any

from app.agent.state import ResearchState
from app.tools.backtest import format_backtest_summary, run_buy_and_hold_backtest
from app.tools.indicators import calculate_basic_indicators, format_indicator_summary
from app.tools.llm import LLMProviderError, MockLLMProvider, get_llm_provider
from app.tools.market_data import MarketDataProviderError, MockMarketDataProvider, get_market_data_provider
from app.tools.report_quality import evaluate_report_quality, format_quality_summary


def task_parser(state: ResearchState) -> ResearchState:
    task = state["task"]
    parsed_task = {
        "symbol": task["symbol"],
        "market": task["market"],
        "time_range": task["time_range"],
        "intent": "trend_and_risk_analysis",
        "language": "zh-CN",
    }
    return _append_step(
        state,
        node_name="TaskParser",
        title="解析研究任务",
        input_summary=f"用户提交 {task['symbol']}、{task['market']} 市场、{task['time_range']} 周期。",
        output_summary=f"解析得到 symbol={task['symbol']}、market={task['market']}、intent=trend_and_risk_analysis。",
        duration_ms=180,
        updates={"parsed_task": parsed_task},
    )


def data_planner(state: ResearchState) -> ResearchState:
    parsed_task = state["parsed_task"]
    data_plan = {
        "requires_market_data": True,
        "requires_indicators": True,
        "requires_news": True,
        "requires_backtest": True,
        "indicators": ["MA20", "MA60", "period_return", "volatility", "max_drawdown"],
        "backtest_strategy": "buy_and_hold",
    }
    return _append_step(
        state,
        node_name="DataPlanner",
        title="规划数据需求",
        input_summary=f"研究意图：{parsed_task['intent']}。",
        output_summary="需要行情数据、基础技术指标、公开事件摘要和买入持有基准回测。",
        duration_ms=310,
        updates={"data_plan": data_plan},
    )


def market_data_fetcher(state: ResearchState) -> ResearchState:
    task = state["task"]
    provider = get_market_data_provider()
    provider_name = provider.__class__.__name__
    try:
        market_data = provider.get_daily_prices(task["symbol"], task["time_range"])
    except MarketDataProviderError as error:
        state = _append_tool_call(
            state,
            tool_name=f"{provider_name}.get_daily_prices",
            input_summary=f"symbol={task['symbol']}, market={task['market']}, range={task['time_range']}",
            output_summary="Primary market data provider failed; workflow will route to MarketDataFallback.",
            duration_ms=1200,
            status="FAILED",
            error_message=str(error),
        )
        return _append_step(
            state,
            node_name="MarketDataFetcher",
            title="获取行情数据",
            input_summary=f"{task['symbol']} {task['time_range']} 日线 OHLCV。",
            output_summary=f"{provider_name} 获取行情失败，进入 MarketDataFallback 分支。",
            duration_ms=1210,
            status="FAILED",
            error_message=str(error),
            updates={
                "market_data_error": {
                    "provider": provider_name,
                    "message": str(error),
                }
            },
        )

    candle_count = len(market_data["candles"])
    state = _append_tool_call(
        state,
        tool_name=f"{provider_name}.get_daily_prices",
        input_summary=f"symbol={task['symbol']}, market={task['market']}, range={task['time_range']}",
        output_summary=f"从 {market_data['source']} 加载 {candle_count} 条 OHLCV 日线数据。",
        duration_ms=840,
    )
    return _append_step(
        state,
        node_name="MarketDataFetcher",
        title="获取行情数据",
        input_summary=f"{task['symbol']} {task['time_range']} 日线 OHLCV。",
        output_summary=f"完成 {market_data['source']} 行情数据加载，共 {candle_count} 条。",
        duration_ms=910,
        updates={"market_data": market_data},
    )


def market_data_fallback(state: ResearchState) -> ResearchState:
    task = state["task"]
    market_data_error = state.get("market_data_error", {})
    fallback_provider = MockMarketDataProvider()
    market_data = fallback_provider.get_daily_prices(task["symbol"], task["time_range"])
    market_data = {
        **market_data,
        "coverage": "fallback",
        "fallback_from": market_data_error.get("provider", "unknown"),
        "fallback_reason": market_data_error.get("message", "unknown provider error"),
    }
    candle_count = len(market_data["candles"])
    state = _append_tool_call(
        state,
        tool_name=f"{fallback_provider.__class__.__name__}.get_daily_prices",
        input_summary=f"symbol={task['symbol']}, market={task['market']}, range={task['time_range']}",
        output_summary=f"Primary provider failed; loaded {candle_count} fallback mock OHLCV candles.",
        duration_ms=320,
    )
    return _append_step(
        state,
        node_name="MarketDataFallback",
        title="降级获取行情",
        input_summary=f"原 provider={market_data.get('fallback_from')}，错误={market_data.get('fallback_reason')}",
        output_summary=f"已使用本地 mock OHLCV 生成 {candle_count} 条 fallback 数据。",
        duration_ms=350,
        updates={"market_data": market_data},
    )


def indicator_calculator(state: ResearchState) -> ResearchState:
    market_data = state["market_data"]
    indicator_summary = calculate_basic_indicators(market_data)
    summary_text = format_indicator_summary(indicator_summary)
    data_source_label = _format_market_data_source(market_data)
    state = _append_tool_call(
        state,
        tool_name="IndicatorTool.calculate_basic_indicators",
        input_summary=f"{indicator_summary['candles']} 条 OHLCV 日线数据。",
        output_summary=summary_text,
        duration_ms=230,
    )
    return _append_step(
        state,
        node_name="IndicatorCalculator",
        title="计算技术指标",
        input_summary=f"{data_source_label}。",
        output_summary=summary_text,
        duration_ms=250,
        updates={"indicator_summary": indicator_summary},
    )


def news_researcher(state: ResearchState) -> ResearchState:
    task = state["task"]
    news_summary = {
        "themes": ["设备需求", "AI 功能发布", "服务业务增长", "监管压力"],
        "source": "mock_news_summary",
        "degraded": False,
    }
    return _append_step(
        state,
        node_name="NewsResearcher",
        title="整理公开事件",
        input_summary=f"{task['symbol']} 风险导向研究请求。",
        output_summary="整理设备需求、AI 功能发布、服务业务增长和监管压力四类主题。",
        duration_ms=1120,
        updates={"news_summary": news_summary},
    )


def backtest_runner(state: ResearchState) -> ResearchState:
    market_data = state["market_data"]
    task = state["task"]
    backtest_result = run_buy_and_hold_backtest(market_data)
    summary_text = format_backtest_summary(backtest_result)
    state = _append_tool_call(
        state,
        tool_name="BacktestTool.run_buy_and_hold_backtest",
        input_summary=f"{task['symbol']} 区间复权收盘价序列。",
        output_summary=summary_text,
        duration_ms=170,
    )
    return _append_step(
        state,
        node_name="BacktestRunner",
        title="运行基准回测",
        input_summary=f"{task['symbol']} {task['time_range']} 历史价格。",
        output_summary=summary_text,
        duration_ms=210,
        updates={"backtest_result": backtest_result},
    )


def report_writer(state: ResearchState) -> ResearchState:
    task = state["task"]
    indicators = state["indicator_summary"]
    backtest = state["backtest_result"]
    news_summary = state.get("news_summary", {})
    llm_provider = get_llm_provider()
    llm_provider_name = llm_provider.__class__.__name__
    try:
        llm_commentary = llm_provider.generate_report_commentary(task, indicators, backtest, news_summary)
    except LLMProviderError as error:
        state = _append_tool_call(
            state,
            tool_name=f"{llm_provider_name}.generate_report_commentary",
            input_summary=f"symbol={task['symbol']}, range={task['time_range']}, report_writer",
            output_summary="Primary LLM provider failed; workflow will route to LLMReportFallback.",
            duration_ms=1800,
            status="FAILED",
            error_message=str(error),
        )
        return _append_step(
            state,
            node_name="ReportWriter",
            title="生成投研报告",
            input_summary="指标、回测和事件摘要。",
            output_summary=f"{llm_provider_name} 生成报告失败，进入 LLMReportFallback 分支。",
            duration_ms=1810,
            status="FAILED",
            error_message=str(error),
            updates={
                "llm_error": {
                    "provider": llm_provider_name,
                    "message": str(error),
                }
            },
        )
    state = _append_tool_call(
        state,
        tool_name=f"{llm_provider_name}.generate_report_commentary",
        input_summary=f"symbol={task['symbol']}, range={task['time_range']}, report_writer",
        output_summary=f"Generated report commentary with {llm_commentary['source']}.",
        duration_ms=620,
    )
    report = _build_report(state, llm_commentary)
    return _append_step(
        state,
        node_name="ReportWriter",
        title="生成投研报告",
        input_summary="行情、指标、回测、事件摘要和 LLM commentary。",
        output_summary=f"使用 {llm_commentary['source']} 生成结构化报告。",
        duration_ms=1450,
        updates={"report": report},
    )


def llm_report_fallback(state: ResearchState) -> ResearchState:
    task = state["task"]
    indicators = state["indicator_summary"]
    backtest = state["backtest_result"]
    news_summary = state.get("news_summary", {})
    llm_error = state.get("llm_error", {})
    fallback_llm_provider = MockLLMProvider()
    llm_commentary = fallback_llm_provider.generate_report_commentary(task, indicators, backtest, news_summary)
    llm_commentary = {
        **llm_commentary,
        "source": "mock_llm_fallback",
        "fallback_from": llm_error.get("provider", "unknown"),
        "fallback_reason": llm_error.get("message", "unknown LLM error"),
    }
    state = _append_tool_call(
        state,
        tool_name=f"{fallback_llm_provider.__class__.__name__}.generate_report_commentary",
        input_summary=f"symbol={task['symbol']}, range={task['time_range']}, fallback_report_writer",
        output_summary="Generated deterministic fallback report commentary.",
        duration_ms=280,
    )
    report = _build_report(state, llm_commentary)
    return _append_step(
        state,
        node_name="LLMReportFallback",
        title="降级生成报告",
        input_summary=f"原 provider={llm_commentary.get('fallback_from')}，错误={llm_commentary.get('fallback_reason')}",
        output_summary="已使用确定性 mock LLM 模板生成 fallback 报告。",
        duration_ms=320,
        updates={"report": report},
    )


def report_reviewer(state: ResearchState) -> ResearchState:
    report = state["report"]
    review_result = evaluate_report_quality(report, state.get("tool_calls", []))
    review_summary = format_quality_summary(review_result)
    state = _append_tool_call(
        state,
        tool_name="ReportQualityReviewer.evaluate_report_quality",
        input_summary=f"report_id={report['id']}, checks={len(review_result['checks'])}",
        output_summary=review_summary,
        duration_ms=190,
        status="SUCCESS" if review_result["passed"] else "FAILED",
        error_message=None if review_result["passed"] else review_result["summary"],
    )
    report = {
        **report,
        "quality_score": review_result["quality_score"],
        "review_checks": review_result["checks"],
        "review_summary": review_result["summary"],
        "review_passed": review_result["passed"],
    }
    return _append_step(
        state,
        node_name="ReportReviewer",
        title="审核报告质量",
        input_summary="已生成的报告 JSON 和 Markdown。",
        output_summary="检查必需章节、免责声明和缺少依据的预测性表述。",
        duration_ms=420,
        updates={"review_result": review_result, "report": report},
    )


def _build_markdown_report(
    task: dict[str, Any],
    title: str,
    summary: str,
    indicators: dict[str, Any],
    backtest: dict[str, Any],
    data_source_label: str,
) -> str:
    return f"""# {title}

## 核心观点

{summary} 本报告基于{data_source_label}、指标计算和买入并持有回测生成，用于验证 Agent 工具调用链路。

## 行情走势

数据区间从 {backtest['start_date']} 到 {backtest['end_date']}，收盘价从 {backtest['start_price']} 变化到 {backtest['end_price']}。

## 技术指标快照

- MA20：{indicators['ma20']}
- MA60：{indicators['ma60']}
- 区间收益：{indicators['period_return']:.2%}
- 年化波动率：{indicators['annualized_volatility']:.2%}
- 最大回撤：{indicators['max_drawdown']:.2%}

## 新闻与事件

当前新闻节点仍使用 mock 摘要，覆盖设备需求、AI 功能发布、服务业务增长和监管压力等主题。

## 基准回测

买入并持有收益为 {backtest['total_return']:.2%}，最大回撤为 {backtest['max_drawdown']:.2%}，持有交易日为 {backtest['holding_days']} 天。

## 主要风险

- 市场对 AI 功能的预期较高
- 硬件换机周期存在不确定性
- 监管与平台费用压力
- 大型科技股估值倍数变化带来的敏感性

## 免责声明

本报告仅用于投研工作流演示，基于本地样例数据和公开分析流程生成，不构成任何投资建议。
"""


def _build_report(state: ResearchState, llm_commentary: dict[str, Any]) -> dict[str, Any]:
    task = state["task"]
    indicators = state["indicator_summary"]
    backtest = state["backtest_result"]
    market_data = state["market_data"]
    title = f"{task['symbol']} {task['time_range']} 投研简报"
    summary = llm_commentary["summary"]
    data_source_label = _format_market_data_source(market_data)
    data_source = _build_market_data_source(market_data)
    report = {
        "id": f"{task['id']}-report",
        "task_id": task["id"],
        "title": title,
        "summary": summary,
        "stance": llm_commentary["stance"],
        "confidence": llm_commentary["confidence"],
        "sections": [
            {
                "title": "行情走势",
                "body": f"{data_source_label}区间从 {backtest['start_date']} 到 {backtest['end_date']}，收盘价从 {backtest['start_price']} 变为 {backtest['end_price']}。",
            },
            {
                "title": "技术指标快照",
                "body": format_indicator_summary(indicators),
            },
            {
                "title": "新闻与事件",
                "body": "当前仍使用 mock 新闻摘要，覆盖设备需求、AI 功能发布、服务业务增长和监管压力。",
            },
            {
                "title": "基准回测",
                "body": format_backtest_summary(backtest),
            },
            {
                "title": "主要风险",
                "body": "主要风险包括估值敏感性、产品周期预期、监管压力和 AI 执行不确定性。",
            },
        ],
        "sources": [
            data_source,
            {"title": "本地指标计算工具", "url": "local://tools/indicators", "type": "local_tool"},
            {"title": "本地回测工具", "url": "local://tools/backtest", "type": "local_tool"},
            {
                "title": f"报告生成：{llm_commentary['source']}",
                "url": "local://providers/llm",
                "type": "llm",
            },
        ],
        "disclaimer": "本报告仅用于投研工作流演示，不构成任何投资建议。",
        "markdown": _build_markdown_report(task, title, summary, indicators, backtest, data_source_label),
        "created_at": datetime.now(timezone.utc),
    }
    return report


def _format_market_data_source(market_data: dict[str, Any]) -> str:
    source = market_data.get("source", "unknown")
    coverage = market_data.get("coverage", "unknown")
    if coverage == "fallback":
        fallback_from = market_data.get("fallback_from", "primary provider")
        return f"fallback 本地 mock OHLCV 数据（原 provider：{fallback_from}）"
    if source == "twelve_data":
        return "Twelve Data 真实历史行情数据"
    if source == "alpha_vantage":
        return "Alpha Vantage 真实历史行情数据"
    if source == "mock_ohlcv":
        return "本地 mock OHLCV 数据"
    return f"{source} 行情数据"


def _build_market_data_source(market_data: dict[str, Any]) -> dict[str, str]:
    source = market_data.get("source", "unknown")
    coverage = market_data.get("coverage", "unknown")
    if coverage == "fallback":
        return {
            "title": _format_market_data_source(market_data),
            "url": "local://mock/ohlcv",
            "type": "fallback_data",
        }
    if source == "twelve_data":
        return {
            "title": "Twelve Data 真实历史行情",
            "url": "https://twelvedata.com/",
            "type": "market_data",
        }
    if source == "alpha_vantage":
        return {
            "title": "Alpha Vantage 真实历史行情",
            "url": "https://www.alphavantage.co/",
            "type": "market_data",
        }
    return {
        "title": "本地 mock OHLCV 数据",
        "url": "local://mock/ohlcv",
        "type": "mock_data",
    }


def _append_step(
    state: ResearchState,
    *,
    node_name: str,
    title: str,
    input_summary: str,
    output_summary: str,
    duration_ms: int,
    updates: dict[str, Any],
    status: str = "SUCCESS",
    error_message: str | None = None,
) -> ResearchState:
    task = state["task"]
    steps = [*state.get("steps", [])]
    steps.append(
        {
            "id": f"{task['id']}-step-{len(steps) + 1}",
            "task_id": task["id"],
            "node_name": node_name,
            "title": title,
            "status": status,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_ms": duration_ms,
            "error_message": error_message,
        }
    )
    return {**state, **updates, "steps": steps}


def _append_tool_call(
    state: ResearchState,
    *,
    tool_name: str,
    input_summary: str,
    output_summary: str,
    duration_ms: int,
    status: str = "SUCCESS",
    error_message: str | None = None,
) -> ResearchState:
    task = state["task"]
    tool_calls = [*state.get("tool_calls", [])]
    tool_calls.append(
        {
            "id": f"{task['id']}-tool-{len(tool_calls) + 1}",
            "task_id": task["id"],
            "step_id": f"{task['id']}-pending-step",
            "tool_name": tool_name,
            "status": status,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_ms": duration_ms,
            "error_message": error_message,
        }
    )
    return {**state, "tool_calls": tool_calls}
