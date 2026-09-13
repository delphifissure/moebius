# S26 — The depth stage on truth: can a depth model recover a hidden layer's depth from its completed picture? (Sprint 18, 2026-09-13)

The R5 stack puts a depth model after the layer model: *decompose the picture into complete layers, run a depth model on
each layer, normalise against the full-scene depth* (the user's proposal, R5 §3). R5 §5 said the depth stage could be
scored **before** any layer model exists, because the truth kit holds every hidden layer's exact colour and depth. This
note is that test. It separates "the depth stage works" from "the layer model works": the layer model is replaced by the
truth's own completed colour (the best a RevealLayer / RLD could ever return), and three depth stages are scored against
the truth's hidden depth, next to the plane law the app uses today, on the same texels.

**One-line result.** The two are complementary and the split is by *class*, not by scene: on **background layers** (what is
behind the object) the plane law beats every model on 19 of 19 scenes, typically by an order of magnitude, and the models
fail outright where the hidden depth range lies outside the visible one (the hedge wall S32, the hills behind the crown in
S15); on the **object's own back faces** (self-occlusion) every model beats the plane law on 16–17 of 17 scenes, by one to
two orders of magnitude, because the plane law has no notion of an object's far side. DepthLab, run as a completion model
with our known depth, is the weakest of the three on both sets in this setting (§4).

## 1. Protocol (all offline, CPU; scripts in `research/s26/`)

**Pictures.** For each scene with an env45 truth (S2, S5, S7, S9, S10, S11, S12, S15, S16, S26, S27, S31, S32, P1–P6; 19
scenes, plate 800×450) two completed pictures are built from `scope_gt.npz` (`ds_build.py`):
- `peel1`: the front surface removed at every texel that has an ever-visible hidden layer; the first hidden layer's
  exact colour is painted there (any class 2–5). This is the "first ever-visible hidden layer" the plane law is scored
  against in every kit note since Sprint 1.
- `bg`: the occluding *object* removed entirely: the first hidden layer that is background or another thing (class 2/3);
  texels whose hidden layers are all the object's own back faces keep the source colour. This is what a RevealLayer
  background layer is.
- Revealed sky gets the scene's sky colour; it has no finite depth and is excluded from the metres error, as in
  `check_app_band.py`.

**Sets scored** (per texel, truth = that layer's depth in metres behind the window): `bg` (class 2/3 layers; 4.5 k – 70 k
texels per scene), `own` (first hidden layer is the object's own back face, class 4/5; 0.3 k – 34 k), `peel1` (both).

**Models.** *DA3-Mono-Large* (the app's chosen depth source; process_res 1008 as in the S8 bake-off; 10 s/picture).
*MoGe-3 ViT-L* (MIT, weights of 2026-08-18) **without its sparse 3D refiner**: the refiner needs FlexGEMM, a CUDA/Triton
kernel package with no CPU build, so the model was built from its checkpoint with the refiner dropped and run with
`refine_steps=0` — MoGe-3's base prediction, and labelled as such everywhere (16 s/picture). *DepthLab* (Apache-2.0,
Marigold/SD2-based RGB + known depth + mask → completed depth): the two UNets loaded from the released state dicts, CLIP-H
image conditioning, README settings (processing 768, strength 0.8, blend on, guidance 1; 20 DDIM steps, the README's lower
recommended count), fp32 on CPU (155 s/picture); input = the completed picture, known depth = the true visible depth on the
texels whose colour is the source picture's, mask = the hidden set + sky. As DepthLab's own `infer.py` does, the unknown
region of the known-depth map is filled with the nearest known value before the pipeline (the first run of the driver
left zeros there, and DepthLab read every hole as "nearest possible" — S2's wall came back at 0.005 m; the buffer showed
it, the driver was fixed and every DepthLab number here is from the rerun). A second DepthLab run with strength 1.0 (the
model alone, no interpolated prior) on six scenes is reported separately (§4).

**Alignment — the "normalise against the scene depth" step, made honest.** A model's output is fitted to the true visible
depth on the *visible* texels only (`m_fit`: colour is the source's, depth finite), never on the hidden ones: a robust
affine fit (two rounds of 3×MAD trimming) in three spaces — disparity affine, depth affine, depth scale — and the space
with the smallest visible residual in metres is kept. That choice uses visible data only. Then:
- **global + clamp**: the fitted output on the hidden set, with the ordering clamp *hidden ≥ visible at the same texel*
  (a135: a hidden layer lies behind the surface that hides it). This is the stack's honest default.
- **local**: the user's normalisation in its strong form — per connected hidden component the fit is made only on the
  visible texels within one equivalent radius √(A/π) of the component (scale-free; no constant), falling back to the global
  fit below 100 fit texels.
- **oracle**: the same fit made on the hidden truth itself — the best *any* normalisation could do with that output's
  shape; it separates "shape wrong" from "scale/offset wrong". Not a usable arm.
- A prediction at or beyond infinity (a disparity fit at ≤ 0) is not dropped: it is scored at the scene's farthest finite
  surface and counted (`inf`). The first draft of the scorer dropped them, which flattered DA3 on S15 bg by 14×
  (0.087 → 1.20 m); corrected before anything was written down.

**Plane law.** `plateF.f32` from the newest current-law probe of each scene (`_16plane*_c`, else `_ceil`, else the base
plane probe), in metres through the app's depth law, on exactly the same texels. Its band covers 97–100 % of the hidden
set on every scene except S5 (thin poles, 51 %) and S32 (81–86 %).

**Control.** Each model was also run on the source picture; its visible residual after the fit is the "can it read this
synthetic scene at all" number: 0.0003–0.005 m on the miniature scenes (0.3–4 % of scene depth), 0.11–0.19 m on S15
(8.6 m deep, sky). The kit's flat-shaded renders are readable by both models.

## 2. Results

Median |error| in metres on each set; the plane law next to each model's *global fit + clamp*, the *local* fit, and the
*oracle* bound. (`tables.md` in `research/s26/` has every number; `sheet_<S>.png` the buffers.)

**background and other-thing layers (classes 2/3)** — median |error| in metres (in brackets: % of the set's hidden-depth p95)

| scene | scene depth | n | plane law | da3 clamp | da3 local | moge3 clamp | moge3 local | depthlab clamp | depthlab local | depthlab1 clamp | depthlab1 local | oracle (best model) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.192 | 22383 | 0.0000 (0%) | 0.0018 (1%) | 0.0005 (0%) | 0.0011 (1%) | 0.0007 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| P2 | 0.192 | 32836 | 0.0000 (0%) | 0.0025 (1%) | 0.0021 (1%) | 0.0037 (2%) | 0.0039 (2%) | 0.0015 (1%) | 0.0015 (1%) | 0.0043 (2%) | 0.0043 (2%) | 0.0011 (1%) |
| P3 | 0.192 | 35794 | 0.0000 (0%) | 0.0016 (1%) | 0.0011 (1%) | 0.0014 (1%) | 0.0017 (1%) | 0.0003 (0%) | 0.0003 (0%) | – | – | 0.0003 (0%) |
| P4 | 0.192 | 45879 | 0.0000 (0%) | 0.0030 (2%) | 0.0027 (1%) | 0.0029 (2%) | 0.0029 (2%) | 0.0009 (0%) | 0.0009 (0%) | – | – | 0.0011 (1%) |
| P5 | 0.192 | 24961 | 0.0000 (0%) | 0.0018 (1%) | 0.0017 (1%) | 0.0021 (1%) | 0.0010 (1%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| P6 | 0.192 | 26544 | 0.0000 (0%) | 0.0015 (1%) | 0.0012 (1%) | 0.0009 (0%) | 0.0009 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| S10 | 0.096 | 52676 | 0.0000 (0%) | 0.0002 (0%) | 0.0002 (0%) | 0.0008 (1%) | 0.0002 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| S11 | 0.096 | 36512 | 0.0000 (0%) | 0.0005 (0%) | 0.0000 (0%) | 0.0009 (1%) | 0.0000 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0000 (0%) |
| S12 | 0.128 | 16975 | 0.0000 (0%) | 0.0013 (1%) | 0.0000 (0%) | 0.0006 (1%) | 0.0000 (0%) | 0.0001 (0%) | 0.0000 (0%) | – | – | 0.0001 (0%) |
| S15 | 8.64 | 17669 | 0.0027 (0%) | 1.2019 (17%) | 0.4777 (7%) | 1.1514 (16%) | 0.3460 (5%) | 0.0310 (0%) | 0.0310 (0%) | 0.9396 (13%) | 0.0533 (1%) | 0.0196 (0%) |
| S16 | 0.16 | 4513 | 0.0000 (0%) | 0.0016 (1%) | 0.0013 (1%) | 0.0032 (2%) | 0.0010 (1%) | 0.0006 (0%) | 0.0007 (0%) | – | – | 0.0002 (0%) |
| S2 | 0.128 | 16454 | 0.0000 (0%) | 0.0006 (0%) | 0.0003 (0%) | 0.0019 (1%) | 0.0007 (1%) | 0.0003 (0%) | 0.0003 (0%) | 0.0003 (0%) | 0.0003 (0%) | 0.0002 (0%) |
| S26 | 0.112 | 25631 | 0.0000 (0%) | 0.0008 (1%) | 0.0005 (0%) | 0.0027 (2%) | 0.0011 (1%) | 0.0004 (0%) | 0.0004 (0%) | – | – | 0.0004 (0%) |
| S27 | 0.24 | 4894 | 0.0000 (0%) | 0.0008 (0%) | 0.0006 (0%) | 0.0032 (1%) | 0.0004 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| S31 | 0.128 | 70400 | 0.0000 (0%) | 0.0006 (0%) | 0.0039 (3%) | 0.0145 (11%) | 0.0138 (11%) | 0.0645 (50%) | 0.0647 (51%) | 0.0735 (57%) | 0.0735 (57%) | 0.0000 (0%) |
| S32 | 43.2 | 40000 | 0.0002 (0%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.7521 (42%) | 0.0366 (2%) |
| S5 | 0.08 | 1608 | 0.0000 (0%) | 0.0002 (0%) | 0.0001 (0%) | 0.0012 (2%) | 0.0008 (1%) | 0.0000 (0%) | 0.0000 (0%) | – | – | 0.0000 (0%) |
| S7 | 0.192 | 35348 | 0.0000 (0%) | 0.0013 (1%) | 0.0011 (1%) | 0.0009 (0%) | 0.0013 (1%) | 0.0002 (0%) | 0.0002 (0%) | 0.0015 (1%) | 0.0015 (1%) | 0.0002 (0%) |
| S9 | 0.112 | 62682 | 0.0000 (0%) | 0.0011 (1%) | 0.0009 (1%) | 0.0021 (2%) | 0.0023 (2%) | 0.0006 (1%) | 0.0006 (1%) | – | – | 0.0035 (3%) |

**the object's own back faces (classes 4/5)** — median |error| in metres (in brackets: % of the set's hidden-depth p95)

| scene | scene depth | n | plane law | da3 clamp | moge3 clamp | depthlab clamp | depthlab1 clamp | oracle (best model) |
|---|---|---|---|---|---|---|---|---|
| P1 | 0.192 | 6187 | 0.1309 (68%) | 0.0107 (6%) | 0.0132 (7%) | 0.1283 (67%) | – | – |
| P2 | 0.192 | 33945 | 0.0182 (10%) | 0.0049 (3%) | 0.0048 (3%) | 0.1111 (58%) | 0.0066 (3%) | – |
| P3 | 0.192 | 23207 | 0.0752 (39%) | 0.0066 (3%) | 0.0061 (3%) | 0.1296 (67%) | – | – |
| P4 | 0.192 | 28727 | 0.0378 (20%) | 0.0071 (4%) | 0.0067 (3%) | 0.1105 (58%) | – | – |
| P5 | 0.192 | 1559 | 0.1360 (71%) | 0.0568 (30%) | 0.0829 (43%) | 0.1359 (71%) | – | – |
| P6 | 0.192 | 2241 | 0.1355 (71%) | 0.0943 (49%) | 0.1335 (70%) | 0.1356 (71%) | – | – |
| S10 | 0.096 | 10815 | 0.0482 (50%) | 0.0056 (6%) | 0.0166 (17%) | 0.0468 (49%) | – | – |
| S11 | 0.096 | 7934 | 0.0541 (56%) | 0.0505 (53%) | 0.0524 (55%) | 0.0541 (56%) | – | – |
| S12 | 0.128 | 3202 | 0.0762 (60%) | 0.0073 (6%) | 0.0695 (54%) | 0.0751 (59%) | – | – |
| S15 | 8.64 | 13448 | 3.7916 (53%) | 0.0096 (0%) | 0.0066 (0%) | 2.6474 (37%) | 1.9608 (28%) | – |
| S2 | 0.128 | 2813 | 0.0468 (37%) | 0.0085 (7%) | 0.0038 (3%) | 0.0046 (4%) | 0.0051 (4%) | – |
| S26 | 0.112 | 4447 | 0.0571 (51%) | 0.0067 (6%) | 0.0096 (9%) | 0.0479 (43%) | – | – |
| S27 | 0.24 | 337 | 0.1135 (47%) | 0.0089 (4%) | 0.0101 (4%) | 0.0528 (22%) | – | – |
| S32 | 43.2 | 2400 | 0.0072 (0%) | 0.0034 (0%) | 0.0034 (0%) | 0.0037 (0%) | 0.0037 (0%) | – |
| S5 | 0.08 | 402 | 0.0559 (70%) | 0.0284 (36%) | 0.0546 (68%) | 0.0558 (70%) | – | – |
| S7 | 0.192 | 22825 | 0.1258 (66%) | 0.0074 (4%) | 0.0071 (4%) | 0.1179 (61%) | 0.0271 (14%) | – |
| S9 | 0.112 | 776 | 0.0320 (29%) | 0.0320 (29%) | 0.0347 (31%) | 0.0315 (28%) | – | – |

**first hidden layer, all classes** — median |error| in metres (in brackets: % of the set's hidden-depth p95)

| scene | scene depth | n | plane law | da3 clamp | da3 local | moge3 clamp | moge3 local | depthlab clamp | depthlab local | depthlab1 clamp | depthlab1 local | oracle (best model) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.192 | 22383 | 0.0000 (0%) | 0.0040 (2%) | 0.0020 (1%) | 0.0044 (2%) | 0.0030 (2%) | 0.0014 (1%) | 0.0010 (1%) | – | – | 0.0028 (1%) |
| P2 | 0.192 | 42210 | 0.0124 (6%) | 0.0049 (3%) | 0.0339 (18%) | 0.0055 (3%) | 0.0613 (32%) | 0.1045 (54%) | 0.1046 (54%) | 0.0069 (4%) | 0.0084 (4%) | 0.0047 (2%) |
| P3 | 0.192 | 36878 | 0.0098 (5%) | 0.0072 (4%) | 0.0199 (10%) | 0.0090 (5%) | 0.0278 (14%) | 0.1182 (62%) | 0.1183 (62%) | – | – | 0.0078 (4%) |
| P4 | 0.192 | 47380 | 0.0096 (5%) | 0.0069 (4%) | 0.0207 (11%) | 0.0086 (4%) | 0.0139 (7%) | 0.0831 (43%) | 0.0831 (43%) | – | – | 0.0083 (4%) |
| P5 | 0.192 | 24961 | 0.0000 (0%) | 0.0028 (1%) | 0.0027 (1%) | 0.0025 (1%) | 0.0018 (1%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| P6 | 0.192 | 26544 | 0.0000 (0%) | 0.0030 (2%) | 0.0034 (2%) | 0.0014 (1%) | 0.0012 (1%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0001 (0%) |
| S10 | 0.096 | 52680 | 0.0000 (0%) | 0.0018 (2%) | 0.0011 (1%) | 0.0017 (2%) | 0.0008 (1%) | 0.0005 (1%) | 0.0005 (1%) | – | – | 0.0011 (1%) |
| S11 | 0.096 | 36512 | 0.0000 (0%) | 0.0016 (2%) | 0.0006 (1%) | 0.0019 (2%) | 0.0001 (0%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0012 (1%) |
| S12 | 0.128 | 16975 | 0.0000 (0%) | 0.0016 (1%) | 0.0000 (0%) | 0.0012 (1%) | 0.0000 (0%) | 0.0003 (0%) | 0.0000 (0%) | – | – | 0.0003 (0%) |
| S15 | 8.64 | 26140 | 0.1818 (3%) | 0.1261 (2%) | 0.0777 (1%) | 0.0213 (0%) | 0.3651 (5%) | 1.6709 (23%) | 1.6660 (23%) | 1.3543 (19%) | 1.3618 (19%) | 0.0170 (0%) |
| S16 | 0.16 | 4513 | 0.0000 (0%) | 0.0016 (1%) | 0.0013 (1%) | 0.0032 (2%) | 0.0010 (1%) | 0.0006 (0%) | 0.0007 (0%) | – | – | 0.0002 (0%) |
| S2 | 0.128 | 16454 | 0.0000 (0%) | 0.0008 (1%) | 0.0004 (0%) | 0.0016 (1%) | 0.0008 (1%) | 0.0005 (0%) | 0.0005 (0%) | 0.0007 (1%) | 0.0007 (1%) | 0.0003 (0%) |
| S26 | 0.112 | 25631 | 0.0000 (0%) | 0.0029 (3%) | 0.0017 (2%) | 0.0050 (4%) | 0.0048 (4%) | 0.0046 (4%) | 0.0046 (4%) | – | – | 0.0014 (1%) |
| S27 | 0.24 | 4894 | 0.0000 (0%) | 0.0022 (1%) | 0.0012 (0%) | 0.0012 (0%) | 0.0014 (1%) | 0.0005 (0%) | 0.0005 (0%) | – | – | 0.0002 (0%) |
| S31 | 0.128 | 70400 | 0.0000 (0%) | 0.0006 (0%) | 0.0039 (3%) | 0.0145 (11%) | 0.0138 (11%) | 0.0645 (50%) | 0.0647 (51%) | 0.0735 (57%) | 0.0735 (57%) | 0.0000 (0%) |
| S32 | 43.2 | 42400 | 0.0002 (0%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.7197 (40%) | 0.0378 (2%) |
| S5 | 0.08 | 1608 | 0.0000 (0%) | 0.0035 (4%) | 0.0058 (7%) | 0.0017 (2%) | 0.0009 (1%) | 0.0001 (0%) | 0.0001 (0%) | – | – | 0.0082 (10%) |
| S7 | 0.192 | 36559 | 0.0103 (5%) | 0.0064 (3%) | 0.0166 (9%) | 0.0086 (4%) | 0.0199 (10%) | 0.1000 (52%) | 0.1001 (52%) | 0.0213 (11%) | 0.0214 (11%) | 0.0068 (4%) |
| S9 | 0.112 | 62682 | 0.0000 (0%) | 0.0012 (1%) | 0.0009 (1%) | 0.0025 (2%) | 0.0028 (2%) | 0.0012 (1%) | 0.0012 (1%) | – | – | 0.0023 (2%) |

**Wins (median |error|, global fit + clamp vs the plane law)**

- bg: da3 beats the plane law on 0 of 19 scenes
- bg: moge3 beats the plane law on 0 of 19 scenes
- bg: depthlab beats the plane law on 0 of 19 scenes
- bg: depthlab1 beats the plane law on 0 of 6 scenes
- own: da3 beats the plane law on 17 of 17 scenes
- own: moge3 beats the plane law on 16 of 17 scenes
- own: depthlab beats the plane law on 12 of 17 scenes
- own: depthlab1 beats the plane law on 5 of 5 scenes
- peel1: da3 beats the plane law on 5 of 19 scenes
- peel1: moge3 beats the plane law on 5 of 19 scenes
- peel1: depthlab beats the plane law on 0 of 19 scenes
- peel1: depthlab1 beats the plane law on 1 of 6 scenes

## 3. What the numbers say

1. **Background layers: the plane law is the right instrument.** Exact (0.0000 m) on every planar scene; 0.0027 m on the
   hills behind S15's crown; 0.0002 m on the ground beyond the hedge wall (S32). The models with the global fit land at
   0.0002–0.004 m on the planar scenes (0.2–4 % of scene depth — good, but never better), and fail on the two scenes where
   the hidden background is not in the visible depth range: S15 bg 1.0–1.2 m (78–80 % of the hidden hill texels read as
   sky by DA3 and MoGe-3), S32 0.72–0.75 m (both models; the visible set is a 1–5 cm strip in front of a hedge that
   fills the frame, and no affine extrapolates it 40× outward; the oracle at 0.037 m shows their *shape* is right, the
   scale/offset is unrecoverable from what is visible). The local fit helps only where the hidden component is small
   and its rim is informative (S11/S12 bg to 0.0000; S15 bg 1.20 → 0.48 for DA3) and hurts elsewhere (S31 0.0006 →
   0.0039; S15 peel1 for MoGe-3 0.02 → 0.37, the crown's many small components each get a noisy fit). **This is the
   answer to "normalise against the full-scene depth": it is exact when the hidden range is inside the visible range and
   it cannot be made to work when it is not — and a disocclusion band is, by construction, often behind everything
   visible near it.**
2. **The object's own back faces: the models are the right instrument.** The plane law puts the *background* there
   (S15 crown and trunk backs: 3.79 m off; P1–P6, S7, S10–S12, S26: 0.03–0.14 m, i.e. the whole object thickness), and no
   variant of it can know better. DA3 / MoGe-3 with the clamp: S15 0.0096 / 0.0066 m, P2 0.0049 / 0.0048, P3 0.0066 /
   0.0061, S7 0.0074 / 0.0071, S10 0.0056 / 0.017, S2 0.0085 / 0.0038 — a 5–400× improvement. The clamp matters: without
   it the raw model put the back faces *in front of* the front face on P2–P4 and S7 (0.02–0.06 m); with it the error is
   a few millimetres. Thin objects are the exception (S5 poles, S9, S11's thin things, P5/P6's small leaves: 0.03–0.13 m,
   the clamp cannot help because the model never resolved the object).
3. **DepthLab is a third kind of instrument: it continues the known depth, very well, and that is all it does.** Given
   the true visible depth around the hole it returns the background layer at 0.0001–0.0006 m on every planar scene
   (better than DA3 / MoGe-3's 0.0002–0.004, because it is anchored in metres and needs no fit) and 0.031 m on the hills
   behind S15's crown where the pure models fail at 1.2 m — but never better than the plane law (0.0000 / 0.0027), and
   it fails where the plane law does not: S31's wall behind a hedge that spans the frame (0.065 m, a wide hole filled
   with a gradient towards the floor) and S32 (0.75 m, like everything else). On the object's own back faces it behaves
   like the plane law (P1–P4, S7, S10, S12, S15, S26: 0.05–2.6 m, the background put where the object's back is),
   because the known depth around an object is the background; only S2, S27 and S32 come out right. Its visible residual
   is 0.0001–0.015 m by construction (blend diffusion keeps the known latents). So DepthLab is a learned continuation of
   the known depth: on backgrounds it lands between the pure models and the plane law, on self-occlusion it is the plane
   law's equal. Its strength-1 run is §4. It is also 15× slower than DA3 and needs 13 GB of weights.
4. **What this does to the R5 stack.** Stage 4 ("depth of each layer") splits by class, and both halves already exist:
   the plane law for the background layer (it is exact where the background is a continued surface, which is the only
   case a background *can* be predicted without the layer's own evidence), and a depth model on the completed *object*
   layer with the ordering clamp for the object's own far side. The normalisation for the object layer must be fitted on
   that object's visible depth (its front), not on the whole picture — the local fit's idea, applied per object rather
   than per hole. The models' background numbers (0.2–4 % of scene depth on planar scenes) also say what to expect from
   the layer-model route when the background is *not* a continued surface: a few per cent, not the plane law's exactness.
5. **Caveats, stated.** (a) The kit's scenes are synthetic and flat-shaded; the models read them (control), but their
   priors were built on photographs. (b) The completed colour is the *truth's*; a real layer model adds its own error on
   top. (c) MoGe-3 ran without its refiner. (d) DepthLab ran at 20 steps and one seed; the paper uses 50 and GPU. (e) The
   kit's depths are in metres at miniature scale (window 0.16 m); every number is also given as a percentage of the set's
   hidden depth p95 for that reason. (f) S15 and S32 are the only scenes whose hidden background is not inside the
   visible depth range; the porous set P1–P6 has open backgrounds and reads as "planar".

## 4. DepthLab at strength 1.0

Strength 1.0 removes DepthLab's interpolated prior: the hole is denoised from pure noise, with the known region still
held by blend diffusion. Six scenes, same everything else (`depthlab1` columns above; 180–240 s/picture).

| scene | set | strength 0.8 (clamp) | strength 1.0 (clamp) | plane law | best pure model (clamp) |
|---|---|---|---|---|---|
| S15 | bg (hills behind the crown) | 0.031 | 0.940 | 0.0027 | 1.15 (MoGe-3) |
| S15 | own (crown / trunk backs) | 2.65 | 1.96 | 3.79 | 0.0066 (MoGe-3) |
| P2 | bg | 0.0015 | 0.0043 | 0.0000 | 0.0025 (DA3) |
| P2 | own | 0.111 | 0.0066 | 0.018 | 0.0048 (MoGe-3) |
| S7 | bg | 0.0002 | 0.0015 | 0.0000 | 0.0009 (MoGe-3) |
| S7 | own | 0.118 | 0.027 | 0.126 | 0.0071 (MoGe-3) |
| S31 | bg (wall behind a frame-wide hedge) | 0.065 | 0.074 | 0.0000 | 0.0006 (DA3) |
| S32 | bg (ground beyond the hedge wall) | 0.752 | 0.752 | 0.0002 | 0.752 |
| S2 | bg / own | 0.0003 / 0.0046 | 0.0003 / 0.0051 | 0.0000 / 0.047 | 0.0006 / 0.0038 |

Reading: with the prior (0.8) DepthLab is a continuation of the known depth (backgrounds good, own faces wrong); without
it (1.0) it behaves like a pure depth model conditioned on the known region (own faces recovered on P2 and S7, backgrounds
worse, S15 lost both ways). Neither setting beats the plane law on a background or the clamped pure models on an object's
far side, and the two settings want opposite classes — the same split as §3, seen inside one model.

## 5. Files

`research/s26/`: `ds_build.py` (pictures + truth), `ds_run.py` (DA3 / MoGe-3 base), `ds_depthlab.py` (DepthLab driver,
CPU, fp32, tagged runs), `ds_score.py` (alignment, clamp, local, oracle, plane law, infinity rule), `ds_sheet.py`,
`ds_table.py`, `scores.json`, `tables.md`, `timing.json`, `sheet_<S>.png` for all 19 scenes. Disk note: to fit DepthLab's
weights the superseded intermediate-sprint probe dumps (`*_s10d/_s12/_s13/_s14/_s14b`, `photo_v*`, `photo_plane_v*`,
`b_*_s14*`, `b_*_repo8*`) and the MoGe-2 cache were deleted from the ignored `harness/shots/a257probe`; the `_c`/`_ceil`
probes every note cites are untouched.
