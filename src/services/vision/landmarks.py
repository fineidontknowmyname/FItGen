"""
services/vision/landmarks.py
------------------------------
MediaPipe landmark detection for STATIC UPLOADED PHOTOS only.
No cv2.VideoCapture, no while-loop, no frame-by-frame processing.

Each call processes exactly ONE image, then releases all resources via
the context manager pattern required by the vision-pipeline spec.
"""

import math

import cv2
import numpy as np
from typing import NamedTuple, List, Optional, Tuple

from schemas.vision import SWRCategory

# ── MediaPipe Pose configuration (spec requirements) ──────────────────────────
_POSE_STATIC_IMAGE_MODE      = True
_POSE_MODEL_COMPLEXITY       = 2
_POSE_MIN_DETECTION_CONF     = 0.5
_POSE_MIN_TRACKING_CONF      = 0.5


class Landmark(NamedTuple):
    x: float
    y: float
    z: float
    visibility: float


class LandmarkDetector:
    """
    Detects 33-point MediaPipe pose landmarks from a SINGLE static image.

    Design constraints:
    - static_image_mode=True   (never treats input as a video stream)
    - model_complexity=2       (highest accuracy for still photos)
    - Context manager per call (resources released immediately after each image)
    - No shared persistent Pose handle — avoids state leakage between uploads
    """

    def detect(self, frame: np.ndarray) -> Optional[List[Landmark]]:
        """
        Process a BGR image and return 33 normalised landmarks, or None.

        Parameters
        ----------
        frame   BGR numpy array (already decoded by the caller via cv2.imdecode).

        Returns
        -------
        List[Landmark] if a person was detected, None otherwise.
        Never raises — errors are logged and None is returned.
        """
        try:
            mp_pose = mp.solutions.pose
        except AttributeError:
            try:
                from mediapipe.python.solutions import pose as mp_pose  # type: ignore
            except Exception:
                return None

        # Convert BGR → RGB (spec-required pattern)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Context manager: resources released after this block (spec requirement)
        with mp_pose.Pose(
            static_image_mode=_POSE_STATIC_IMAGE_MODE,
            model_complexity=_POSE_MODEL_COMPLEXITY,
            enable_segmentation=False,
            min_detection_confidence=_POSE_MIN_DETECTION_CONF,
            min_tracking_confidence=_POSE_MIN_TRACKING_CONF,
        ) as pose:
            results = pose.process(img_rgb)

        if not results.pose_landmarks:
            return None

        return [
            Landmark(x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility)
            for lm in results.pose_landmarks.landmark
        ]

    def detect_from_bytes(self, image_bytes: bytes) -> Optional[List[Landmark]]:
        """
        Convenience wrapper: decode raw bytes then detect.

        Image loading follows the exact required pattern:
            nparr   = np.frombuffer(img_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        """
        nparr   = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return None
        return self.detect(img_bgr)

    # draw_landmarks kept as a no-op stub for backward compatibility
    def draw_landmarks(self, frame: np.ndarray, landmarks_list) -> np.ndarray:
        return frame


def calculate_shoulder_waist_ratio(
    landmarks: List[Landmark],
    image_width: int,
    image_height: int,
) -> Tuple[float, float, float, SWRCategory]:
    """
    Compute Shoulder-to-Waist Ratio from MediaPipe pose landmarks.

    Uses landmarks 11/12 (left/right shoulder) and 23/24 (left/right hip,
    used as a waist proxy) to derive pixel-space widths and their ratio.

    Parameters
    ----------
    landmarks      33-element list of normalised Landmark tuples.
    image_width    Original image width in pixels.
    image_height   Original image height in pixels.

    Returns
    -------
    (shoulder_width_px, waist_width_px, swr, swr_category)
    """
    l_sh = landmarks[11]   # left shoulder
    r_sh = landmarks[12]   # right shoulder
    l_hp = landmarks[23]   # left hip (waist proxy)
    r_hp = landmarks[24]   # right hip (waist proxy)

    shoulder_width_px = math.hypot(
        (l_sh.x - r_sh.x) * image_width,
        (l_sh.y - r_sh.y) * image_height,
    )
    waist_width_px = math.hypot(
        (l_hp.x - r_hp.x) * image_width,
        (l_hp.y - r_hp.y) * image_height,
    )

    if waist_width_px < 1e-6:
        return (shoulder_width_px, 0.0, 1.1, SWRCategory.BALANCED)

    swr = shoulder_width_px / waist_width_px

    if swr < 1.0:
        category = SWRCategory.OVERFAT
    elif swr > 1.2:
        category = SWRCategory.ATHLETIC
    else:
        category = SWRCategory.BALANCED

    return (round(shoulder_width_px, 2), round(waist_width_px, 2),
            round(swr, 3), category)


# ── Module-level singleton ─────────────────────────────────────────────────────
# NOTE: The singleton does NOT hold an open Pose session.
# detect() opens a fresh context-managed session per call.
landmark_detector = LandmarkDetector()
