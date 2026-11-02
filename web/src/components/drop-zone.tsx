"use client";

import { useState, type DragEvent } from "react";
import { megabytes } from "@/lib/format";

type Props = { file: File | null; onFile: (file: File) => void; disabled: boolean };

/** A large target for dragging a file in; clicking it opens the file picker. */
export function DropZone({ file, onFile, disabled }: Props) {
  const [over, setOver] = useState(false);

  function drop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setOver(false);
    const dropped = event.dataTransfer.files[0];
    if (dropped && !disabled) onFile(dropped);
  }

  return (
    <label
      htmlFor="file"
      onDragEnter={(event) => {
        event.preventDefault();
        setOver(true);
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={() => setOver(false)}
      onDrop={drop}
      className={`focus-within:outline-accent grid min-h-44 cursor-pointer place-items-center content-center gap-1.5 rounded-xl border-[1.5px] border-dashed p-6 text-center transition-colors focus-within:outline-2 focus-within:outline-offset-4 ${
        over ? "border-accent bg-accent/10" : "border-line bg-panel hover:border-accent/70"
      }`}
    >
      <input
        id="file"
        type="file"
        accept="audio/*,video/*"
        className="sr-only"
        disabled={disabled}
        onChange={(event) => {
          const chosen = event.target.files?.[0];
          if (chosen) onFile(chosen);
        }}
      />
      <strong className="text-base">
        {file ? file.name : "Drop a file here or click to choose"}
      </strong>
      <span className="text-muted text-sm">
        {file ? megabytes(file.size) : "mp3, wav, m4a, mp4, webm… anything ffmpeg reads"}
      </span>
    </label>
  );
}
