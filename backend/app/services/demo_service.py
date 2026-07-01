from app.db.repository import AnalysisRepository
from app.models.schemas import (
    AnalysisTaskCreate,
    AnalysisTaskResponse,
    AnalysisTaskSummaryResponse,
    ResearchReportResponse,
    ToolCallResponse,
    WorkflowStepResponse,
)
from app.services.demo_artifacts import build_demo_artifacts, build_seed_demo_task, seed_demo_task_id
from app.services.task_executor import InlineDemoTaskExecutor, InlineTaskExecutor


class DemoService:
    def __init__(self) -> None:
        self._repository = AnalysisRepository()
        self._executor = InlineDemoTaskExecutor(self._repository)
        self._workflow_executor = InlineTaskExecutor(self._repository)
        self._seed_demo_task()

    def create_demo_task(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        return self._executor.submit(payload)

    def create_workflow_task(self, payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
        return self._workflow_executor.submit(payload)

    def list_tasks(
        self,
        *,
        limit: int = 20,
        symbol: str | None = None,
        status: str | None = None,
        run_mode: str | None = None,
    ) -> list[AnalysisTaskSummaryResponse]:
        return [
            AnalysisTaskSummaryResponse(**task)
            for task in self._repository.list_task_summaries(
                limit=limit,
                symbol=symbol,
                status=status,
                run_mode=run_mode,
            )
        ]

    def get_task(self, task_id: str) -> AnalysisTaskResponse:
        task = self._repository.get_task(task_id)
        return AnalysisTaskResponse(**task)

    def get_steps(self, task_id: str) -> list[WorkflowStepResponse]:
        return [WorkflowStepResponse(**step) for step in self._repository.get_steps(task_id)]

    def get_tool_calls(self, task_id: str) -> list[ToolCallResponse]:
        return [ToolCallResponse(**tool_call) for tool_call in self._repository.get_tool_calls(task_id)]

    def get_report(self, task_id: str) -> ResearchReportResponse:
        return ResearchReportResponse(**self._repository.get_report(task_id))

    def _seed_demo_task(self) -> None:
        task_id = seed_demo_task_id()
        try:
            self._repository.get_task(task_id)
        except KeyError:
            task = build_seed_demo_task()
            task.setdefault("run_mode", "demo")
            steps, tool_calls, report = build_demo_artifacts(task_id)
            self._repository.save_analysis(task, steps, tool_calls, report)


demo_service = DemoService()
