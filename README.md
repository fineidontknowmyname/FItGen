# FitGen AI

> **AI-powered personalised fitness plan generator — runs entirely on your machine.**
> Paste YouTube fitness videos, optionally upload body photos, and receive a structured
> 4-week progressive workout plan + 7-day diet plan + transformation roadmap as a
> downloadable PDF. No cloud AI costs. No subscriptions. No data leaves your device.

---

## What It Does

You provide:
- Age, height, weight, fitness level, goals, equipment, injuries
- Hours of physical activity per day
- 0–5 YouTube links (workout videos, diet videos, exercise tutorials) — **optional**
- 3 body photos (front / side / back) for body composition analysis — **optional**

FitGen gives you:
- **4-week progressive workout plan** with individual exercises per day, sets, reps, rest times, and form cues
- **4-phase 13-week transformation roadmap** with per-phase goals and realistic outcome projections
- **7-day personalised diet plan** with TDEE-based calorie targets and macro breakdown
- **Body composition analysis** — estimated body fat %, muscle level, V-taper ratio, shoulder-to-waist ratio
- **Downloadable PDF** — 7 sections: Cover · Metrics · SWR · Diet · Roadmap · Timeline · Workout Guide

Everything runs locally via Ollama. No OpenAI. No Gemini. No internet required after setup.

---

## Three Operating Modes

| Mode | Input | What drives the plan |
|---|---|---|
| **A — Profile only** | Biometrics + goals | Built-in exercise + meal library |
| **B — Profile + YouTube** | Biometrics + 1–5 video URLs | LLM extracts exercises and meals from transcripts |
| **C — Profile + YouTube + Photos** | All of the above + 3 body photos | Full pipeline including body composition analysis |

All 3 modes produce a complete PDF. YouTube and photos are entirely optional.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI (async, Python 3.11) |
| LLM | Ollama — Gemma3:4b (local inference) |
| Vision — Pose | MediaPipe Pose 0.10.9 (landmark detection, SWR) |
| Vision — Body Comp | MobileNetV2 + TensorFlow (on-device) |
| Task Queue | Celery + Redis (async job processing) |
| Database | SQLAlchemy 2.0 + SQLite |
| PDF Export | ReportLab |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| YouTube | youtube-transcript-api (parallel fetch) |
| Validation | Pydantic v2 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                     │
│  Landing → Signup → Onboarding → Dashboard → Status    │
│  useJobStatus hook polls GET /api/v1/plans/job/{id}     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────┐
│                  FASTAPI BACKEND                          │
│  /api/v1/plans    /api/v1/users    /api/v1/vision       │
│  Lifespan: DB init + model preload + Ollama health check│
└──────┬───────────────────────────┬──────────────────────┘
       │ Celery dispatch           │ Direct call
       ▼                           ▼
┌─────────────┐        ┌──────────────────────────────────┐
│ Redis Broker│        │         CORE ENGINES              │
│ (job queue) │        │  orchestrator → bmi, tdee,       │
└──────┬──────┘        │  protein, capacity, scorer,      │
       ▼               │  scheduler, meal_selector,       │
┌─────────────┐        │  progression, safety             │
│   Celery    │        └──────────────────────────────────┘
│   Worker    │
│  tasks.py   │──→ Ollama (Gemma3:4b) — LLM inference
│             │──→ MediaPipe + MobileNetV2 — vision
│             │──→ YouTubeService — transcript fetch
│             │──→ pdf_architect — ReportLab PDF render
│             │──→ SQLAlchemy — persist plan to DB
└─────────────┘
```

---

## PDF Report — 7 Sections

| # | Section | Content |
|---|---|---|
| 1 | Cover | User name, generation date, goal summary |
| 2 | User Metrics | BMI, BMR, TDEE, calorie target, macros, ideal weight range, activity level |
| 3 | Body Composition | Fat % range, muscle level, V-taper ratio, SWR analysis with plan adjustment notes |
| 4 | Diet Plan | 7-day meal table with per-slot calorie targets (breakfast 25% / lunch 35% / dinner 30% / snack 10%) |
| 5 | Transformation Roadmap | 4-phase 13-week plan with per-phase goals, expected fat % change, strength milestones |
| 6 | Realistic Timeline | 3 weeks → 2 months → 4 months → 6 months → 1 year outcome projections |
| 7 | Workout Guide | Day-by-day exercise tables with sets/reps/rest + form cues |

---

## Formulas Used

| Calculation | Formula | File |
|---|---|---|
| BMR | Mifflin-St Jeor (gender-specific) | `core/tdee.py` |
| TDEE | BMR × PAL factor (6 activity levels) | `core/tdee.py` |
| Calorie target | max(1200, TDEE + goal_delta) | `core/tdee.py` |
| Protein | 1.6–2.2 g/kg scaled by capacity score | `core/protein.py` |
| BMI | weight_kg / height_m² | `core/bmi.py` |
| Ideal weight | Devine formula ± range | `core/bmi.py` |
| Body fat % | RFM formula (height / waist proxy) | `services/vision/body_composition.py` |
| SWR | shoulder_px / waist_px (MediaPipe landmarks 11,12,23,24) | `services/vision/landmarks.py` |
| Capacity score | Strength + activity + BMI + muscle + SWR bonuses | `core/capacity.py` |
| Progressive overload | reps × (1 + week × 0.05 × capacity) | `core/progression.py` |

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | **3.11.x** (not 3.12+) | Backend runtime — MediaPipe 0.10.9 requires 3.11 |
| Node.js | 18+ | Frontend runtime |
| Ollama | Latest | Local LLM server (run as tray app on Windows) |
| Redis | 3.x+ | Celery message broker |

> ⚠️ **Python 3.11 is required.** MediaPipe and TensorFlow do not support Python 3.12+.

> ⚠️ **Windows users:** Run Ollama as the desktop tray app. Never run `ollama serve` manually — it will conflict.

---

## Setup

### 1. Clone

```bash
git clone https://github.com/yourusername/fitgen.git
cd fitgen
```

### 2. Python 3.11 virtual environment

```bash
# Windows (CMD — not PowerShell)
py -3.11 -m venv venv
venv\Scripts\activate.bat

# Mac/Linux
python3.11 -m venv venv
source venv/bin/activate

# Verify
python --version   # must show Python 3.11.x
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ MediaPipe version matters. If you see import errors, pin exactly:
> ```bash
> pip install mediapipe==0.10.9 "protobuf>=3.11,<4"
> ```

### 4. Environment variables

```bash
copy .env.example .env     # Windows
cp .env.example .env       # Mac/Linux
```

Edit `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite+aiosqlite:///./fitgen.db
SECRET_KEY=change-this-to-a-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Pull Ollama model

Install Ollama from https://ollama.com, launch it, then:

```bash
ollama pull gemma3:4b
```

| Model | Size | CPU Speed |
|---|---|---|
| gemma3:1b | ~800 MB | Fastest |
| gemma3:4b | ~2.5 GB | **Recommended** |
| gemma3:12b | ~7 GB | Slow on CPU-only |

### 6. Install Redis

**Windows** — download and run the MSI installer:
```
https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi
```
Redis runs as a Windows service automatically after install.

**Mac:**
```bash
brew install redis && brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server && sudo systemctl start redis
```

Verify:
```bash
redis-cli ping   # → PONG
```

### 7. Frontend setup

```bash
cd frontend
npm install
cd ..
```

---

## Running the App

> ⚠️ **Windows users: use CMD, not PowerShell.** PYTHONPATH must be set before starting Celery and uvicorn.

### Quick start (Windows)

Double-click `start.bat` in the project root. It opens all required terminals and launches the browser automatically.

To stop everything: double-click `stop.bat`.

### Manual start

Open **3 terminals** from the project root, all in CMD with venv activated:

```cmd
venv\Scripts\activate.bat
set PYTHONPATH=src
```

**Terminal 1 — Celery worker:**
```cmd
python -m celery -A workers.celery_app worker --loglevel=info --pool=solo
```

**Terminal 2 — FastAPI backend:**
```cmd
uvicorn src.main:app --reload --port 8000 --reload-dir src
```

**Terminal 3 — Frontend:**
```cmd
cd frontend && npm run dev
```

Open: **http://localhost:3000**

---

## API Reference

### Plans

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/plans/generate` | Submit plan job → `202 { job_id, status }` |
| GET | `/api/v1/plans/job/{id}` | Poll job status → `{ status, result? }` |
| GET | `/api/v1/plans/job/{id}/pdf` | Download completed PDF |

### Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/users/` | Create user profile |
| GET | `/api/v1/users/me` | Get current user |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PUT | `/api/v1/users/{id}` | Replace user profile |
| DELETE | `/api/v1/users/{id}` | Delete user |

### Vision

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/vision/analyze-body` | Upload 1–3 photos → `BodyComposition` |

Required header: `X-Vision-Consent: true`

Body: `multipart/form-data` with fields: `front` (required), `side`, `back`, `user_height_cm`, `gender`, `consent`

### System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/health/redis` | Redis connectivity |
| GET | `/health/celery` | Celery worker status |
| GET | `/health/db` | Database connectivity |

---

## Plan Generation Flow

```
1. POST /api/v1/plans/generate
   → validates GeneratePlanRequest (Pydantic)
   → dispatches generate_plan_task.delay() to Celery via Redis
   → returns { job_id, status: "pending" } in ~200ms

2. Celery worker picks up the job:
   → detects Mode A / B / C from request
   → Mode B/C: fetches YouTube transcripts in parallel
   → Mode B/C: Ollama classifies videos (workout/diet/motivation)
   → Mode B/C: Ollama extracts ExerciseLibrary + diet guidance
   → Mode A:   loads default exercise + meal library
   → computes BodyMetrics (BMI, TDEE, macros, protein)
   → runs safety filter (injuries + equipment)
   → scores + selects exercises (5-factor scoring)
   → builds weekly split schedule (Upper/Lower or Full Body)
   → applies 4-week progressive overload
   → builds 4-phase transformation roadmap
   → renders 7-section PDF via ReportLab
   → persists to SQLite, marks job SUCCESS

3. GET /api/v1/plans/job/{id}
   → reads AsyncResult from Redis
   → returns status: pending → running → done

4. GET /api/v1/plans/job/{id}/pdf
   → streams PDF bytes to browser
```

---

## Body Composition Analysis

```
POST /api/v1/vision/analyze-body
Headers: X-Vision-Consent: true
Body: multipart/form-data
  front:          <image file>   ← required
  side:           <image file>   ← optional
  back:           <image file>   ← optional
  user_height_cm: 175
  gender:         male
  consent:        true
```

**What it measures:**

- **Body fat %** — RFM formula using MediaPipe landmarks → returned as `fat_pct_low` / `fat_pct_high` range
- **Muscle level** — MobileNetV2 feature magnitude heuristic (Low / Moderate / High / Very High)
- **V-taper ratio** — shoulder_cm / hip_cm
- **Shoulder-to-waist ratio (SWR)** — landmarks 11,12 vs 23,24
  - SWR > 1.2 → Athletic — plan intensity +10%
  - SWR 1.0–1.2 → Balanced — standard plan
  - SWR < 1.0 → Overfat — extra cardio day injected

**Photo tips for best results:**
- Stand against a plain background
- Good even lighting, no shadows
- Full body visible head to toe
- Minimal clothing (shorts only)
- Front: face the camera directly
- Side: stand perpendicular, arms relaxed
- Back: stand straight, arms at sides

---

## Exercise Scoring — 5 Factors

| Factor | Weight | Logic |
|---|---|---|
| Goal match | 35% | Does exercise align with user's primary goal? |
| Equipment | 25% | Is required equipment in user's available list? |
| Difficulty | 20% | Is difficulty within user's experience level ± 1? |
| Muscle balance | 15% | Does the week need this muscle group? |
| Data quality | 5% | Does exercise have form cues attached? |

Hard disqualifiers: targets injured muscle group OR requires unavailable equipment → score = 0.

---

## Transformation Roadmap — 4 Phases

| Phase | Weeks | Focus | Progression |
|---|---|---|---|
| 1 — Foundation | 1–4 | Learn movement patterns | +1 rep/exercise/week |
| 2 — Development | 5–8 | Progressive overload | +1 set on compounds, add accessory |
| 3 — Intensification | 9–12 | Peak conditioning | Drop sets, 2nd cardio day |
| 4 — Deload | 13 | Recovery | −40% weight, same structure |

---

## Known Limitations

| Issue | Status |
|---|---|
| No real JWT auth — session is localStorage-based | Planned |
| MobileNetV2 uses ImageNet weights as muscle proxy | Needs fine-tuned model at `models/body_composition.keras` |
| No in-app plan viewer — PDF download only | Planned |
| Protein target computed in two places (protein.py + orchestrator.py) | Low priority drift risk |
| Windows only tested — Mac/Linux untested | Community contributions welcome |

---

## Project Structure

```
fitgen/
├── start.bat                      # One-click Windows startup
├── stop.bat                       # One-click Windows shutdown
├── src/
│   ├── main.py                    # FastAPI app + lifespan manager
│   ├── api/v1/endpoints/
│   │   ├── plans.py               # Async job dispatch + polling
│   │   ├── users.py               # User CRUD
│   │   ├── vision.py              # Body composition upload
│   │   └── health.py              # Health check endpoints
│   ├── core/
│   │   ├── orchestrator.py        # Pipeline coordinator (Mode A/B/C)
│   │   ├── capacity.py            # Intensity score (0.5–1.5)
│   │   ├── exercise_scorer.py     # 5-factor cherry-picking
│   │   ├── scheduler.py           # Weekly split builder
│   │   ├── meal_selector.py       # 7-day diet plan
│   │   ├── progression.py         # 4-week overload
│   │   ├── safety.py              # Injury + equipment filter
│   │   ├── tdee.py                # BMR + TDEE + calorie target
│   │   ├── protein.py             # Protein + macro targets
│   │   └── bmi.py                 # BMI + Devine ideal weight
│   ├── db/                        # SQLAlchemy ORM layer
│   ├── integrations/
│   │   └── ollama_client.py       # Ollama REST client
│   ├── services/
│   │   ├── intelligence/          # YouTube + transcripts + summarizer
│   │   └── vision/                # MediaPipe + MobileNetV2
│   ├── reporting/pdf_architect.py # 7-section ReportLab PDF
│   └── workers/                   # Celery app + tasks
└── frontend/
    └── src/
        ├── app/                   # Next.js pages
        ├── components/            # ServiceStatus, JobStatusPoller, UI
        ├── hooks/useJobStatus.ts  # 3s polling hook
        └── lib/api.ts             # Typed axios API client
```

---

## Roadmap

- [ ] JWT authentication + bcrypt password hashing
- [ ] Train MobileNetV2 body composition classifier on real dataset
- [ ] In-app plan viewer (currently PDF-only)
- [ ] Docker + docker-compose for one-command setup
- [ ] PATCH endpoint for partial profile updates
- [ ] Rate limiting on plan generation
- [ ] Celery Flower monitoring dashboard
- [ ] Mac/Linux testing + CI

---

## License

MIT — Genesis Tech
