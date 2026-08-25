from typing import List
from schemas.content import Exercise
from schemas.common import Injury, Equipment

class SafetyFilterEngine:
    def filter_exercises(self, exercises: List[Exercise], injuries: List[Injury], available_equipment: List[Equipment]) -> List[Exercise]:
        """
        Filters exercises based on user injuries and available equipment.
        """
        safe_list = []
        
        for exercise in exercises:
            
            missing_equipment = [
                eq for eq in exercise.equipment_needed 
                if eq not in available_equipment and eq != Equipment.bodyweight
            ]
            
            if missing_equipment:
                continue # Skip exercise
                
            # 2. Injury Check
            # If exercise works a muscle that is injured, skip it.
            # Matching "muscles_worked" (list of strings) against "injuries" (list of Enum)
            # We assume muscles_worked uses the same vocabulary keys as Injury where applicable.
            
            is_unsafe = False
            for muscle in exercise.muscles_worked:
                # Normalize string comparison
                muscle_key = muscle.lower().strip()
                if any(inj.value == muscle_key for inj in injuries):
                    is_unsafe = True
                    break
            
            if is_unsafe:
                continue
                
            safe_list.append(exercise)
            
        return safe_list

safety_engine = SafetyFilterEngine()
