# R1 first-hand: the papers R1's seven agent passes relied on, read directly

Date: 2026-09-24. R1 (2026-09-07) was built from seven literature passes run by agents (`R1_passes/`), mostly from
abstracts, snippets and repositories because paper hosts were blocked. The user asked that every paper an agent read be
read first-hand. arXiv is still blocked here; the Hugging Face mirror serves full text for papers it indexes (mostly
2023 onward). Texts fetched are kept in `research/papers/r1/`.

**Already read first-hand elsewhere** (not repeated): Zhang & Tam 2005, Ndjiki-Nya et al. 2011, Criminisi et al. 2004,
Shade et al. 1998 (LDI), Shih et al. 2020 (3D Photography), Daribo & Pesquet-Popescu 2010, Oh et al. 2009, Gautier et
al. 2011, Sun et al. 2005, Bornemann & März 2007 — in `S55_per_paper_notes.md`; Depth Anything V2, Dhamo-style
counterfactual depth, Amodal Depth Anything, PACO, Amodal3R — in `R8_per_paper_notes.md`; Generative Omnimatte — in
`S63c_first_hand.md`.

**Not reachable here** (the mirror returns 404; listed at the end for the user to supply): SLIDE, One Shot 3D
Photography, 3D Ken Burns, Tucker & Snavely 2020, Worldsheet, SynSin, Flash3D, Displacement Fields, SharpNet, Boosting
Monocular Depth, Liba sky segmentation, Shin et al. 2019, AdaMPI, MINE, Spring, Dhamo 2019, Tulsiani 2018, Infinite
Nature, Lai et al. 2018, MoGe (v1), and every pre-arXiv DIBR paper not in S55.

---

## Depth Pro (2410.02073 v2, ICLR 2025) — read in full

**What it is.** Metric depth plus horizontal FOV from one image, no intrinsics needed; fixed 1536² network (plain ViT
patch encoders at several scales, 35 patches, plus a global image encoder, DPT-style decoder); 2.25 MP in 0.3 s on a
V100. Trained on canonical inverse depth (so near content is weighted), two stages: real + synthetic, then **synthetic
only** to sharpen boundaries (gradient/Laplacian losses on synthetic data only, because real ground truth is wrong at
boundaries). FOV head trained separately. Limitation stated: translucent surfaces and volumetric scattering.

**The boundary metric (§3.2), exactly.** An occluding contour between neighbours i, j exists when d(j)/d(i) > 1 + t/100;
F1 averaged over t = 5 … 25 (%), weighted towards the high end, after non-maximum suppression to penalise blur. For
matting datasets the binary mask is **α > 0.1** and only **recall** can be computed (a mask marks some, not all, true
contours).

**Results (Table 2).** Boundary F1 on Sintel 0.409 (next: Metric3D v2 0.321, UniDepth 0.316); **recall on the
hair/fur matting sets AM-2k 0.173 and P3M 0.168** (Depth Anything V2 0.107/0.131, Marigold 0.064/0.101); DIS-5k 0.077.

**Checking R1.**
- R1 §2.7's "scale-free ratio test, t swept 1.05–1.25" is right (t = 5–25 %).
- R1 §2.3 argues: the metric scores recall against the α = 0.1 contour, "i.e. the OUTERMOST extent of hair and foliage,
  so a model that scores well assigns foreground depth to the whole silhouette including its gaps". **Half right.** The
  α > 0.1 mask does put the rewarded edge at the outer fringe of soft hair (mixed pixels count as foreground) — true for
  *fringes*. But a gap with α ≤ 0.1 inside the silhouette is also a mask boundary, so its contour is in the recall
  denominator; a model that fills gaps loses recall rather than gains it. The metric does not reward filling porosity.
- The conclusion R1 drew ("a better depth model will not fix porosity; porosity must come from the image") survives on
  better evidence: **the best model recovers only ~17 % of hair/fur contours** on matting data. Most fine boundaries are
  simply missing from every depth map; the image (matte) must supply them.

**For moebius.** Keep the scale-free ratio test as our contour criterion where we need one (we already reason in
disparity ratios). The 17 % figure is the number to quote for why soft/porous edges go through a matte and the αDepth
two-layer edge model rather than through a better depth map.

---

## TMPI — Tiled Multiplane Images (2309.14291, ICCV 2023, Meta) — read in full

**Method.** Monocular depth (DPT) → a two-headed U-Net predicts a **learned** per-pixel confidence and a denoised depth →
the image is cut into square tiles of **h = 64 px** with stride **r = h − h/8** (one-eighth overlap) → in each tile,
**confidence-weighted k-means with k = n** clusters on depth gives the n plane depths *and* a per-pixel label map → layers
are peeled with the labels, their holes **filled by upsampling valid values from a Gaussian pyramid** (push–pull), then a
second network refines the RGBA; each plane's colour is a blend of the input and a per-plane predicted background. The
confidence network is trained self-supervised (L1 between input depth and the discretised depth); the RGBA network on
AdaMPI-style warp-back pseudo pairs, COCO + DPT. Rendered as textured quads.

**Evidence.** n = 4 planes per tile vs 32 for baselines. Spaces: PSNR 24.93 / LPIPS 0.175 (AdaMPI 26.17 / 0.229; SVMPI
25.42 / 0.210); Tanks & Temples 18.69 / 0.267 (AdaMPI 18.62 / 0.270). Evaluation crops 15 % of the border and scores the
whole frame. Plane placement (Table 3, discretised-depth MAE ×10⁻³ on noisy input): weighted k-means 27.1, plain k-means
35.3, linear spacing 48.7. 91.6 ms and 3.2 GB peak at 350×630 on a 3080. Failure: thin features inconsistent across
tiles; more than 8 planes stops helping.

**Checking R1.** R1 §2.2 says "12.5 %-width tiles, per tile a confidence-weighted 3-cluster k-means on disparity places
four planes — a tuning-free local rule for plug depth (the farthest local mode)". **Corrections:** the 12.5 % is the
*tile overlap* (r = h − h/8), not the tile width (tiles are 64 px, about ⅙ of a 384-px training image); k-means uses
**k = n = 4** clusters for four planes, not 3; the confidence weights are **learned**, so the rule is not tuning-free in
our sense (it has no hand threshold, but it has a trained network); "the farthest local mode" as a plug depth is R1's
inference, not the paper's.

**For moebius.** Two useful facts: (1) plain per-tile k-means on disparity is a threshold-free way to name the few depth
modes in a neighbourhood, and weighting by a confidence roughly halves its error against linear spacing — a candidate
cross-check for the plane far side's run clustering; (2) the paper fills each layer's hidden part with a Gaussian-pyramid
push–pull before any network — the same cheap wash R1 attributed to Solh & AlRegib, used in practice.

---

## Invisible Stitch (2404.19758, Oxford VGG) — read in full

**Method.** Fine-tune ZoeDepth into a **depth-completion** model g(image, mask, partial depth): two extra input channels,
teacher Marigold on NYU v2 images, scale-invariant loss (λ = 0.85); half the time the partial depth is zeroed so plain
prediction is kept. The masks are **made by warping predicted depth to random viewpoints** (from Places365). In their
360° pipeline SD-inpaints the new view, g completes its depth against the existing point cloud, and **ramps at object
edges are "snapped": high-gradient pixels are masked and refilled from their nearest neighbours**, so every pixel goes to
the object or to its surround (no floaters). They also note SD's VAE alters pixels outside the hole and use an
asymmetric VAE to reduce it.

**Evidence.** A benchmark that scores **only the extrapolated region** against true depth (ScanNet 7 832 view pairs;
Hypersim 19 243 pairs, overlap ≥ 0.8). MAE: ours 0.0816 / 0.7295, ZoeDepth + global scale-and-shift 0.1293 / 0.7872,
LucidDreamer's interpolation 0.1604 / 0.8057, CostDCNet 0.585 / 4.01. Ablation (Table 3): **random masks instead of
warped masks 0.7734 → 0.1015 on ScanNet** — the mask shape is the largest single factor; image-only prediction + global
alignment 0.1335.

**Checking R1.** R1 §2.2/§2.5 is right that it is image + partial depth + mask completion usable as a bake-stage
hidden-depth estimator. R1's "the hidden depth is a smooth interpolant of the rim in all of them, floors bulge into the
hole" is **not in this paper** (nor in InFusion below); it is an agent generalisation with no stated source.

**For moebius.** (1) Third independent confirmation (with Geometric Reciprocity and TrajectoryCrafter) that
**view-change-shaped masks** are what matter — here a 7× error reduction from mask shape alone. (2) Their edge "snap" is
the ramp collapse we built (colour-guided on our side). (3) The VAE-alters-kept-pixels warning applies to our SD return:
paste source pixels back outside the hole after decoding.

---

## InFusion (2404.11613, ECCV 2024) — read in full

**Method.** A latent-diffusion **depth-completion** model initialised from Marigold: input = noisy depth latent + masked
clean depth latent + latent of the (SDXL-inpainted) RGB + mask (13 channels); depth normalised by its 2nd/98th
percentiles (affine-invariant). Trained on SceneFlow (FlyingThings + Driving, >100 k synthetic frames) with **random
square/stroke masks**, 8×A100 for a day. Used to place 3D-Gaussian points in a removed region, then 50–150 iterations of
Gaussian fine-tuning on the one reference view; a progressive multi-view variant for heavy occlusion.

**Evidence.** SPIn-NeRF benchmark, inpainted regions of held-out views: LPIPS 0.421 / FID 92.6 vs SPIn-NeRF 0.465 / 156.6
and Gaussian Grouping 0.454 / 123.5; 40 s vs 5 h / 20 min. **No depth-accuracy number** — the depth model is judged only
through final renders and figures (Fig. 5: LaMa/SDXL inpainting of colour-mapped depth is lossy; mono depth + alignment
leaves discontinuities). Limitation: lighting changes across views; complex objects in 360° scenes.

**Checking R1.** R1's description of the model is accurate. As above, "smooth interpolant … floors bulge" is not in the
paper.

**For moebius.** InFusion and Invisible Stitch both say the same thing we measured on our own plates: completing depth
*conditioned on the image of the fill* beats aligning an unconditioned depth map, and inpainting a colour-mapped depth
image is lossy. Our plane-law depth for the hole is geometry-only; the image-conditioned completion is the candidate
second opinion for the plate depth once SD has painted the plate colour (Invisible Stitch is the lighter of the two:
ZoeDepth-sized, one pass).

---

## Stable Virtual Camera (SEVA, 2503.14489, Stability AI) — read in full (appendix tables partly)

**Method.** SD 2.1 inflated to 3-D self-attention plus 1-D attention across views (1.3 B; 1.5 B with optional temporal
convolutions), conditioned on input-view latents, **Plücker ray embeddings**, a CLIP embedding; **no 3-D representation**.
576² images; trained with context T = 8 then 21. Sampling: for more targets than fit, a **two-pass procedural** scheme —
anchors first (with a spatial memory bank for long paths), then the frames between anchors; "interp" ordering gives
smooth video, one-pass gives flicker.

**Evidence.** Small-viewpoint set NVS: best in most splits (e.g. LLFF P = 3 +6 dB); with **one input image the scale is
ambiguous** and they sweep the camera-normalisation unit per scene to report the best. **Large-viewpoint, one input
image: 12.9–15.3 dB PSNR** (Mip360, DL3DV, T&T, CO3D). Limitations: humans, animals and water degrade; trajectories that
pass through objects flicker; viewpoints far from the inputs degrade.

**Checking R1.** R1 §2.2 quotes SEVA's "v1.0 shipped 'foreground objects detached from the background'". **That phrase
is not in the paper**; it must come from the repository's release notes, which cannot be checked here. The broader R1
point (no generative NVS model yields a per-pixel layered asset for a browser) stands — SEVA re-generates whole frames.

**For moebius.** Two consistent data points with TrajectoryCrafter: generating a large novel view from one image lands
around 13–15 dB against truth, and single-image scale is ambiguous. Their anchors-then-fill sampling is the same
keyframe pattern as DiffuEraser's pre-inference and our "paint the static layer once".

---

## MoGe-2 (2507.02546, Microsoft, NeurIPS 2025) — read in full (main tables' cells partly lost; appendix tables survived)

**Method.** MoGe's **affine-invariant point map** (DINOv2-L, robust optimal alignment solver, multi-scale local
supervision), plus a **separate metric scale** predicted from the CLS token by an MLP, trained with a stop-gradient on
the aligned scale — so scale errors do not disturb relative geometry. Focal/shift recovered from the point map.
**Real-data refinement:** a synthetic-only MoGe flags real depth that disagrees *locally* (per-sphere alignment, several
radii) — mainly LiDAR/RGB mis-sync and SfM holes at boundaries — and refills the flagged pixels by **log-depth Poisson
completion**: match the gradients of the synthetic model's log depth inside the region, with the real depth as the
Dirichlet boundary (Eq. 7). 24 datasets, 32 A100 for 120 h.

**Evidence.** Best relative and metric geometry averaged over 10 / 7 datasets (metric point map rank 1.64 vs UniDepth V2
2.43, Depth Pro 3.29); boundary F1 "comparable to Depth Pro" using far fewer tokens. Ablation: synthetic-only data gives
the sharpest edges (F1 13.3) but worst geometry; raw real data the reverse (10.3); refined real data 12.5 with near-best
geometry. Latency 29–108 ms (A100, FP16) for 484²–1188² input. **Limitations stated:** thin lines and hair; straight
structures under large foreground/background scale differences; metric scale out of distribution.

**Checking R1.** R1 §2.7 and pass 7 credit MoGe-2 with "metric, FOV, **sky validity mask**". Metric and FOV: yes. **A
sky/validity mask is not described anywhere in the MoGe-2 paper** (it is a MoGe-1/repository output); the claim cannot be
supported from this text.

**For moebius.** The log-depth Poisson completion is directly usable: to give a painted plate a depth, run a depth model
on the painted image and **keep only its log-depth gradients inside the hole, with our known rim depth as the boundary
condition**. That is image-conditioned (like Invisible Stitch/InFusion), costs one depth pass and one sparse solve, and
cannot drift from the rim — a principled alternative to aligning a whole depth map.

---

## UniDepthV2 (2502.20110) — read (method, evaluation, efficiency)

Metric 3-D from one image with **no intrinsics input**: a camera module predicts pinhole residuals that are turned into a
dense azimuth/elevation ray map, which prompts the depth module by cross-attention; output in a pseudo-spherical space
(azimuth, elevation, log-depth) so camera and depth errors are disentangled; a geometric-invariance loss across
augmented views; an **edge-guided scale-shift-invariant loss** on patches around image edges (median/MAD-normalised
inverse depth); and an **uncertainty output** trained without extra labels (evaluated by AUSE / Spearman). Beyond ~5 MP
every compared model becomes memory-bound. **Checking R1:** "predicts intrinsics", "edge-guided local SSI loss",
"confidence (v2)", "pseudo-spherical" — all accurate.

## GeoCalib (2409.06704, ECCV 2024) and Perspective Fields (2212.03239, CVPR 2023) — read (method and results)

**Perspective Fields** predict, per pixel, the **up-vector** (projected inverse gravity) and the **latitude** (angle of
the ray above the horizontal plane; 0 on the horizon); a small ParamNet turns them into roll, pitch, FoV **and principal
point** — the representation survives cropping and warping, where centred-pinhole calibrators fail (pitch error −40 %
on crops). Object cut-outs need a separate distilled model. **GeoCalib** feeds a learned perspective field and
per-pixel confidences into a Levenberg–Marquardt optimisation of the camera (gravity + focal, pinhole or fisheye), can
take any known parameters as priors, and outputs uncertainties that track the true error; it beats both classical
vanishing-point methods (which fail outside Manhattan scenes) and pure regressors on median roll/pitch/FoV.

**Checking R1.** "Gravity, horizon, focal" from either — accurate.

**For moebius.** A point R1 did not draw: **paintings and cropped photographs often have an off-centre principal
point**, which a centred-pinhole assumption misreads as pitch. Perspective Fields recovers the principal point; if we
ever fit a ground plane or horizon to a picture (R1's A2 step), it should come from a field that allows the shift.

---

## Floating No More / ORG (2407.18914, ECCV 2024) — read (method, data, experiments)

**Method.** For an object-centric image, predict two dense fields with a PVTv2/SegFormer network: a **Perspective Field**
(up-vector + latitude, as above) and **pixel height** — the image distance from a point to its vertical projection on the
ground — for **both the front (first entry) and the back (last exit) surface** along each ray. Grid search on the
perspective field gives FoV and roll/pitch; a closed-form reprojection turns pixel heights into a depth map and a point
cloud standing on the ground plane. Trained on 3.36 M Blender renders of Objaverse objects (512², random FoV and
viewpoint; a CUDA ray tracer for front/back pixel heights). Principal point assumed at the centre.

**Evidence.** Better AbsRel/δ₁ and point-cloud metrics than LeReS, MiDaS/DPT + CTRL-C and Zero-123 on unseen object and
human sets; the gain grows with viewpoint diversity; shadows and reflections with correct contact.

**Checking R1.** R1 §2.4 cites ORG for "ground contact" — right. Two refinements: (1) R1's "shadow footprint is the only
image cue to depth extent" comes from the pass's OutCast quote, not from ORG; (2) ORG **does predict a back surface per
pixel** (as a pixel height), so R1's "Shin et al. 2019 — the only scene-level predictor of an object's back surface" is
true only at *scene* level; ORG does it per object (masked, object-centric, trained on synthetic objects).

**For moebius.** ORG's back-surface pixel height is exactly the "thickness field" R1 wanted for self-occlusion, in a
form that needs no metric scale; it applies to isolated objects on a ground plane, which is the starwatcher/gladiator
case rather than the painting-full-of-figures case. Candidate for the object-layer back face if the plane law ever needs
a learned thickness.

---

## HairGuard (2601.03362, ETH / Disney Research) — read (method)

Soft boundaries modelled as matting: I = α·FG + (1−α)·BG. A **depth fixer** (DINOv2/DPT features + a U-Net pixel branch
fed Sobel edges of the input depth) outputs a **gate map** G and a residual, d̂ = d_in·G + d_res·(1−G), so it edits only
soft-boundary pixels and plugs onto any depth model; training pairs are synthesised from **matting datasets** composited
over backgrounds (a low α threshold gives the fine target, a high threshold plus blur the degraded input). For view
synthesis: forward-warp with the fixed depth, a generative painter for the holes, and a **colour fuser** that removes
the "redundant background colours" a warped soft edge carries and the painter's hallucinated texture. Observations
stated: Depth Anything V2 breaks hair; **Depth Pro puts soft-boundary depth behind the true surface, detaching hair**;
latent models degrade fine texture. **Checking R1:** cited only as "the learned form" of soft visibility — fair.

**For moebius.** Their observation that a warped soft edge carries background colour is the same point as αDepth and
the EasyOmnimatte un-compositing: an edge pixel must be split into FG and BG before it moves.

## Modeling Depth Ambiguity — MDA (2606.02552, Michigan / NVIDIA) — read (method, sky section)

**Flying points explained:** a pixel straddling an edge is trained towards one depth, so the loss pulls it to a value
between the two surfaces, on neither. MDA replaces the single (confidence-weighted Laplace) output with a **K-component
mixture** — depth, confidence and weight per component, only the last layer changed — and decodes by choosing the most
likely component, so a boundary pixel lands on the foreground *or* the background, never between. Instantiated on
**DA3** and VGGT, negligible overhead, robust to input blur. Extensions: transparent objects (several components active
at once = several depth layers) and **sky as its own component** at infinite depth.

**Checking R1.** "'Modeling Depth Ambiguity' 2026 sky mixture component" — accurate.

**For moebius.** This is the cleanest statement of why our silhouettes ramp and of what fixes it: at an edge pixel
keep **two** depth hypotheses and assign the pixel to one. Our colour-guided ramp collapse does the assignment after
the fact; an MDA-style DA3 would give the two hypotheses (front and back depth at the same pixel) directly — which is
also what the αDepth soft-edge layer needs. Worth checking whether MDA weights for DA3 are released.

---

## Gen3DSR (2404.03421, 3DV 2025), LayerPano3D (2408.13252), Scene4U (2504.00387) — read (method sections)

- **Gen3DSR.** Entity segmentation (CropFormer), OneFormer to split entities into things and stuff, Perspective Fields for
  the camera, Marigold depth. Things: amodal completion + per-object single-view reconstruction, placed by depth.
  Stuff: all background entities are merged into one mask and a **small SDF MLP (plus a colour MLP) is fitted to their
  unprojected points**, which continues the background behind the objects. Limitations: errors of each stage propagate.
- **LayerPano3D** (text → panorama). Layers are made by **panoptic segmentation (ADE20K) of all visible assets, each
  given the 75th-percentile depth of its mask, then K-means into N depth layers** — not by a stuff/things split. Each
  layer's hidden part is filled with Flux-Fill + a panorama LoRA; each layer's depth is completed conditioned on the
  inpainted layer and the masked depth of the layer behind; lifted to 3D Gaussians.
- **Scene4U** (real panorama). Open-vocabulary segmentation, then an **LLM groups segments into dynamic objects,
  foreground, background and sky**; layers repaired back to front with FLUX inpainting; depth estimation + completion;
  layered 3DGS training.

**Checking R1.** R1 §2.5 says the 2024–25 literature (Gen3DSR, LayerPano3D, Scene4U, Generative Omnimatte) "converged on
one rule: background = the union of panoptic stuff classes … represented as a surface fitted to their depth; things are
the separable layers". **Overstated.** Only Gen3DSR uses the stuff/things split with a fitted background surface (an SDF,
not a depth surface); LayerPano3D clusters *all* assets by depth; Scene4U lets an LLM decide the grouping (with sky as its
own class); Generative Omnimatte is per-object removal and has no stuff model at all. The quote attributed to Gen3DSR is a
paraphrase of the sentence above.

**For moebius.** What they do share, and what matters to us: **fill layers back to front, each conditioned on the layer
behind**, and **complete each layer's depth conditioned on its own inpainted image and the depth behind it** (LayerPano3D
Eq. 1) — the same order and conditioning as our plate → object-layer build. Our depth-only reveal geometry does not need
semantic classes to decide what tears; semantics would only be a tie-breaker.

---

## Tree-D Fusion (2407.10330, ECCV 2024) and pix2gestalt (2401.14398, CVPR 2024) — read (method, results, limits)

**Tree-D Fusion.** From one street-view image and a genus label: optimise a NeRF with score distillation from two
tree-adapted diffusion priors (SD + LoRA on tree photos, Zero123 on synthetic trees) to get a **3-D crown envelope**,
fill it with point markers, then **grow branches into it by space colonisation** (a genus-conditioned developmental
model). 600 k trees released. Best for symmetric trees; shapes limited by the simulator. **Checking R1:** "fills a crown
envelope … never per-gap depth" — accurate (the paper recovers an envelope and grows plausible structure, not the observed
gaps).

**pix2gestalt.** An image-conditioned diffusion model (from SD, trained on synthetic occluded/whole pairs) that, given a
point or mask prompt on a partly visible object, **synthesises the whole object alone**; sampling gives several
completions; works on paintings. SD-XL inpainting, by contrast, "often hallucinates extraneous, unrealistic details";
failures include common-sense/physics errors (a car completed facing the wrong way). **Checking R1:** "completes a
silhouette hidden by ANOTHER object … applicable to stacked occluders, not to self-occlusion" — accurate. The VRAM and
speed figures in the pass are from the repository, not the paper.

---

## Summary

**Read first-hand here (17):** Depth Pro, TMPI, Invisible Stitch, InFusion, Stable Virtual Camera, MoGe-2, UniDepthV2,
GeoCalib, Perspective Fields, Floating No More, HairGuard, MDA, Gen3DSR, LayerPano3D, Scene4U, Tree-D Fusion,
pix2gestalt. Plus the ten classical papers already read in S55 and the R8 set.

**Corrections to R1:**

| R1 said | The paper says |
|---|---|
| Depth Pro's metric rewards foreground depth over a silhouette "including its gaps" | α > 0.1 edges include internal gaps; filling gaps loses recall. The real support for "porosity comes from the image": best model recovers ~17 % of hair/fur contours |
| TMPI: 12.5 %-width tiles, 3-cluster k-means for four planes, tuning-free | 64-px tiles with ⅛ overlap; k = n = 4; confidence weights are learned |
| Hidden depth in InFusion / Invisible Stitch "a smooth interpolant of the rim … floors bulge" | not in either paper |
| SEVA v1.0 "foreground objects detached from the background" | not in the paper (repository note at best) |
| MoGe-2 has a sky validity mask | not described in MoGe-2 |
| 2024–25 scene papers "converged on one rule" (stuff = background surface) | only Gen3DSR does that; LayerPano3D clusters by depth, Scene4U by LLM |
| Shin 2019 the only predictor of an object's back surface | ORG predicts per-pixel back-surface pixel height (object-level) |

**New, useful for the current work:** MoGe-2's log-depth Poisson completion (depth for a painted hole from a depth
model's gradients, pinned to our rim); MDA's two-hypothesis edge pixels on DA3 (the principled form of ramp collapse and
the input αDepth needs); Invisible Stitch's 7× gain from view-change-shaped masks (third confirmation of the round-trip
mask idea); Perspective Fields' principal-point recovery for cropped pictures; ORG's back-surface pixel height as a
learned thickness.

**Still second-hand — needs the texts (please supply as .md or PDF if you want these checked):**
SLIDE (Jampani et al., ICCV 2021, arXiv 2109.01068) — R1's "single most reusable paper" and the source of its
soft-visibility and disocclusion-extent formulas; One Shot 3D Photography (Kopf et al., SIGGRAPH 2020, 2008.12298);
3D Ken Burns (Niklaus et al., SIGGRAPH Asia 2019, 1909.05483); Tucker & Snavely, single-view MPI (CVPR 2020,
2004.11364); Boosting Monocular Depth (Miangoleh et al., CVPR 2021, 2105.14021); Zitnick et al., "High-quality video view
interpolation using a layered representation" (SIGGRAPH 2004); Solh & AlRegib, hierarchical hole filling (IEEE JSTSP
2012); Müller et al., reliability-based 3D video view synthesis (EURASIP JIVP 2008); Zinger, Do & de With (JVCIR 2010);
Monster Mash (Dvorožňák et al., SIGGRAPH Asia 2020). Lower priority: Worldsheet, SynSin, Flash3D, SharpNet, Displacement
Fields, AdaMPI, MINE, Spring, Shin et al. 2019, Liba et al. 2020.
