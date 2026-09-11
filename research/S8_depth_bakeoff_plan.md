# Plan — the depth-model bake-off (decided before anything is run; runs in a NEW session after the network policy is widened)

## Context

The pipeline's per-line law, its seams and its holes all sit on one input: the depth map. §11b
showed that the Depth Anything V2 Large map's extra bits are noise (lag-1 autocorrelation 0.16 of
the sub-8-bit part) and that the model changed the band by 45 % between two exports. Before any
tolerance or seam work continues, the input has to be chosen deliberately. The user wants a
bake-off with no blind alleys: criteria fixed in advance, one decision rule, one deliverable.

Survey (2026-09-11, sources in the reply): the candidates that publish edge/boundary numbers and
ship weights are **Depth Pro** (Apple, metric, 2.25 MP native, best published boundary F1;
reported fragility on sky/clutter), **MoGe-2** (Microsoft, metric point map + depth + normals +
FOV, boundary F1 comparable to Depth Pro with better relative geometry; MoGe-3 exists on arXiv
2607.17967 with an MLX port but no confirmed PyTorch release), **Pixel-Perfect Depth** (NeurIPS
2025, pixel-space diffusion, "flying-pixel-free", edge Chamfer 0.12 vs Depth Pro 0.14 vs MoGe-2
0.13 on Hypersim, Apache-2.0, weights on HF, slower), and **Depth Anything 3 Mono-Large**
(predicts depth not disparity; claims over DA2 without published boundary numbers; the natural
in-family upgrade). The baseline is the DA2-Large map already in hand.

This container cannot fetch weights (huggingface.co, hf-mirror and Apple's CDN are blocked by the
organisation's egress policy — 403 class, not retryable; PyPI and raw.githubusercontent are open;
no GPU). The user cannot change the policy from their settings. So the split is: **the user runs
one Colab notebook (five cells, ~20 minutes, T4 GPU) that writes every model's float `.npy` and
16-bit inverse-depth PNG into one zip; pushes the zip to `moebiusv2`; everything after that runs
here autonomously.** The cells are written from the repos' own READMEs / `run.py` (fetched
2026-09-11): Depth Pro (`apple/ml-depth-pro`, checkpoint from Apple's CDN, `model.infer(image,
f_px)` → metres), MoGe-2 (`Ruicheng/moge-2-vitl`, `model.infer(tensor)` → `depth` metres +
`mask`), Pixel-Perfect Depth (`gangweix/pixel-perfect-depth`, `run.py --img_path … --save_npy`,
4 sampling steps, DA2 semantics, needs `ppd.pth` + `depth_anything_v2_vitl.pth` in `checkpoints/`),
DA3-Mono-Large (`depth_anything_3.api.DepthAnything3.from_pretrained("depth-anything/DA3MONO-LARGE")`,
`model.inference([path]).depth[0]`). A model whose Colab cell fails is recorded as "not run" with
the error and the bake-off proceeds without it.

## What is fixed before running

**Models (four + baseline):** Depth Pro (`apple/DepthPro-hf` via transformers; fall back to the
apple repo + `depth_pro.pt`), MoGe-2 ViT-L (`Ruicheng/moge-2-vitl` via `pip install
git+https://github.com/microsoft/MoGe`), Pixel-Perfect Depth (`gangweix/pixel-perfect-depth`,
its released weights; default steps, no ensembling unless the README's default is ensembling),
DA3-Mono-Large (`depth-anything/DA3MONO-LARGE` via the ByteDance repo). Baseline: the existing
`depth16.png` (DA2-Large). Each model runs once on the photograph at its own native resolution
handling, output resampled to 851×1023 only if the model cannot take that size, and each produces
**a float `.npy` (the raw output, depth or inverse depth as the model defines it) and a 16-bit PNG
of inverse depth scaled 0…65535** (the app's convention: bright = near, affine in disparity).
Metric models' metres are converted to inverse depth before scaling; the metres are kept in the
`.npy`.

**Criteria (all existing instruments; nothing new is built):**
1. *Noise at the texel scale* (from the float): lag-1 autocorrelation and σ of the sub-8-bit
   part; the 5-texel along-row affine residual in disparity, as in §11b. This is the number that
   decides whether a 16-bit map is worth more than 8 bits and sizes the future noise term.
2. *Edge sharpness at the rims* (from the 8-bit requantisation baked through the app): the
   `[S3]` run structure (runs per line, median length), thin share, crossings; the band at
   15/25/35/45°; carrier–carrier seams and their class split (`seam_audit.py`); plate tears.
3. *Holes on the user's path* (`ui_path.js`, seams stretched, the seven offsets).
4. *Sky and the vignette*: whether the corners and any sky are put at infinity or as a wall
   (visual, on the map sheet), and the `[S2c]`/sky-class counts where present.
5. *Visual*: the maps sheet (all five maps at 8 bits + differences to the baseline) and an angle
   sheet per model at 27°, 45°, 52°/24°, 56°/19°.

**Decision rule:** rank by criterion 1 (lowest along-line noise relative to its own 8-bit
quantum) among models whose criterion 2 is not worse than the DA2 baseline on seams and tears
and whose criterion 3 is single-digit holes; criterion 4 breaks ties; the user's eye on the
sheets is the final authority. The winner becomes the photograph's depth (a default change — only
with the user's live pass), and its float output is the input to the noise-term tolerance design.

**What is out of scope:** no model fine-tuning, no ensembles across models, no more than one run
per model, no new instruments, no change to the app's law. If a model cannot be installed or run
on CPU within ~30 minutes of wall time, it is recorded as "not run: reason" and the bake-off
proceeds without it.

## Steps

1. (me, now) Write the Colab notebook cells to `research/bakeoff_colab.md` in the review repo
   and hand them to the user: cell 0 (upload the photograph as `photo.png`, common helpers that
   save `<model>.npy` + `<model>_disp16.png` with bright = near, sky/invalid at the far end),
   cells 1–4 (one model each, independent, each wrapped so a failure prints and moves on), cell 5
   (zip `bakeoff_outputs.zip` for one download).
2. (user) Run the notebook on a T4, download the zip, push it to `moebiusv2` main.
3. (me) Unzip to `research/bakeoff/`; criterion 1 offline on each `.npy` (the §11b script
   pattern); confirm each PNG is 16-bit, full range, the photograph's size.
4. For each model: 8-bit requantisation → `a257_probe.js` (TAG `photo_bo_<model>`) →
   `seam_audit.py` → `s16_table.py` extended to five columns; then `ui_path.js` (TAG
   `ui_bo_<model>`, OPTS `plane,wash,picture,off,35,off,stretched,off`) → `ui_holes.py`. Serial
   on port 8099; never edit `moebius.js` while a page loads.
5. Sheets: maps sheet (five maps + differences), one angle sheet per model.
6. Note §12 "The depth bake-off" in `research/S5_photograph_note.md` with the table, the
   decision, and the reasons for any model not run; commit and push both repos; send the sheets.

## Files

- new: `research/S8_depth_bakeoff_plan.md` (this plan, committed so the new session can read
  it), `research/bakeoff/` outputs, scratchpad chain `bakeoff_chain.sh`.
- reused: `harness/a257_probe.js`, `harness/ui_path.js`, `scratchpad/seam_audit.py` (levels
  argument), `scratchpad/s16_table.py`, `scratchpad/ui_holes.py`.

## Verification

Every model row in the §12 table is filled from a log line, not memory; the baseline row
reproduces §11b's numbers (64 354 seams / 155 874 tears at 8 bits); the decision rule is applied
as written; the sheets are sent.
