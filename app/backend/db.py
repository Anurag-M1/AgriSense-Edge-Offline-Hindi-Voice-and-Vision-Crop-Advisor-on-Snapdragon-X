"""
db.py — SQLite database for AgriSense Edge.

Stores diagnostic cases, user feedback, settings, and knowledge base vectors.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    """SQLite database manager for AgriSense Edge."""

    def __init__(self, db_path: str | Path = "data/agrisense.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Open database connection and create tables if needed."""
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        assert self._conn is not None

        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                disease_label TEXT,
                confidence REAL,
                farmer_question TEXT,
                llm_response TEXT,
                backend_used TEXT,
                latency_ms REAL,
                metadata_json TEXT
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                helpful INTEGER,  -- 1 = yes, 0 = no, NULL = no response
                comment TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            );

            CREATE TABLE IF NOT EXISTS kb_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                crop TEXT,
                disease TEXT,
                language TEXT DEFAULT 'hi',
                chunk_text TEXT NOT NULL,
                embedding BLOB,  -- numpy array stored as bytes
                metadata_json TEXT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        self._conn.commit()

    def save_case(
        self,
        disease_label: str,
        confidence: float,
        farmer_question: str,
        llm_response: str,
        backend_used: str,
        latency_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Save a diagnostic case to the database.

        Returns:
            The case ID.
        """
        assert self._conn is not None

        cursor = self._conn.execute(
            """INSERT INTO cases
               (disease_label, confidence, farmer_question, llm_response,
                backend_used, latency_ms, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                disease_label,
                confidence,
                farmer_question,
                llm_response,
                backend_used,
                latency_ms,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid  # type: ignore

    def save_feedback(self, case_id: int, helpful: bool | None, comment: str = "") -> None:
        """Save user feedback for a case."""
        assert self._conn is not None

        self._conn.execute(
            "INSERT INTO feedback (case_id, helpful, comment) VALUES (?, ?, ?)",
            (case_id, 1 if helpful else (0 if helpful is not None else None), comment),
        )
        self._conn.commit()

    def save_kb_vector(
        self,
        source_file: str,
        crop: str,
        disease: str,
        chunk_text: str,
        embedding: bytes,
        language: str = "hi",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Save a knowledge base vector entry.

        Returns:
            The entry ID.
        """
        assert self._conn is not None

        cursor = self._conn.execute(
            """INSERT INTO kb_vectors
               (source_file, crop, disease, language, chunk_text, embedding, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                source_file,
                crop,
                disease,
                language,
                chunk_text,
                embedding,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid  # type: ignore

    def get_kb_vectors(
        self, crop: str | None = None, disease: str | None = None
    ) -> list[sqlite3.Row]:
        """Retrieve knowledge base vectors, optionally filtered by crop/disease."""
        assert self._conn is not None

        query = "SELECT * FROM kb_vectors WHERE 1=1"
        params: list[str] = []

        if crop:
            query += " AND crop = ?"
            params.append(crop)
        if disease:
            query += " AND disease = ?"
            params.append(disease)

        return self._conn.execute(query, params).fetchall()

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value."""
        assert self._conn is not None

        row = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value."""
        assert self._conn is not None

        self._conn.execute(
            """INSERT INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))
               ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
            (key, value, value),
        )
        self._conn.commit()
