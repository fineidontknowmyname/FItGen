import math

import cv2
import mediapipe as mp
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
   
    def detect(self, frame: np.ndarray) -> Optional[List[Landmark]]:
        
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
