const $ = (id) => document.getElementById(id);
const form = $("form");
const input = $("file");
const drop = $("drop");
const status = $("status");
let last = null;

function clock(seconds) {
  const s = Math.max(0, Math.round(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const rest = String(s % 60).padStart(2, "0");
  return h ? `${h}:${String(m).padStart(2, "0")}:${rest}` : `${m}:${rest}`;
}

function showFile() {
  const file = input.files[0];
  $("drop-title").textContent = file ? file.name : "Drop a file here or click to choose";
  $("drop-hint").textContent = file
    ? `${(file.size / 1024 / 1024).toFixed(1)} MB`
    : "mp3, wav, m4a, mp4, webm… anything ffmpeg reads";
}

input.addEventListener("change", showFile);
for (const name of ["dragenter", "dragover"])
  drop.addEventListener(name, (event) => {
    event.preventDefault();
    drop.classList.add("over");
  });
for (const name of ["dragleave", "drop"])
  drop.addEventListener(name, () => drop.classList.remove("over"));
drop.addEventListener("drop", (event) => {
  event.preventDefault();
  if (event.dataTransfer.files.length) {
    input.files = event.dataTransfer.files;
    showFile();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!input.files[0]) return;
  const button = $("run");
  button.disabled = true;
  $("result").hidden = true;
  const started = performance.now();
  const tick = () => {
    status.textContent = `Transcribing… ${clock((performance.now() - started) / 1000)} (the first run also loads the model)`;
  };
  tick();
  const timer = setInterval(tick, 1000);
  try {
    const response = await fetch("/api/transcribe", { method: "POST", body: new FormData(form) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || response.statusText);
    last = data;
    render(data);
    status.textContent = "";
  } catch (error) {
    status.textContent = error.message;
  } finally {
    clearInterval(timer);
    button.disabled = false;
  }
});

function render(data) {
  $("stat-language").textContent = data.language || "—";
  $("stat-duration").textContent = clock(data.duration);
  $("stat-elapsed").textContent = `${data.elapsed.toFixed(1)} s`;
  $("stat-speed").textContent = data.elapsed ? `${(data.duration / data.elapsed).toFixed(1)}× real time` : "—";
  $("stat-device").textContent = `${data.backend} · ${data.device}`;
  const list = $("segments");
  list.replaceChildren(
    ...data.segments.map((segment) => {
      const item = document.createElement("li");
      const time = document.createElement("time");
      time.textContent = clock(segment.start);
      const text = document.createElement("span");
      text.textContent = segment.text.trim();
      item.append(time, text);
      return item;
    }),
  );
  $("result").hidden = false;
}

$("copy").addEventListener("click", async () => {
  if (!last) return;
  await navigator.clipboard.writeText(last.text);
  $("copy").textContent = "Copied";
  setTimeout(() => ($("copy").textContent = "Copy text"), 1500);
});

for (const button of document.querySelectorAll("[data-download]"))
  button.addEventListener("click", () => {
    if (!last) return;
    const kind = button.dataset.download;
    const body = kind === "txt" ? last.text : last[kind];
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([body], { type: "text/plain;charset=utf-8" }));
    link.download = `${(last.file || "transcript").replace(/\.[^.]+$/, "")}.${kind}`;
    link.click();
    URL.revokeObjectURL(link.href);
  });
