from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi

log = logging.getLogger(__name__)

# Hard cap applied to every transcript before returning.
# 12 000 chars ≈ 3 000 tokens (GPT-style 4 chars/token) — safe for most
# LLM context windows and keeps Ollama prompts responsive.
TOKEN_GUARD: int = 12_000


class YouTubeService:
   
    # ── Core helpers (unchanged public API) ───────────────────────────────────

    def extract_video_id(self, url: str) -> Optional[str]:
       
        parsed = urlparse(url.strip())

        # Standard: https://www.youtube.com/watch?v=VIDEO_ID
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

        # Short: https://youtu.be/VIDEO_ID
        if parsed.hostname in ("youtu.be",):
            path_part = parsed.path.lstrip("/")
            return path_part.split("?")[0] or None

        # Embed / legacy
        parts = parsed.path.split("/")
        if len(parts) >= 3 and parts[1] in ("embed", "v"):
            return parts[2] or None

        return None

    def get_transcript(self, video_id: str) -> Optional[str]:
       
        try:
            entries = YouTubeTranscriptApi.get_transcript(video_id)
            full    = " ".join(e["text"] for e in entries)
            guarded = self._apply_token_guard(full)
            log.debug("Transcript fetched  video_id=%s  chars=%d", video_id, len(guarded))
            return guarded
        except Exception as exc:
            log.warning("Transcript fetch failed  video_id=%s  error=%s", video_id, exc)
            return None

    # ── New higher-level helpers ───────────────────────────────────────────────

    def get_transcript_for_url(self, url: str) -> Optional[str]:
        
        video_id = self.extract_video_id(url)
        if not video_id:
            log.warning("Could not extract video ID from URL: %s", url)
            return None
        return self.get_transcript(video_id)

    async def fetch_many(
        self,
        urls: List[str],
        *,
        skip_failed: bool = True,
    ) -> Dict[str, str]:
        
        unique_urls: List[str] = list(dict.fromkeys(urls))   # preserve order, remove dupes

        async def _fetch_one(url: str) -> tuple[str, Optional[str]]:
            text = await asyncio.to_thread(self.get_transcript_for_url, url)
            return url, text

        results: list[tuple[str, Optional[str]]] = await asyncio.gather(
            *[_fetch_one(u) for u in unique_urls],
            return_exceptions=False,
        )

        output: Dict[str, str] = {}
        for url, text in results:
            if text:
                output[url] = text
            elif not skip_failed:
                output[url] = ""
            else:
                log.info("Skipping failed URL: %s", url)

        log.info(
            "fetch_many: %d/%d URLs succeeded",
            len(output), len(unique_urls),
        )
        return output

    # ── Token guard ────────────────────────────────────────────────────────────

    @staticmethod
    def _apply_token_guard(text: str, limit: int = TOKEN_GUARD) -> str:
       
        if len(text) <= limit:
            return text
        truncated = text[:limit]
        last_space = truncated.rfind(" ")
        return truncated[:last_space] if last_space > 0 else truncated


# Module-level singleton
youtube_service = YouTubeService()
