# Colab

No GPU on your machine? This notebook runs [Whisper large-v3 Studio](../README.md) on Colab's GPU.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/letsrunai/whisper-large-v3-studio/blob/main/colab/whisper-large-v3-studio.ipynb)

1. Open it with the badge.
2. **Runtime → Change runtime type → T4 GPU** (any GPU works).
3. Run the cells from top to bottom: install, upload a file, transcribe, download the `.srt`.

The transcribe cell prints the text, the time it took, the speed against real time and the peak GPU memory.

It installs a tagged release of [server/](../server/), so the notebook keeps working while `main` changes.

## The web app on Colab

The last section opens the lite web page inside Colab. Colab's free tier does not allow working mainly through a web UI and may end such sessions ([Colab FAQ](https://research.google.com/colaboratory/faq.html)), so that section is only for runtimes paid with compute units. On the free tier, use the cells. The full Next.js page in [web/](../web/) is for running on your own machine.
