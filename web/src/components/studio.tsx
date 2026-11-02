"use client";

import { useEffect, useState, type FormEvent } from "react";
import { transcribe, type Task, type Transcript } from "@/lib/api";
import { clock } from "@/lib/format";
import { DropZone } from "./drop-zone";
import { TranscriptView } from "./transcript-view";

const LANGUAGES: [string, string][] = [
  ["", "Detect"],
  ["en", "English"],
  ["tr", "Turkish"],
  ["de", "German"],
  ["fr", "French"],
  ["es", "Spanish"],
  ["it", "Italian"],
  ["pt", "Portuguese"],
  ["nl", "Dutch"],
  ["ru", "Russian"],
  ["ar", "Arabic"],
  ["hi", "Hindi"],
  ["ja", "Japanese"],
  ["ko", "Korean"],
  ["zh", "Chinese"],
];

/** The whole app: choose a file and options, send it, show the transcript. */
export function Studio() {
  const [file, setFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [language, setLanguage] = useState("");
  const [task, setTask] = useState<Task>("transcribe");
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState("");
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const busy = startedAt !== null;

  // The page plays the chosen file itself, so segments can seek in it.
  function choose(chosen: File) {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(URL.createObjectURL(chosen));
    setFile(chosen);
    setTranscript(null);
    setError("");
  }

  useEffect(() => {
    if (startedAt === null) return;
    const timer = setInterval(() => setSeconds((Date.now() - startedAt) / 1000), 500);
    return () => clearInterval(timer);
  }, [startedAt]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    setError("");
    setTranscript(null);
    setSeconds(0);
    setStartedAt(Date.now());
    try {
      setTranscript(await transcribe(file, language, task));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setStartedAt(null);
    }
  }

  return (
    <>
      <form onSubmit={(event) => void submit(event)} className="grid gap-4">
        <DropZone file={file} disabled={busy} onFile={choose} />
        <div className="flex flex-wrap items-end gap-4">
          <label className="text-muted grid gap-1.5 text-sm">
            Language
            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              className="border-line bg-panel text-foreground focus-visible:outline-accent h-10 rounded-lg border px-3 focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              {LANGUAGES.map(([code, label]) => (
                <option key={code} value={code}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <fieldset className="text-muted grid gap-1.5 text-sm">
            <legend className="mb-1.5">Output</legend>
            <div className="text-foreground flex flex-wrap gap-4">
              {(
                [
                  ["transcribe", "Same language"],
                  ["translate", "Translate to English"],
                ] as const
              ).map(([value, label]) => (
                <label key={value} className="inline-flex items-center gap-2">
                  <input
                    type="radio"
                    name="task"
                    value={value}
                    checked={task === value}
                    onChange={() => setTask(value)}
                    className="accent-accent"
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>
          <button
            type="submit"
            disabled={!file || busy}
            className="bg-accent text-accent-ink focus-visible:outline-accent h-10 rounded-lg px-5 font-bold transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-sm:w-full sm:ml-auto"
          >
            {busy ? "Transcribing…" : "Transcribe"}
          </button>
        </div>
      </form>

      <p role="status" aria-live="polite" className="text-muted mt-4 min-h-6">
        {busy && `Transcribing… ${clock(seconds)} (the first run also loads the model)`}
        {!busy && error && <span className="text-red-400">{error}</span>}
      </p>

      {transcript && <TranscriptView transcript={transcript} audioUrl={audioUrl} />}
    </>
  );
}
