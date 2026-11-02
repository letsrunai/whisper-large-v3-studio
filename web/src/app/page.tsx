import { Studio } from "@/components/studio";

export default function Home() {
  return (
    <>
      <main className="mx-auto w-full max-w-3xl px-5 pt-12 pb-6">
        <header className="mb-7">
          <p className="text-accent text-sm font-semibold tracking-wide">
            letsrunai · open model, your machine
          </p>
          <h1 className="mt-1.5 mb-2 text-3xl leading-tight font-bold sm:text-4xl">
            Whisper large-v3 Studio
          </h1>
          <p className="text-muted">
            Drop an audio or video file. Get timestamped text and subtitles. Nothing leaves this
            computer.
          </p>
        </header>
        <Studio />
      </main>
      <footer className="text-muted mx-auto w-full max-w-3xl px-5 pt-4 pb-10 text-sm">
        Model:{" "}
        <a
          className="text-foreground underline"
          href="https://huggingface.co/openai/whisper-large-v3"
        >
          openai/whisper-large-v3
        </a>{" "}
        (Apache-2.0) · Code:{" "}
        <a
          className="text-foreground underline"
          href="https://github.com/letsrunai/whisper-large-v3-studio"
        >
          letsrunai/whisper-large-v3-studio
        </a>
      </footer>
    </>
  );
}
