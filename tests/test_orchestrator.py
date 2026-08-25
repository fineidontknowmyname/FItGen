import pytest

from core.orchestrator import PlanOrchestrator, plan_orchestrator


def test_plan_orchestrator_singleton_importable():
    assert isinstance(plan_orchestrator, PlanOrchestrator)


def test_compute_body_metrics(user_profile):
    bm = plan_orchestrator._compute_body_metrics(user_profile, capacity_score=1.0)

    assert bm.bmr > 0
    assert 1200 < bm.tdee < 8000
    assert bm.protein_g > 0
    assert bm.carbs_g >= 0
    assert bm.fat_g > 0
    assert 10 < bm.bmi < 60


async def test_classify_videos_empty_input_returns_empty_dict():
    result = await plan_orchestrator._classify_videos({})

    assert result == {}


async def test_generate_plan_async_dispatches_or_skips_without_broker(user_profile):
    from schemas.plan import GeneratePlanRequest, JobStatus

    request = GeneratePlanRequest(
        user_profile=user_profile,
        youtube_urls=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )

    try:
        job = await plan_orchestrator.generate_plan_async(request)
    except Exception as exc:
        if any(kw in str(exc).lower() for kw in ("connection", "redis", "kombu")):
            pytest.skip(f"Celery broker not available in this environment: {exc}")
        raise

    assert job.status == JobStatus.pending
    assert len(job.job_id) > 0
