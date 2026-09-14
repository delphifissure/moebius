# S29 — SAM 2.1 in the browser: live clicks (Sprint 21, 2026-09-14)

**Ask.** "Wire in SAM 2.1 in the browser for live clicks." Click an object in the app, see its mask, keep it; the kept
objects are the object map (export, Object view, layer import, S28 highlight). Behind one button; no default changed.

## 1. What runs where

| piece | what | size | source |
|---|---|---|---|
| runtime | onnxruntime-web 1.22.0 (`ort.min.js` + the WASM/JSEP binary it loads) | 0.36 + 22 MB | jsdelivr CDN (`window._ortBase` overrides) |
| image encoder | `onnx-community/sam2.1-hiera-small-ONNX` `vision_encoder.onnx` (+ `_data`), fp32 | 162 MB | Hugging Face, fetched once, kept in the Cache API (`window._sam2Base`, `_sam2Variant` = `fp16` / `quantized` / `q4f16` override) |
| prompt encoder + mask decoder | `prompt_encoder_mask_decoder.onnx` (+ `_data`) | 21 MB | same |
| provider | WebGPU when `navigator.gpu` exists, else WASM (`window._sam2EP` forces one) | | |

The export is Transformers.js's: encoder in `pixel_values` (1×3×1024×1024, resized without padding, ImageNet mean/std,
the processor's recipe) → three feature maps; decoder in `input_points` (1×1×P×2, in the 1024 frame), `input_labels`
(int64: 1 keep, 0 exclude), `input_boxes` (1×0×4, none) → `iou_scores` (3), `pred_masks` (3 × 256 × 256 logits),
`object_score_logits`. Masks are bilinearly upsampled to the plate grid (align_corners = false, as `F.interpolate`) and
thresholded at 0 (SAM 2's `mask_threshold`).

**Checked against the torch predictor** (`scratchpad/sam2onnx/validate.py`, the troll at 851 × 1023): single click on the
chest — the three ONNX candidates match torch's three at IoU 0.985 / 0.977 / 0.947 (4 472 / 57 748 / 310 104 px vs
4 427 / 56 741 / 293 998); four clicks — the best-scored ONNX candidate (135 189 px, iou 0.51) matches torch's
`multimask_output=False` mask (134 236 px) at IoU 0.988. The export returns the three multimask candidates always; torch's
single-mask path (dynamic stability fallback) chose the same one. CPU ORT encoder 4.6 s on 4 threads.

## 2. The click mode (`window._samLive`, button `🖱️ Click objects (SAM 2.1 live)`)

- **Rest pose held.** While the mode is on, `isSweeping` is set (the tracking block is skipped) and the camera sits at the
  reference eye. There a texel's screen position does not depend on its depth, so the layer's flat plane (its
  `PlaneGeometry`, ray in the mesh's local frame, uv from the bounding box) maps screen ↔ source exactly. Measured
  headlessly: the rendered colour at `srcToScreen(p)` vs the source colour at p, 400 random texels — median |Δ| 3.3 (8-bit
  channels) against 20 for a shuffled pairing; `screenToSrc(srcToScreen(123.4, 456.7))` = (123.40, 456.70).
- **One click = one decoder pass** (WASM headless 280–370 ms; the picture is encoded once: 24.6 s WASM single-thread here,
  seconds on WebGPU). The mask shown is the candidate SAM rates best by its own IoU estimate — the official predictor's
  `argmax(scores)`; no threshold of ours. **Tab** cycles to the other two (one click on the troll's chest gives the torso;
  Tab gives the whole figure or a muscle). **Alt-click** adds an exclude point (Shift/Ctrl/Meta-drag is the app's manual
  view drag, which takes the pointerdown first; Shift-click its split-plane drag). **Backspace** undoes the last click (or,
  with none pending, the last kept object). **Enter** keeps the object: it becomes the next id, the nearer object wins an
  overlap (mean disparity over the mask, as the offline script), `_setObjectIds` installs the map, and the S28 highlight of
  the new object comes on at once. **Esc** leaves; the kept map stays.
- While clicking the foreground is shown as it is (a new paint class 10 = untouched) with the pending mask blue, and the
  plate untinted (the C classes would show magenta / cyan through the silhouette fringes). The app's own canvas handlers
  (the depth-peek click that shows the portal-plane guide, the scale click, dblclick) are stopped at the window's capture
  phase while the mode is on — the first headless run had the guide's wireframe across every shot because the replayed
  click also reached the peek.
- Requires a Build first (the map lives on the plate grid `_qbSize`; front depth from `_qbDQ`).

## 3. Headless replay of the offline clicks (`harness/sam_live.js`, `harness/shots/samlive/troll/`)

Same clicks as S28 §2, dispatched as real pointer events at the screen position of each source pixel; WASM provider
(no WebGPU in headless); the ONNX files and ORT served locally (`harness/vendor/{ort,sam2}`, gitignored symlinks).

| object | clicks | candidates (px / SAM iou), best first | kept | IoU vs the offline script's mask |
|---|---|---|---|---|
| troll | (300,190) | 2 900 / 0.90, 4 131 / 0.52, 31 313 / 0.05 | | |
| | +(300,350) | 36 926 / 0.32, 120 812 / 0.21, 6 164 / 0.09 | | |
| | +(250,650) | 122 844 / 0.41, 40 509 / 0.35, 11 227 / 0.20 | | |
| | +(330,800) | **134 593 / 0.51**, 71 223 / 0.44, 7 883 / 0.20 | 134 593 px | **0.993** (offline 134 236) |
| woman | (470,700) | 32 237 / 0.54, 15 266 / 0.40, 1 201 / 0.09 | | |
| | +(455,500) | **28 736 / 0.857**, 33 280 / 0.853, 3 068 / 0.17 | 28 736 px | 0.89 (offline 32 289: SAM's own near-tie, 0.857 vs 0.853 — Tab gives the other) |

Start-up in the sandbox: 214 s (183 MB from the local server into the Cache API + sessions + encode); on a repeat visit
the files come from the cache. Decoder per click 280–370 ms on WASM. Band continuation on the live map: 258 943 band
texels, 204 762 joined, 54 181 unjoined (the S28 figures with the offline map: 194 739 / 64 204).

## 4. What to expect on a real machine (LIVE_PASS §7)

Chrome / Edge with WebGPU: first visit downloads 183 MB (progress in the status line), encode in a few seconds, clicks
instant. Safari / Firefox without WebGPU: WASM, encode 10–40 s, clicks under half a second. The files are cached per
origin (open the app from the same address each time). If the CDN or Hugging Face is blocked, put the files next to the app
and set `window._ortBase = 'vendor/ort/'`, `window._sam2Base = 'vendor/sam2/'` in the console before pressing the button.

## 5. Not done / next

- The amodal outline (the whole troll behind the woman) still needs an amodal decoder (pix2gestalt / a SAMEO reproduction,
  R5 §1e); the browser path gives the visible mask, which is what SAMEO's front end would also start from.
- Box prompts in the browser (drag a rectangle) would be the SAMEO input form; the export accepts `input_boxes`. Not wired.
- The single-thread WASM encode could be 3–4× faster with cross-origin isolation (COOP/COEP headers → threads); a static
  file server does not send them, so it is left as is.
