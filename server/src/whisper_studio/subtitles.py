"""Turn transcription segments into .srt and .vtt subtitle files."""

from __future__ import annotations

from collections.abc import Iterable

from .engine import Segment


def timestamp(seconds: float, separator: str = ",") -> str:
    """HH:MM:SS,mmm for SRT; WebVTT uses a dot before the milliseconds."""
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def _cues(segments: Iterable[Segment]):
    for segment in segments:
        text = segment.text.strip()
        if text:
            yield segment, text


def to_srt(segments: Iterable[Segment]) -> str:
    blocks = [
        f"{index}\n{timestamp(segment.start)} --> {timestamp(segment.end)}\n{text}\n"
        for index, (segment, text) in enumerate(_cues(segments), start=1)
    ]
    return "\n".join(blocks)


def to_vtt(segments: Iterable[Segment]) -> str:
    blocks = [
        f"{timestamp(segment.start, '.')} --> {timestamp(segment.end, '.')}\n{text}\n"
        for segment, text in _cues(segments)
    ]
    return "WEBVTT\n\n" + "\n".join(blocks)
