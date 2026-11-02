from pathlib import Path

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


def test_without_a_web_build_the_lite_page_is_served():
    client = TestClient(create_app(FakeEngine(), web_build=None))
    assert "Whisper large-v3 Studio" in client.get("/").text
    assert client.get("/lite/app.js").status_code == 200


def test_a_web_build_is_served_next_to_the_api(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>Next.js build</h1>")
    (tmp_path / "_next").mkdir()
    (tmp_path / "_next" / "app.js").write_text("console.log(1)")
    client = TestClient(create_app(FakeEngine(), web_build=tmp_path))
    assert client.get("/").text == "<h1>Next.js build</h1>"
    assert client.get("/_next/app.js").status_code == 200
    response = client.post("/api/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert response.json()["text"] == "Hi. Bye."


def test_the_dev_server_on_port_7861_may_call_the_api():
    client = TestClient(create_app(FakeEngine(), web_build=None))
    response = client.options(
        "/api/transcribe",
        headers={"Origin": "http://localhost:7861", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:7861"
    other = client.options(
        "/api/transcribe",
        headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in other.headers


def test_transcribe_returns_text_segments_and_subtitles():
    engine = FakeEngine()
    client = TestClient(create_app(engine, web_build=None))
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
    client = TestClient(create_app(engine, web_build=None))
    client.post("/api/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert engine.calls[0][1:] == (None, "transcribe")

    failing = TestClient(create_app(FakeEngine(fail=True), web_build=None))
    response = failing.post("/api/transcribe", files={"file": ("a.wav", b"x", "audio/wav")})
    assert response.status_code == 422
    assert "Could not transcribe" in response.json()["detail"]
