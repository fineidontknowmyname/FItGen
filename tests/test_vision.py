import numpy as np

from services.fitness.engine import fitness_engine
from services.vision.landmarks import Landmark, landmark_detector


def test_landmark_detector_returns_none_for_blank_image():
    blank_image = np.zeros((480, 640, 3), dtype=np.uint8)

    landmarks = landmark_detector.detect(blank_image)

    assert landmarks is None


def test_calculate_angle_right_angle():
    a = Landmark(x=1.0, y=0.0, z=0.0, visibility=1.0)
    b = Landmark(x=0.0, y=0.0, z=0.0, visibility=1.0)
    c = Landmark(x=0.0, y=1.0, z=0.0, visibility=1.0)

    angle = fitness_engine.calculate_angle(a, b, c)

    assert abs(angle - 90.0) < 0.1


def test_analyze_form_squat_returns_knee_angle_metric():
    hip = Landmark(x=1.0, y=0.0, z=0.0, visibility=1.0)
    knee = Landmark(x=0.0, y=0.0, z=0.0, visibility=1.0)
    ankle = Landmark(x=0.0, y=1.0, z=0.0, visibility=1.0)

    landmarks = [Landmark(x=0.0, y=0.0, z=0.0, visibility=0.0) for _ in range(33)]
    landmarks[24] = hip
    landmarks[26] = knee
    landmarks[28] = ankle

    result = fitness_engine.analyze_form("squat", landmarks)

    assert "metrics" in result
    assert "knee_angle" in result["metrics"]
