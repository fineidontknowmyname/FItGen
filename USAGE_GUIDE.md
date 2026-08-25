# FitGen AI — User Guide & AI Codebase Exploration

> This guide covers two things:
> 1. How to use FitGen AI as an end user
> 2. How to explore and understand the codebase using AI assistants (Claude, ChatGPT, Gemini)

---

## Table of Contents

- [Using FitGen AI](#using-fitgen-ai)
  - [Sign Up](#1-sign-up)
  - [Onboarding](#2-onboarding)
  - [Body Photos](#3-body-photos-optional)
  - [Generate Your Plan](#4-generate-your-plan)
  - [Status Page](#5-status-page)
  - [Your PDF](#6-your-pdf)
  - [Tips for Best Results](#tips-for-best-results)
- [Exploring the Codebase with AI](#exploring-the-codebase-with-ai)
  - [Project Context Prompt](#project-context-prompt)
  - [Prompts by Topic](#prompts-by-topic)

---

## Using FitGen AI

### 1. Sign Up

Create a local account. No email verification. No cloud. Your data lives only on your machine.

---

### 2. Onboarding

Fill in your profile:

| Field | Notes |
|---|---|
| Age, Height, Weight | Used for BMR, TDEE, BMI calculations |
| Gender | Affects Mifflin-St Jeor BMR formula |
| Fitness Goal | weight_loss / muscle_gain / endurance_gain / strength_gain / general_fitness |
| Fitness Level | beginner / intermediate / advanced |
| Equipment | bodyweight / dumbbells / barbell / resistance_bands / pull_up_bar / gym_full |
| Injuries | Muscle groups to avoid — safety filter removes those exercises automatically |
| Daily Activity | Hours of activity per day — affects TDEE activity multiplier |

---

### 3. Body Photos (Optional)

Upload up to 3 photos for body composition analysis:

- **Front** — required if using vision
- **Side** — improves accuracy
- **Back** — improves accuracy

**For best results:**
- Plain background, even lighting, no shadows
- Full body visible head to toe
- Shorts only — no baggy clothing
- Stand straight, arms relaxed at sides
- Camera at chest height — not above or below

**What gets returned:**
- Estimated body fat % range (`fat_pct_low` / `fat_pct_high`)
- V-taper ratio (shoulder width / hip width)
- Shoulder-to-waist ratio — Athletic / Balanced / Overfat
- Posture assessment
- Muscle level estimate — Low / Moderate / High / Very High

>>ProTip: Use AI tool to enhance your image and then, upload it to FitGen for better results.
> These are geometry-based estimates from MediaPipe landmarks, not clinical measurements.
> Use as directional guidance only.

---

### 4. Generate Your Plan

On the dashboard, optionally paste YouTube URLs split into:
- **Workout URLs** — exercise tutorials, workout videos
- **Diet URLs** — nutrition advice, meal prep videos

Any YouTube video with captions/auto-transcripts enabled will work.
FitGen fetches the transcript and extracts exercises and diet advice using a local LLM.

**Without YouTube URLs:** FitGen uses its built-in exercise and meal library — still produces a complete plan.

Click **Generate Plan** — you'll be redirected to the status page automatically.

---

### 5. Status Page

The job runs in the background. Page polls every 3 seconds.

| Status | Meaning |
|---|---|
| `pending` | Queued in Redis, worker not yet picked up |
| `running` | Fetching transcripts / calling Ollama / building plan |
| `done` | PDF ready to download |
| `failed` | Error — check the Celery terminal for details |

**Typical times:**
- Mode A (no YouTube): 1–2 min
- Mode B (YouTube only): 2–5 min
- Mode C (YouTube + photos): 3–6 min

---

### 6. Your PDF

7 sections in every generated plan:

| Section | Content |
|---|---|
| Cover | Name, date, goal, plan mode |
| Body Metrics | BMI, BMR, TDEE, calorie target, macros, ideal weight |
| Body Composition | Fat % range, V-taper, SWR category, muscle level |
| Diet Plan | 7-day meals with per-slot calorie targets |
| Transformation Roadmap | 4-phase 13-week plan with milestones |
| Realistic Timeline | 3 weeks → 6 months → 1 year projections |
| Workout Guide | Day-by-day exercises with sets, reps, rest, form cues |

---

### Tips for Best Results

- **YouTube tip:** Use videos with manual captions — auto-generated captions are noisier but still work
- **Goal tip:** Be specific — `muscle_gain` and `strength_gain` produce very different plans
- **Equipment tip:** Only list equipment you actually have — the safety filter is strict
- **Injury tip:** Always fill injuries — the filter removes exercises targeting those muscle groups
- **Photo tip:** Take photos before filling the form — analysis results feed into plan intensity

---

## Exploring the Codebase with AI

Use these prompts with Claude, ChatGPT, Gemini, or any AI assistant.
Always start with the **Project Context Prompt** before asking specific questions.

---

### Project Context Prompt

Paste this first in any new AI conversation about FitGen:

```
I'm working on a project called FitGen AI. Here is the full context:

FitGen is a local AI-powered fitness plan generator built with:
- FastAPI backend (Python 3.11) with async endpoints
- Celery + Redis for async job queue
- Ollama running Gemma3:4b locally for LLM inference (no OpenAI)
- MediaPipe 0.10.9 for body composition analysis from photos
- ReportLab for PDF generation
- Next.js 14 + TypeScript + Tailwind CSS frontend
- SQLAlchemy 2.0 + SQLite database
- Pydantic v2 for validation

`src/` is installed as an editable package (`pip install -e .`, see `pyproject.toml`), so all imports use bare module names from anywhere — no `PYTHONPATH` needed
(e.g. `from core.orchestrator import ...` not `from src.core.orchestrator import ...`).

The main flow is:
1. User submits profile + optional YouTube URLs + optional body photos
2. FastAPI dispatches a Celery task via Redis
3. Celery worker runs the full pipeline:
   - Fetches YouTube transcripts
   - Calls Ollama to extract exercises and diet advice
   - Computes biometrics (BMI, TDEE, macros, protein)
   - Runs safety filter (injuries + equipment)
   - Scores and selects exercises (5-factor scoring)
   - Builds 4-week progressive workout plan
   - Builds 7-day diet plan
   - Generates 7-section PDF via ReportLab
4. Frontend polls GET /api/v1/plans/job/{id} every 3 seconds
5. User downloads PDF when status is "done"

Three operating modes:
- Mode A: Profile only → uses built-in exercise/meal library
- Mode B: Profile + YouTube URLs → LLM extracts from transcripts
- Mode C: Profile + YouTube + Photos → full pipeline with vision

Key files:
- src/main.py — FastAPI app entry point
- src/core/orchestrator.py — pipeline coordinator
- src/workers/tasks.py — Celery task
- src/reporting/pdf_architect.py — PDF generation
- src/services/vision/ — MediaPipe body composition
- src/integrations/ollama_client.py — Ollama LLM calls
- frontend/src/lib/api.ts — typed API client
- frontend/src/app/onboarding/page.tsx — onboarding flow
- frontend/src/app/dashboard/page.tsx — plan generation UI

Now I have a question: [YOUR QUESTION HERE]
```

---

### Prompts by Topic

#### Understanding the overall architecture
```
Using the FitGen context above, explain how a plan generation request
flows from the moment the user clicks "Generate Plan" in the browser
all the way to the PDF being ready for download.
Walk through every layer — frontend, FastAPI, Redis, Celery, Ollama, PDF.
```

---

#### Understanding the vision pipeline
```
Using the FitGen context above, explain how the body composition analysis works.
Specifically:
- How does MediaPipe detect pose landmarks from a static photo?
- How is the shoulder-to-waist ratio (SWR) calculated from landmarks?
- How is body fat % estimated using the RFM formula?
- How do these results affect the generated workout plan?
Focus on these files: services/vision/landmarks.py, services/vision/body_composition.py,
services/vision/model_loader.py
```

---

#### Understanding exercise selection
```
Using the FitGen context above, explain the 5-factor exercise scoring system.
How does FitGen decide which exercises to include in the final plan?
What are the hard disqualifiers?
How does the capacity score affect exercise intensity?
Focus on: core/exercise_scorer.py, core/capacity.py, core/safety.py
```

---

#### Understanding nutrition calculations
```
Using the FitGen context above, walk me through how FitGen calculates:
1. BMR using Mifflin-St Jeor
2. TDEE from BMR and activity level
3. Calorie target adjustment based on goal
4. Protein target in grams
5. Full macro breakdown (protein / carbs / fats)
Focus on: core/tdee.py, core/protein.py, core/bmi.py
```

---

#### Understanding the PDF structure
```
Using the FitGen context above, explain how the PDF is generated.
What are the 7 sections and what data populates each one?
How does ReportLab render the tables and layout?
Focus on: reporting/pdf_architect.py
```

---

#### Understanding the Celery async flow
```
Using the FitGen context above, explain the async job system.
How does a plan generation job get dispatched, tracked, and completed?
What happens if Ollama is slow or a YouTube transcript fails to fetch?
Focus on: workers/celery_app.py, workers/tasks.py, api/v1/endpoints/plans.py
```

---

#### Debugging a specific error
```
Using the FitGen context above, I'm seeing this error:
[PASTE YOUR ERROR HERE]

The error occurs when [DESCRIBE WHAT YOU WERE DOING].
Which file is most likely responsible and what should I check?
```

---

#### Adding a new feature
```
Using the FitGen context above, I want to add [DESCRIBE FEATURE].
Which files would I need to modify?
What schema changes would be needed in src/schemas/?
Would this require a new Celery task or can it be added to the existing pipeline?
Give me a step-by-step implementation plan before writing any code.
```

---

#### Code review of a specific file
```
Using the FitGen context above, review this file for me:
[PASTE FILE CONTENTS]

Look for:
- Any `src.`-prefixed import (the package is installed via `pip install -e .`; bare imports only)
- Pydantic v2 compatibility issues
- Async/sync mismatches (FastAPI async endpoints calling sync functions)
- Any hardcoded values that should be in config/settings.py
```
