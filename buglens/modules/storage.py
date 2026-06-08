"""
SQLite storage for BugLens analyses.

The Streamlit app and FastAPI backend share this store so analysis
history can survive process restarts without introducing a separate
service.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .analyzer import AnalysisResult


def _default_db_path() -> Path:
    override = os.getenv("BUGLENS_DB_PATH")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "data" / "buglens.sqlite3"


class BugLensStore:
    def __init__(self, db_path: Optional[Path | str] = None) -> None:
        self.db_path = Path(db_path) if db_path else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    created_ts REAL NOT NULL,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    issue_count INTEGER NOT NULL,
                    error_count INTEGER NOT NULL,
                    warning_count INTEGER NOT NULL,
                    info_count INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_ts ON analyses(created_ts)")

    @staticmethod
    def _issue_counts(result: AnalysisResult) -> Dict[str, int]:
        counts = {"error": 0, "warning": 0, "info": 0}
        for issue in result.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> dict:
        payload = json.loads(row["payload_json"])
        result = AnalysisResult.from_dict(json.loads(row["result_json"]))
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "payload": payload,
            "result": result,
            "title": row["title"],
            "score": row["score"],
            "grade": row["grade"],
            "verdict": row["verdict"],
            "issue_count": row["issue_count"],
            "error_count": row["error_count"],
            "warning_count": row["warning_count"],
            "info_count": row["info_count"],
        }

    @staticmethod
    def to_json_record(record: dict) -> dict:
        return {
            "id": record["id"],
            "created_at": record["created_at"],
            "payload": record["payload"],
            "result": record["result"].to_dict(),
            "title": record["title"],
            "score": record["score"],
            "grade": record["grade"],
            "verdict": record["verdict"],
            "issue_count": record["issue_count"],
            "error_count": record["error_count"],
            "warning_count": record["warning_count"],
            "info_count": record["info_count"],
        }

    def save_analysis(
        self,
        payload: Dict,
        result: AnalysisResult,
        *,
        analysis_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> dict:
        record_id = analysis_id or uuid.uuid4().hex[:12]
        created_label = created_at or datetime.now().strftime("%Y-%m-%d %H:%M")
        counts = self._issue_counts(result)
        record = {
            "id": record_id,
            "created_at": created_label,
            "payload": dict(payload),
            "result": result,
            "title": payload.get("title", "").strip() or "Untitled defect",
            "score": result.score.total,
            "grade": result.score.grade,
            "verdict": result.score.verdict,
            "issue_count": len(result.issues),
            "error_count": counts["error"],
            "warning_count": counts["warning"],
            "info_count": counts["info"],
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO analyses (
                    id, created_at, created_ts, title, payload_json, result_json,
                    score, grade, verdict, issue_count, error_count, warning_count, info_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    created_at=excluded.created_at,
                    created_ts=excluded.created_ts,
                    title=excluded.title,
                    payload_json=excluded.payload_json,
                    result_json=excluded.result_json,
                    score=excluded.score,
                    grade=excluded.grade,
                    verdict=excluded.verdict,
                    issue_count=excluded.issue_count,
                    error_count=excluded.error_count,
                    warning_count=excluded.warning_count,
                    info_count=excluded.info_count
                """,
                (
                    record["id"],
                    record["created_at"],
                    datetime.now().timestamp(),
                    record["title"],
                    json.dumps(record["payload"], ensure_ascii=False),
                    json.dumps(result.to_dict(), ensure_ascii=False),
                    record["score"],
                    record["grade"],
                    record["verdict"],
                    record["issue_count"],
                    record["error_count"],
                    record["warning_count"],
                    record["info_count"],
                ),
            )
        return record

    def list_analyses(self, limit: Optional[int] = 24) -> List[dict]:
        query = "SELECT * FROM analyses ORDER BY created_ts ASC"
        params: Iterable[object] = ()
        if limit is not None:
            query = "SELECT * FROM analyses ORDER BY created_ts DESC LIMIT ?"
            params = (limit,)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        records = [self._row_to_record(row) for row in rows]
        if limit is not None:
            records.reverse()
        return records

    def get_analysis(self, analysis_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        return self._row_to_record(row) if row else None

    def delete_analysis(self, analysis_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
            return cursor.rowcount > 0

    def clear_analyses(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM analyses")
            return cursor.rowcount
