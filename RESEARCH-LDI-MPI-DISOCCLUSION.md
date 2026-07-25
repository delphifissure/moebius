# Layered Depth Images, Multiplane Images, and Disocclusion Inpainting
## A meta-analysis, 1993–2026, read against the moebius architecture

Companion to `REVIEW.md`. Where `REVIEW.md` measures what the build does, this
document asks a different question: **of the things this project keeps
rediscovering, which were already settled by the field, which were settled and
then abandoned for good reasons, and which are genuinely open?**

Scope constraints taken from the brief:
- open source, **no commercial licence required**
- **performant**, ideally training-free; a trained model is acceptable only if
  its weights AND its training data are legally unencumbered
- must work on **any image** — photograph, oil painting, comic/ink art

Every licence claim below was checked against the primary repository or licence
file in July 2026 and is cited. Licences change; re-verify at integration time.
I am not a lawyer and none of this is legal advice.

---

## 0. Executive summary

**Three things this project got right that the literature agrees with, and
should be protected:**

1. **"Complete the world without the foreground," not "fill a band."**
   (`REVIEW.md` §4, Addendum 3.) This is the field's settled answer, arrived at
   independently three times: LDI-with-connectivity, the VFX "clean plate", and
   amodal completion. A band of N pixels is provably always the wrong width.
2. **Depth-displaced layers, not flat planes** (Addendum 3, "MPI shape").
   This is exactly the MPI→layered-mesh conversion that Google shipped for
   browser/mobile light-field video in 2020, and exactly Samsung's
   multiplane-to-layer result. It is the right endgame.
3. **"The ink was the segmentation all along"** (Addendum 56). This is the
   single most important observation in the whole review, and the field agrees:
   layer boundaries should come from segmentation/matting, not from thresholded
   depth. Everything downstream of that insight got easier.

**Four rabbit holes, in descending order of cost:**

1. **The view cone is the bug.** One number — the app's own measured `k`,
   the screen shift in source texels across the full depth range at the cone
   rim — simultaneously causes the 8-bit failure, the fold limit, the v2
   ghosting/banding, the band starvation, the 9× plate margin, and the 60-second
   backstop sweep. At 851 px source, `k = 775`. Everything else is downstream.
   §1 derives this. **This is the finding.**
2. **Screen-space band/rind/cut heuristics.** The 3DTV industry spent
   2005–2016 on exactly this family and concluded it has a hard ceiling. D1–D11
   are not novel defects; they are that literature's known failure list.
3. **Chasing depth-estimator errors with renderer geometry.** Stroke-depth
   repair, ink-follows-layer, the adopt-map, the footing rule, the wire rule —
   ~15 addenda of geometry surgery on what is a depth-estimation problem with a
   published fix (mask-guided layered depth refinement) and a better input.
4. **Precision applied before the law is fixed.** a101/a102 refined the fold
   criterion to 0.03% and changed no rendered pixel (Addendum 116's own
   verdict). The envelope was right; the quantity was wrong.

**Recommended stack** (§11, full rationale there): MoGe or Depth-Anything-3
Base/Mono (both permissive) for depth + field of view → SAM 2 (Apache-2.0) for
layer boundaries → 4–8 **soft-alpha, depth-displaced, amodally completed
layers** → depth completed first by slope-continuation, colour completed by
background-restricted self-similar synthesis (training-free, style-agnostic,
works identically on a photo and a Frazetta) with an optional permissive
learned inpainter as an offline detail pass. And **two cones**: an honest
geometric one sized by `k`, and a separate baked cinematic one if the wide
look matters.

---

## 1. The one number

This section is the reason to read the rest.

### 1.1 Definitions

Let the source be `W` px wide, and let depth be expressed as normalised
disparity `δ ∈ [0,1]`. The app already computes the quantity that matters:

```
shift(z) = -ex·z/(D−z),   ex = D·tan(bgViewFadeEndDeg)      [REVIEW.md:5497]
k        = |shift(near) − shift(far)|  in source texels     [Addendum 108]
```

`k` is **the screen displacement, in source pixels, between the near and far
ends of the depth range, at the rim of the supported view cone.** The app
exposes it as `max(|m0|,|m1|)` from `bgShiftLUTFor(pw,ph)`
(`REVIEW.md`:6270). Measured (Addendum 110):

| source | k (mean) | fold limit √2/k | in 8-bit levels |
|---|---|---|---|
| 851×1023 (troll) | **775** | 0.00182 | 0.47 |
| 1920×1080 (star) | **818** | 0.00173 | 0.44 |
| 2047×1200 (photo) | **909** | 0.00156 | 0.40 |
| 3000×1688 (warrior) | **1279** | 0.00111 | 0.28 |

At 851 px wide, a surface spanning the full depth range sweeps **775 px — 91%
of the image width — across the supported cone.**

### 1.2 Five "separate" problems that are one problem

Every quantity below is `k` wearing a different hat.

**(a) Depth bit budget.** A quantisation step `q` folds a one-texel quad when
`q·k ≥ √2`. Need `q < √2/k`. At `k=775`, `q < 0.0018`, i.e. **≥ 10 bits
minimum**, float in practice. One 8-bit level is 2.2–3.5× the fold limit — the
smallest change the input can express already folds. `REVIEW.md`:5746 states
this exactly, and 5793 names the only three knobs: *more bits, lower source
resolution, or a narrower cone.*

**(b) Fold limit / tear criterion.** A quad folds when `Δδ·k ≥ √2`. This is the
same inequality as (a). a117's finding that the fold test dropped 40% of the
mesh is not a bug in the test; it is `k` being large enough that most real
surface slopes fold.

**(c) Reveal-benefit gate.** An edge with depth step `Δδ` opens a disocclusion
of `Δδ·k` px at the rim. Addendum 47's proposed "only tear a cliff that pays for
itself (≥2 px of reveal)" is `Δδ·k ≥ 2` — **the same inequality again**, up to a
constant. The fold criterion and the reveal criterion are one criterion. This
is worth stating in the code as one function.

**(d) MPI / layer count.** The classical MPI sampling rule — from Zhou et al.
2018 and made explicit by Srinivasan et al. 2019 — is that adjacent planes must
not differ by more than ~1 px of disparity at the rendered view, and hence
*the renderable view range scales linearly with plane count*. So
`N_planes ≳ k`. **v2 ships 20 planes against `k = 775`: each plane step is a
39 px parallax discontinuity.** That is the ghosting and the banding the user
reports, predicted to within the measurement, from the project's own number. No
amount of binning cleverness fixes a 39× shortfall; only fewer required pixels
of parallax (smaller `k`) or continuous depth inside each layer does.

**(e) Completion extent.** A foreground/background step of `Δδ = 0.5` opens
`0.5 × 775 = 388` px of disocclusion — **46% of the image width behind a single
occluder.** `bgBandMaxGrowPx = 28` was not mis-tuned by a factor of 2; it was
short by a factor of ~14. D2 ("84% of edges truncated") and D3 and the a113
margin blow-up (691×60 → 851×1023 px, plate 0.87 → 7.8 Mtexel) are all this
number. The backstop sweep (60 s, 65% of the v1 bake) exists to police a plate
whose required extent is set by `k`.

### 1.3 What happens if `k` is 30 instead of 775

Every shipped single-image 3D-photo system — Facebook/Meta 3D photos, 3D Ken
Burns, Leia/Immersity, Apple spatial photos — operates in the regime where the
maximum disparity excursion is a few tens of pixels. That is not timidity; it
is the geometry. At `k ≈ 30`:

| consequence | at k = 775 | at k = 30 |
|---|---|---|
| 8-bit depth quantum vs fold limit | 2.2–3.5× over | 0.12× — safe |
| triangles folding (troll) | 33.6% | ~0% |
| planes needed for artifact-free MPI | ~775 | ~30 (v2 already ships 20) |
| completion depth behind an occluder | up to 388 px | up to 15 px — *a band works* |
| plate margin | 851×1023 px, 7.8 Mtexel | ~30 px skirt |
| backstop sweep | 60 s | unnecessary |

The entire 116-addendum heuristic stack — band, rind, cut, dilate, bleed,
disarm, uvRate, mismatch gate, backstop sweep, viewpoint scan, dequantiser,
cap cards — is machinery for surviving a `k` that no single-image
representation can support. **This is the rabbit hole.** Not any individual
heuristic: the parameter that made all of them necessary.

Addendum 113 widened the cone 90° → 120° (a109), which tightened the fold limit
to 3.7–6.1× one 8-bit level from 2.2–3.5× (`REVIEW.md`:6173). The cone was
widened *after* the cost was measured and named.

### 1.4 The honest framing

There are two different products here and they have been fused:

- **The geometric cone.** Faithful parallax reconstructed from what the image
  actually contains, plus a bounded, defensible amount of completion. Sized by
  `k`, and `k` is set by the layer count and completion extent you can afford.
  Everything is measurable, testable, and pixel-faithful at rest. Probably
  `k ∈ [20, 60]`.
- **The cinematic cone.** The wide, dramatic move. Beyond the geometric cone
  you are not *rendering* the scene, you are *generating* it: at 0.85× the rim
  of a 120° cone the majority of what is on screen was never in the source
  image. This is legitimate and can look wonderful — but it is a generative
  problem, baked offline, judged by eye, and it should not be allowed to set
  thresholds for the geometric path.

Fusing them means every generative requirement leaks into the geometry as a
constant that no measurement can satisfy. Splitting them is, in my reading, the
single highest-value change available.

---

## 2. History I — foundations (1993–2004)

The ideas moebius uses were all fixed in this decade.

| year | work | what it established |
|---|---|---|
| 1993 | Chen & Williams, *View Interpolation for Image Synthesis* | morph between images using per-pixel correspondence; holes named as *the* problem |
| 1994 | Wang & Adelson, *Representing Moving Images with Layers* | scenes decompose into ordered layers with alpha; the layer is the unit |
| 1995 | McMillan & Bishop, *Plenoptic Modeling* | the warp-order theorem — back-to-front painter's order for image warps, still what MPI compositing relies on |
| 1996 | Levoy & Hanrahan, *Light Field Rendering*; Gortler et al., *The Lumigraph* | the 4D plenoptic parameterisation. **The Lumigraph also introduced pull–push**, the pyramid scattered-data interpolation moebius uses today for gap fill |
| 1996 | Collins, *space-sweep stereo* | the plane-sweep volume — the direct ancestor of the MPI |
| 1998 | Baker, Szeliski & Anandan, *A Layered Approach to Stereo Reconstruction* | layers with per-layer plane + residual disparity: **depth-displaced layers, 26 years ago** |
| **1998** | **Shade, Gortler, He & Szeliski, *Layered Depth Images*** | multiple depth-pixels per ray from one camera; incremental warp; *sprites with depth* as the cheap case. The origin point |
| 1999 | Chang, Bishop & Lastra, *LDI Tree* | multi-resolution LDI — sampling rate must follow the output view |
| 1999 | Szeliski & Golland, *Stereo Matching with Transparency and Matting* | fractional alpha at occlusion boundaries is necessary, not cosmetic |
| 2000 | Oliveira, Bishop & McAllister, *Relief Texture Mapping* | factor the warp into pre-warp + texture map — the "run it on the GPU" move |
| 2000–01 | Bertalmío et al.; 2004 Telea | PDE / fast-marching inpainting. Both in OpenCV (BSD) today |
| 2003–04 | Criminisi, Pérez & Toyama, *Object Removal by Exemplar-Based Inpainting* | confidence × data-term priority; structure before texture. The template every later exemplar method varies |
| 2004 | Fehn, *DIBR* | the standard 2D+depth pipeline; asymmetric depth smoothing to trade hole size against geometric distortion |

**Reading for moebius:** two things were already true in 1998 that the current
architecture has been re-deriving. First, Baker/Szeliski/Anandan's layers carry
their own disparity field — flat planes were never the only option. Second,
Szeliski & Golland established that occlusion boundaries need *fractional*
alpha. moebius's binary cut producing a "1px moire comb" (a117) and the
"picket-fence comb along the bottom margin" are the 1999 result reappearing.

---

## 3. History II — the DIBR/3DTV era (2005–2016): the heuristic graveyard

This is the era that matters most for this project, because it is the era whose
conclusions moebius is currently re-running from the start.

Between the 3DTV push and the free-viewpoint-video standards work, several
hundred papers attacked exactly one problem: *given one colour image and one
depth map, fill the holes that appear when you move the camera.* The families
tried, essentially all of them present somewhere in `REVIEW.md`:

1. **Depth-map preprocessing.** Smooth the depth so holes never open
   (Fehn 2004; asymmetric/edge-preserving variants). Trades holes for geometric
   distortion — the "rubber plate effect", uneven object enlargement. moebius
   rediscovered this exact trade as a86: *"a86 trades banding for folding"*
   (`REVIEW.md`:5788).
2. **Horizontal/background extrapolation.** Fill each hole row from the
   background side only. Cheap, correct in prior, ugly in texture. moebius's
   directional fill (reflect/smooth, 7496–7522) is this.
3. **Hierarchical hole filling (pull–push pyramids).** Fast, always converges,
   always blurry. moebius's `method=pullpush`.
4. **Depth-aided exemplar inpainting.** Criminisi with the priority term
   modified so background patches win and foreground patches are excluded from
   the source region (Daribo & Saito 2011; Gautier et al. 2011; Ahn & Kim 2013;
   and Burke's depth-aided exemplar study). The best-quality classical answer,
   and still the best *style-agnostic* answer today (§8).
5. **Joint Projection Filling** (Jantet, Guillemot et al., 2011). Fill the
   *depth* first by projecting and closing along the epipolar direction, then
   backward-project the texture, then a **full-Z depth-aided inpaint**. The
   canonical statement of "complete depth before colour, and let depth choose
   the colour source."
6. **LDI-based view synthesis with depth-based inpainting** (2015–16). Build
   the second layer in the *source* view, inpaint it there, then warp.
7. **Mesh DIBR with triangle dropping.** Build a mesh at 1 vertex/texel, drop
   or push-to-background triangles that span a depth discontinuity, usually in
   a geometry shader. This is `REVIEW.md` §4's recommended re-architecture,
   published circa 2004–2010.

**The conclusion the field reached, and it is the load-bearing lesson here:**
target-view hole filling is a dead end. Everything after ~2016 fills in the
**source view**, into an explicit layered representation, before any warping
happens. The reasons are exactly D1–D3: any screen-space rule has to decide
*at render time*, per pixel, per pose, with no memory, whether a pixel is real
content or a stretched artifact — and no local test can do that reliably. Which
is why the modern systems all pay once, offline, and render trivially.

`REVIEW.md` §4 reaches this conclusion independently and correctly: *"The
heuristic stack is the architecture telling you the geometry is wrong."* That
sentence is the 2005–2016 literature in one line.

---

## 4. History III — the learned layered era (2017–2020)

| year | work | contribution | licence note |
|---|---|---|---|
| 2017 | Penner & Zhang, **Soft3D** | soft visibility/uncertainty volume, **not learned**; still one of the best non-neural quality points | — |
| **2018** | Zhou, Tucker, Flynn, Fyffe, Snavely, **Stereo Magnification** | **introduces the MPI**: N front-parallel RGBA planes at fixed disparities, composited back-to-front. Trained on RealEstate10K | RealEstate10K is YouTube-derived; provenance is murky for commercial use |
| 2019 | Flynn et al., **DeepView** | MPI by learned gradient descent; the quality bar | Google |
| 2019 | Mildenhall et al., **LLFF** | per-view MPIs + blending; made MPI practical for real capture | verify before use |
| 2019 | **Srinivasan et al., *Pushing the Boundaries of View Extrapolation with MPIs*** | **the theory**: renderable view range scales *linearly* with MPI disparity sampling frequency. This is §1(d) | — |
| 2019 | Niklaus et al., **3D Ken Burns Effect from a Single Image** | the first strong single-image 3D-photo pipeline: depth → point cloud → context-aware colour+depth inpainting → re-render | **CC BY-NC-SA 4.0 — non-commercial, excluded** |
| **2020** | **Shih, Su, Kopf & Huang, *3D Photography using Context-aware Layered Depth Inpainting*** | LDI with **explicit pixel connectivity**; iterative context-aware inpainting of colour **and** depth **and** edges into the occluded region | **MIT** — the most directly relevant permissive reference implementation |
| 2020 | Kopf et al., **One Shot 3D Photography** | the shipped mobile system: fast depth ("Tiefenrausch"), LDI, tearing at discontinuities, on-device | Meta |
| 2020 | Tucker & Snavely, **Single-View MPI** | MPI from one image; scale-invariant training | RealEstate10K |
| 2020 | **Broxton et al., *Immersive Light Field Video with a Layered Mesh Representation*** | **MSI volume → a small fixed number of RGBA+depth layers**, texture-atlased, rendered on mobile VR *and in a browser*. The industrial proof that "few depth-displaced layers" is the right runtime form | Google |
| 2020 | Attal et al., **MatryODShka** | multi-sphere images for 6DoF 360 | — |
| 2020 | Mildenhall et al., **NeRF** | the fork in the road (§5) | — |

**Reading for moebius:** Shih et al. 2020 is the closest published relative of
what moebius is building, it is MIT-licensed, and its central design decision —
an LDI whose pixels carry *explicit connectivity*, so a tear is a topological
fact rather than a per-frame screen-space test — is precisely `REVIEW.md` §4's
recommendation. Broxton et al. 2020 is the proof that the Addendum 3 "MPI
shape" (depth-displaced layers, few of them, browser-renderable) is not
speculative: Google shipped it.

---

## 5. History IV — consolidation, and the fork (2021–2023)

NeRF (2020) and 3D Gaussian Splatting (2023) took over the *multi-view*
problem completely. Layered representations did not die; they **specialised**
into exactly moebius's niche: **single image, real-time, commodity/web GPU,
no per-scene optimisation.** That specialisation is what the 2021–2023 layered
papers are about.

| year | work | contribution | licence |
|---|---|---|---|
| 2021 | **Jampani et al., SLIDE** | **soft layering** beats hard depth layering — hard layers cannot represent hair, thin structures, ribbons. Plus depth-aware inpainting training. Modular: segmentation/matting can be swapped in | no public code |
| 2021 | Li et al., **MINE** | continuous-depth MPI via a NeRF-style decoder | — |
| 2022 | Han et al., **AdaMPI** | adaptive plane placement + in-the-wild single-view training | **non-commercial — excluded** |
| **2022** | **Kim et al., *Layered Depth Refinement with Mask Guidance*** (CVPR) | decompose depth by a mask, refine + **inpaint/outpaint depth per layer**. The published fix for "the estimator smeared this boundary" | — |
| 2022–23 | Solovev et al., **MLI (multiplane-to-layer images)** | convert an MPI into **a few deformable textured layers**. Same conclusion as Broxton, reached from the learning side | Samsung |
| 2023 | Zhang et al., **Structural MPI** (CVPR) | **slanted, structure-aligned planes** — kills the discretisation artifact that front-parallel planes cause on ramps and ground | — |
| 2023 | **SAMPLING** (ICCV) | scene-adaptive hierarchical plane placement | — |
| 2023 | **Khan, Lanman & Xiao, *Tiled Multiplane Images*** (ICCV) | **local depth complexity is low**: split the image into tiles, each needing only a handful of planes. The most practical MPI variant | **CC-BY-NC — excluded** (repo archived 2026) |
| 2023 | **SinMPI** | expanded MPI with generative outpainting for single-image | — |
| 2023 | Kerbl et al., **3D Gaussian Splatting** | — | **original Inria/MPII rasteriser is non-commercial**; use **gsplat (Apache-2.0)** |

**Reading for moebius:** three independent results in this window all say the
same thing and all contradict "20 flat planes":

- **S-MPI**: front-parallel planes are wrong for slanted surfaces — the ground
  ramp *will* band. moebius measured exactly this (Addendum 92, "the
  banding/silk/staircase family").
- **TMPI**: depth complexity is *local*. Globally you need many planes; in any
  small region you need 2–4. moebius's per-layer-plates work is the same idea.
- **MLI / layered mesh**: the runtime form should be a few layers *with their
  own depth*, not many flat ones.

And **SLIDE**'s soft-layering result is the direct answer to the thin-lift /
ribbon / staff-taffy / filament / confetti families that consume roughly a
dozen addenda. Those are all one defect: **hard binary layer assignment applied
to sub-pixel and semi-transparent structure.** The published fix is fractional
alpha at layer boundaries (i.e. matting), not a better threshold.

---

## 6. History V — the foundation-model era (2024–2026)

The layered-representation *research* literature has largely gone quiet, because
the hard part moved upstream: monocular geometry got good enough that the
representation stopped being the bottleneck.

**Monocular depth / geometry**

| model | year | output | licence (July 2026) |
|---|---|---|---|
| MiDaS 3.1 / DPT | 2020–22 | relative depth | **MIT**, code + weights |
| Marigold | CVPR 2024 | affine-invariant depth, diffusion prior | **Apache-2.0**; SD backbone under CreativeML OpenRAIL-M; trained on **synthetic only** (Hypersim, Virtual KITTI 2) |
| Depth Anything V2 | 2024 | relative depth | **Small = Apache-2.0; Base/Large/Giant = CC-BY-NC-4.0** |
| Depth Pro (Apple) | 2024 | sharp metric depth | **Apple personal-use licence — commercial use not granted** |
| **MoGe / MoGe-2** | CVPR 2025 | **point map + depth + normals + FOV**, ~60 ms | **MIT** (DINOv2 subtree Apache-2.0) |
| **Depth Anything 3** | Nov 2025 | depth, rays, pose, optional 3DGS head | **code Apache-2.0**; **Small, Base, DA3METRIC-LARGE, DA3MONO-LARGE = Apache-2.0**; Large/Giant/Nested = CC-BY-NC-4.0 |
| VGGT / π³ / MapAnything | 2025 | multi-view geometry | verify individually; several are non-commercial |

**Segmentation:** SAM 2 (Meta, 2024) — **Apache-2.0**, strong zero-shot
generalisation to unseen visual domains.

**Inpainting**

| model | year | licence | notes |
|---|---|---|---|
| LaMa | WACV 2022 | **Apache-2.0** code+model; **trained on Places2**, whose terms are non-commercial research — a provenance flag, not a code-licence problem | FFC, prompt-free, fast, resolution-robust to ~2k |
| MAT / ZITS / CoModGAN | 2022 | mixed, several non-commercial | CoModGAN shows higher *context awareness* than LaMa on art |
| SD 1.5 / SDXL inpainting | 2022–23 | CreativeML Open RAIL-M (permissive-with-use-restrictions, not OSI-open) | needs prompts; ControlNet-depth conditioning available |
| FLUX.1 Fill [dev] | 2024 | **non-commercial — excluded** | current quality leader |
| BRIA inpainting | 2024–25 | **100% licensed training data** (Getty, Alamy, Envato…) with liability cover — but a **paid commercial licence** | the only "clean dataset" option, at a price |
| **Moebius** (hustvl / HUST + vivo AI Lab) | **ECCV 2026** | **Apache-2.0, code + weights** | **0.22 B params**, ~26 ms/step, >15× faster than FLUX.1-Fill-dev at comparable quality on 6 benchmarks; **prompt-free, mask-based**; distilled from PixelHacker. Name collision with this project is a coincidence |

**Reading for moebius:** the licence landscape is much better than it was two
years ago and much worse than it looks. The *famous* checkpoints in this space —
Depth Anything V2 Large, DA3 Large/Giant, Depth Pro, 3D Ken Burns, TMPI, AdaMPI,
FLUX Fill, the original 3DGS rasteriser — are all non-commercial. The
permissively-licensed frontier is: **MoGe (MIT)**, **DA3 Base / DA3MONO-LARGE
(Apache-2.0)**, **Marigold (Apache-2.0, synthetic-only training data)**,
**MiDaS/DPT (MIT)**, **SAM 2 (Apache-2.0)**, **LaMa (Apache-2.0)**, and
**hustvl/Moebius (Apache-2.0)**. That is a complete stack, and it is a good one.

---

## 7. The eight invariants

What 28 years of this problem actually agreed on. Each is a claim moebius can
test against its own harness.

1. **Fill in the source view, into an explicit representation. Never in the
   target view.** Proven by the 2005–2016 DIBR era, re-proven by `REVIEW.md`
   D1–D11.
2. **Layer boundaries are occlusion boundaries — and they come from
   segmentation, not from thresholded depth.** Depth decides placement
   *within* a layer. (SLIDE's modularity claim; MaskDepth's premise;
   moebius's Addendum 56.)
3. **Parallax is linear in disparity.** Every threshold — tear, fold, plane
   count, band width, completion extent, depth bit budget — must be expressed
   as *pixels of shift at the rim*, which makes them one threshold. (§1.)
4. **Completion is amodal and total, or it is wrong.** "The world without the
   foreground," not a strip. Any finite band under-covers at some pose;
   the required extent is `Δδ·k` and is unbounded in the band's own terms.
5. **Depth first, then colour, and colour sourced only from the background
   side.** (Joint Projection Filling; depth-aided exemplar inpainting; Shih
   et al.'s edge→depth→colour ordering.) A colour fill at the wrong depth
   moves at the wrong rate and reads as a smear no matter how good it looks
   at rest — which is precisely `REVIEW.md`'s "the wash reads as smudge".
6. **Boundaries need fractional alpha.** Hard layer assignment cannot represent
   hair, ink strokes, thin ribbons, or antialiased silhouettes. (Szeliski &
   Golland 1999 → SLIDE 2021.) Binary cuts produce combs.
7. **The supported view cone is a property of the representation, not of the
   UI.** It is `≈ N_layers` pixels of disparity for a layered representation.
   Advertise it, fade at it, and do not let it be a slider.
8. **Heuristic count is a smell.** The field's whole trajectory was *fewer*
   screen-space rules and *more* explicit geometry decided once, offline.

---

## 8. Disocclusion inpainting of colour and depth — taxonomy, and what survives contact with a painting

### 8.1 Depth completion (do this first)

Almost nobody writes papers about this and it matters more than the colour.
The requirement: behind an occlusion boundary, produce a depth field that
**continues the background surface's slope**, not a constant, and not a
diffusion of the foreground's rim value.

- **Constant/plateau fill** — the naive choice, and the cause of a whole class
  of artifacts: the fill sits at a fixed depth, so it slides at a different rate
  than the ground it continues, and reads as a detached sheet. `REVIEW.md`
  Addendum 3 already documents this ("Law 3 amendment") and got it right.
- **Slope continuation / plane extrapolation from the background side** —
  fit a local plane to the background rim and extend it. Training-free, exact,
  O(N). This should be the default and is what Addendum 63b ("gradient-true
  fill values") converged on.
- **Pull–push / hierarchical** on the *disparity* field, not depth. Smooth by
  construction, correct low frequencies, needs the slope term added back.
- **Mask-guided layered depth refinement** (Kim et al., CVPR 2022) — the
  learned version: given a mask, decompose and inpaint/outpaint the depth per
  layer. This is the published answer to moebius's stroke-depth/ink-depth
  family, and it is trained self-supervised with arbitrary masks on RGB-D data.
- **Anti-pattern:** inpainting depth with a *colour* inpainter. Depth has no
  texture; it has structure. A texture model will invent detail that becomes
  visible geometry.

### 8.2 Colour completion — six classes

| class | examples | cost | prompt? | **behaviour on painting/comic art** |
|---|---|---|---|---|
| **A. PDE / diffusion** | Bertalmío 2001, Telea 2004 (OpenCV, BSD) | ~free | no | Style-neutral but structureless; fine for ≤5 px, mud beyond |
| **B. Pyramid / pull–push** | Gortler 1996; hierarchical hole filling | ~free | no | Style-neutral, always blurry. Correct as a *base layer* only |
| **C. Exemplar / patch synthesis** | Criminisi 2004; PatchMatch 2009; Image Melding 2012; GIMP resynthesizer (GPL, 2001) | cheap–moderate | no | **The only class that is style-agnostic by construction** — it copies patches from the same image, so a Frazetta fill is made of Frazetta pixels and an ink-line fill is made of ink lines. See 8.3 |
| **D. Geometry-aware exemplar (DIBR)** | Daribo & Saito 2011; Gautier 2011; Joint Projection Filling 2011 | moderate | no | Class C + the right prior: source region restricted to background-side patches, priority weighted by depth. **This is the correct classical answer to disocclusion specifically** |
| **E. Learned feed-forward** | LaMa (Apache-2.0), MAT, CoModGAN | fast (ms) | no | Photo-biased. LaMa is excellent at periodic/structural continuation and degrades gracefully; on art it tends to smooth brushwork and lose line weight. CoModGAN scores higher on context awareness for art (Escher study) |
| **F. Diffusion** | SD/SDXL inpaint (OpenRAIL), FLUX Fill (**NC**), **hustvl/Moebius (Apache-2.0)** | 26 ms/step – seconds | varies | Best absolute quality; can be steered toward a style via context and ControlNet-depth. Risk: no cross-view consistency, and it will happily invent photographic texture unless constrained |

### 8.3 The generality argument — why "any image" points at C/D first

This is the crux of the brief and it has a clean answer.

**Learned inpainters have a style prior. Patch-based inpainters have none.**
LaMa, MAT, CoModGAN, SD, FLUX and Moebius were all trained overwhelmingly on
photographs (Places2, CelebA-HQ, FFHQ, LAION-scale web images). Asked to fill a
hole in a Moebius panel or a Frazetta oil, they produce something with
*photographic* local statistics: continuous tone where there should be flat
colour, no line weight, wrong grain. The Escher *Print Gallery* study is the
published data point — even the best of them needed either costly fine-tuning
or a human picking among generative samples to be usable on art.

Exemplar synthesis has the opposite property: because every output pixel is
copied from the input image, **the fill inherits the source's style exactly,
for free, with no training and no domain assumption.** Halftone stays halftone,
impasto stays impasto, cel-shaded flats stay flat, film grain stays grain. For
a system whose contract is "any image we throw at it," this is not a small
advantage; it is the whole requirement.

The known weakness of exemplar synthesis — it cannot invent *semantics*, only
continue texture and structure — is much less damaging in the disocclusion case
than in general object removal, because disocclusions are (a) adjacent to the
content that should continue into them and (b) small, **if `k` is small**. This
is another way in which §1 is load-bearing: at `k ≈ 30`, class D is
comfortably sufficient and needs no model at all; at `k = 775` nothing but a
generative model can cover the hole, and then you inherit its style prior.

**Patent flag, stated and not resolved.** Adobe's `US8861869B2`
("Determining correspondence between image regions", the PatchMatch randomized
nearest-neighbour search) is listed as active with an anticipated expiry of
**2030-08-16**, with related patents `US8340463B1` and `US8233739B1` also
active. This covers the specific randomized-search algorithm, not exemplar
inpainting generally. Alternatives that predate or avoid it: Criminisi et al.
(Microsoft, filed 2003 — term expired), Efros–Leung / Ashikhmin coherence
synthesis, Harrison's resynthesizer (2001, GPL, ships in GIMP), OpenCV
`xphoto::inpaint` (SHIFTMAP / FSR, BSD), and any exhaustive or
hierarchically-pruned NN search. Take advice before shipping a PatchMatch-shaped
search commercially.

### 8.4 The pragmatic recommendation

**Two tiers, and a style lock.**

- **Tier 1 (default, universal, training-free):** depth by slope-continuation →
  colour by **background-restricted exemplar synthesis seeded from a pull–push
  base**. Class D. No model, no weights, no licence, identical behaviour on a
  photo and a woodcut. This is what should run at import for every asset.
- **Tier 2 (opt-in, offline, per-layer):** a permissive learned inpainter over
  the same mask and the same completed depth. **hustvl/Moebius (Apache-2.0,
  0.22 B, ~26 ms/step, prompt-free)** is the standout candidate on the stated
  criteria and did not exist when this project's SD path was designed; LaMa
  (Apache-2.0) is the conservative alternative; SD-inpaint + ControlNet-depth
  is the high-ceiling option if OpenRAIL is acceptable.
- **Style lock on Tier 2 output** (cheap, and it is what makes Tier 2 safe on
  art): after inpainting, project the fill's colour statistics onto the source
  layer's — palette / histogram match against the surrounding annulus, plus a
  gradient-domain (Poisson) blend at the seam, optionally a per-channel
  quantisation match for flat/cel art. A photo-trained model then cannot inject
  photographic tone into a painted layer, because you overwrite the statistics
  it got wrong while keeping the structure it got right.

---

## 9. Licence and suitability table

Everything below was checked against its repository or licence file in
July 2026. **Bold = recommended for a commercial, permissively-licensed stack.**

### Depth / geometry

| model | licence | fit for art? | verdict |
|---|---|---|---|
| **MoGe / MoGe-2** (Microsoft) | **MIT** | good, open-domain by design | **Best default.** Gives point map + **FOV**, which removes the "what focal length is this painting?" guess that currently drives the frustum/dolly/subject-pin work |
| **Depth Anything 3 — Base / Small / DA3MONO-LARGE / DA3METRIC-LARGE** | **Apache-2.0** | strong | **Best pure-depth option.** Note Large/Giant/Nested are CC-BY-NC |
| **Marigold** | **Apache-2.0**, synthetic-only training data | **best-in-class on stylised input** (SD prior) | **Best for paintings**; slow (multi-step), but this is an import-time cost |
| **MiDaS 3.1 / DPT** | **MIT** | robust by construction | Conservative baseline; mixed-dataset scale-shift-invariant training is *why* it generalises off-domain |
| Depth Anything V2 Small | Apache-2.0 | fair | usable; Base/Large/Giant are CC-BY-NC |
| Depth Pro (Apple) | Apple personal-use | excellent boundaries | **excluded — no commercial grant** |
| ComicsDepth (IVRL, WACV 2022) | research | comics-specific | Useful *idea* (translate art→photo domain, then estimate); check licence before use |

### Layering / representation

| work | licence | verdict |
|---|---|---|
| **3D Photo Inpainting** (Shih et al., CVPR 2020) | **MIT** | **The reference implementation to study.** LDI with explicit connectivity + joint colour/depth/edge inpainting |
| **SAM 2** | **Apache-2.0** | **Use it.** Layer boundaries from segmentation, generalises zero-shot to illustration |
| Tiled MPI (TMPI) | CC-BY-NC | excluded — but the *idea* (local depth complexity is low) is free |
| AdaMPI | non-commercial | excluded |
| 3D Ken Burns | CC-BY-NC-SA | excluded |
| 3DGS (Inria) | non-commercial | excluded; use **gsplat (Apache-2.0)** if splats are ever wanted |

### Inpainting

| model | licence | verdict |
|---|---|---|
| **Classical exemplar (Criminisi-class, resynthesizer, OpenCV xphoto)** | GPL / BSD / expired-patent | **Tier 1.** Style-agnostic, training-free, zero licence risk on the algorithm itself (see 8.3 patent flag on PatchMatch specifically) |
| **hustvl/Moebius** | **Apache-2.0** code + weights | **Tier 2 first pick.** 0.22 B, ~26 ms/step, prompt-free, mask-based |
| **LaMa** | **Apache-2.0** code + weights (Places2 provenance flag) | Tier 2 conservative pick; fast, prompt-free, resolution-robust |
| SD 1.5 / SDXL inpaint | CreativeML Open RAIL-M | acceptable-with-restrictions; needs prompts; ControlNet-depth available |
| FLUX.1 Fill [dev] | non-commercial | excluded |
| BRIA inpainting | licensed data + **paid** commercial licence | the "clean dataset" answer if the budget exists |

---

## 10. moebius, read against the literature

Addendum families mapped onto prior art. This is not a criticism of the work —
the measurement discipline in `REVIEW.md` is better than most published papers.
It is a map of which battles were already fought.

| moebius work | prior art | status |
|---|---|---|
| Band / rind / cut / dilate / bleed / disarm (D1–D11) | 2005–2016 DIBR target-view hole filling | **Settled and abandoned by the field.** `REVIEW.md` §4 reaches the same verdict |
| Pre-tear FG at depth cliffs | Mesh DIBR triangle dropping (~2004); LDI explicit connectivity (Shih 2020) | **Correct.** Standard practice |
| "World without foreground" plate | VFX clean plate; amodal completion; LDI second layer | **Correct.** The right target |
| Depth-displaced layers (Addendum 3) | Baker/Szeliski/Anandan 1998; MLI 2022; layered mesh 2020 | **Correct, and this is the endgame.** Shipped by Google to browsers in 2020 |
| "The ink was the segmentation" (A56) | SLIDE 2021 modularity; MaskDepth 2022 | **The key insight.** Now take it further: use SAM 2 and delete the ink machinery |
| Stroke-depth repair, adopt-map, footing rule, wire rule, ink-follows-layer | Mask-guided layered depth refinement (Kim 2022); domain translation for comics (ComicsDepth 2021) | **Fighting the estimator in the renderer.** Fix upstream |
| Thin-lift / ribbon / staff-taffy / filaments / confetti | SLIDE soft layering; Szeliski & Golland 1999 | **One defect, not five: binary layer assignment.** Needs fractional alpha (matting) |
| Fold limit, a101/a102 exact envelope | MPI disparity sampling (Srinivasan 2019) | **Right law, wrong quantity** (Addendum 116 says so). It is the same law as plane count and reveal benefit |
| a86 dequantiser (banding ↔ folding trade) | Fehn 2004 depth smoothing (holes ↔ distortion trade) | **The 2004 trade, rediscovered.** Not resolvable at this layer |
| 8-bit → float depth ingest (a99) | — | **Correct and necessary.** But only because `k` is large |
| Backstop sweep (60 s), all-viewpoint scan (2.75 s, pruned 0 px) | — | **Pure cost of a large `k`.** Delete with the cone |
| Pull–push fill | Gortler et al. 1996 | Correct as a *base*; never as the final answer (blur is inherent) |
| v2 = 20 full completed planes, cheapest **and** best-looking | MPI (Zhou 2018) | **The measurement is the answer.** Amodal completion done properly beats every heuristic. Its ghosting is the textbook plane-count artifact — 20 planes against `k = 775` |
| 120° cone | Srinivasan 2019: range ∝ sampling frequency | **The rabbit hole** (§1) |

---

## 11. Recommended architecture

Consistent with `REVIEW.md`'s standing recommendation and with Addendum 116's
measurement that **v2 is both the cheapest complete mode and the best-looking**.
That measurement should be trusted; the recommendation is to keep v2's *shape*
(completed planes) and fix its *sampling* (too few, and flat).

**Import (once per asset, target < 10 s):**

1. **Geometry.** MoGe (MIT) → affine-invariant point map + **FOV**, at float
   precision. Optional second opinion from Marigold (Apache-2.0) for stylised
   assets; keep both and let the harness pick per asset class. This retires the
   frustum/lens/subject-pin guesswork and the 8-bit ingest problem at once.
2. **Layers from segmentation, not from depth.** SAM 2 (Apache-2.0) →
   ordered instance/region masks; order them by median disparity. Merge until
   4–8 layers remain. **Layer boundaries are occlusion boundaries; nothing
   else is a boundary.** This retires: band seeding, `bgBandStep`, Otsu, the
   adopt-map, ink-follows-layer, stroke-depth repair, the footing rule.
3. **Soft alpha at boundaries.** Estimate a matte in a few-pixel annulus around
   each layer edge (guided filter / closed-form matting is enough). This
   retires: the graded cut, the comb, thin-lift, ribbons, staff taffy,
   filaments, confetti — they are all the binary assignment.
4. **Amodal completion per layer, depth first.**
   - Depth: slope-continued extrapolation from the background rim into the
     layer's occluded region — the whole region, not a band.
   - Colour: Tier 1 background-restricted exemplar synthesis over a pull–push
     base (§8.4). Tier 2 (offline, optional): hustvl/Moebius or LaMa,
     conditioned on the completed depth, followed by the style lock.
   - Extent: `Δδ·k` px past each boundary, from the same `k` function as the
     tear test. One number, one function, one place in the code.
5. **Emit each layer as a coarse displaced mesh** carrying its own depth,
   decimated in flat regions (safe, because layers no longer share seams).
   Not 20 flat planes; not one 9 M-vertex sheet.

**Runtime:** composite the layers back-to-front. No cut, no rind, no
backstop, no viewpoint scan, no cap cards, no fold test, no gap generator.
Rest fidelity is pixel-exact by construction, because at zero offset every
layer projects to its own source pixels.

**And set the cone from the representation.** With `L` layers each carrying
continuous depth, the artifact-free excursion is bounded by completion extent
rather than plane count — but it is still bounded. Measure it: sweep the pose,
find where completed content runs out, and set `bgViewFadeEndDeg` there. Then
fade. If the wide look is required, bake it separately as the cinematic path
and let it be generative.

**Migration order** (each step independently shippable and measurable):

1. **Print `k`.** One line: `bgShiftLUTFor(pw,ph)` at the current cone, per
   asset. Publish it next to every other measurement in `REVIEW.md`. Every
   number in §1 becomes checkable in an afternoon.
2. **Sweep the cone against artifacts** with v2 unchanged — black %, comb
   energy, and plate exposure vs `bgViewFadeEndDeg`. This produces the honest
   cone empirically and costs nothing to run.
3. **Adopt one unified threshold function** `revealPx(Δδ) = Δδ·k`, and route
   tear, fold, band width, completion extent and plane placement through it.
   Delete the private copies (a104 retired three; a113 found a fourth).
4. **SAM 2 layer boundaries + soft alpha**, feeding the existing v2 completed
   planes. Biggest single quality jump, and it deletes the most code.
5. **Per-layer depth displacement** (Addendum 3's design) to replace flat
   binning. Kills the ghosting and the ground-ramp banding together.
6. **Tier 2 inpainting** last, when the geometry no longer needs it to hide
   anything.

---

## 12. If you read five things

1. **Shade, Gortler, He & Szeliski (1998)**, *Layered Depth Images* — the
   origin, and still the clearest statement of the representation.
2. **Shih, Su, Kopf & Huang (2020)**, *3D Photography using Context-aware
   Layered Depth Inpainting* — **MIT-licensed**, closest published relative of
   moebius, and the reference for joint colour+depth+edge completion.
3. **Srinivasan et al. (2019)**, *Pushing the Boundaries of View Extrapolation
   with Multiplane Images* — the disparity-sampling law that is §1.
4. **Jampani et al. (2021)**, *SLIDE* — why soft layering, and why the thin
   structures cannot be fixed with a better threshold.
5. **Broxton et al. (2020)**, *Immersive Light Field Video with a Layered Mesh
   Representation* — the proof that few depth-displaced layers is the right
   runtime form, shipped to a browser.

Runner-up, for the inpainting side specifically: **Jantet, Guillemot et al.
(2011)**, *Joint Projection Filling* — depth first, then colour, sourced from
the background. Fifteen years old and still the correct ordering.

---

## Sources

Historical / representation
- [Layered Depth Images (Shade, Gortler, He, Szeliski, SIGGRAPH 1998)](https://szeliski.org/papers/Shade_LayeredDepthImages_SG98.pdf) · [SIGGRAPH archive](https://history.siggraph.org/learning/layered-depth-images-by-shade-gortler-he-and-szeliski/) · [MSR page](https://www.microsoft.com/en-us/research/publication/layered-depth-images/)
- [The Lumigraph (Gortler et al., 1996)](http://www.cs.columbia.edu/~allen/PHOTOPAPERS/lumigraph.pdf) — origin of pull–push · [The Pull-Push Algorithm Revisited](https://www.scitepress.org/papers/2009/17726/17726.pdf)
- [A Review of Image-based Rendering Techniques (Shum & Kang)](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/review_image_rendering.pdf)
- [Stereo Magnification (SIGGRAPH 2018) — SIGGRAPH archive](https://history.siggraph.org/learning/stereo-magnification-learning-view-synthesis-using-multiplane-images-by-flynn-zhou-tucker-fyffe-and-snavely/)
- [Pushing the Boundaries of View Extrapolation with Multiplane Images (Srinivasan et al., CVPR 2019)](https://arxiv.org/abs/1905.00413) · [PDF](https://openaccess.thecvf.com/content_CVPR_2019/papers/Srinivasan_Pushing_the_Boundaries_of_View_Extrapolation_With_Multiplane_Images_CVPR_2019_paper.pdf)
- [One Shot 3D Photography (Kopf et al., SIGGRAPH 2020)](https://arxiv.org/pdf/2008.12298) · [project page](https://facebookresearch.github.io/one_shot_3d_photography/)
- [Immersive Light Field Video with a Layered Mesh Representation (Broxton et al., SIGGRAPH 2020)](https://history.siggraph.org/experience/immersive-light-field-video-with-a-layered-mesh-representation-by-broxton-flynn-overbeck-erickson-hedman-et-al/)
- [Single-View View Synthesis with Multiplane Images (Tucker & Snavely, CVPR 2020)](https://openaccess.thecvf.com/content_CVPR_2020/papers/Tucker_Single-View_View_Synthesis_With_Multiplane_Images_CVPR_2020_paper.pdf)
- [Structural Multiplane Image (CVPR 2023)](https://openaccess.thecvf.com/content/CVPR2023/papers/Zhang_Structural_Multiplane_Image_Bridging_Neural_View_Synthesis_and_3D_Reconstruction_CVPR_2023_paper.pdf)
- [SAMPLING: Scene-adaptive Hierarchical Multiplane Images (ICCV 2023)](https://arxiv.org/pdf/2309.06323)
- [Tiled Multiplane Images for Practical 3D Photography (ICCV 2023)](https://arxiv.org/abs/2309.14291) · [code (CC-BY-NC)](https://github.com/facebookresearch/TMPI)
- [SinMPI (SIGGRAPH Asia 2023)](https://arxiv.org/html/2312.11037v1)
- [Self-improving Multiplane-to-layer Images (Samsung)](https://samsunglabs.github.io/MLI/)

3D photo / disocclusion
- [3D Photography using Context-aware Layered Depth Inpainting (Shih et al., CVPR 2020) — MIT](https://github.com/vt-vl-lab/3d-photo-inpainting) · [paper](https://arxiv.org/pdf/2004.04727) · [project](https://shihmengli.github.io/3D-Photo-Inpainting/)
- [SLIDE: Single Image 3D Photography with Soft Layering and Depth-aware Inpainting (ICCV 2021)](https://openaccess.thecvf.com/content/ICCV2021/papers/Jampani_SLIDE_Single_Image_3D_Photography_With_Soft_Layering_and_Depth-Aware_ICCV_2021_paper.pdf) · [project](https://varunjampani.github.io/slide/)
- [3D Ken Burns Effect from a Single Image (Niklaus et al., 2019) — CC BY-NC-SA](https://github.com/sniklaus/3d-ken-burns) · [paper](https://arxiv.org/abs/1909.05483)
- [Layered Depth Refinement with Mask Guidance (Kim et al., CVPR 2022)](https://openaccess.thecvf.com/content/CVPR2022/papers/Kim_Layered_Depth_Refinement_With_Mask_Guidance_CVPR_2022_paper.pdf) · [project](https://sooyekim.github.io/MaskDepth/)
- [Joint Projection Filling for occlusion handling in DIBR (Jantet, Guillemot et al., 2011)](https://inria.hal.science/hal-00628019/en)
- [Depth-Aided Exemplar-Based Disocclusion Filling for DIBR View Synthesis](https://web.stanford.edu/class/ee368/Project_Autumn_1516/Reports/Burke.pdf)
- [Object Removal by Exemplar-Based Inpainting (Criminisi, Pérez, Toyama)](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/criminisi_cvpr2003.pdf)
- [PatchMatch (Barnes et al., SIGGRAPH 2009)](https://dl.acm.org/doi/10.1145/1576246.1531330) · [US8861869B2 — active, anticipated expiry 2030-08-16](https://patents.google.com/patent/US8861869B2/en)

Depth / geometry models
- [MoGe (Microsoft, CVPR 2025 Oral) — MIT](https://github.com/microsoft/MoGe) · [paper](https://arxiv.org/abs/2410.19115)
- [Depth Anything 3 (ByteDance, Nov 2025) — per-variant licences](https://github.com/ByteDance-Seed/Depth-Anything-3) · [project](https://depth-anything-3.github.io/)
- [Depth Anything V2 — Small Apache-2.0, Base/Large/Giant CC-BY-NC](https://github.com/DepthAnything/Depth-Anything-V2) · [licence issue thread](https://github.com/DepthAnything/Depth-Anything-V2/issues/162)
- [Marigold (CVPR 2024) — Apache-2.0, synthetic-only training](https://github.com/prs-eth/marigold) · [paper](https://arxiv.org/pdf/2312.02145)
- [MiDaS 3.1 / DPT — MIT](https://github.com/isl-org/MiDaS)
- [Depth Pro (Apple) — restrictive licence](https://github.com/apple/ml-depth-pro/blob/main/LICENSE)
- [Estimating Image Depth in the Comics Domain (WACV 2022)](https://arxiv.org/abs/2110.03575) · [code](https://github.com/IVRL/ComicsDepth)
- [Evaluating Zero-Shot Monocular Depth Estimation Models on artworks (Eurographics)](https://diglib.eg.org/collections/0c402616-19d4-4e64-b61f-e486ddb50788)
- [From pictorial space to tactile form: AI-based 2.5D reconstruction from modern artwork paintings (Frontiers, 2026)](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1821454/full)

Segmentation / inpainting models
- [SAM 2 — Apache-2.0](https://ai.meta.com/blog/segment-anything-2/) · [paper](https://arxiv.org/pdf/2408.00714)
- [LaMa (WACV 2022) — Apache-2.0](https://github.com/advimman/lama) · [project](https://advimman.github.io/lama-project/)
- [Moebius: 0.2B Lightweight Image Inpainting (ECCV 2026) — Apache-2.0](https://github.com/hustvl/Moebius) · [paper](https://arxiv.org/abs/2606.19195)
- [Comparison of CoModGANs, LaMa and GLIDE for Art Inpainting — Escher's Print Gallery (CVPRW 2022)](https://arxiv.org/abs/2205.01741)
- [BRIA inpainting — 100% licensed training data, paid commercial licence](https://huggingface.co/briaai/BRIA-2.3-Inpainting)
- [Places365 / Places2 dataset terms](https://github.com/CSAILVision/places365)
- [gsplat — Apache-2.0](https://arxiv.org/pdf/2409.06765) · [original 3DGS licence (non-commercial)](https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md)

Industry practice
- [Art of Stereo Conversion: 2D to 3D (fxguide)](https://www.fxguide.com/fxfeatured/art-of-stereo-conversion-2d-to-3d/) — clean plates, roto, occlusion fill
- [StereoBrush: Interactive 2D to 3D Conversion Using Discontinuous Warps (Disney Research)](https://studios.disneyresearch.com/wp-content/uploads/2019/03/StereoBrush-Interactive-2D-to-3D-Conversion-Using-Discontinuous-Warps.pdf)
