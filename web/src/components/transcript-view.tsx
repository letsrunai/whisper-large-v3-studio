"use client";

import { useEffect, useRef, useState } from "react";
import type { Transcript } from "@/lib/api";
import { baseName, clock } from "@/lib/format";

type Props = { transcript: Transcript; audioUrl: string | null };

function download(name: string, body: string) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([body], { type: "text/plain;charset=utf-8" }));
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

const button =
  "h-10 rounded-lg border border-line bg-panel px-3.5 text-sm transition-colors hover:border-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

/** Stats, downloads, the audio and the segments; clicking a segment plays from there. */
export function TranscriptView({ transcript, audioUrl }: Props) {
  const audio = useRef<HTMLAudioElement>(null);
  const [now, setNow] = useState(-1);
  const [copied, setCopied] = useState(false);
  const name = baseName(transcript.file);
  const speed = transcript.elapsed ? transcript.duration / transcript.elapsed : 0;
  const playing = transcript.segments.findIndex((s) => now >= s.start && now < s.end);

  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 1500);
    return () => clearTimeout(timer);
  }, [copied]);

  function seek(seconds: number) {
    if (!audio.current) return;
    audio.current.currentTime = seconds;
    void audio.current.play();
  }

  const stats = [
    ["Language", transcript.language || "—"],
    ["Audio", clock(transcript.duration)],
    ["Took", `${transcript.elapsed.toFixed(1)} s`],
    ["Speed", speed ? `${speed.toFixed(1)}× real time` : "—"],
    ["Ran on", `${transcript.backend} · ${transcript.device}`],
  ];

  return (
    <section className="mt-2 grid gap-4" aria-label="Transcript">
      <dl className="grid grid-cols-[repeat(auto-fit,minmax(130px,1fr))] gap-2.5">
        {stats.map(([label, value]) => (
          <div key={label} className="border-line bg-panel rounded-xl border px-3.5 py-3">
            <dt className="text-muted text-xs">{label}</dt>
            <dd className="mt-0.5 font-semibold">{value}</dd>
          </div>
        ))}
      </dl>

      {audioUrl && (
        <audio
          ref={audio}
          src={audioUrl}
          controls
          className="w-full"
          onTimeUpdate={(event) => setNow(event.currentTarget.currentTime)}
        />
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className={button}
          onClick={() =>
            void navigator.clipboard.writeText(transcript.text).then(() => setCopied(true))
          }
        >
          {copied ? "Copied" : "Copy text"}
        </button>
        <button
          type="button"
          className={button}
          onClick={() => download(`${name}.txt`, transcript.text)}
        >
          Download .txt
        </button>
        <button
          type="button"
          className={button}
          onClick={() => download(`${name}.srt`, transcript.srt)}
        >
          Download .srt
        </button>
        <button
          type="button"
          className={button}
          onClick={() => download(`${name}.vtt`, transcript.vtt)}
        >
          Download .vtt
        </button>
      </div>

      <ol className="divide-line border-line bg-panel divide-y overflow-hidden rounded-xl border">
        {transcript.segments.map((segment, index) => (
          <li key={`${segment.start}-${index}`}>
            <button
              type="button"
              onClick={() => seek(segment.start)}
              disabled={!audioUrl}
              aria-current={index === playing ? "true" : undefined}
              className={`grid w-full grid-cols-[64px_1fr] gap-3 px-3.5 py-2.5 text-left transition-colors hover:bg-white/5 focus-visible:bg-white/5 focus-visible:outline-none disabled:cursor-default ${
                index === playing ? "bg-accent/10" : ""
              }`}
            >
              <time className="text-accent font-mono text-sm leading-7">
                {clock(segment.start)}
              </time>
              <span>{segment.text.trim()}</span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
