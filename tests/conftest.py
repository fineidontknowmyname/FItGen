import pytest

from schemas.common import ActivityLevel, ExperienceLevel, FitnessGoal, Gender
from schemas.user import PhysicalActivity, StrengthMetrics, UserMetrics, UserProfile


@pytest.fixture
def user_profile() -> UserProfile:
    return UserProfile(
        biometrics=UserMetrics(age=28, weight_kg=80.0, height_cm=178.0, gender=Gender.male),
        metrics=StrengthMetrics(pushup_count=25, situp_count=20, squat_count=30),
        physical_activity=PhysicalActivity(
            activity_level=ActivityLevel.moderately_active,
            physical_activity_hours_per_day=1.0,
        ),
        injuries=[],
        equipment=[],
        experience_level=ExperienceLevel.intermediate,
        fitness_goal=FitnessGoal.muscle_gain,
    )
