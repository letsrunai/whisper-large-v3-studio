# Whisper large-v3 Studio

Drop an audio or video file, get timestamped text and subtitles (`.srt`, `.vtt`). Runs [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) on your own machine; nothing is uploaded anywhere.

| | |
|---|---|
| **Model** | Whisper large-v3 (1.55B parameters) |
| **Task** | Speech → text in 99 languages, or translate to English |
| **Memory** | 3.8 GB peak on Apple Silicon (MLX) |
| **Time** | 6:09 English recording in 74 s · 3:39 Turkish recording in 21 s (MacBook Pro M3 Max) |
| **Cost** | $0 on your machine, or a Colab GPU runtime |
| **Closed alternative** | OpenAI's hosted transcription API, billed per minute of audio |
| **License** | Model: Apache-2.0 · Code: MIT |

## Three ways to run it

### 1. On your own machine

You need [uv](https://docs.astral.sh/uv/), [ffmpeg](https://ffmpeg.org/) and [Node.js](https://nodejs.org/) 20 or newer.

```bash
git clone https://github.com/letsrunai/whisper-large-v3-studio
cd whisper-large-v3-studio
npm run setup
npm start
```

Open http://127.0.0.1:7860 and drop a file. The page plays your file next to the transcript: click any line to hear it from there. The first run downloads the model weights (about 3 GB) into the Hugging Face cache.

### 2. No GPU? On Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/letsrunai/whisper-large-v3-studio/blob/main/colab/whisper-large-v3-studio.ipynb)

The notebook runs the same server on Colab's GPU with a lighter page. See [colab/](colab/).

### 3. From the terminal

```bash
cd server
uv run whisper-studio transcribe talk.mp3 --srt talk.srt
uv run whisper-studio transcribe interview.m4a --language tr
uv run whisper-studio transcribe podcast.mp3 --translate
```

It prints the text, then the backend, the time it took, the speed against real time and the peak memory. The numbers in the table above come from this command.

## What is where

```
whisper-large-v3-studio/
├── server/   Python: runs the model, serves /api/transcribe and the page, whisper-studio command
├── web/      Next.js: the page you use on your own machine
└── colab/    the notebook for running it on Colab's GPU
```

| Part | Stack |
|---|---|
| [server/](server/) | Python 3.10+, FastAPI, Uvicorn; mlx-whisper on Apple Silicon, faster-whisper on NVIDIA and CPU |
| [web/](web/) | Next.js (static export), React, TypeScript, Tailwind CSS, ESLint, Prettier |
| [colab/](colab/) | Jupyter notebook; installs `server/` and opens its lite page |

## How it runs the model

The server picks the fastest way to run the same large-v3 weights on your machine:

| Machine | Backend | Weights |
|---|---|---|
| Apple Silicon Mac | [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) on the GPU | [mlx-community/whisper-large-v3-mlx](https://huggingface.co/mlx-community/whisper-large-v3-mlx) |
| NVIDIA GPU | [faster-whisper](https://github.com/SYSTRAN/faster-whisper), float16 | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) |
| CPU only | faster-whisper, int8 | same as above |

## Development

```bash
npm run dev     # server on :7860 and the page on http://localhost:7861, with hot reload
npm run check   # web: TypeScript, ESLint, Prettier · server: pytest
```

## License

The code is MIT. OpenAI releases the model weights under Apache-2.0, which allows commercial use.
