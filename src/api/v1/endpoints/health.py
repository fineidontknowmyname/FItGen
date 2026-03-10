from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any

from config.settings import settings
from db.session import get_db
from db.models import UserRecord # dummy import for sqlalchemy
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from workers.celery_app import celery_app
import logging

log = logging.getLogger(__name__)

router = APIRouter()

@router.get("", summary="Liveness probe")
def health_check() -> Dict[str, Any]:
    """Returns 200 OK — no DB or broker dependency."""
    return {"status": "ok", "environment": settings.ENVIRONMENT, "version": "1.0.0"}

@router.get("/redis", summary="Redis ping")
async def redis_health() -> JSONResponse:
    start = time.perf_counter()
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        latency = (time.perf_counter() - start) * 1000
        return JSONResponse(status_code=200, content={"redis": "ok", "latency_ms": round(latency, 2)})
    except Exception as exc:
        log.error("Redis health check failed: %s", exc)
        return JSONResponse(status_code=503, content={"redis": "error", "detail": str(exc)})

@router.get("/celery", summary="Celery ping")
def celery_health_check() -> JSONResponse:
    # Sync because celery control ping is sync
    try:
        inspector = celery_app.control.ping(timeout=3.0)
        # inspector is a dict of {worker_node_name: {"ok": "pong"}}
        # if empty, no workers are listening
        if inspector:
            return JSONResponse(status_code=200, content={"celery": "ok", "workers": len(inspector)})
        else:
            return JSONResponse(status_code=503, content={"celery": "error", "detail": "No Celery workers responded to ping"})
    except Exception as exc:
        log.error("Celery health check failed: %s", exc)
        return JSONResponse(status_code=503, content={"celery": "error", "detail": str(exc)})

@router.get("/db", summary="Database ping")
async def db_health(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        return JSONResponse(status_code=200, content={"db": "ok", "latency_ms": round(latency, 2)})
    except Exception as exc:
        log.error("DB health check failed: %s", exc)
        return JSONResponse(status_code=503, content={"db": "error", "detail": str(exc)})
