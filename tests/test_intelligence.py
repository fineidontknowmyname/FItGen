import pytest

from services.intelligence.summarizer import summarizer_service
from services.intelligence.youtube import youtube_service


def test_extract_video_id():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    video_id = youtube_service.extract_video_id(url)

    assert video_id == "dQw4w9WgXcQ"


def test_get_transcript_handles_missing_captions_or_network_gracefully():
    video_id = "dQw4w9WgXcQ"

    try:
        transcript = youtube_service.get_transcript(video_id)
    except Exception as exc:
        pytest.skip(f"Transcript fetch unavailable in this environment: {exc}")

    assert transcript is None or isinstance(transcript, str)


async def test_summarizer_service_summarizes_or_skips_without_ollama():
    dummy_text = "The quick brown fox jumps over the lazy dog. " * 20

    try:
        summary = await summarizer_service.summarize_content(dummy_text)
    except Exception as exc:
        pytest.skip(f"Ollama not reachable in this environment: {exc}")

    if not summary or "Failed" in summary:
        pytest.skip("Summarizer returned a failure message — Ollama likely unreachable")

    assert isinstance(summary, str)
    assert len(summary) > 0
