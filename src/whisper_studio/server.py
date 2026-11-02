"""The web app: one page, one endpoint that turns an uploaded file into text and subtitles."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .engine import LazyEngine
from .subtitles import to_srt, to_vtt

STATIC = Path(__file__).parent / "static"


def create_app(engine: LazyEngine | None = None) -> FastAPI:
    app = FastAPI(title="Whisper large-v3 Studio")
    whisper = engine or LazyEngine()

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.post("/api/transcribe")
    async def transcribe(
        file: UploadFile = File(...),
        language: str = Form(""),
        task: Literal["transcribe", "translate"] = Form("transcribe"),
    ) -> dict:
        suffix = Path(file.filename or "audio").suffix or ".audio"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            shutil.copyfileobj(file.file, temp)
            path = temp.name
        try:
            result = await run_in_threadpool(
                whisper.transcribe, path, language.strip() or None, task
            )
        except Exception as error:  # ffmpeg or the model refused the file
            raise HTTPException(422, f"Could not transcribe this file: {error}") from error
        finally:
            Path(path).unlink(missing_ok=True)
        return {
            **asdict(result),
            "file": file.filename,
            "srt": to_srt(result.segments),
            "vtt": to_vtt(result.segments),
        }

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
