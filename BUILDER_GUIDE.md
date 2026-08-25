# FitGen AI — Builder Manual

> This guide is for developers who want to run, modify, or extend FitGen AI.
> Covers Ollama setup, model selection, local development, and architecture decisions.

---

## Table of Contents

- [How It Works Under the Hood](#how-it-works-under-the-hood)
- [Ollama Setup](#ollama-setup)
  - [Install Ollama](#1-install-ollama)
  - [Choose a Model](#2-choose-a-model)
  - [Pull and Test](#3-pull-and-test)
  - [How FitGen Uses Ollama](#4-how-fitgen-uses-ollama)
  - [Switching Models](#5-switching-models)
  - [Prompt Engineering Tips](#6-prompt-engineering-tips)
- [Local Development](#local-development)
  - [Environment Setup](#environment-setup)
  - [Running Services](#running-services)
  - [Import Convention](#import-convention-critical)
  - [Adding a New Endpoint](#adding-a-new-endpoint)
  - [Adding a New Core Module](#adding-a-new-core-module)
- [Key Architecture Decisions](#key-architecture-decisions)
- [Known Gotchas](#known-gotchas)

---

## How It Works Under the Hood

```
User submits form
       │
       ▼
POST /api/v1/plans/generate
       │  validates via Pydantic GeneratePlanRequest
       │  dispatches generate_plan_task.delay()
       ▼
Redis (job queue)
       │
       ▼
Celery Worker — workers/tasks.py
       │
       ├── [Mode B/C] YouTubeService.fetch_transcripts()
       │       └── youtube-transcript-api → raw transcript text
       │
       ├── [Mode B/C] OllamaClient.extract_exercises()
       │       └── POST http://localhost:11434/api/generate
       │           prompt: "Extract exercises from this transcript..."
       │           returns: ExerciseLibrary (JSON)
       │
       ├── [Mode C] VisionAnalyzer.analyze()
       │       └── MediaPipe Pose → landmarks → SWR, fat%, muscle level
       │
       ├── Orchestrator.build_plan()
       │       ├── tdee.py       → BMR, TDEE, calorie target
       │       ├── protein.py    → macro targets
       │       ├── capacity.py   → intensity score
       │       ├── safety.py     → remove injury/equipment conflicts
       │       ├── exercise_scorer.py → 5-factor scoring
       │       ├── scheduler.py  → weekly split
       │       ├── progression.py → 4-week overload
       │       └── meal_selector.py → 7-day diet
       │
       ├── PDFArchitect.render()
       │       └── ReportLab → 7-section PDF → /tmp/plans/{job_id}.pdf
       │
       └── DB.save_plan() → SQLite
```

---

## Ollama Setup

### 1. Install Ollama

**Windows:** Download from https://ollama.com — installs as a tray app.
Launch it from the system tray. It runs on `http://localhost:11434`.

> ⚠️ Never run `ollama serve` manually on Windows — the tray app already serves it.
> Running both causes a port conflict.

**Mac:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
# Should return JSON with list of installed models
```

---

### 2. Choose a Model

FitGen works with any Ollama model. Recommended options:

| Model | Size | RAM Needed | CPU Speed | Quality |
|---|---|---|---|---|
| `gemma3:1b` | ~800 MB | 4 GB | Very fast | Basic — good for testing |
| `gemma3:4b` | ~2.5 GB | 8 GB | Fast | **Recommended — best balance** |
| `gemma3:12b` | ~7 GB | 16 GB | Slow on CPU | High quality, needs good hardware |
| `mistral:7b` | ~4 GB | 8 GB | Moderate | Good alternative |
| `llama3.2:3b` | ~2 GB | 6 GB | Fast | Lightweight alternative |
| `phi3:mini` | ~2 GB | 4 GB | Very fast | Smallest option |

**Rule of thumb:**
- 8 GB RAM → `gemma3:4b`
- 16 GB RAM → `gemma3:12b` for higher quality plans
- CPU only → stay at 4b or smaller

---

### 3. Pull and Test

```bash
# Pull the model
ollama pull gemma3:4b

# Test it works
ollama run gemma3:4b "Say hello in one sentence"

# List installed models
ollama list

# Check what's currently running
ollama ps
```

Test the API directly — same call FitGen makes:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:4b",
  "prompt": "List 3 chest exercises in JSON format with name and sets fields.",
  "stream": false
}'
```

---

### 4. How FitGen Uses Ollama

FitGen makes two Ollama calls per plan generation (Mode B/C only):

**Call 1 — Exercise extraction**
```
File: src/integrations/ollama_client.py

Prompt:
  "You are a fitness expert. Extract all exercises from this transcript.
   Return ONLY valid JSON: { exercises: [...] }
   Transcript: {transcript_text}"

Output: ExerciseLibrary fed into exercise_scorer.py
```

**Call 2 — Diet guidance extraction**
```
Prompt:
  "Extract nutrition and meal advice from this transcript.
   Return ONLY valid JSON with meal recommendations."

Output: Seeds the meal_selector.py with video-sourced diet advice
```

Both calls use `stream: false` and expect raw JSON back.
The client strips markdown fences before parsing.

---

### 5. Switching Models

Change in `.env`:
```env
OLLAMA_MODEL=gemma3:4b
```

Or override temporarily at startup:
```bash
OLLAMA_MODEL=mistral:7b uvicorn main:app --reload --port 8000 --reload-dir src
```

After switching, test with a short YouTube URL first to confirm the model returns parseable JSON.

---

### 6. Prompt Engineering Tips

If a model returns bad JSON or misses exercises, tune prompts in
`src/integrations/ollama_client.py`:

```python
# Be explicit — works better across all models
prompt = f"""You are a fitness data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract exercises from this text:
{transcript[:3000]}

Required format:
{{
  "exercises": [
    {{"name": "Push-Up", "sets": 3, "reps": 10, "muscle_group": "chest"}}
  ]
}}

JSON only:"""
```

**If the model is slow:**
- Truncate transcripts: `transcript[:3000]` is usually enough
- Reduce `max_tokens` in the Ollama call
- Switch to `gemma3:1b` for faster iteration during development

---

## Local Development

### Environment Setup

```cmd
cd "D:\path\to\koda"
py -3.11 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.lock.txt
pip install -e . --no-deps
```

The first command installs exact, hash-pinned dependency versions from `requirements.lock.txt` — reproducible across machines instead of whatever's newest on PyPI on install day. The second (see `pyproject.toml`) registers the `src/` packages for import from anywhere without re-resolving against `requirements.txt`'s loose ranges. This is a one-time step per venv — no `PYTHONPATH` needed afterward, on any shell, from any working directory.

Adding or bumping a dependency: edit `requirements.txt`, then regenerate the lock with `uv pip compile requirements.txt --python-version 3.11 --generate-hashes -o requirements.lock.txt` (requires [uv](https://github.com/astral-sh/uv)), then `pip install -r requirements.lock.txt`. Commit both files together.

Verify MediaPipe:
```cmd
python -c "import mediapipe as mp; print(mp.__version__)"
# Must print: 0.10.9

python -c "
import mediapipe as mp
pose = mp.solutions.pose.Pose(static_image_mode=True)
print('MediaPipe OK')
"
```

---

### Running Services

Each in its own terminal with venv activated:

```cmd
# Terminal 1 — Celery worker
python -m celery -A workers.celery_app worker --loglevel=info --pool=solo

# Terminal 2 — FastAPI
uvicorn main:app --reload --port 8000 --reload-dir src

# Terminal 3 — Frontend
cd frontend && npm run dev
```

Or double-click `start.bat`.

Verify all services:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/redis
curl http://localhost:8000/health/celery
curl http://localhost:8000/health/db
```

All should return `{"status": "ok"}`.

---

### Import Convention

`src/` is registered as an installable package (`pyproject.toml`, `pip install -e .`), so every top-level directory under it (`db`, `core`, `schemas`, `api`, `workers`, ...) is importable by its bare name from anywhere — no `PYTHONPATH`, no `src.` prefix, no dependence on your current working directory or how you launched the process:

```python
# ✅ Correct — works everywhere, always
from core.orchestrator import build_plan
from config.settings import settings
from db.session import get_db
from workers.celery_app import celery_app

# ❌ Wrong — the src/ directory is not itself a package
from src.core.orchestrator import build_plan
```

`main.py` and `exceptions.py` are registered the same way (`py-modules` in `pyproject.toml`), so `main:app` resolves directly too — no `src.main:app`.

Celery invocation:
```cmd
python -m celery -A workers.celery_app worker ...
```

Uvicorn:
```cmd
uvicorn main:app ...
```

If you add a new top-level directory under `src/`, give it an `__init__.py` (regular package, matching every other directory here) so `pip install -e .`'s package discovery (`tool.setuptools.packages.find`, `where = ["src"]`) picks it up — otherwise it silently won't be importable outside `src/` itself.

---

### Adding a New Endpoint

1. Create `src/api/v1/endpoints/yourmodule.py`
2. Register in `src/api/v1/api.py`:
```python
from api.v1.endpoints import yourmodule
api_router.include_router(yourmodule.router, prefix="/yourmodule", tags=["yourmodule"])
```
3. Add schemas in `src/schemas/`
4. Test: `curl http://localhost:8000/api/v1/yourmodule/yourpath`

---

### Adding a New Core Module

1. Create `src/core/yourmodule.py`
2. Import in `src/core/orchestrator.py` where it fits
3. Add fields to `src/schemas/plan.py` if needed
4. Update `src/reporting/pdf_architect.py` if it affects the PDF

---

## Key Architecture Decisions

| Decision | Reason |
|---|---|
| Celery + Redis over FastAPI BackgroundTasks | Plan generation takes 2–6 min. BackgroundTasks ties up the worker. Celery is isolated. |
| SQLite over PostgreSQL | Local-first, single user. Zero config. PostgreSQL planned for multi-user. |
| Ollama over OpenAI | Zero API costs, offline after setup, no data leaving the machine. |
| MediaPipe 0.10.9 pinned | 0.10.14+ removed `mp.solutions` API. 0.10.9 is the last stable version with it. |
| `protobuf>=3.11,<4` pinned | MediaPipe 0.10.9 incompatible with protobuf 4.x. Must be pinned. |
| `static_image_mode=True` | We process single photos not video. Static mode re-initialises per image — correct for this use case. |
| `pip install -e .` (`pyproject.toml`) | Registers `src/`'s packages for import from anywhere, without `PYTHONPATH` or a `src.` prefix, regardless of launch method. |
| `--pool=solo` for Celery | Windows doesn't support the default `prefork` pool. Solo runs single-threaded — fine for local use. |

---

## Known Gotchas

| Gotcha | Fix |
|---|---|
| `mediapipe has no attribute 'solutions'` | Wrong version. Run: `pip install mediapipe==0.10.9 "protobuf>=3.11,<4"` |
| `Cannot import runtime_version from google.protobuf` | TensorFlow/protobuf conflict. Uninstall tensorflow, reinstall mediapipe==0.10.9 |
| Celery not picking up jobs | Check `redis-cli ping` returns PONG. Check `pip show fitgen-koda` succeeds in the active venv (i.e. `pip install -e .` was run). |
| `422 Field required` on vision endpoint | Axios default `Content-Type: application/json` breaks multipart. Use bare `axios.post()` not the api instance for file uploads. |
| Ollama times out | Model too large for RAM. Switch to smaller model in `.env`. |
| PDF encoding issues (`â€"` instead of `—`) | Use unicode directly in ReportLab strings: `\u2014` |
| `ModuleNotFoundError` for `db`/`core`/etc. | `pip install -e .` hasn't been run in this venv. Run it once — no PYTHONPATH workaround needed afterward, on any shell. |
| Ollama port conflict on Windows | Don't run `ollama serve` — tray app already serves it. Kill duplicate in Task Manager. |
