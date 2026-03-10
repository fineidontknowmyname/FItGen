"""
api/v1/endpoints/vision.py
---------------------------
Body composition analysis endpoint — static uploaded photos ONLY.

No video capture, no frame-by-frame loops. Each request processes
exactly one set of images (1–3 views) and returns immediately.

Endpoint
────────
POST /vision/analyze-body

  Accepts 1–3 images (front, side, back views) as multipart file uploads.
  Requires explicit user consent via the `X-Vision-Consent: true` header.
  Returns a BodyComposition Pydantic model, always — never raises 422 for
  pose-detection failure; instead returns stub values with confidence=0.0
  and pose_detected=False so the frontend can show an appropriate message.

Privacy & consent
──────────────────
Body image analysis is sensitive.  Callers MUST include the header:

    X-Vision-Consent: true

Requests without this header receive HTTP 451 (Unavailable For Legal Reasons).

All inference runs on-device (MediaPipe + MobileNetV2); no image bytes are
sent to any external service.
"""

from __future__ import annotations

import logging
from typing import Annotated, List

import cv2
import numpy as np

from fastapi import (
    APIRouter,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
    status,
)

from schemas.vision import BodyComposition
from services.vision.body_composition import body_composition_service

log = logging.getLogger(__name__)

router = APIRouter()

# ── Constants (spec requirements) ─────────────────────────────────────────────

_MAX_IMAGE_BYTES       = 10 * 1024 * 1024   # 10 MB per image
_MIN_IMAGE_DIMENSION   = 200                 # px — minimum 200×200
_ALLOWED_MIME          = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
_CONSENT_HEADER        = "x-vision-consent"


# ── Consent guard ──────────────────────────────────────────────────────────────

def _require_consent(x_vision_consent: str | None) -> None:
    """Raise HTTP 451 if the caller hasn't sent the consent header."""
    if not x_vision_consent or x_vision_consent.strip().lower() != "true":
        raise HTTPException(
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
            detail=(
                "Body image analysis requires explicit consent. "
                "Include the header 'X-Vision-Consent: true' in your request."
            ),
        )


# ── Validation helper ──────────────────────────────────────────────────────────

async def _read_image(file: UploadFile) -> bytes:
    """
    Read and validate a single uploaded image file.

    Validation (spec requirements):
    - Accepted MIME types: jpg, jpeg, png, webp
    - Maximum file size: 10 MB
    - Minimum resolution: 200×200 pixels

    If format/size/resolution validation fails → returns stub bytes (b"")
    and logs a warning.  The service layer handles stub bytes gracefully
    (returns confidence=0.0, pose_detected=False).

    Raises HTTP 400 only for completely wrong MIME type (not a photo at all).
    """
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}' for '{file.filename}'. "
                f"Accepted types: {', '.join(sorted(_ALLOWED_MIME))}"
            ),
        )

    data = await file.read()

    if not data:
        log.warning("Image '%s' is empty — will use stub values", file.filename)
        return b""

    if len(data) > _MAX_IMAGE_BYTES:
        log.warning(
            "Image '%s' exceeds 10 MB (%d bytes) — will use stub values",
            file.filename, len(data),
        )
        return b""   # service will return stub with confidence=0

    # Minimum resolution check
    nparr = np.frombuffer(data, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is not None:
        h, w = img.shape[:2]
        if h < _MIN_IMAGE_DIMENSION or w < _MIN_IMAGE_DIMENSION:
            log.warning(
                "Image '%s' is %dx%d — below minimum %dx%d. Will use stub values.",
                file.filename, w, h, _MIN_IMAGE_DIMENSION, _MIN_IMAGE_DIMENSION,
            )
            return b""

    return data


# ── Endpoint ───────────────────────────────────────────────────────────────────

@router.post(
    "/analyze-body",
    response_model=BodyComposition,
    summary="Multi-view body composition analysis (on-device MobileNetV2)",
    description=(
        "Upload 1–3 **static photos** (front, side, rear) for body composition analysis.\n\n"
        "**Static photos only** — no video, no real-time capture.\n\n"
        "Analysis runs entirely on-device (MobileNetV2 + MediaPipe Pose) — "
        "no image data leaves the server.\n\n"
        "**Required header:** `X-Vision-Consent: true`\n\n"
        "**Response field `pose_detected`:** `true` = MediaPipe found landmarks → "
        "full analysis. `false` = stub/estimated values used."
    ),
)
async def analyze_body(
    front: Annotated[UploadFile, File(description="Front-view image (required)")],
    side:  Annotated[UploadFile | None, File(description="Side-view image (optional)")] = None,
    back:  Annotated[UploadFile | None, File(description="Rear-view image (optional)")] = None,
    consent: Annotated[str | None, Form(description="Must be 'true' to consent")] = None,
    x_vision_consent: Annotated[
        str | None,
        Header(alias="X-Vision-Consent", description="Must be 'true' to consent to image analysis"),
    ] = None,
    user_height_cm: Annotated[float, Form(description="User height in cm for body-fat calibration")] = 175.0,
    gender: Annotated[str, Form(description="'male' or 'female' — affects RFM constant")] = "male",
) -> BodyComposition:
    """
    Analyse up to three **static** body photos and return a `BodyComposition` result.

    The endpoint **never raises** for pose-detection failure — instead it returns
    stub values with ``confidence=0.0`` and ``pose_detected=False``.  The frontend
    should check ``pose_detected`` to show the appropriate message:

    - ``pose_detected=True``  → "Body analysis complete"
    - ``pose_detected=False`` → "Could not detect pose — using estimated values"

    Parameters
    ----------
    front           Front-view image (JPEG/PNG/WebP, ≤ 10 MB, min 200×200 px). Required.
    side            Side-view image. Optional but improves V-taper accuracy.
    back            Rear-view image. Optional.
    x_vision_consent Must be "true" (case-insensitive).
    user_height_cm  Known height used to calibrate pixel → cm scale.
    gender          "male" or "female" — influences the RFM body-fat constant.
    """
    # ── Consent gate (accept from form field OR header) ────────────────────
    _require_consent(consent or x_vision_consent)

    # ── Validate gender param ──────────────────────────────────────────────
    if gender.lower() not in ("male", "female"):
        raise HTTPException(
            status_code=400,
            detail="'gender' must be 'male' or 'female'.",
        )

    # ── Validate & read images ─────────────────────────────────────────────
    # _read_image returns b"" (stub) for invalid/oversized/low-res files;
    # the service handles b"" gracefully (returns confidence=0, pose_detected=False).
    images: List[bytes] = []

    front_bytes = await _read_image(front)
    images.append(front_bytes)

    if side is not None:
        images.append(await _read_image(side))

    if back is not None:
        images.append(await _read_image(back))

    log.info(
        "analyze-body: received %d image(s)  height=%.1f cm  gender=%s",
        len(images), user_height_cm, gender,
    )

    # ── Run inference ──────────────────────────────────────────────────────
    # Never raises — errors produce stub BodyComposition with confidence=0.0
    try:
        result = await body_composition_service.analyze(
            images=images,
            user_height_cm=user_height_cm,
            gender=gender.lower(),
        )
    except Exception as exc:
        log.exception("Body composition analysis failed unexpectedly: %s", exc)
        # Return stub instead of raising — spec requirement: never raise for pose failure
        return BodyComposition(
            is_valid_person=False,
            confidence=0.0,
            pose_detected=False,
            posture_assessment="Analysis error — using estimated values",
        )

    # Log outcome for observability
    if not result.pose_detected:
        log.info(
            "analyze-body: pose NOT detected — returning stub values  "
            "is_valid_person=%s  confidence=%.3f",
            result.is_valid_person, result.confidence,
        )
    else:
        log.info(
            "analyze-body: pose detected  confidence=%.3f  fat=%.1f–%.1f%%",
            result.confidence,
            result.fat_pct_low or 0.0,
            result.fat_pct_high or 0.0,
        )

    return result
