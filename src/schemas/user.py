from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from schemas.common import Gender, ExperienceLevel, Injury, Equipment, FitnessGoal, ActivityLevel


class UserMetrics(BaseModel):
    age: int = Field(ge=15, le=60, description="Age in years")
    weight_kg: float = Field(ge=30.0, le=200.0, description="Weight in kilograms")
    height_cm: float = Field(ge=95.0, le=250.0, description="Height in centimeters")
    gender: Gender  # male | female only

    @field_validator("age", mode="before")
    @classmethod
    def clamp_age(cls, v):  # noqa: N805
        """Clamp incoming age to 15–60 instead of rejecting it."""
        return max(15, min(60, int(v)))

    @field_validator("gender", mode="before")
    @classmethod
    def normalise_gender(cls, v):  # noqa: N805
        """Map unrecognised gender values to 'male' instead of rejecting."""
        return v if v in ("male", "female") else "male"


class StrengthMetrics(BaseModel):
    pushup_count: int = Field(ge=0, le=100, description="Max consecutive pushups")
    situp_count: int = Field(ge=0, le=100, description="Max consecutive situps")
    squat_count: int = Field(ge=0, le=100, description="Max consecutive bodyweight squats")
    run_time_min: Optional[float] = Field(None, ge=0.0, le=120.0, description="1km run time in minutes")
    run_distance_km: Optional[float] = Field(None, ge=0.0, le=42.0, description="Max run distance in km")


class PhysicalActivity(BaseModel):
    activity_level: ActivityLevel = Field(
        default=ActivityLevel.moderately_active,
        description="General daily activity level",
    )
    physical_activity_hours_per_day: float = Field(
        default=1.0, ge=0.0, le=16.0,
        description="Hours per day spent in deliberate physical activity (exercise, sport, etc.)",
    )


class UserProfile(BaseModel):
    model_config = {"populate_by_name": True, "extra": "ignore"}

    biometrics: UserMetrics
    metrics: StrengthMetrics
    physical_activity: Optional[PhysicalActivity] = None

    # Accept both "injuries" and flat injuries list
    injuries: List[Injury] = Field(default_factory=list)

    # Accept both "equipment" and "equipment_available"
    equipment: List[Equipment] = Field(default_factory=list, alias="equipment")
    equipment_available: Optional[List[Equipment]] = Field(default=None, alias="equipment_available")

    experience_level: ExperienceLevel
    fitness_goal: FitnessGoal
    analysis_consent: bool = Field(default=False)

    # Accept flat physical_activity_hours_per_day at top level
    physical_activity_hours_per_day: Optional[float] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def _normalize_fields(self) -> "UserProfile":
        # Merge equipment_available → equipment if equipment is empty
        if not self.equipment and self.equipment_available:
            self.equipment = self.equipment_available
        # Merge flat physical_activity_hours_per_day into nested physical_activity
        if self.physical_activity_hours_per_day is not None and self.physical_activity is None:
            self.physical_activity = PhysicalActivity(
                physical_activity_hours_per_day=self.physical_activity_hours_per_day
            )
        return self


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str
    goals: List[str]
    equipment_available: List[str] = []
    injuries: List[str] = []
    dietary_restrictions: List[str] = []
    physical_activity_hours_per_day: float = 1.0