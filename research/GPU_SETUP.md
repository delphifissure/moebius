# Getting a GPU under this work (2026-09-15)

**Where we are.** The cloud sessions this work runs in have no GPU and a fixed memory budget; the docs point workloads
beyond that at two doors: *Remote Control* (Claude Code on your own hardware, Pro and Max) and *self-hosted environments*
(your own runners, Team and Enterprise, public beta). Nothing in the Anthropic-hosted environment can be configured to
have a GPU. The sandbox's network is the **Trusted** allowlist (Hugging Face, npm, pip, GitHub work; Modal, RunPod, Lambda,
Replicate, Vast were all unreachable when probed on 2026-09-15), so a GPU behind an API is also closed until an environment
with a **Custom** allowlist is made.

**What needs the GPU** (from R5, S26, S30 §6):

| job | VRAM | disk | notes |
|---|---|---|---|
| pix2gestalt (amodal completion, the red section) | ~10 GB | 16 GB ckpt | SD-1.5-class diffusion, 256²; minutes per object on CPU would be hours — GPU seconds |
| Amodal3R (per-object 3D: sides and back) | 16–24 GB | ~10 GB | TRELLIS-based, CUDA extensions (spconv, flash-attn); CUDA only |
| SAM 2.1 video (memory attention across a clip) | 8–16 GB | 0.2 GB | runs on CPU slowly; GPU for clips |
| RevealLayer (FLUX-dev backbone) / RLD | 40–62 GB | 30–40 GB | R5: 62 GB per image for RLD's setting; an 80 GB card |
| MoGe-3 refiner (FlexGEMM), DepthLab, DA3 | 12–24 GB | 5–10 GB | the S26 depth stage at full strength |
| a SAMEO reproduction (fine-tune a mask decoder) | 24–40 GB | datasets 50+ GB | hours to a day |

One **A100 80 GB or H100 80 GB** covers everything; an **L40S / A6000 48 GB** covers everything but RLD/RevealLayer; a
**24 GB card** (4090, L4, A10) covers pix2gestalt, Amodal3R, SAM 2 video, the depth models. Disk: 200 GB.

## Option 1 (recommended): a GPU box, and this session teleported onto it

Claude Code runs on the box itself; the agent has the GPU as a local device, exactly as it has the CPU here. Everything in
the repos (harness scripts, notes, the S27/S28/S29 paths) works unchanged.

1. **Rent** (or use your own machine with an NVIDIA card). RunPod "GPU Pod", Lambda Cloud, or any provider with a plain
   Ubuntu + CUDA image and SSH: A100 80 GB (≈ $1.5–2.5/h) for the full list, L40S 48 GB (≈ $1/h) without RLD. Add a
   200 GB volume. A spot/interruptible instance is fine for probes, not for a training run.
2. **On the box**, as your user (Ubuntu 22.04/24.04, CUDA 12.x driver already there on provider images):
   ```bash
   sudo apt-get update && sudo apt-get install -y git git-lfs ffmpeg python3.11 python3.11-venv nodejs npm
   curl -fsSL https://claude.ai/install.sh | bash        # Claude Code CLI
   claude auth login                                     # the same claude.ai account as this session
   mkdir -p /home/user && cd /home/user                  # the notes and harnesses assume these two paths side by side
   git clone https://github.com/delphifissure/moebius.git
   git clone https://github.com/delphifissure/moebiusv2.git
   python3.11 -m venv /home/user/gpuenv && . /home/user/gpuenv/bin/activate
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   pip install numpy pillow scipy onnxruntime-gpu transformers huggingface_hub playwright-core
   nvidia-smi                                            # the card, the driver, free memory
   ```
   (If `/home/user` is not writable, clone anywhere and `ln -s` the two directories to `/home/user/moebius` and
   `/home/user/moebiusv2`.)
3. **Continue this session there**, with its whole history:
   ```bash
   cd /home/user/moebius && git checkout claude/moebius-disocclusion-review-oa9exr
   claude --teleport session_01Nx9xQvX4gye4SywWYM9H9C
   ```
   Teleport needs a clean checkout of the same repository and the same claude.ai account. The terminal gets its own copy
   of the session; from then on the work happens on the box. To keep steering from a phone or the web, run
   `/remote-control` inside that session. (A fresh `claude` in the same directory also works — the notes carry the state;
   point it at `S30_one_pass_probe.md` §6 and `R5_layered_stack.md`.)
4. **First jobs, in order** (each is a probe with a number at the end, as before): pix2gestalt on the troll behind the
   woman (amodal mask → `obj_<k>_color/_visible.png` → the S27 import → the S28 red section); SAM 2.1 video propagation on
   a short clip; Amodal3R on the woman (a mesh; render its hidden faces to see what "orange beyond the silhouette" would
   be); then RevealLayer on the six pictures if the card has 80 GB.

Trades: + the agent works exactly as here, with the GPU; + all weights live on the box's disk once; + `nvidia-smi` and
real timings. − a machine to start and stop (bill by the hour; stop it when idle); − the first setup of Amodal3R /
RevealLayer is CUDA-extension work (an hour or two).

## Option 2: a GPU behind an API from a cloud session (no box to babysit)

Make a cloud environment with **Custom** network access (claude.ai/code → environment settings → **Network access:
Custom** → **Allowed domains**, one per line) and start sessions in it. Candidates: Modal (`api.modal.com`, `modal.com`;
token as environment variables `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` — visible to the session), RunPod serverless
(`api.runpod.ai`; key as an **API credential** on the environment, attached by the proxy so the session never sees it),
Replicate (`api.replicate.com`, same). The agent then writes a GPU function per model (a container image with the
weights in a volume) and calls it from the sandbox; results come back as files.

Trades: + per-second billing, nothing to stop; + scales to several jobs at once. − every model becomes a container
image to build and debug remotely; − unverified from here whether the provider's client survives the sandbox's HTTP
CONNECT proxy (Modal's gRPC in particular) until the allowlist exists; − large artefacts (a 16 GB checkpoint) move into
the provider's storage, not the sandbox.

## Option 3 (Team/Enterprise only): a self-hosted environment

An Owner turns on **Allow self-hosted environments** (admin settings → Cloud environments), creates an environment, and
runs the runner on a GPU host; sessions started from claude.ai can then be routed to it and execute on that host with
the GPU. Same effect as option 1 with the claude.ai UI kept; not available on Pro/Max.

**Recommendation:** option 1 with an A100 80 GB (or L40S 48 GB if RLD can wait), teleport this session, run the four
probes in §1's order. Budget: a few hours of GPU time for the probes; the SAMEO reproduction is a separate decision.
