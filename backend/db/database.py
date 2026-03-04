"""
SQLite storage for research history using aiosqlite.
"""
import aiosqlite
import json
import logging
from datetime import datetime
from typing import Optional, List
from backend.models.schemas import CompanyResearch, ResearchStatus

logger = logging.getLogger(__name__)

DB_PATH = "scout.db"


async def init_db() -> None:
    """Create tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS research (
                id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                extracted_data TEXT,
                briefing TEXT,
                error TEXT
            )
        """)
        await db.commit()
    logger.info("Database initialized.")


async def save_research(research: CompanyResearch) -> None:
    """Insert or update a CompanyResearch record."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO research
                (id, company_name, status, created_at, updated_at, extracted_data, briefing, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                research.id,
                research.company_name,
                research.status.value,
                research.created_at.isoformat(),
                research.updated_at.isoformat(),
                research.extracted_data.model_dump_json() if research.extracted_data else None,
                research.briefing.model_dump_json() if research.briefing else None,
                research.error,
            ),
        )
        await db.commit()


async def get_research(research_id: str) -> Optional[CompanyResearch]:
    """Fetch a single research record by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM research WHERE id = ?", (research_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return _row_to_research(dict(row))


async def get_all_research(limit: int = 50) -> List[CompanyResearch]:
    """Fetch recent research records, most recent first."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM research ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [_row_to_research(dict(row)) for row in rows]


def _row_to_research(row: dict) -> CompanyResearch:
    """Convert a database row dict to a CompanyResearch model."""
    from backend.models.schemas import ExtractedData, Briefing

    extracted_data = None
    if row.get("extracted_data"):
        try:
            extracted_data = ExtractedData.model_validate_json(row["extracted_data"])
        except Exception:
            pass

    briefing = None
    if row.get("briefing"):
        try:
            briefing = Briefing.model_validate_json(row["briefing"])
        except Exception:
            pass

    return CompanyResearch(
        id=row["id"],
        company_name=row["company_name"],
        status=ResearchStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        extracted_data=extracted_data,
        briefing=briefing,
        error=row.get("error"),
    )
