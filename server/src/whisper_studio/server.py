"""The web app: the page and one endpoint that turns an uploaded file into text and subtitles.

The page is the Next.js app in web/ once it is built into web/out. Without that build, as in a
pip install on Colab, the lite page next to this file is served instead.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .engine import LazyEngine
from .subtitles import to_srt, to_vtt

LITE = Path(__file__).parent / "lite"
# server/src/whisper_studio/server.py → the repository root is three folders up.
WEB_BUILD = Path(os.environ.get("WHISPER_STUDIO_WEB", Path(__file__).parents[3] / "web" / "out"))
# `npm run dev` serves the Next.js app on port 7861 and calls this server directly.
DEV_ORIGINS = ["http://localhost:7861", "http://127.0.0.1:7861"]


def create_app(engine: LazyEngine | None = None, web_build: Path | None = WEB_BUILD) -> FastAPI:
    app = FastAPI(title="Whisper large-v3 Studio")
    whisper = engine or LazyEngine()
    app.add_middleware(CORSMiddleware, allow_origins=DEV_ORIGINS, allow_methods=["POST"])

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

    if web_build and (web_build / "index.html").is_file():
        app.mount("/", StaticFiles(directory=web_build, html=True), name="web")
    else:

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(LITE / "index.html")

        app.mount("/lite", StaticFiles(directory=LITE), name="lite")
    return app
