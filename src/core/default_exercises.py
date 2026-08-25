from __future__ import annotations

from typing import List

from schemas.content import Exercise
from schemas.common import Equipment, ExperienceLevel, FitnessGoal, Injury


# ── Master Exercise Library ────────────────────────────────────────────────────
# 50 exercises across chest / back / legs / shoulders / arms / core / cardio
# Each entry follows the Exercise Pydantic schema exactly.

_LIBRARY: List[Exercise] = [

    # ── CHEST ──────────────────────────────────────────────────────────────────

    Exercise(
        name="Push-Up",
        description="Classic bodyweight pressing movement that builds chest, shoulder, and tricep strength.",
        instructions=[
            "Start in a high plank with hands shoulder-width apart.",
            "Lower your chest to just above the floor while keeping elbows at ~45 degrees.",
            "Press explosively back to the start position.",
            "Keep your core braced and hips level throughout.",
        ],
        benefits=["Builds chest and tricep strength", "No equipment required", "Improves core stability"],
        muscles_worked=["chest", "triceps", "shoulders", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Avoid sagging hips", "Stop if wrist pain occurs"],
    ),

    Exercise(
        name="Wide Push-Up",
        description="Push-up variation with a wider hand placement to emphasise the chest more.",
        instructions=[
            "Place hands wider than shoulder width.",
            "Follow standard push-up form.",
            "Feel the stretch across your chest at the bottom.",
        ],
        benefits=["Greater chest stretch", "Builds pec width"],
        muscles_worked=["chest", "shoulders", "triceps"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Avoid flaring elbows excessively"],
    ),

    Exercise(
        name="Dumbbell Chest Press",
        description="Foundational horizontal pressing movement performed with dumbbells on a flat surface.",
        instructions=[
            "Lie on a flat bench or floor holding a dumbbell in each hand at chest level.",
            "Press the dumbbells up until arms are fully extended.",
            "Lower slowly over 2–3 seconds back to chest.",
            "Keep feet flat and lower back neutral.",
        ],
        benefits=["Builds chest mass", "Greater range of motion than barbell", "Strengthens triceps"],
        muscles_worked=["chest", "triceps", "shoulders"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not drop elbows below bench level", "Use spotter for heavy loads"],
    ),

    Exercise(
        name="Dumbbell Flye",
        description="Isolation exercise that stretches and contracts the chest through a wide arc.",
        instructions=[
            "Lie flat holding dumbbells above your chest with a slight elbow bend.",
            "Open your arms wide in an arc until you feel a chest stretch.",
            "Squeeze the chest to bring the dumbbells back together.",
        ],
        benefits=["Deep chest stretch", "Chest isolation", "Improves shoulder mobility"],
        muscles_worked=["chest", "shoulders"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep a soft elbow bend", "Avoid excessively heavy weight"],
    ),

    Exercise(
        name="Barbell Bench Press",
        description="King of chest exercises — heavy horizontal pressing for maximum strength and hypertrophy.",
        instructions=[
            "Lie on a bench with eyes under the bar, feet flat on the floor.",
            "Grip slightly wider than shoulder-width.",
            "Unrack the bar and lower it to mid-chest.",
            "Press back up in a slight arc until arms lock out.",
        ],
        benefits=["Maximum chest + tricep strength", "Measurable progression", "Builds upper body mass"],
        muscles_worked=["chest", "triceps", "shoulders"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Always use a spotter", "Keep wrists straight", "Do not bounce bar off chest"],
    ),

    Exercise(
        name="Diamond Push-Up",
        description="Tricep-dominant push-up variation that also engages the inner chest.",
        instructions=[
            "Form a diamond shape with index fingers and thumbs below your chest.",
            "Lower your chest toward your hands.",
            "Press back up, feeling the triceps work.",
        ],
        benefits=["Tricep and inner chest focus", "Bodyweight", "Builds pushing strength"],
        muscles_worked=["triceps", "chest", "shoulders"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Can strain wrists — use fists if needed"],
    ),

    # ── BACK ───────────────────────────────────────────────────────────────────

    Exercise(
        name="Bodyweight Row (Inverted Row)",
        description="Horizontal pulling exercise using a table or low bar to build back thickness.",
        instructions=[
            "Lie under a sturdy table or low bar, gripping it with arms extended.",
            "Keep your body straight and pull your chest up to the bar.",
            "Lower with control.",
        ],
        benefits=["Builds back and biceps", "Scalable for beginners", "No gym needed"],
        muscles_worked=["back", "biceps", "rear shoulders"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Ensure the table is stable before loading it"],
    ),

    Exercise(
        name="Dumbbell Bent-Over Row",
        description="Single-arm or bilateral rowing movement to build back thickness and strength.",
        instructions=[
            "Hinge at the hip until your torso is ~45 degrees.",
            "Let the dumbbell hang at arm's length.",
            "Drive your elbow back and up, squeezing the shoulder blade at the top.",
            "Lower slowly.",
        ],
        benefits=["Mid and upper back thickness", "Bicep involvement", "Core anti-rotation"],
        muscles_worked=["back", "biceps", "rear shoulders", "core"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep a neutral spine", "Do not round the lower back"],
    ),

    Exercise(
        name="Pull-Up",
        description="Vertical pulling compound movement — the ultimate test of upper body relative strength.",
        instructions=[
            "Hang from a bar with an overhand grip, hands shoulder-width apart.",
            "Pull until your chin clears the bar by driving your elbows to your hips.",
            "Lower under control until arms are fully extended.",
        ],
        benefits=["Builds lat width", "Requires no machine", "Improves grip strength"],
        muscles_worked=["back", "biceps", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Do not kip unless trained", "Avoid shrug at the top"],
    ),

    Exercise(
        name="Chin-Up",
        description="Underhand-grip pull-up that shifts emphasis toward the biceps.",
        instructions=[
            "Hang with palms facing you, shoulder-width grip.",
            "Pull up until chin clears the bar.",
            "Lower with control.",
        ],
        benefits=["Bicep + back combination", "Easier than pull-up for beginners", "Great strength builder"],
        muscles_worked=["biceps", "back", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep shoulder blades depressed throughout"],
    ),

    Exercise(
        name="Barbell Bent-Over Row",
        description="Heavy bilateral rowing for maximum back mass and strength.",
        instructions=[
            "Hinge until torso is nearly parallel to the floor.",
            "Grip bar just wider than shoulder width.",
            "Drive bar to your navel, squeezing both shoulder blades together.",
            "Lower with control.",
        ],
        benefits=["Maximum back thickness", "Deadlift carryover", "Full posterior chain engagement"],
        muscles_worked=["back", "biceps", "glutes", "hamstrings"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Maintain flat back", "Do not jerk the bar"],
    ),

    Exercise(
        name="Lat Pulldown",
        description="Machine-based vertical pull that mimics the pull-up for lat development.",
        instructions=[
            "Grip the bar wider than shoulder width, palms facing away.",
            "Sit and place thighs under the pad.",
            "Pull the bar to your upper chest, leading with your elbows.",
            "Return the bar slowly until arms are fully extended.",
        ],
        benefits=["Safe lat development", "Load adjustable", "Good pull-up progression"],
        muscles_worked=["back", "biceps", "rear shoulders"],
        equipment_needed=[Equipment.machine],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not pull behind the neck", "Avoid swinging excessively"],
    ),

    # ── LEGS ───────────────────────────────────────────────────────────────────

    Exercise(
        name="Bodyweight Squat",
        description="Fundamental lower-body movement pattern targeting quads, glutes, and hamstrings.",
        instructions=[
            "Stand with feet shoulder-width apart, toes slightly out.",
            "Push hips back and bend knees until thighs are parallel to the floor.",
            "Drive through your heels to stand back up.",
            "Keep chest up and knees tracking over toes throughout.",
        ],
        benefits=["Builds leg and glute strength", "Improves mobility", "No equipment"],
        muscles_worked=["quadriceps", "glutes", "hamstrings", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not let knees cave inward", "Keep heels on the floor"],
    ),

    Exercise(
        name="Goblet Squat",
        description="Squat variation holding a dumbbell at chest height for improved posture and depth.",
        instructions=[
            "Hold a dumbbell vertically at chest height.",
            "Squat deep while keeping the dumbbell close to your body.",
            "Press knees out and maintain an upright torso.",
            "Stand back up fully.",
        ],
        benefits=["Teaches squat mechanics", "Glute and quad development", "Core engagement"],
        muscles_worked=["quadriceps", "glutes", "core"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep torso upright", "Do not round lower back"],
    ),

    Exercise(
        name="Barbell Back Squat",
        description="The foundational compound strength movement for overall lower body development.",
        instructions=[
            "Position the bar on your upper traps and grip slightly wider than shoulder width.",
            "Unrack and step back, feet shoulder-width, toes slightly out.",
            "Descend until thighs are at or below parallel.",
            "Drive back up through your heels.",
        ],
        benefits=["Maximum leg and glute strength", "Systemic hypertrophy", "Athletic base builder"],
        muscles_worked=["quadriceps", "glutes", "hamstrings", "core", "back"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Use a spotter or safety bars", "Warm up thoroughly", "Do not round the lower back"],
    ),

    Exercise(
        name="Romanian Deadlift (Dumbbell)",
        description="Hip-hinge movement targeting the posterior chain — hamstrings, glutes, and lower back.",
        instructions=[
            "Hold dumbbells in front of your thighs, feet hip-width.",
            "Hinge at the hips, pushing them back as the dumbbells slide down your legs.",
            "Feel a hamstring stretch, then drive hips forward to stand.",
            "Keep the weights close to your body the whole way.",
        ],
        benefits=["Hamstring and glute development", "Improves hip-hinge mechanics", "Lower back strength"],
        muscles_worked=["hamstrings", "glutes", "lower back"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep a neutral spine at all times", "Do not round lower back"],
    ),

    Exercise(
        name="Barbell Deadlift",
        description="Total-body strength exercise — one of the most effective compound movements in existence.",
        instructions=[
            "Stand with mid-foot under bar, feet hip-width.",
            "Hinge to grip the bar just outside your legs.",
            "Flatten your back, brace your core, and pull by pushing the floor away.",
            "Lock out hips and knees at the top. Lower with control.",
        ],
        benefits=["Whole posterior chain strength", "Highest systemic stimulus of any lift", "Grip strength"],
        muscles_worked=["hamstrings", "glutes", "back", "core", "quadriceps"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Never round lower back under load", "Start light and progress slowly"],
    ),

    Exercise(
        name="Reverse Lunge",
        description="Single-leg exercise that builds quad and glute strength with less knee stress than forward lunges.",
        instructions=[
            "Stand tall, step one foot back and lower until rear knee hovers above the floor.",
            "Keep front shin vertical and chest upright.",
            "Push through the front heel to return to standing.",
            "Alternate legs.",
        ],
        benefits=["Balance and coordination", "Single-leg strength", "Less knee stress than forward lunge"],
        muscles_worked=["quadriceps", "glutes", "hamstrings"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep front knee behind toes", "Control the descent"],
    ),

    Exercise(
        name="Dumbbell Walking Lunge",
        description="Dynamic lunge variation that adds locomotion and functional challenge.",
        instructions=[
            "Hold a dumbbell in each hand.",
            "Step forward into a lunge, lower rear knee toward the floor.",
            "Drive off the rear foot to bring it forward for the next step.",
            "Continue for the prescribed reps/distance.",
        ],
        benefits=["Quad and glute strength", "Improves gait and balance", "Metabolic challenge"],
        muscles_worked=["quadriceps", "glutes", "hamstrings", "core"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep torso upright", "Control each step"],
    ),

    Exercise(
        name="Glute Bridge",
        description="Floor-based hip extension that isolates and activates the glutes without spinal load.",
        instructions=[
            "Lie on your back, knees bent, feet flat and hip-width.",
            "Drive through heels to lift hips until body forms a straight line from knees to shoulders.",
            "Squeeze glutes hard at the top for 1 second.",
            "Lower slowly.",
        ],
        benefits=["Glute activation and strength", "Safe for lower back issues", "Improves hip extension"],
        muscles_worked=["glutes", "hamstrings", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not hyperextend the lower back at the top"],
    ),

    Exercise(
        name="Bulgarian Split Squat",
        description="Advanced single-leg squat with rear foot elevated — intense quad and glute builder.",
        instructions=[
            "Place rear foot on a bench behind you, front foot about a stride ahead.",
            "Sink the rear knee toward the floor while keeping the front shin vertical.",
            "Drive through the front heel to return to the start.",
        ],
        benefits=["Even stronger glute and quad stimulus than back squat", "Addresses imbalances", "Athletic"],
        muscles_worked=["quadriceps", "glutes", "hamstrings"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Requires good hip flexor flexibility", "Start without weight"],
    ),

    Exercise(
        name="Calf Raise",
        description="Isolation exercise for the gastrocnemius and soleus muscles.",
        instructions=[
            "Stand on a step or flat floor.",
            "Rise onto your toes as high as possible.",
            "Hold for 1 second at the top, then lower slowly.",
        ],
        benefits=["Calf strength and size", "Ankle stability", "Minimal equipment needed"],
        muscles_worked=["calves"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Use a wall for balance if needed"],
    ),

    # ── SHOULDERS ──────────────────────────────────────────────────────────────

    Exercise(
        name="Pike Push-Up",
        description="Bodyweight overhead pressing movement that targets the shoulders.",
        instructions=[
            "Start in a downward-dog position — hips high, body forming an inverted V.",
            "Bend elbows to lower your head toward the floor.",
            "Press back up into the starting position.",
        ],
        benefits=["Shoulder and tricep strength", "No equipment", "Handstand push-up progression"],
        muscles_worked=["shoulders", "triceps", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep core braced throughout", "Avoid neck strain"],
    ),

    Exercise(
        name="Dumbbell Overhead Press",
        description="Standing or seated bilateral pressing for shoulder mass and overhead strength.",
        instructions=[
            "Hold dumbbells at shoulder height, palms forward.",
            "Press straight up until arms are fully extended overhead.",
            "Lower slowly to shoulder level.",
        ],
        benefits=["Shoulder mass and strength", "Tricep involvement", "Core stability"],
        muscles_worked=["shoulders", "triceps", "core"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not flare lower back", "Keep core tight when standing"],
    ),

    Exercise(
        name="Dumbbell Lateral Raise",
        description="Isolation exercise for the medial deltoid — the key muscle for shoulder width.",
        instructions=[
            "Hold dumbbells at your sides, slight bend in elbows.",
            "Raise arms out to shoulder height, leading with the elbows.",
            "Lower slowly over 3 seconds.",
        ],
        benefits=["Shoulder width", "Medial delt isolation", "Aesthetic shoulder development"],
        muscles_worked=["shoulders"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Use light weight", "Do not shrug at the top"],
    ),

    Exercise(
        name="Barbell Overhead Press",
        description="Foundational compound pressing exercise for overhead strength and size.",
        instructions=[
            "Hold bar at shoulder-width, just above your collarbones.",
            "Press the bar directly overhead until arms lock out.",
            "Lower with control to the starting position.",
        ],
        benefits=["Maximum shoulder and tricep strength", "Pairs with bench press for balanced development"],
        muscles_worked=["shoulders", "triceps", "core"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Keep ribs down", "Do not hyperextend spine to press"],
    ),

    Exercise(
        name="Face Pull (Resistance Band)",
        description="Rear delt and rotator-cuff exercise using a band — essential for shoulder health.",
        instructions=[
            "Attach a band to a door at face height.",
            "Pull the band toward your face, separating your hands at the end range.",
            "Hold 1 second, then slowly return.",
        ],
        benefits=["Rear delt and rotator cuff", "Counteracts pressing imbalances", "Shoulder health"],
        muscles_worked=["rear shoulders", "upper back"],
        equipment_needed=[Equipment.resistance_band],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not use excessive weight/band tension"],
    ),

    # ── BICEPS ─────────────────────────────────────────────────────────────────

    Exercise(
        name="Dumbbell Bicep Curl",
        description="Classic bicep isolation exercise.",
        instructions=[
            "Hold a dumbbell in each hand at your sides, palms forward.",
            "Curl both dumbbells to shoulder height by bending the elbows.",
            "Squeeze biceps at the top, then lower slowly over 2 seconds.",
        ],
        benefits=["Bicep peak and size", "Forearm strength", "Classic movement"],
        muscles_worked=["biceps", "forearms"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Avoid swinging", "Keep elbows pinned to your sides"],
    ),

    Exercise(
        name="Resistance Band Curl",
        description="Bicep curl using a resistance band — great for home training.",
        instructions=[
            "Stand on the middle of a band, hold one end in each hand.",
            "Curl up to shoulder height.",
            "Lower slowly.",
        ],
        benefits=["Adjustable resistance", "No dumbbell needed", "Bicep isolation"],
        muscles_worked=["biceps", "forearms"],
        equipment_needed=[Equipment.resistance_band],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Ensure band is secured underfoot"],
    ),

    Exercise(
        name="Hammer Curl",
        description="Neutral-grip curl variation that also develops the brachialis and forearms.",
        instructions=[
            "Hold dumbbells with a neutral grip (palms facing each other).",
            "Curl up without rotating your wrist.",
            "Lower slowly.",
        ],
        benefits=["Brachialis and bicep thickness", "Forearm strength", "Elbow-friendly"],
        muscles_worked=["biceps", "brachialis", "forearms"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep elbows stationary"],
    ),

    Exercise(
        name="Barbell Barbell Curl",
        description="Heavy bilateral curl for maximum bicep overload.",
        instructions=[
            "Hold a barbell with a supinated grip, shoulder-width.",
            "Curl the bar to shoulder height, squeezing at the top.",
            "Lower under control.",
        ],
        benefits=["Maximum bicep overload", "Strong grip engagement", "Classic mass builder"],
        muscles_worked=["biceps", "forearms"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Avoid swinging torso", "Keep wrists neutral"],
    ),

    # ── TRICEPS ────────────────────────────────────────────────────────────────

    Exercise(
        name="Tricep Dip (Bench)",
        description="Bodyweight tricep exercise using a bench or chair.",
        instructions=[
            "Place hands on a bench behind you, legs extended.",
            "Lower your body by bending the elbows to ~90 degrees.",
            "Press back up to full arm extension.",
        ],
        benefits=["Tricep mass", "No equipment except a surface", "Compound pressing carryover"],
        muscles_worked=["triceps", "shoulders", "chest"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep hips close to the bench", "Avoid shoulder pain — reduce range if needed"],
    ),

    Exercise(
        name="Overhead Tricep Extension (Dumbbell)",
        description="Long-head tricep isolation — the stretch position maximises hypertrophy.",
        instructions=[
            "Hold one dumbbell with both hands overhead.",
            "Lower the dumbbell behind your head by bending elbows.",
            "Press back up to full extension.",
        ],
        benefits=["Tricep long-head development", "Elbow lockout strength", "Good EMG activation"],
        muscles_worked=["triceps"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Keep elbows pointing forward", "Avoid hitting the back of your head"],
    ),

    Exercise(
        name="Resistance Band Tricep Pushdown",
        description="Cable-style tricep isolation performed with a resistance band.",
        instructions=[
            "Attach a band overhead (door or bar).",
            "Hold the band with both hands, elbows locked to your sides.",
            "Push the band down until arms are fully extended.",
            "Return slowly.",
        ],
        benefits=["Tricep isolation", "Home-friendly", "Adjustable resistance"],
        muscles_worked=["triceps"],
        equipment_needed=[Equipment.resistance_band],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep elbows stationary throughout"],
    ),

    Exercise(
        name="Close-Grip Bench Press",
        description="Barbell bench press with a narrow grip to shift emphasis onto the triceps.",
        instructions=[
            "Lie on bench, grip bar just inside shoulder-width.",
            "Lower bar to lower chest with elbows close to your body.",
            "Press back up to lockout.",
        ],
        benefits=["Tricep mass and strength", "Bench press carryover", "Heavy overload possible"],
        muscles_worked=["triceps", "chest", "shoulders"],
        equipment_needed=[Equipment.barbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Do not let elbows flare out", "Use a spotter"],
    ),

    # ── CORE ───────────────────────────────────────────────────────────────────

    Exercise(
        name="Plank",
        description="Isometric core stability exercise targeting the entire anterior core.",
        instructions=[
            "Start in a forearm plank — elbows under shoulders, body in a straight line.",
            "Squeeze your glutes and brace your core.",
            "Hold the position for the prescribed time."
        ],
        benefits=["Full core activation", "Safe for lower back", "No equipment"],
        muscles_worked=["core", "glutes", "shoulders"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not let hips sag or rise", "Breathe normally"],
    ),

    Exercise(
        name="Dead Bug",
        description="Anti-extension core exercise that trains deep stabilisers safely.",
        instructions=[
            "Lie on your back, arms pointed to the ceiling, knees at 90 degrees.",
            "Brace your core and press lower back into the floor.",
            "Slowly lower one arm overhead while extending the opposite leg.",
            "Return and repeat on the other side.",
        ],
        benefits=["Deep core stability", "Lower-back safe", "Corrective exercise"],
        muscles_worked=["core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Never let the lower back arch away from the floor"],
    ),

    Exercise(
        name="Bicycle Crunch",
        description="Dynamic ab exercise incorporating rotation for oblique development.",
        instructions=[
            "Lie on your back, hands behind your head.",
            "Bring one knee to your chest while rotating the opposite elbow toward it.",
            "Alternate sides with a controlled cycling motion.",
        ],
        benefits=["Rectus abdominis and oblique development", "No equipment", "Metabolic burn"],
        muscles_worked=["core", "obliques"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Do not pull on the neck", "Control the movement; avoid rushing"],
    ),

    Exercise(
        name="Hanging Knee Raise",
        description="Hanging core exercise targeting lower abs.",
        instructions=[
            "Hang from a pull-up bar with a shoulder-width grip.",
            "Brace your core and raise your knees toward your chest.",
            "Lower slowly without swinging.",
        ],
        benefits=["Lower ab development", "Grip strength", "Functional core"],
        muscles_worked=["core", "hip flexors"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Do not swing — use controlled movement only"],
    ),

    Exercise(
        name="Ab Wheel Rollout",
        description="Advanced anti-extension core exercise with high difficulty.",
        instructions=[
            "Kneel with hands on the ab wheel directly below your shoulders.",
            "Roll forward until your body is nearly parallel to the floor.",
            "Brace hard and roll back.",
        ],
        benefits=["Extreme core activation", "Builds long-lever core strength", "Athletic carry-over"],
        muscles_worked=["core", "shoulders", "back"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.advanced,
        safety_warnings=["Do not let your hips sag", "Start with a short range of motion"],
    ),

    Exercise(
        name="Side Plank",
        description="Lateral core stability exercise targeting the obliques.",
        instructions=[
            "Lie on one side, prop yourself up on your forearm.",
            "Lift hips off the floor so your body is a straight line.",
            "Hold the prescribed time, then switch sides.",
        ],
        benefits=["Oblique strength", "Lateral core stability", "No equipment"],
        muscles_worked=["obliques", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep hips stacked", "Do not let them sag toward the floor"],
    ),

    # ── CARDIO / FULL BODY──────────────────────────────────────────────────────

    Exercise(
        name="Burpee",
        description="Full-body metabolic exercise combining a squat, push-up, and jump.",
        instructions=[
            "Squat down and place your hands on the floor.",
            "Jump or step feet back into a push-up position.",
            "Perform a push-up.",
            "Jump feet to your hands, then explode upward into a jump with arms overhead.",
        ],
        benefits=["Full body conditioning", "High calorie burn", "No equipment"],
        muscles_worked=["chest", "core", "quadriceps", "glutes", "shoulders"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["High impact — avoid with knee or ankle injuries", "Land softly"],
    ),

    Exercise(
        name="Mountain Climber",
        description="Dynamic plank variation that builds core strength and cardiovascular fitness simultaneously.",
        instructions=[
            "Start in a high plank.",
            "Drive one knee toward your chest, then quickly switch legs.",
            "Maintain a flat back and stable hips throughout.",
        ],
        benefits=["Core + cardio combination", "No equipment", "Calorie burn"],
        muscles_worked=["core", "shoulders", "quadriceps"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Keep hips level — do not bounce them up and down"],
    ),

    Exercise(
        name="Jump Squat",
        description="Plyometric squat that develops explosive leg power and burns calories.",
        instructions=[
            "Perform a bodyweight squat.",
            "At the bottom, explode upward as high as possible.",
            "Land softly with bent knees and immediately sink into the next rep.",
        ],
        benefits=["Explosive leg power", "High calorie burn", "Athletic development"],
        muscles_worked=["quadriceps", "glutes", "calves", "core"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Land with soft knees", "Avoid on hard floors without shoes"],
    ),

    Exercise(
        name="High Knees",
        description="Running-in-place cardio drill that elevates heart rate quickly.",
        instructions=[
            "Run in place driving knees as high as your waist.",
            "Pump opposite arm with each knee raise.",
            "Maintain a fast, controlled tempo.",
        ],
        benefits=["Cardiovascular conditioning", "Hip flexor strength", "Warm-up"],
        muscles_worked=["hip flexors", "core", "quadriceps", "calves"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Land on the balls of your feet", "Avoid in low-clearance spaces"],
    ),

    Exercise(
        name="Resistance Band Squat",
        description="Squat with a band around the knees or held at shoulder height for added resistance.",
        instructions=[
            "Stand on a resistance band, hold the handles at shoulder height.",
            "Squat to parallel depth.",
            "Drive through your heels to stand.",
        ],
        benefits=["Leg and glute development", "Band provides variable resistance", "Home-friendly"],
        muscles_worked=["quadriceps", "glutes", "core"],
        equipment_needed=[Equipment.resistance_band],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Ensure band handles are secure", "Keep knees tracking over toes"],
    ),

    Exercise(
        name="Dumbbell Romanian Deadlift",
        description="Hip hinge hamstring and glute developer using dumbbells.",
        instructions=[
            "Hold dumbbells in front of thighs.",
            "Hinge at the hip, pushing glutes back.",
            "Lower dumbbells down your legs until you feel a hamstring stretch.",
            "Drive hips forward to return to standing.",
        ],
        benefits=["Hamstring and glute focus", "Lower back strength", "Posterior chain"],
        muscles_worked=["hamstrings", "glutes", "lower back"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.intermediate,
        safety_warnings=["Flat back throughout", "Do not lock out knees hard"],
    ),

    Exercise(
        name="Step-Up",
        description="Functional unilateral lower body exercise using a bench or step.",
        instructions=[
            "Step one foot onto a bench or box.",
            "Drive through the elevated heel to bring your body up.",
            "Step down with control.",
            "Alternate legs.",
        ],
        benefits=["Single-leg strength", "Functional movement", "Glute activation"],
        muscles_worked=["quadriceps", "glutes", "hamstrings"],
        equipment_needed=[Equipment.bodyweight],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Use a stable surface", "Keep torso upright"],
    ),

    Exercise(
        name="Chest Supported Dumbbell Row",
        description="Pendlay-style row with chest supported to eliminate cheating and lower back strain.",
        instructions=[
            "Lie face-down on a 45-degree incline bench.",
            "Let dumbbells hang at arm's length.",
            "Row both dumbbells up to your sides, squeezing shoulder blades.",
            "Lower slowly.",
        ],
        benefits=["Pure back isolation", "Removes lower back from the equation", "Safe for back injuries"],
        muscles_worked=["back", "biceps", "rear shoulders"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Chest fully on the bench throughout"],
    ),

    Exercise(
        name="Cable Row",
        description="Machine-based horizontal pull for mid-back development.",
        instructions=[
            "Sit at the cable machine, feet on the platform.",
            "Pull the handle to your navel, squeezing shoulder blades together.",
            "Extend arms slowly under tension.",
        ],
        benefits=["Mid-back development", "Constant cable tension", "Safe for beginners"],
        muscles_worked=["back", "biceps", "rear shoulders"],
        equipment_needed=[Equipment.machine],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Control the return — do not let the stack crash"],
    ),

    Exercise(
        name="Reverse Flye",
        description="Rear delt isolation exercise for shoulder balance and posture.",
        instructions=[
            "Hinge at the hip ~45 degrees, holding dumbbells.",
            "Raise arms out to the side in a wide arc, leading with thumbs.",
            "Squeeze rear delts at the top and lower slowly.",
        ],
        benefits=["Rear delt development", "Posture correction", "Shoulder balance"],
        muscles_worked=["rear shoulders", "upper back"],
        equipment_needed=[Equipment.dumbbell],
        difficulty=ExperienceLevel.beginner,
        safety_warnings=["Use light weight", "Do not shrug at the top"],
    ),
]


# ── Public API ─────────────────────────────────────────────────────────────────

def get_default_exercises(
    goal: FitnessGoal,
    equipment: List[Equipment],
    experience_level: ExperienceLevel,
    injuries: List[Injury] | None = None,
    top_n: int = 25,
) -> List[Exercise]:
   
    from core.exercise_scorer import exercise_scorer
    from schemas.user import UserProfile, UserMetrics, StrengthMetrics
    from schemas.common import Gender

    injuries = injuries or []

    # ── Step 1: equipment filter ──────────────────────────────────────────────
    # Keep exercises whose required equipment is a subset of what the user has.
    # Always allow Equipment.bodyweight.
    equipment_set = set(equipment) | {Equipment.bodyweight}
    equipment_filtered = [
        ex for ex in _LIBRARY
        if all(eq in equipment_set for eq in ex.equipment_needed)
    ]

    # ── Step 2: injury filter (keyword-based, same logic as SafetyFilterEngine)
    if injuries:
        injury_values = {inj.value for inj in injuries}
        equipment_filtered = [
            ex for ex in equipment_filtered
            if not any(
                muscle.lower().strip() in injury_values
                for muscle in ex.muscles_worked
            )
        ]

    if not equipment_filtered:
        # Ultimate fallback — return bodyweight exercises only
        equipment_filtered = [
            ex for ex in _LIBRARY if ex.equipment_needed == [Equipment.bodyweight]
        ]

    # ── Step 3: score using ExerciseScorer ────────────────────────────────────
    # Build a minimal UserProfile for the scorer (biometrics are not needed
    # by the scoring factors; only experience_level, equipment, and goal are).
    proxy_profile = UserProfile(
        biometrics=UserMetrics(age=25, weight_kg=70, height_cm=175, gender=Gender.male),
        metrics=StrengthMetrics(pushup_count=10, situp_count=10, squat_count=15),
        experience_level=experience_level,
        equipment=list(equipment),
        fitness_goal=goal,
    )

    scored = exercise_scorer.score_and_rank(equipment_filtered, proxy_profile, top_n=top_n)
    return [se.exercise for se in scored]
