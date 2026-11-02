from whisper_studio.engine import Result, Segment
from whisper_studio.subtitles import timestamp, to_srt, to_vtt

SEGMENTS = [
    Segment(0.0, 2.5, " Hello there."),
    Segment(2.5, 3.0, "   "),
    Segment(3661.007, 3662.9994, " One hour in."),
]


def test_timestamps_round_to_milliseconds():
    assert timestamp(0) == "00:00:00,000"
    assert timestamp(3661.007) == "01:01:01,007"
    assert timestamp(59.9996) == "00:01:00,000"
    assert timestamp(-1) == "00:00:00,000"
    assert timestamp(1.5, ".") == "00:00:01.500"


def test_srt_numbers_cues_and_skips_empty_text():
    assert to_srt(SEGMENTS) == (
        "1\n00:00:00,000 --> 00:00:02,500\nHello there.\n"
        "\n"
        "2\n01:01:01,007 --> 01:01:02,999\nOne hour in.\n"
    )


def test_vtt_has_a_header_and_dot_milliseconds():
    vtt = to_vtt(SEGMENTS)
    assert vtt.startswith("WEBVTT\n\n00:00:00.000 --> 00:00:02.500\nHello there.\n")
    assert "01:01:01.007 --> 01:01:02.999" in vtt


def test_result_text_joins_trimmed_segments():
    result = Result("en", 4.0, SEGMENTS, 1.0, "fake", "CPU")
    assert result.text == "Hello there. One hour in."
