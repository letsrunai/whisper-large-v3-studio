from fastapi.testclient import TestClient

from whisper_studio.engine import Result, Segment
from whisper_studio.server import create_app


class FakeEngine:
    """Stands in for the model: records the call and answers with two segments."""

    def __init__(self, fail: bool = False):
        self.calls = []
        self.fail = fail

    def transcribe(self, path, language, task):
        with open(path, "rb") as audio:
            self.calls.append((audio.read(), language, task))
        if self.fail:
            raise RuntimeError("ffmpeg could not read it")
        return Result(
            "en", 3.0, [Segment(0, 1.2, " Hi."), Segment(1.2, 3.0, " Bye.")], 0.5, "fake", "CPU"
        )


def test_page_and_assets_are_served():
    client = TestClient(create_app(FakeEngine()))
    assert "Whisper large-v3 Studio" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200


def test_transcribe_returns_text_segments_and_subtitles():
    engine = FakeEngine()
    client = TestClient(create_app(engine))
    response = client.post(
        "/api/transcribe",
        files={"file": ("talk.mp3", b"audio-bytes", "audio/mpeg")},
        data={"language": "en", "task": "translate"},
    )
    assert response.status_code == 200
    body = response.json()
    assert engine.calls == [(b"audio-bytes", "en", "translate")]
    assert body["text"] == "Hi. Bye."
    assert body["file"] == "talk.mp3"
    assert body["srt"].startswith("1\n00:00:00,000 --> 00:00:01,200\nHi.\n")
    assert body["vtt"].startswith("WEBVTT")
    assert [s["text"] for s in body["segments"]] == [" Hi.", " Bye."]


def test_language_left_empty_is_detected_and_bad_files_are_refused():
    engine = FakeEngine()
    client = TestClient(create_app(engine))
    client.post("/api/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert engine.calls[0][1:] == (None, "transcribe")

    failing = TestClient(create_app(FakeEngine(fail=True)))
    response = failing.post("/api/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert response.status_code == 422
    assert "Could not transcribe" in response.json()["detail"]
