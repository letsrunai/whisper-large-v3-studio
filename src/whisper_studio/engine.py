"""Run Whisper large-v3 with the fastest backend this machine has.

Both backends load the same large-v3 weights, converted for their runtime:
- Apple Silicon: mlx-whisper on the GPU (mlx-community/whisper-large-v3-mlx).
- Everything else: faster-whisper on CUDA when there is a GPU, otherwise on the CPU
  (Systran/faster-whisper-large-v3).
Set WHISPER_BACKEND=mlx or WHISPER_BACKEND=faster-whisper to choose by hand.
"""

from __future__ import annotations

import os
import platform
import threading
import time
from dataclasses import dataclass, field
from typing import Literal, Protocol

Task = Literal["transcribe", "translate"]

MLX_MODEL = "mlx-community/whisper-large-v3-mlx"
FASTER_WHISPER_MODEL = "large-v3"
SAMPLE_RATE = 16_000


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Result:
    language: str
    duration: float
    segments: list[Segment]
    elapsed: float
    backend: str
    device: str
    text: str = field(init=False)

    def __post_init__(self) -> None:
        self.text = " ".join(s.text.strip() for s in self.segments if s.text.strip())


class Engine(Protocol):
    name: str
    device: str

    def transcribe(self, path: str, language: str | None, task: Task) -> Result: ...


class MlxEngine:
    name = "mlx-whisper"
    device = "Apple Silicon GPU"

    def __init__(self, model: str = MLX_MODEL) -> None:
        import mlx_whisper  # noqa: F401  (fail early when it is missing)

        self.model = model

    def transcribe(self, path: str, language: str | None, task: Task) -> Result:
        import mlx_whisper
        from mlx_whisper.audio import load_audio

        started = time.perf_counter()
        audio = load_audio(path)
        output = mlx_whisper.transcribe(
            audio, path_or_hf_repo=self.model, language=language, task=task
        )
        return Result(
            language=output.get("language") or language or "",
            duration=len(audio) / SAMPLE_RATE,
            segments=[
                Segment(float(s["start"]), float(s["end"]), s["text"])
                for s in output.get("segments", [])
            ],
            elapsed=time.perf_counter() - started,
            backend=self.name,
            device=self.device,
        )


class FasterWhisperEngine:
    name = "faster-whisper"

    def __init__(self, model: str = FASTER_WHISPER_MODEL) -> None:
        import ctranslate2
        from faster_whisper import WhisperModel

        cuda = ctranslate2.get_cuda_device_count() > 0
        self.device = "CUDA GPU" if cuda else "CPU"
        self.model = WhisperModel(
            model,
            device="cuda" if cuda else "cpu",
            compute_type="float16" if cuda else "int8",
        )

    def transcribe(self, path: str, language: str | None, task: Task) -> Result:
        started = time.perf_counter()
        segments, info = self.model.transcribe(
            path, language=language, task=task, beam_size=5, vad_filter=True
        )
        # The segments are a generator: the work happens while this list fills.
        collected = [Segment(s.start, s.end, s.text) for s in segments]
        return Result(
            language=info.language,
            duration=info.duration,
            segments=collected,
            elapsed=time.perf_counter() - started,
            backend=self.name,
            device=self.device,
        )


def _apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def create_engine(backend: str | None = None) -> Engine:
    choice = (backend or os.environ.get("WHISPER_BACKEND") or "").lower()
    if choice == "mlx" or (not choice and _apple_silicon()):
        try:
            return MlxEngine()
        except ImportError:
            if choice == "mlx":
                raise
    return FasterWhisperEngine()


class LazyEngine:
    """Loads the model on first use and runs one transcription at a time."""

    def __init__(self, backend: str | None = None) -> None:
        self._backend = backend
        self._engine: Engine | None = None
        self._lock = threading.Lock()

    def get(self) -> Engine:
        with self._lock:
            if self._engine is None:
                self._engine = create_engine(self._backend)
            return self._engine

    def transcribe(self, path: str, language: str | None, task: Task) -> Result:
        engine = self.get()
        with self._lock:
            return engine.transcribe(path, language, task)
