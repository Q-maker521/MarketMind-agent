from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.data.demo import DEMO_REPORT, DEMO_STEPS, DEMO_TASK, DEMO_TASK_ID, DEMO_TOOL_CALLS
from app.models.schemas import AnalysisTaskCreate


def build_demo_task(payload: AnalysisTaskCreate, task_id: str | None = None, run_mode: str = "demo") -> dict:
    now = datetime.now(timezone.utc)
    task = deepcopy(DEMO_TASK)
    task["id"] = task_id or _build_task_id(payload)
    task["symbol"] = payload.symbol.upper()
    task["market"] = payload.market.upper()
    task["question"] = payload.question
    task["time_range"] = payload.time_range
    task["run_mode"] = run_mode
    task["created_at"] = now
    task["updated_at"] = now
    return task


def build_seed_demo_task() -> dict:
    return deepcopy(DEMO_TASK)


def build_demo_artifacts(task_id: str) -> tuple[list[dict], list[dict], dict]:
    step_id_map: dict[str, str] = {}
    steps: list[dict] = []

    for index, step in enumerate(DEMO_STEPS, start=1):
        new_step = deepcopy(step)
        new_step_id = f"{task_id}-step-{index}"
        step_id_map[step["id"]] = new_step_id
        new_step["id"] = new_step_id
        new_step["task_id"] = task_id
        steps.append(new_step)

    tool_calls: list[dict] = []
    for index, tool_call in enumerate(DEMO_TOOL_CALLS, start=1):
        new_tool_call = deepcopy(tool_call)
        new_tool_call["id"] = f"{task_id}-tool-{index}"
        new_tool_call["task_id"] = task_id
        new_tool_call["step_id"] = step_id_map.get(tool_call["step_id"], tool_call["step_id"])
        tool_calls.append(new_tool_call)

    report = deepcopy(DEMO_REPORT)
    report["id"] = f"{task_id}-report"
    report["task_id"] = task_id

    return steps, tool_calls, report


def seed_demo_task_id() -> str:
    return DEMO_TASK_ID


def _build_task_id(payload: AnalysisTaskCreate) -> str:
    return f"task-{payload.symbol.lower()}-{payload.time_range}-{uuid4().hex[:8]}"
