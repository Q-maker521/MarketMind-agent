from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    AnalysisTaskCreate,
    AnalysisTaskResponse,
    AnalysisTaskSummaryResponse,
    ProviderDiagnosticsRequest,
    ProviderDiagnosticsResponse,
    ResearchReportResponse,
    SystemCapabilitiesResponse,
    ToolCallResponse,
    WorkflowStepResponse,
)
from app.core.config import settings
from app.services.demo_service import demo_service
from app.services.demo_artifacts import seed_demo_task_id
from app.services.provider_diagnostics import run_provider_diagnostics

router = APIRouter()


@router.get("/system/capabilities", response_model=SystemCapabilitiesResponse)
def get_system_capabilities() -> SystemCapabilitiesResponse:
    configured_provider = settings.market_data_provider.lower()
    alpha_vantage_configured = bool(settings.alpha_vantage_api_key)
    external_market_data_ready = configured_provider == "twelve_data" or (
        configured_provider == "alpha_vantage" and alpha_vantage_configured
    )
    effective_provider = configured_provider if external_market_data_ready else "mock"
    configured_llm_provider = settings.llm_provider.lower()
    llm_api_key_configured = bool(settings.llm_api_key)
    external_llm_ready = (
        configured_llm_provider == "openai_compatible"
        and bool(settings.llm_api_base_url)
        and llm_api_key_configured
        and bool(settings.llm_model)
    )
    effective_llm_provider = "openai_compatible" if external_llm_ready else "mock"

    notes = [
        "Demo mode uses fixed sample artifacts.",
        "Workflow mode runs LangGraph with persisted steps and tool calls.",
    ]
    if configured_provider == "twelve_data":
        notes.append("Twelve Data is configured as a real market data provider.")
    elif external_market_data_ready:
        notes.append("Alpha Vantage is configured; market-data failures fall back to mock OHLCV.")
    else:
        notes.append("External market data is not active; mock OHLCV keeps the public demo stable.")
    if external_llm_ready:
        notes.append("OpenAI-compatible LLM is configured; report generation failures fall back to mock templates.")
    else:
        notes.append("External LLM is not active; deterministic mock report writing keeps the demo stable.")

    return SystemCapabilitiesResponse(
        app_env=settings.app_env,
        workflow_engine="LangGraph",
        persistence="SQLite",
        configured_market_data_provider=configured_provider,
        effective_market_data_provider=effective_provider,
        alpha_vantage_configured=alpha_vantage_configured,
        uses_mock_market_data=effective_provider == "mock",
        external_market_data_ready=external_market_data_ready,
        configured_llm_provider=configured_llm_provider,
        effective_llm_provider=effective_llm_provider,
        llm_model=settings.llm_model or None,
        llm_api_key_configured=llm_api_key_configured,
        uses_mock_llm=effective_llm_provider == "mock",
        external_llm_ready=external_llm_ready,
        supported_markets=["US"],
        supported_time_ranges=["1mo", "3mo", "6mo", "1y"],
        notes=notes,
    )


@router.post("/system/provider-diagnostics", response_model=ProviderDiagnosticsResponse)
def create_provider_diagnostics(payload: ProviderDiagnosticsRequest) -> ProviderDiagnosticsResponse:
    return run_provider_diagnostics(payload)


@router.post("/analysis-tasks", response_model=AnalysisTaskResponse)
def create_analysis_task(payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
    return demo_service.create_demo_task(payload)


@router.post("/analysis-tasks/workflow", response_model=AnalysisTaskResponse)
def create_workflow_analysis_task(payload: AnalysisTaskCreate) -> AnalysisTaskResponse:
    return demo_service.create_workflow_task(payload)


@router.get("/analysis-tasks", response_model=list[AnalysisTaskSummaryResponse])
def list_analysis_tasks(
    limit: int = Query(default=20, ge=1, le=100),
    symbol: str | None = Query(default=None, min_length=1, max_length=16),
    status: str | None = Query(default=None),
    run_mode: str | None = Query(default=None),
) -> list[AnalysisTaskSummaryResponse]:
    return demo_service.list_tasks(limit=limit, symbol=symbol, status=status, run_mode=run_mode)


@router.get("/analysis-tasks/demo", response_model=AnalysisTaskResponse)
def get_demo_task() -> AnalysisTaskResponse:
    return demo_service.get_task(seed_demo_task_id())


@router.get("/analysis-tasks/{task_id}", response_model=AnalysisTaskResponse)
def get_analysis_task(task_id: str) -> AnalysisTaskResponse:
    try:
        return demo_service.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis task not found") from exc


@router.get("/analysis-tasks/{task_id}/steps", response_model=list[WorkflowStepResponse])
def get_analysis_steps(task_id: str) -> list[WorkflowStepResponse]:
    _ensure_task(task_id)
    return demo_service.get_steps(task_id)


@router.get("/analysis-tasks/{task_id}/tool-calls", response_model=list[ToolCallResponse])
def get_tool_calls(task_id: str) -> list[ToolCallResponse]:
    _ensure_task(task_id)
    return demo_service.get_tool_calls(task_id)


@router.get("/analysis-tasks/{task_id}/report", response_model=ResearchReportResponse)
def get_report(task_id: str) -> ResearchReportResponse:
    _ensure_task(task_id)
    return demo_service.get_report(task_id)


def _ensure_task(task_id: str) -> None:
    try:
        demo_service.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis task not found") from exc
