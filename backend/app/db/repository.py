import json
from datetime import datetime
from typing import Any

from app.db.database import get_connection, initialize_database


def _serialize_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _task_from_row(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "symbol": row["symbol"],
        "market": row["market"],
        "question": row["question"],
        "time_range": row["time_range"],
        "run_mode": row["run_mode"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "error_message": row["error_message"],
    }


def _step_from_row(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "task_id": row["task_id"],
        "node_name": row["node_name"],
        "title": row["title"],
        "status": row["status"],
        "input_summary": row["input_summary"],
        "output_summary": row["output_summary"],
        "duration_ms": row["duration_ms"],
        "error_message": row["error_message"],
    }


def _tool_call_from_row(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "task_id": row["task_id"],
        "step_id": row["step_id"],
        "tool_name": row["tool_name"],
        "status": row["status"],
        "input_summary": row["input_json"],
        "output_summary": row["output_summary"],
        "duration_ms": row["duration_ms"],
        "error_message": row["error_message"],
    }


def _report_from_row(row: Any) -> dict[str, Any]:
    report_json = json.loads(row["report_json"])
    return {
        "id": row["id"],
        "task_id": row["task_id"],
        "title": row["title"],
        "summary": row["summary"],
        "stance": row["stance"],
        "confidence": row["confidence"],
        "sections": json.loads(row["sections_json"]),
        "sources": json.loads(row["sources_json"]),
        "disclaimer": row["disclaimer"],
        "markdown": row["report_markdown"],
        "quality_score": row["quality_score"],
        "review_passed": report_json.get("review_passed"),
        "review_summary": report_json.get("review_summary"),
        "review_checks": report_json.get("review_checks", []),
        "created_at": row["created_at"],
    }


def _find_provider_name(tool_names: list[str], suffix: str) -> str | None:
    for tool_name in reversed(tool_names):
        if tool_name.endswith(suffix):
            return tool_name.split(".", 1)[0]
    return None


class AnalysisRepository:
    def __init__(self) -> None:
        initialize_database()

    def save_analysis(
        self,
        task: dict[str, Any],
        steps: list[dict[str, Any]],
        tool_calls: list[dict[str, Any]],
        report: dict[str, Any],
    ) -> None:
        normalized_task = {key: _serialize_datetime(value) for key, value in task.items()}
        normalized_report = {key: _serialize_datetime(value) for key, value in report.items()}

        with get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analysis_tasks (
                    id, symbol, market, question, time_range, run_mode, status,
                    created_at, updated_at, started_at, finished_at, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_task["id"],
                    normalized_task["symbol"],
                    normalized_task["market"],
                    normalized_task["question"],
                    normalized_task["time_range"],
                    normalized_task.get("run_mode", "demo"),
                    normalized_task["status"],
                    normalized_task["created_at"],
                    normalized_task["updated_at"],
                    normalized_task.get("started_at"),
                    normalized_task.get("finished_at"),
                    normalized_task.get("error_message"),
                ),
            )

            connection.execute("DELETE FROM tool_calls WHERE task_id = ?", (normalized_task["id"],))
            connection.execute("DELETE FROM agent_steps WHERE task_id = ?", (normalized_task["id"],))
            connection.execute("DELETE FROM research_reports WHERE task_id = ?", (normalized_task["id"],))

            for index, step in enumerate(steps):
                normalized_step = {key: _serialize_datetime(value) for key, value in step.items()}
                connection.execute(
                    """
                    INSERT INTO agent_steps (
                        id, task_id, node_name, title, status, input_summary,
                        output_summary, started_at, finished_at, duration_ms,
                        error_message, sequence_index
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized_step["id"],
                        normalized_step["task_id"],
                        normalized_step["node_name"],
                        normalized_step["title"],
                        normalized_step["status"],
                        normalized_step["input_summary"],
                        normalized_step["output_summary"],
                        normalized_step.get("started_at"),
                        normalized_step.get("finished_at"),
                        normalized_step["duration_ms"],
                        normalized_step.get("error_message"),
                        index,
                    ),
                )

            for index, tool_call in enumerate(tool_calls):
                normalized_call = {key: _serialize_datetime(value) for key, value in tool_call.items()}
                connection.execute(
                    """
                    INSERT INTO tool_calls (
                        id, task_id, step_id, tool_name, status, input_json,
                        output_summary, duration_ms, created_at, error_message,
                        sequence_index
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized_call["id"],
                        normalized_call["task_id"],
                        normalized_call["step_id"],
                        normalized_call["tool_name"],
                        normalized_call["status"],
                        normalized_call["input_summary"],
                        normalized_call["output_summary"],
                        normalized_call["duration_ms"],
                        normalized_call.get("created_at", normalized_task["created_at"]),
                        normalized_call.get("error_message"),
                        index,
                    ),
                )

            report_json = json.dumps(normalized_report, ensure_ascii=False)
            connection.execute(
                """
                INSERT INTO research_reports (
                    id, task_id, title, summary, stance, confidence,
                    sections_json, sources_json, disclaimer, report_markdown,
                    report_json, quality_score, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_report["id"],
                    normalized_report["task_id"],
                    normalized_report["title"],
                    normalized_report["summary"],
                    normalized_report["stance"],
                    normalized_report["confidence"],
                    json.dumps(normalized_report["sections"], ensure_ascii=False),
                    json.dumps(normalized_report["sources"], ensure_ascii=False),
                    normalized_report["disclaimer"],
                    normalized_report["markdown"],
                    report_json,
                    normalized_report.get("quality_score"),
                    normalized_report["created_at"],
                ),
            )

    def get_task(self, task_id: str) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute("SELECT * FROM analysis_tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            return _task_from_row(row)

    def list_tasks(
        self,
        *,
        limit: int = 20,
        symbol: str | None = None,
        status: str | None = None,
        run_mode: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if symbol:
            clauses.append("UPPER(symbol) = UPPER(?)")
            params.append(symbol)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if run_mode:
            clauses.append("run_mode = ?")
            params.append(run_mode)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM analysis_tasks
                {where_sql}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
            return [_task_from_row(row) for row in rows]

    def list_task_summaries(
        self,
        *,
        limit: int = 20,
        symbol: str | None = None,
        status: str | None = None,
        run_mode: str | None = None,
    ) -> list[dict[str, Any]]:
        tasks = self.list_tasks(limit=limit, symbol=symbol, status=status, run_mode=run_mode)
        return [{**task, **self._get_task_audit(task["id"])} for task in tasks]

    def _get_task_audit(self, task_id: str) -> dict[str, Any]:
        with get_connection() as connection:
            tool_rows = connection.execute(
                """
                SELECT tool_name, status
                FROM tool_calls
                WHERE task_id = ?
                ORDER BY sequence_index
                """,
                (task_id,),
            ).fetchall()
            report_row = connection.execute(
                """
                SELECT quality_score
                FROM research_reports
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (task_id,),
            ).fetchone()

        tool_names = [row["tool_name"] for row in tool_rows]
        failed_tool_calls = sum(1 for row in tool_rows if row["status"] == "FAILED")
        market_data_provider = _find_provider_name(tool_names, ".get_daily_prices")
        llm_provider = _find_provider_name(tool_names, ".generate_report_commentary")
        return {
            "quality_score": report_row["quality_score"] if report_row is not None else None,
            "failed_tool_calls": failed_tool_calls,
            "has_fallback": failed_tool_calls > 0,
            "market_data_provider": market_data_provider,
            "llm_provider": llm_provider,
        }

    def get_steps(self, task_id: str) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM agent_steps WHERE task_id = ? ORDER BY sequence_index",
                (task_id,),
            ).fetchall()
            return [_step_from_row(row) for row in rows]

    def get_tool_calls(self, task_id: str) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM tool_calls WHERE task_id = ? ORDER BY sequence_index",
                (task_id,),
            ).fetchall()
            return [_tool_call_from_row(row) for row in rows]

    def get_report(self, task_id: str) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM research_reports WHERE task_id = ? ORDER BY created_at DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(task_id)
            return _report_from_row(row)
