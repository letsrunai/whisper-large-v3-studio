"""whisper-studio: start the web app, or transcribe one file from the terminal."""

from __future__ import annotations

import argparse
import resource
import sys
from pathlib import Path


def _peak_memory_gb(backend: str) -> str:
    if backend == "mlx-whisper":
        # MLX keeps the model in GPU memory, which the process's RSS does not show.
        import mlx.core as mx

        peak = mx.get_peak_memory() if hasattr(mx, "get_peak_memory") else mx.metal.get_peak_memory()
        return f"peak GPU memory {peak / 1024**3:.1f} GB"
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux kilobytes. On CUDA the model sits in VRAM, so check nvidia-smi.
    return f"peak process memory {peak / (1024**3 if sys.platform == 'darwin' else 1024**2):.1f} GB"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="whisper-studio", description=__doc__)
    parser.add_argument("--backend", choices=["mlx", "faster-whisper"], help="Default: the fastest one here.")
    commands = parser.add_subparsers(dest="command")

    serve = commands.add_parser("serve", help="Start the web app (the default).")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=7860)

    run = commands.add_parser("transcribe", help="Transcribe one file and report the time it took.")
    run.add_argument("file", type=Path)
    run.add_argument("--language", default=None, help="Such as en or tr; detected when left out.")
    run.add_argument("--translate", action="store_true", help="Translate to English.")
    run.add_argument("--srt", type=Path, help="Also write subtitles here.")

    args = parser.parse_args(argv)

    if args.command == "transcribe":
        from .engine import create_engine
        from .subtitles import to_srt

        engine = create_engine(args.backend)
        result = engine.transcribe(
            str(args.file), args.language, "translate" if args.translate else "transcribe"
        )
        print(result.text)
        if args.srt:
            args.srt.write_text(to_srt(result.segments), encoding="utf-8")
        speed = result.duration / result.elapsed if result.elapsed else 0
        print(
            f"\n{result.backend} on {result.device}: {result.duration:.1f}s of audio "
            f"in {result.elapsed:.1f}s ({speed:.1f}x real time), language {result.language}, "
            f"{_peak_memory_gb(result.backend)}",
            file=sys.stderr,
        )
        return

    import uvicorn

    from .engine import LazyEngine
    from .server import create_app

    host = getattr(args, "host", "127.0.0.1")
    port = getattr(args, "port", 7860)
    print(f"Whisper large-v3 Studio: http://{host}:{port}", file=sys.stderr)
    uvicorn.run(create_app(LazyEngine(args.backend)), host=host, port=port)


if __name__ == "__main__":
    main()
