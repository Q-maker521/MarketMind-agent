from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELED"]
StepStatus = Literal["WAITING", "RUNNING", "SUCCESS", "FAILED", "SKIPPED"]


class AnalysisTaskCreate(BaseModel):
    symbol: str = Field(default="AAPL", min_length=1, max_length=16)
    market: str = Field(default="US", min_length=1, max_length=16)
    question: str = Field(default="Analyze AAPL over the last 6 months.", min_length=1)
    time_range: str = Field(default="6mo", min_length=1, max_length=16)


class AnalysisTaskResponse(BaseModel):
    id: str
    symbol: str
    market: str
    question: str
    time_range: str
    run_mode: str = "demo"
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None


class AnalysisTaskSummaryResponse(AnalysisTaskResponse):
    quality_score: float | None = None
    failed_tool_calls: int = 0
    has_fallback: bool = False
    market_data_provider: str | None = None
    llm_provider: str | None = None


class WorkflowStepResponse(BaseModel):
    id: str
    task_id: str
    node_name: str
    title: str
    status: StepStatus
    input_summary: str
    output_summary: str
    duration_ms: int
    error_message: str | None = None


class ToolCallResponse(BaseModel):
    id: str
    task_id: str
    step_id: str
    tool_name: str
    status: StepStatus
    input_summary: str
    output_summary: str
    duration_ms: int
    error_message: str | None = None


class ReportSection(BaseModel):
    title: str
    body: str


class ResearchReportResponse(BaseModel):
    id: str
    task_id: str
    title: str
    summary: str
    stance: Literal["bullish", "neutral", "bearish"]
    confidence: float = Field(ge=0, le=1)
    sections: list[ReportSection]
    sources: list[dict[str, Any]]
    disclaimer: str
    markdown: str
    quality_score: float | None = None
    review_passed: bool | None = None
    review_summary: str | None = None
    review_checks: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class SystemCapabilitiesResponse(BaseModel):
    app_env: str
    workflow_engine: str
    persistence: str
    configured_market_data_provider: str
    effective_market_data_provider: str
    alpha_vantage_configured: bool
    uses_mock_market_data: bool
    external_market_data_ready: bool
    configured_llm_provider: str
    effective_llm_provider: str
    llm_model: str | None
    llm_api_key_configured: bool
    uses_mock_llm: bool
    external_llm_ready: bool
    supported_markets: list[str]
    supported_time_ranges: list[str]
    notes: list[str]
