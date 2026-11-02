# Whisper large-v3 Studio

Drop an audio or video file, get timestamped text and subtitles (`.srt`, `.vtt`). Runs [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) on your own machine; nothing is uploaded anywhere.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/letsrunai/whisper-large-v3-studio/blob/main/colab.ipynb)

| | |
|---|---|
| **Model** | Whisper large-v3 (1.55B parameters) |
| **Task** | Speech → text in 99 languages, or translate to English |
| **Memory** | 3.8 GB peak on Apple Silicon (MLX) |
| **Time** | 6:09 English recording in 74 s · 3:39 Turkish recording in 21 s (MacBook Pro M3 Max) |
| **Cost** | $0 on your machine, or a Colab GPU runtime |
| **Closed alternative** | OpenAI's hosted transcription API, billed per minute of audio |
| **License** | Model: Apache-2.0 · Code: MIT |

## Quick start

You need [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/).

```bash
git clone https://github.com/letsrunai/whisper-large-v3-studio
cd whisper-large-v3-studio
uv run whisper-studio
```

Open http://127.0.0.1:7860 and drop a file. The first run downloads the model weights (about 3 GB) into the Hugging Face cache.

No GPU? The Colab notebook runs the same app on Colab's GPU.

## From the terminal

```bash
uv run whisper-studio transcribe talk.mp3 --srt talk.srt
uv run whisper-studio transcribe interview.m4a --language tr
uv run whisper-studio transcribe podcast.mp3 --translate
```

It prints the text, then the backend, the time it took, the speed against real time and the peak memory. The numbers in the table above come from this command.

## How it runs

The app picks the fastest way to run the same large-v3 weights on your machine:

| Machine | Backend | Weights |
|---|---|---|
| Apple Silicon Mac | [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) on the GPU | [mlx-community/whisper-large-v3-mlx](https://huggingface.co/mlx-community/whisper-large-v3-mlx) |
| NVIDIA GPU | [faster-whisper](https://github.com/SYSTRAN/faster-whisper), float16 | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) |
| CPU only | faster-whisper, int8 | same as above |

Choose one by hand with `--backend` before the command, or with the `WHISPER_BACKEND` environment variable:

```bash
uv run whisper-studio --backend faster-whisper serve --port 8000
```

## Tech stack

- Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/) and Uvicorn
- mlx-whisper on Apple Silicon, faster-whisper everywhere else
- One page of HTML, CSS and JavaScript; no build step

```
src/whisper_studio/
├── engine.py      picks the backend and runs the model
├── subtitles.py   .srt and .vtt
├── server.py      the web app and /api/transcribe
├── __main__.py    whisper-studio serve | transcribe
└── static/        the page
```

## Development

```bash
uv run pytest
```

The tests replace the model with a stand-in, so they run in a second without a GPU.

## License

The code is MIT. OpenAI releases the model weights under Apache-2.0, which allows commercial use.
