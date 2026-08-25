from __future__ import annotations

# ── Re-export db dependency so endpoints only need to import from here ─────────

from db.session import get_db as get_db  # noqa: F401 (re-export)


# ── Auth ───────────────────────────────────────────────────────────────────────

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token, InvalidTokenError
from db.models import UserRecord

_bearer_scheme = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserRecord:
    if credentials is None:
        raise _CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise _CREDENTIALS_EXCEPTION

    user_id = payload.get("sub")
    if not user_id:
        raise _CREDENTIALS_EXCEPTION

    result = await db.execute(select(UserRecord).where(UserRecord.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise _CREDENTIALS_EXCEPTION

    return user


# ── Orchestrator ────────────────────────────────────────────────────────────────

from core.orchestrator import plan_orchestrator, PlanOrchestrator


def get_orchestrator() -> PlanOrchestrator:
    """Return the module-level PlanOrchestrator singleton."""
    return plan_orchestrator


# ── Ollama client ───────────────────────────────────────────────────────────────

from integrations.ollama_client import ollama_client, OllamaClient


def get_ollama_client() -> OllamaClient:
   
    return ollama_client


# ── Vision model registry ───────────────────────────────────────────────────────

from services.vision.model_loader import model_registry, ModelRegistry


def get_vision_model() -> ModelRegistry:
    
    return model_registry


# ── Body composition service ────────────────────────────────────────────────────

from services.vision.body_composition import (
    body_composition_service,
    BodyCompositionService,
)


def get_body_composition() -> BodyCompositionService:
    """Return the BodyCompositionService singleton (wraps MobileNetV2 + MediaPipe)."""
    return body_composition_service


# ── Summarizer ──────────────────────────────────────────────────────────────────

from services.intelligence.summarizer import summarizer_service, SummarizerService


def get_summarizer() -> SummarizerService:
    """Return the SummarizerService singleton (classify + extract via Ollama)."""
    return summarizer_service


# ── YouTube service ─────────────────────────────────────────────────────────────

from services.intelligence.youtube import youtube_service, YouTubeService


def get_youtube_service() -> YouTubeService:
    """Return the YouTubeService singleton (multi-URL parallel transcript fetch)."""
    return youtube_service


# ── Settings ────────────────────────────────────────────────────────────────────

from config.settings import get_settings, Settings  # noqa: F401 (re-export)
