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
