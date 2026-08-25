import numpy as np

from services.fitness.engine import fitness_engine
from services.vision.landmarks import Landmark
from schemas.user import UserProfile, UserMetrics, Gender, StrengthMetrics, ExperienceLevel, FitnessGoal

def verify_biometrics():
    print("--- Verifying Biometric Extraction ---")
    
    # 1. Setup Mock User Profile
    user_profile = UserProfile(
        biometrics=UserMetrics(
            age=25,
            weight_kg=75.0,
            height_cm=180.0, # 180cm
            gender=Gender.male
        ),
        metrics=StrengthMetrics(pushup_count=10, situp_count=10, squat_count=10),
        experience_level=ExperienceLevel.intermediate,
        fitness_goal=FitnessGoal.muscle_gain
    )
    
    # Shoulders (Wide)
    l_shoulder = Landmark(x=0.6, y=0.2, z=0.0, visibility=1.0)
    r_shoulder = Landmark(x=0.4, y=0.2, z=0.0, visibility=1.0)
    # Width = 0.2 units. cm = 0.2 * 225 = 45cm
    
    # Hips (Narrower)
    l_hip = Landmark(x=0.55, y=0.5, z=0.0, visibility=1.0)
    r_hip = Landmark(x=0.45, y=0.5, z=0.0, visibility=1.0)
    # Width = 0.1 units. cm = 0.1 * 225 = 22.5cm
    
    l_ankle = Landmark(x=0.55, y=0.9, z=0.0, visibility=1.0)
    r_ankle = Landmark(x=0.45, y=0.9, z=0.0, visibility=1.0)
    
    # Fill dummy landmarks list
    landmarks = [Landmark(0,0,0,0)] * 33
    landmarks[11] = l_shoulder
    landmarks[12] = r_shoulder
    landmarks[23] = l_hip
    landmarks[24] = r_hip
    landmarks[27] = l_ankle
    landmarks[28] = r_ankle
    
    results = fitness_engine.calculate_biometric_ratios(landmarks, user_profile)
    print("Biometric Results:", results)
    
    if "v_taper_ratio" in results and "estimated_body_fat_pct" in results:
        print(f"✅ V-Taper: {results['v_taper_ratio']}")
        print(f"✅ Est Body Fat: {results['estimated_body_fat_pct']}%")
        
        # Check logic roughly
        if results['v_taper_ratio'] > 1.5:
             print("✅ V-Taper logic seems sound (Shoulders > Hips)")
    else:
        print("❌ Missing keys in result")

if __name__ == "__main__":
    verify_biometrics()
