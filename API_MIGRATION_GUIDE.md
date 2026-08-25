# FitGen AI — Cloud API Migration Guide

> This guide walks you through replacing Ollama (local LLM) with a cloud API provider.
> Every change is isolated to a single file: `src/integrations/ollama_client.py`
> Everything else — Celery, orchestrator, PDF, vision — stays exactly the same.

---

## Table of Contents

- [Overview](#overview)
- [How the LLM is Used in FitGen](#how-the-llm-is-used-in-fitgen)
- [Option 1 — OpenAI (GPT-4o / GPT-3.5)](#option-1--openai)
- [Option 2 — Anthropic Claude](#option-2--anthropic-claude)
- [Option 3 — Google Gemini](#option-3--google-gemini)
- [Option 4 — Groq (Fast Free Tier)](#option-4--groq-fast-free-tier)
- [Option 5 — OpenRouter (Any Model)](#option-5--openrouter-any-model)
- [Updating .env](#updating-env)
- [Updating Settings](#updating-settings)
- [Testing Your Integration](#testing-your-integration)
- [Cost Estimates](#cost-estimates)
- [Switching Between Local and Cloud](#switching-between-local-and-cloud)

---

## Overview

FitGen's LLM integration is intentionally thin — all LLM calls go through one file:

```
src/integrations/ollama_client.py
```

To switch from Ollama to any cloud API, you only need to:
1. Install the provider's SDK
2. Rewrite `ollama_client.py` to call the new API
3. Add the API key to `.env`
4. Update `src/config/settings.py` to load the new key

No changes needed in orchestrator, tasks, schemas, or frontend.

---

## How the LLM is Used in FitGen

Before migrating, understand what FitGen actually asks the LLM to do.
There are two calls made per plan generation (Mode B/C only):

### Call 1 — Exercise Extraction
```
Input:  YouTube transcript text (up to ~3000 chars)
Task:   Extract structured exercise data
Output: JSON — list of exercises with name, sets, reps, muscle group, form cues
```

### Call 2 — Diet Guidance Extraction
```
Input:  YouTube transcript text
Task:   Extract meal and nutrition advice
Output: JSON — meal recommendations with calorie and macro guidance
```

Both calls:
- Expect **JSON only** in the response — no markdown, no explanation
- Are non-streaming (`stream: false` equivalent)
- Have a max output of ~1000 tokens
- Are called from `src/integrations/ollama_client.py`

---

## Option 1 — OpenAI

### Install
```bash
pip install openai
```

### Rewrite `src/integrations/ollama_client.py`
```python
import json
import logging
from openai import AsyncOpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

EXERCISE_PROMPT = """You are a fitness data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract all exercises from this transcript:
{transcript}

Required format:
{{
  "exercises": [
    {{
      "name": "Push-Up",
      "sets": 3,
      "reps": 10,
      "muscle_group": "chest",
      "difficulty": "beginner",
      "equipment": "bodyweight",
      "form_cues": "Keep core tight, lower chest to floor"
    }}
  ]
}}

JSON only:"""

DIET_PROMPT = """You are a nutrition data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract meal and nutrition advice from this transcript:
{transcript}

Required format:
{{
  "meals": [
    {{
      "name": "Grilled Chicken Bowl",
      "calories": 550,
      "protein_g": 45,
      "carbs_g": 40,
      "fats_g": 12,
      "meal_type": "lunch"
    }}
  ],
  "daily_advice": "string with general nutrition guidance"
}}

JSON only:"""


async def extract_exercises(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,  # "gpt-4o-mini" recommended
            messages=[
                {"role": "system", "content": "You are a fitness data extractor. Return only valid JSON."},
                {"role": "user", "content": EXERCISE_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,  # Low temp for consistent JSON
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Exercise extraction failed: {e}")
        return {"exercises": []}


async def extract_diet_guidance(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a nutrition data extractor. Return only valid JSON."},
                {"role": "user", "content": DIET_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Diet extraction failed: {e}")
        return {"meals": [], "daily_advice": ""}


async def health_check() -> bool:
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return True
    except Exception:
        return False
```

### .env additions
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## Option 2 — Anthropic Claude

### Install
```bash
pip install anthropic
```

### Rewrite `src/integrations/ollama_client.py`
```python
import json
import logging
import anthropic
from config.settings import settings

logger = logging.getLogger(__name__)

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

EXERCISE_PROMPT = """Extract all exercises from this transcript and return ONLY raw JSON.
No markdown, no explanation, no backticks.

Transcript:
{transcript}

Required format:
{{
  "exercises": [
    {{
      "name": "Push-Up",
      "sets": 3,
      "reps": 10,
      "muscle_group": "chest",
      "difficulty": "beginner",
      "equipment": "bodyweight",
      "form_cues": "Keep core tight"
    }}
  ]
}}"""

DIET_PROMPT = """Extract meal and nutrition advice from this transcript.
Return ONLY raw JSON. No markdown. No explanation.

Transcript:
{transcript}

Required format:
{{
  "meals": [
    {{
      "name": "Grilled Chicken Bowl",
      "calories": 550,
      "protein_g": 45,
      "carbs_g": 40,
      "fats_g": 12,
      "meal_type": "lunch"
    }}
  ],
  "daily_advice": "general nutrition guidance string"
}}"""


async def extract_exercises(transcript: str) -> dict:
    try:
        response = await client.messages.create(
            model=settings.anthropic_model,  # "claude-haiku-4-5-20251001" recommended
            max_tokens=1000,
            system="You are a fitness data extractor. Return only valid JSON. No markdown.",
            messages=[
                {"role": "user", "content": EXERCISE_PROMPT.format(transcript=transcript[:3000])}
            ],
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Exercise extraction failed: {e}")
        return {"exercises": []}


async def extract_diet_guidance(transcript: str) -> dict:
    try:
        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1000,
            system="You are a nutrition data extractor. Return only valid JSON. No markdown.",
            messages=[
                {"role": "user", "content": DIET_PROMPT.format(transcript=transcript[:3000])}
            ],
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Diet extraction failed: {e}")
        return {"meals": [], "daily_advice": ""}


async def health_check() -> bool:
    try:
        await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=5,
            messages=[{"role": "user", "content": "ping"}],
        )
        return True
    except Exception:
        return False
```

### .env additions
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

> **Model recommendation:** Use `claude-haiku-4-5-20251001` — fastest and cheapest.
> Use `claude-sonnet-4-6` for higher quality plan extraction if cost isn't a concern.

---

## Option 3 — Google Gemini

### Install
```bash
pip install google-generativeai
```

### Rewrite `src/integrations/ollama_client.py`
```python
import json
import logging
import google.generativeai as genai
from config.settings import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(settings.gemini_model)

EXERCISE_PROMPT = """You are a fitness data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract all exercises from this transcript:
{transcript}

Required format:
{{
  "exercises": [
    {{
      "name": "Push-Up",
      "sets": 3,
      "reps": 10,
      "muscle_group": "chest",
      "difficulty": "beginner",
      "equipment": "bodyweight",
      "form_cues": "Keep core tight"
    }}
  ]
}}

JSON only:"""

DIET_PROMPT = """You are a nutrition data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract meal and nutrition advice from this transcript:
{transcript}

Required format:
{{
  "meals": [
    {{
      "name": "Grilled Chicken Bowl",
      "calories": 550,
      "protein_g": 45,
      "carbs_g": 40,
      "fats_g": 12,
      "meal_type": "lunch"
    }}
  ],
  "daily_advice": "general guidance string"
}}

JSON only:"""


async def extract_exercises(transcript: str) -> dict:
    try:
        response = await model.generate_content_async(
            EXERCISE_PROMPT.format(transcript=transcript[:3000]),
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Exercise extraction failed: {e}")
        return {"exercises": []}


async def extract_diet_guidance(transcript: str) -> dict:
    try:
        response = await model.generate_content_async(
            DIET_PROMPT.format(transcript=transcript[:3000]),
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Diet extraction failed: {e}")
        return {"meals": [], "daily_advice": ""}


async def health_check() -> bool:
    try:
        await model.generate_content_async("ping")
        return True
    except Exception:
        return False
```

### .env additions
```env
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

> **Model recommendation:** `gemini-1.5-flash` — fast, cheap, generous free tier.

---

## Option 4 — Groq (Fast Free Tier)

Groq runs open-source models (Llama, Mixtral) on their hardware at very high speed.
Free tier is generous — good for development and personal use.

### Install
```bash
pip install groq
```

### Rewrite `src/integrations/ollama_client.py`
```python
import json
import logging
from groq import AsyncGroq
from config.settings import settings

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=settings.groq_api_key)

EXERCISE_PROMPT = """You are a fitness data extractor.
Return ONLY raw JSON. No markdown. No explanation. No backticks.

Extract all exercises from this transcript:
{transcript}

Required format:
{{
  "exercises": [
    {{
      "name": "Push-Up",
      "sets": 3,
      "reps": 10,
      "muscle_group": "chest",
      "difficulty": "beginner",
      "equipment": "bodyweight",
      "form_cues": "Keep core tight"
    }}
  ]
}}

JSON only:"""

DIET_PROMPT = """You are a nutrition data extractor.
Return ONLY raw JSON. No markdown. No explanation.

Extract meal advice from this transcript:
{transcript}

Required format:
{{
  "meals": [
    {{
      "name": "Grilled Chicken Bowl",
      "calories": 550,
      "protein_g": 45,
      "carbs_g": 40,
      "fats_g": 12,
      "meal_type": "lunch"
    }}
  ],
  "daily_advice": "general guidance"
}}

JSON only:"""


async def extract_exercises(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,  # "llama3-8b-8192" recommended
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": EXERCISE_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Exercise extraction failed: {e}")
        return {"exercises": []}


async def extract_diet_guidance(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": DIET_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Diet extraction failed: {e}")
        return {"meals": [], "daily_advice": ""}


async def health_check() -> bool:
    try:
        await client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return True
    except Exception:
        return False
```

### .env additions
```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama3-8b-8192
```

> Get a free API key at https://console.groq.com
> Available models: `llama3-8b-8192`, `llama3-70b-8192`, `mixtral-8x7b-32768`

---

## Option 5 — OpenRouter (Any Model via One API)

OpenRouter lets you access GPT-4o, Claude, Gemini, Llama, Mistral — all through
one OpenAI-compatible API. Useful if you want to switch models without code changes.

### Install
```bash
pip install openai   # OpenRouter uses the OpenAI SDK
```

### Rewrite `src/integrations/ollama_client.py`
```python
import json
import logging
from openai import AsyncOpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# Same prompts as OpenAI option above
EXERCISE_PROMPT = """..."""  # copy from OpenAI option
DIET_PROMPT = """..."""      # copy from OpenAI option


async def extract_exercises(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,  # e.g. "meta-llama/llama-3-8b-instruct"
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": EXERCISE_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Exercise extraction failed: {e}")
        return {"exercises": []}


async def extract_diet_guidance(transcript: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": DIET_PROMPT.format(transcript=transcript[:3000])}
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[OllamaClient] Diet extraction failed: {e}")
        return {"meals": [], "daily_advice": ""}


async def health_check() -> bool:
    return True
```

### .env additions
```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct
```

> Get a key at https://openrouter.ai
> Popular free/cheap models: `meta-llama/llama-3-8b-instruct`, `mistralai/mistral-7b-instruct`

---

## Updating .env

Add only the keys for your chosen provider. Full example:

```env
# ── Existing ──────────────────────────────────
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite+aiosqlite:///./fitgen.db
SECRET_KEY=change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── LLM Provider (pick ONE) ───────────────────

# Option 1 — OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Option 2 — Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# Option 3 — Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash

# Option 4 — Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama3-8b-8192

# Option 5 — OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct

# ── Remove this when using cloud API ──────────
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_MODEL=gemma3:4b
```

---

## Updating Settings

Open `src/config/settings.py` and add fields for your chosen provider:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing fields
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Ollama (keep for backward compat or remove if fully switching)
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"

    # Add whichever provider you chose:
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"

    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3-8b-instruct"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Testing Your Integration

After rewriting `ollama_client.py`, test it directly before running a full plan:

```python
# test_llm.py — run from koda/ root with venv activated
import asyncio
import sys
sys.path.insert(0, "src")

from integrations.ollama_client import extract_exercises, extract_diet_guidance

test_transcript = """
Today we're doing a full chest workout.
Start with 4 sets of 8 to 10 reps of bench press.
Then move to 3 sets of 12 incline dumbbell press.
Finish with 3 sets of cable flies for 15 reps.
"""

async def main():
    print("Testing exercise extraction...")
    result = await extract_exercises(test_transcript)
    print("Exercises:", 
