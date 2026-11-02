# Colab

No GPU on your machine? This notebook runs [Whisper large-v3 Studio](../README.md) on Colab's GPU.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/letsrunai/whisper-large-v3-studio/blob/main/colab/whisper-large-v3-studio.ipynb)

1. Open it with the badge.
2. **Runtime → Change runtime type → T4 GPU** (any GPU works).
3. Run the cells from top to bottom.

It installs [server/](../server/) and opens its lite page inside Colab. The Next.js page in [web/](../web/) is for running on your own machine, where the build step is one command.

The last cell transcribes a file you upload and prints the time it took and the peak GPU memory.
