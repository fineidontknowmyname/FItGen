from services.fitness.engine import fitness_engine
from services.vision.landmarks import Landmark


def _landmarks_wide_shoulders() -> list[Landmark]:
    landmarks = [Landmark(0, 0, 0, 0)] * 33
    landmarks[11] = Landmark(x=0.6, y=0.2, z=0.0, visibility=1.0)   # left shoulder
    landmarks[12] = Landmark(x=0.4, y=0.2, z=0.0, visibility=1.0)   # right shoulder
    landmarks[23] = Landmark(x=0.55, y=0.5, z=0.0, visibility=1.0)  # left hip
    landmarks[24] = Landmark(x=0.45, y=0.5, z=0.0, visibility=1.0)  # right hip
    landmarks[27] = Landmark(x=0.55, y=0.9, z=0.0, visibility=1.0)  # left ankle
    landmarks[28] = Landmark(x=0.45, y=0.9, z=0.0, visibility=1.0)  # right ankle
    return landmarks


def test_calculate_biometric_ratios_returns_expected_keys(user_profile):
    results = fitness_engine.calculate_biometric_ratios(_landmarks_wide_shoulders(), user_profile)

    assert "v_taper_ratio" in results
    assert "estimated_body_fat_pct" in results


def test_calculate_biometric_ratios_v_taper_reflects_wide_shoulders(user_profile):
    results = fitness_engine.calculate_biometric_ratios(_landmarks_wide_shoulders(), user_profile)

    assert results["v_taper_ratio"] > 1.5


def test_calculate_biometric_ratios_flags_insufficient_landmarks(user_profile):
    results = fitness_engine.calculate_biometric_ratios([], user_profile)

    assert "error" in results
