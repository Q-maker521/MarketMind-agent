import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.core.config import settings


def initialize_database() -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS analysis_tasks (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                market TEXT NOT NULL,
                question TEXT NOT NULL,
                time_range TEXT NOT NULL,
                run_mode TEXT NOT NULL DEFAULT 'demo',
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS agent_steps (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                node_name TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                input_summary TEXT NOT NULL,
                output_summary TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                duration_ms INTEGER NOT NULL,
                error_message TEXT,
                sequence_index INTEGER NOT NULL,
                FOREIGN KEY (task_id) REFERENCES analysis_tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tool_calls (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL,
                input_json TEXT NOT NULL,
                output_summary TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                error_message TEXT,
                sequence_index INTEGER NOT NULL,
                FOREIGN KEY (task_id) REFERENCES analysis_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (step_id) REFERENCES agent_steps(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS research_reports (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                stance TEXT NOT NULL,
                confidence REAL NOT NULL,
                sections_json TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                disclaimer TEXT NOT NULL,
                report_markdown TEXT NOT NULL,
                report_json TEXT NOT NULL,
                quality_score REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES analysis_tasks(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_agent_steps_task_id
                ON agent_steps(task_id, sequence_index);

            CREATE INDEX IF NOT EXISTS idx_tool_calls_task_id
                ON tool_calls(task_id, sequence_index);

            CREATE INDEX IF NOT EXISTS idx_research_reports_task_id
                ON research_reports(task_id);
            """
        )
        _ensure_column(connection, "analysis_tasks", "run_mode", "TEXT NOT NULL DEFAULT 'demo'")


def _ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {column["name"] for column in columns}
    if column_name not in existing_columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
