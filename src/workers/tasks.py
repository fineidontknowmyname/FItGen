from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from celery.utils.log import get_task_logger

from workers.celery_app import celery_app

log = get_task_logger(__name__)


async def _persist_plan(job_id: str, status: str, plan_dict: dict | None, error: str | None) -> None:
    try:
        from sqlalchemy import select

        from db.models import FitnessPlanRecord
        from db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(FitnessPlanRecord).where(FitnessPlanRecord.job_id == job_id)
            )
            row = result.scalar_one_or_none()

            if row is None:
                row = FitnessPlanRecord(job_id=job_id)
                session.add(row)

            row.status       = status
            row.plan_json    = plan_dict
            row.error_detail = error
            if status in ("done", "failed"):
                row.completed_at = datetime.now(timezone.utc)

            await session.commit()
            log.info("Persisted plan record  job_id=%s  status=%s", job_id, status)

    except Exception as exc:
        log.warning("Failed to persist plan record  job_id=%s  error=%s", job_id, exc)


async def _run_pipeline(job_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    await _persist_plan(job_id, "running", None, None)

    from schemas.plan import GeneratePlanRequest
    from core.orchestrator import plan_orchestrator

    request = GeneratePlanRequest.model_validate(payload)

    plan = await plan_orchestrator.generate_plan(
        user_profile=request.user_profile,
        youtube_urls=request.youtube_urls or [],
        workout_youtube_urls=request.workout_youtube_urls or [],
        diet_youtube_urls=request.diet_youtube_urls or [],
        transcript_text=request.transcript_text,
        body_composition=request.body_composition,
    )
    plan_dict = plan.model_dump()

    await _persist_plan(job_id, "done", plan_dict, None)
    return plan_dict


@celery_app.task(
    bind=True,
    name="workers.tasks.generate_plan_task",
    max_retries=3,
    soft_time_limit=180,
    time_limit=240,
)
def generate_plan_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    job_id = self.request.id
    log.info("generate_plan_task START  job_id=%s  retry=%d", job_id, self.request.retries)

    try:
        plan_dict = asyncio.run(_run_pipeline(job_id, payload))
        log.info("generate_plan_task DONE  job_id=%s", job_id)
        return plan_dict

    except Exception as exc:
        log.exception(
            "generate_plan_task FAILED  job_id=%s  retry=%d  error=%s",
            job_id, self.request.retries, exc,
        )
        asyncio.run(_persist_plan(job_id, "failed", None, str(exc)))
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
