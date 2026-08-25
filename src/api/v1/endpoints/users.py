"""
api/v1/endpoints/users.py
--------------------------
User profile CRUD backed by SQLAlchemy (replaces the former in-memory dict).

Routes
──────
POST  /users/          Create user account (signup)  → {user_id, name} (201)
POST  /users/login     Authenticate and return token → {access_token, ...} (200)
GET   /users/me        Current user profile           → flat profile dict (200)
GET   /users/{id}      Read profile                  → UserProfile (200)
PUT   /users/{id}      Replace profile               → UserProfile (200)
DELETE /users/{id}     Remove profile                → 204 No Content
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from core.security import create_access_token, hash_password, verify_password
from db.models import UserProfileModel, UserRecord
from db.session import get_db
from schemas.user import UserProfile, SignupRequest

log = logging.getLogger(__name__)

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _fetch_or_404(user_id: str, db: AsyncSession) -> UserProfileModel:
    """Return the ORM row or raise HTTP 404."""
    result = await db.execute(
        select(UserProfileModel).where(UserProfileModel.user_id == user_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return row


def _next_id(row_count: int) -> str:
    """Simple monotonic ID — replace with UUID or auth-issued ID in production."""
    return str(row_count + 1)


def _flatten_profile(row: UserProfileModel) -> dict:
    """
    Build a flat response dict from the ORM row + its JSON blob.

    This gives the frontend easy top-level access to fields like
    ``weight_kg``, ``goals``, etc. without having to dig into the
    nested ``profile_json`` structure.
    """
    profile = row.profile_json or {}
    bio = profile.get("biometrics", {})
    metrics = profile.get("metrics", {})
    pa = profile.get("physical_activity", {}) or {}

    return {
        "id": row.user_id,
        "user_id": row.user_id,
        "email": row.email,
        # FIX: read name directly from UserRecord.name — never derive from email
        "name": row.name,
        # biometrics
        "age": bio.get("age"),
        "gender": bio.get("gender"),
        "weight_kg": bio.get("weight_kg"),
        "height_cm": bio.get("height_cm"),
        # fitness
        "fitness_goal": profile.get("fitness_goal"),
        "goals": [profile.get("fitness_goal")] if profile.get("fitness_goal") else [],
        "fitness_level": profile.get("experience_level"),
        "experience_level": profile.get("experience_level"),
        # metrics
        "pushups_max": metrics.get("pushup_count", 0),
        "squats_max": metrics.get("squat_count", 0),
        "pushup_count": metrics.get("pushup_count", 0),
        "squat_count": metrics.get("squat_count", 0),
        # activity
        "physical_activity_hours_per_day": pa.get("physical_activity_hours_per_day"),
        # body composition (populated after vision analysis)
        "body_fat_pct": profile.get("body_fat_pct"),
        "v_taper": profile.get("v_taper"),
        "swr_category": profile.get("swr_category"),
        # raw profile for advanced use
        "profile": profile,
    }


# ── GET /me  (current user — mock auth) ────────────────────────────────────────

@router.get(
    "/me",
    summary="Get current user profile",
    response_model=None,
)
async def get_current_user_profile(
    current_user: UserRecord = Depends(get_current_user),
) -> Any:
    return _flatten_profile(current_user)


# ── POST /  (signup — creates user account) ────────────────────────────────────

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a user account",
    response_model=None,
)
async def create_user_profile(
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new user account.  Persists name, email, and hashed password
    to the UserRecord row, plus the full profile as JSON.
    """
    # Check if email already exists
    existing = await db.execute(
        select(UserProfileModel).where(UserProfileModel.email == body.email)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Derive next ID
    from sqlalchemy import func as sa_func
    count_result = await db.execute(select(sa_func.count(UserProfileModel.id)))
    count = count_result.scalar_one()
    user_id = _next_id(count)

    # Build profile_json blob from signup data
    profile_json = {
        "biometrics": {
            "age": body.age,
            "weight_kg": body.weight_kg,
            "height_cm": body.height_cm,
            "gender": body.gender.value,
        },
        "metrics": {
            "pushup_count": 0,
            "situp_count": 0,
            "squat_count": 0,
        },
        "experience_level": body.fitness_level.value,
        "fitness_goal": body.goals[0].value,
        "physical_activity": {
            "activity_level": "moderately_active",
            "physical_activity_hours_per_day": body.physical_activity_hours_per_day,
        },
        "equipment": [e.value for e in body.equipment_available],
        "injuries": [i.value for i in body.injuries],
        "dietary_restrictions": body.dietary_restrictions,
        "analysis_consent": False,
    }

    row = UserProfileModel(
        user_id=user_id,
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
        profile_json=profile_json,
    )
    db.add(row)
    await db.flush()
    log.info("Created user account  user_id=%s  email=%s", user_id, body.email)

    return {"user_id": user_id, "name": body.name}


# ── POST /login ─────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    summary="Authenticate user and return token",
    response_model=None,
)
async def login(
    body: dict,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Authenticate a user by email + password.
    Returns access_token, token_type, user_id, and name on success.
    Returns 401 on invalid credentials.
    """
    email = body.get("email", "")
    password = body.get("password", "")

    result = await db.execute(
        select(UserProfileModel).where(UserProfileModel.email == email)
    )
    row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, row.hashed_password or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(row.user_id)

    log.info("User logged in  user_id=%s  email=%s", row.user_id, row.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": row.user_id,
        "name": row.name,
        "email": row.email,
    }


# ── READ ───────────────────────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=UserProfile,
    summary="Get user profile",
)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retrieve a stored user profile by ID."""
    row = await _fetch_or_404(user_id, db)
    return UserProfile.model_validate(row.profile_json)


# ── UPDATE (full replace) ──────────────────────────────────────────────────────

@router.put(
    "/{user_id}",
    response_model=UserProfile,
    summary="Replace user profile",
)
async def update_user_profile(
    user_id: str,
    user_profile: UserProfile,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Fully replace an existing profile.

    Age validation (15–60) is enforced by the Pydantic schema.
    Returns 404 when the user ID does not exist.
    """
    row = await _fetch_or_404(user_id, db)
    row.profile_json = user_profile.model_dump()
    log.info("Updated user profile  user_id=%s", user_id)
    return user_profile


# ── DELETE ─────────────────────────────────────────────────────────────────────

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user profile",
)
async def delete_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a user profile. Returns 204 No Content on success."""
    row = await _fetch_or_404(user_id, db)
    await db.delete(row)
    log.info("Deleted user profile  user_id=%s", user_id)
