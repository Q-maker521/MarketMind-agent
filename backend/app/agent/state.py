from typing import Any, TypedDict


class ResearchState(TypedDict, total=False):
    task: dict[str, Any]
    parsed_task: dict[str, Any]
    data_plan: dict[str, Any]
    market_data: dict[str, Any]
    market_data_error: dict[str, Any]
    indicator_summary: dict[str, Any]
    news_summary: dict[str, Any]
    backtest_result: dict[str, Any]
    llm_error: dict[str, Any]
    report: dict[str, Any]
    review_result: dict[str, Any]
    steps: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    errors: list[str]
