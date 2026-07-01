from abc import ABC, abstractmethod

from app.agent.workflow import run_research_workflow
from app.db.repository import AnalysisRepository
from app.models.schemas import AnalysisTaskCreate, AnalysisTaskResponse
from app.services.demo_artifacts import build_demo_artifacts, build_demo_task


class TaskExecutor(ABC):
    @abstractmethod
    def submit(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        """Submit an analysis task and return its initial state."""


class InlineDemoTaskExecutor(TaskExecutor):
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    def submit(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        task = build_demo_task(payload, run_mode="demo")
        steps, tool_calls, report = build_demo_artifacts(task["id"])
        self._repository.save_analysis(task, steps, tool_calls, report)
        return AnalysisTaskResponse(**task)


class InlineTaskExecutor(TaskExecutor):
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    def submit(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        task = build_demo_task(payload, run_mode="workflow")
        workflow_result = run_research_workflow(task)
        steps = workflow_result["steps"]
        tool_calls = _attach_tool_calls_to_steps(workflow_result["tool_calls"], steps)
        report = workflow_result["report"]
        self._repository.save_analysis(task, steps, tool_calls, report)
        return AnalysisTaskResponse(**task)


class RQTaskExecutor(TaskExecutor):
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    def submit(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        raise NotImplementedError("RQ execution is planned for phase 2.")


def _attach_tool_calls_to_steps(tool_calls: list[dict], steps: list[dict]) -> list[dict]:
    node_to_step_id = {step["node_name"]: step["id"] for step in steps}
    tool_to_node = {
        "MarketDataProvider.get_daily_prices": "MarketDataFetcher",
        "MarketDataProvider.get_mock_daily_prices": "MarketDataFetcher",
        "MockMarketDataProvider.get_daily_prices": "MarketDataFetcher",
        "AlphaVantageMarketDataProvider.get_daily_prices": "MarketDataFetcher",
        "IndicatorTool.calculate_basic_snapshot": "IndicatorCalculator",
        "IndicatorTool.calculate_basic_indicators": "IndicatorCalculator",
        "BacktestTool.buy_and_hold": "BacktestRunner",
        "BacktestTool.run_buy_and_hold_backtest": "BacktestRunner",
        "MockLLMProvider.generate_report_commentary": "ReportWriter",
        "OpenAICompatibleLLMProvider.generate_report_commentary": "ReportWriter",
        "ReportQualityReviewer.evaluate_report_quality": "ReportReviewer",
    }

    normalized_calls: list[dict] = []
    for tool_call in tool_calls:
        node_name = tool_to_node.get(tool_call["tool_name"])
        step_id = node_to_step_id.get(node_name, steps[0]["id"] if steps else tool_call["step_id"])
        normalized_calls.append({**tool_call, "step_id": step_id})

    return normalized_calls
