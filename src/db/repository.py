from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.models import FitnessPlanRecord

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Async variants  (FastAPI endpoints)
# ─────────────────────────────────────────────────────────────────────────────

async def save_plan_async(
    db: AsyncSession,
    *,
    job_id: str,
    status: str,
    user_id: str | None = None,
    request_json: dict | None = None,
    plan_json: dict | None = None,
    error_detail: str | None = None,
    youtube_urls: list[str] | None = None,
) -> FitnessPlanRecord:

    result = await db.execute(
        select(FitnessPlanRecord).where(FitnessPlanRecord.job_id == job_id)
    )
    row: FitnessPlanRecord | None = result.scalar_one_or_none()

    if row is None:
        row = FitnessPlanRecord(job_id=job_id)
        db.add(row)

    row.status = status
    if user_id       is not None: row.user_id      = user_id
    if request_json  is not None: row.request_json = request_json
    if plan_json     is not None: row.plan_json     = plan_json
    if error_detail  is not None: row.error_detail  = error_detail
    if youtube_urls  is not None: row.youtube_urls  = youtube_urls
    if status in ("done", "failed"):
        row.completed_at = datetime.now(timezone.utc)

    await db.flush()
    log.debug("save_plan_async  job_id=%s  status=%s", job_id, status)
    return row


async def get_plan_by_job_id_async(
    db: AsyncSession,
    job_id: str,
) -> Optional[FitnessPlanRecord]:
    """Return the FitnessPlanRecord for ``job_id``, or None if not found."""
    result = await db.execute(
        select(FitnessPlanRecord).where(FitnessPlanRecord.job_id == job_id)
    )
    return result.scalar_one_or_none()


async def list_plans_for_user_async(
    db: AsyncSession,
    user_id: str,
    *,
    limit: int = 20,
    offset: int = 0,
) -> list[FitnessPlanRecord]:
    """Return the most recent plans for a given user (paginated)."""
    result = await db.execute(
        select(FitnessPlanRecord)
        .where(FitnessPlanRecord.user_id == user_id)
        .order_by(FitnessPlanRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# Sync variants  (Celery workers — receive a plain Session)
# ─────────────────────────────────────────────────────────────────────────────

def save_plan(
    db: Session,
    *,
    job_id: str,
    status: str,
    user_id: str | None = None,
    request_json: dict | None = None,
    plan_json: dict | None = None,
    error_detail: str | None = None,
    youtube_urls: list[str] | None = None,
) -> FitnessPlanRecord:
    
    row: FitnessPlanRecord | None = db.execute(
        select(FitnessPlanRecord).where(FitnessPlanRecord.job_id == job_id)
    ).scalar_one_or_none()

    if row is None:
        row = FitnessPlanRecord(job_id=job_id)
        db.add(row)

    row.status = status
    if user_id       is not None: row.user_id      = user_id
    if request_json  is not None: row.request_json = request_json
    if plan_json     is not None: row.plan_json     = plan_json
    if error_detail  is not None: row.error_detail  = error_detail
    if youtube_urls  is not None: row.youtube_urls  = youtube_urls
    if status in ("done", "failed"):
        row.completed_at = datetime.now(timezone.utc)

    db.flush()
    log.debug("save_plan  job_id=%s  status=%s", job_id, status)
    return row


def get_plan_by_job_id(
    db: Session,
    job_id: str,
) -> Optional[FitnessPlanRecord]:
    """Return the FitnessPlanRecord for ``job_id``, or None (synchronous)."""
    return db.execute(
        select(FitnessPlanRecord).where(FitnessPlanRecord.job_id == job_id)
    ).scalar_one_or_none()
