from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any, Optional

import httpx

from config.settings import settings
from schemas.content import ExerciseLibrary

log = logging.getLogger(__name__)

# ── Defaults (overridden by settings when the attributes exist) ────────────────

_DEFAULT_BASE_URL      = "http://localhost:11435"
_DEFAULT_MODEL         = "llama3.2"
_DEFAULT_VISION_MODEL  = "llava"
_REQUEST_TIMEOUT       = 180.0   # seconds — LLM generation can be slow locally


def _cfg(attr: str, default: str) -> str:
    """Read an optional settings attribute gracefully."""
    return getattr(settings, attr, default) or default


# ── Client ─────────────────────────────────────────────────────────────────────

class OllamaClient:
    
    def __init__(self) -> None:
        self.base_url     = settings.effective_ollama_host.rstrip("/")
        self.model_name   = _cfg("OLLAMA_MODEL",    _DEFAULT_MODEL)
        self.vision_model = _cfg("OLLAMA_VISION_MODEL", _DEFAULT_VISION_MODEL)

    # ── Public methods ─────────────────────────────────────────────────────────

    async def extract_exercises(self, transcript_text: str) -> ExerciseLibrary:
       
        clean_text = transcript_text[:50_000]

        prompt = f"""You are an expert fitness data analyst.
Extract all fitness exercises from the following transcript into a structured JSON format.

Rules:
1. Ignore conversational filler.
2. Infer muscles worked and difficulty if not explicitly stated.
3. Identify any specific safety warnings mentioned.
4. Output MUST be valid JSON matching the schema below.
5. Do not include markdown formatting. Just the raw JSON.

Schema:
{{
    "exercises": [
        {{
            "name": "string",
            "description": "string",
            "instructions": ["step 1", "step 2"],
            "benefits": ["benefit 1"],
            "muscles_worked": ["muscle 1"],
            "equipment_needed": ["dumbbell", "bodyweight"],
            "difficulty": "beginner" | "intermediate" | "advanced",
            "safety_warnings": ["warning 1"]
        }}
    ]
}}

Transcript:
{clean_text}"""

        try:
            raw_json = await self.generate_text(prompt, json_mode=True)
            raw_json = self._strip_markdown(raw_json)
            return ExerciseLibrary.model_validate_json(raw_json.strip())
        except Exception as exc:
            log.error("Ollama extraction error: %s", exc)
            return ExerciseLibrary(exercises=[])

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> dict:
        
        try:
            raw_json = await self._generate_vision(image_bytes, prompt)
            raw_json = self._strip_markdown(raw_json)
            return json.loads(raw_json.strip())
        except Exception as exc:
            log.error("Ollama vision error: %s", exc)
            raise

    async def generate_text(self, prompt: str, *, json_mode: bool = False) -> str:
       
        payload: dict[str, Any] = {
            "model":  self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        if json_mode:
            payload["format"] = "json"

        return await self._post_generate(payload)

    # ── Private helpers ────────────────────────────────────────────────────────

    async def _generate_vision(self, image_bytes: bytes, prompt: str) -> str:
        """Call /api/generate with a base64-encoded image for vision models."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload: dict[str, Any] = {
            "model":  self.vision_model,
            "prompt": prompt,
            "images": [b64],
            "stream": False,
            "format": "json",
        }
        return await self._post_generate(payload)

    async def _post_generate(self, payload: dict[str, Any]) -> str:
        
        url = f"{self.base_url}/api/generate"

        def _sync_post() -> str:
            with httpx.Client(timeout=_REQUEST_TIMEOUT) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "")

        return await asyncio.to_thread(_sync_post)

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove ```json / ``` fences that some models emit despite instructions."""
        t = text.strip()
        if t.startswith("```json"):
            t = t[7:]
        elif t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return t.strip()


# ── Module-level singleton ─────────────────────────────────────────────────────

ollama_client = OllamaClient()

# Backward-compat alias — callers that imported `gemini_client` by name will
# still work without touching their import lines during a gradual migration.
gemini_client = ollama_client
