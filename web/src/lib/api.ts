export type Segment = { start: number; end: number; text: string };

export type Transcript = {
  file: string;
  language: string;
  duration: number;
  elapsed: number;
  backend: string;
  device: string;
  text: string;
  segments: Segment[];
  srt: string;
  vtt: string;
};

export type Task = "transcribe" | "translate";

// Empty in the built app, which the Python server serves next to its API; set for `npm run dev`.
const API = process.env.NEXT_PUBLIC_API_URL ?? "";

export async function transcribe(file: File, language: string, task: Task): Promise<Transcript> {
  const body = new FormData();
  body.append("file", file);
  body.append("language", language);
  body.append("task", task);
  let response: Response;
  try {
    response = await fetch(`${API}/api/transcribe`, { method: "POST", body });
  } catch {
    throw new Error(
      "Could not reach the transcription server. Is `uv run whisper-studio` running?",
    );
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail ?? response.statusText);
  return data as Transcript;
}
