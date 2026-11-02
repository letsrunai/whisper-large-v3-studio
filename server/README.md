# server

The Python half of [Whisper large-v3 Studio](../README.md): it runs the model, answers `POST /api/transcribe` and serves the page.

```bash
uv run whisper-studio                       # the app on http://127.0.0.1:7860
uv run whisper-studio transcribe talk.mp3   # one file, with time and memory
uv run pytest                               # tests; the model is replaced with a stand-in
```

| File | What it does |
|---|---|
| `src/whisper_studio/engine.py` | picks mlx-whisper (Apple Silicon) or faster-whisper (NVIDIA, CPU) and runs large-v3 |
| `src/whisper_studio/subtitles.py` | `.srt` and `.vtt` |
| `src/whisper_studio/server.py` | the API, and the page: `web/out` when it is built, otherwise the lite page |
| `src/whisper_studio/lite/` | a single-file page for installs without the web build, such as Colab |
| `src/whisper_studio/__main__.py` | the `whisper-studio` command |

Choose the backend by hand with `--backend mlx` or `--backend faster-whisper` before the command, or the `WHISPER_BACKEND` environment variable. `WHISPER_STUDIO_WEB` points the server at another page build.

`POST /api/transcribe` takes a multipart form: `file`, `language` (empty to detect) and `task` (`transcribe` or `translate`). It returns the language, audio length, time taken, backend, device, text, segments, `srt` and `vtt`.
