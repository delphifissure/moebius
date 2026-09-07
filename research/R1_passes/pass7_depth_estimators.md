# Pass 7 — Monocular depth estimator behaviour for layered rendering, 2019–2026 (agent report, lightly trimmed)

Access caveat from the pass: arXiv, HF, most project pages blocked; [V] = fetched source (GitHub READMEs/code, Apple developer docs); [S] = search snippet only; [U] = unverified.

## 1. Model families and output spaces
- MiDaS / DPT (Ranftl et al. 2020/2021; v3.1 Birkl 2023): relative inverse depth, scale-and-shift invariant [V]; fit disp = s·(1/Z) + t against ≥ 2 known depths; no focal; boundaries smooth, thin structures thickened [S 2110.05885]; 256/384/512 px inputs; 16-bit PNG or PFM; sky → disparity ≈ 0 [V].
- Depth Anything V2 (Yang et al. 2024): relative affine-invariant inverse depth (SSI + gradient-matching) [V]; metric variants (Hypersim indoor 20 m, VKITTI outdoor 80 m) output metres [V]; trained on synthetic labels because real labels are noisy at edges, miss thin structures and mislabel transparent/reflective surfaces [S 2406.09414]; DA-2K has a transparent_reflective category [V]; 518 px, larger input → finer details [V]; no focal.
- Marigold (Ke et al., CVPR 2024): affine-invariant DEPTH (not disparity) [V]; 768 px then upsampled; trained Hypersim + VKITTI 2 [V].
- ZoeDepth (Bhat et al. 2023): metric = MiDaS BEiT-384 backbone + metric-bins head, NYU/KITTI routing [V]; soft edges inherited; unmaintained since May 2025 [V].
- Metric3D v1/v2 (Hu/Yin et al. 2023/2024): metric depth (+ normals) in a canonical camera (f = 1000 px, 512×960), de-canonicalise Z = Z_c · f/1000 [V]; NEEDS focal, else falls back to 9 default focals (scale guessed) [V]; failures: chandeliers, drones, aerial [V].
- UniDepth v1/v2 (Piccinelli et al. 2024/2025): metric depth + predicted intrinsics + confidence (v2); pseudo-spherical representation [V]; v2 adds an edge-guided local SSI loss for sharper edges [V].
- Depth Pro (Bochkovskii et al., Apple, ICLR 2025): canonical inverse depth C, 1/Z = C·W/f_px; f_px from EXIF else predicted FOV [V depth_pro.py]; boundary-sharpness design with shipped boundary metrics; output resized back to input bilinearly [V] (an unavoidable ≤ 1 px ramp); fixed 1536² input, 0.3 s; CLI saves float npz (+ 8-bit turbo JPEG for visualisation only) [V].
- MoGe / MoGe-2 (Microsoft 2024/2025): point map + depth + mask + FOV/intrinsics; MoGe-1 affine-invariant, MoGe-2 metric with sharp details [V]; validity mask handles sky/infinite regions [V]; strong candidate for the unknown z-scale problem.
- Depth Anything 3 (ByteDance 2025): depth-ray representation; metric variant needs focal unless the nested model [V].
- PromptDA (Lin et al., CVPR 2025): metric up to 4K conditioned on a 192×256 LiDAR prompt [V]; not applicable without LiDAR.
- DepthCrafter (Hu et al. 2024): diffusion video depth; code min-max normalises the sequence to [0,1] [V]; 110-frame windows.
- Video Depth Anything (Chen et al., CVPR 2025): relative (DA-V2 head + temporal gradient loss) and metric variants [V]; streaming mode loses accuracy (δ1 0.926 → 0.836) [V].
- Takeaway: relative models are affine in disparity (MiDaS, DA-V2, VDA, DepthCrafter) or in depth (Marigold). A step Δ in normalised disparity is Δ·Z² in depth, so a fixed disparity threshold is far more permissive far away (Shih's depth_threshold 0.04 is in rescaled disparity). Only metric models with a focal define an x/z aspect ratio; Depth Pro, UniDepth, MoGe and DA3-nested estimate the focal so the ratio is self-consistent even if absolutely wrong.

## 2. Boundary evaluation
- Depth Pro boundary metrics [V eval/boundary_metrics.py]: prediction and GT inverted (1/depth) → scale-invariant; an occluding contour exists where the neighbour depth ratio exceeds t, four directions; t swept 1.05 → 1.25 (10 values), weights ∝ t; precision/recall over edges, weighted F1; for matting datasets recall only, after NMS, alpha thresholded at 0.1; no sky masking in the code. Paper numbers vs other models [U].
- Depth Boundary Error, Koch et al. 2018 (iBims-1, ECCV-W; CVIU 2020 follow-up): accuracy and completeness of predicted depth edges vs annotated GT edges [S]; most CNNs "produce smooth edges losing sharp transitions" [S].
- Edge ramp width vs resolution: nothing published directly. Mechanism documented by Miangoleh et al. (Boosting Monocular Depth, CVPR 2021) [V README]: low-res inference gives consistent structure, missing detail; beyond the receptive field gives sharp edges but broken structure; R0/R20 resolution rules. Implication: ramp width is roughly constant in network-input pixels, so it scales with (image width / network input width) after upsampling — our 4 px at 1200 px is consistent with a 1–2 px ramp at 384–518 px input plus bilinear upsampling.

## 3. Resolution behaviour
Fixed-res models upsample their output; structures finer than one network pixel are lost or merged. Tiling: PatchFusion (Li et al. 2024) documents seams and per-tile scale inconsistency, fuses global + patch predictions, 4K [V]. Boosting merges base + R20 via a pix2pix net, 16-bit PNG output [V].

## 4. Quantisation and storage
Every research pipeline stores float or 16-bit (MiDaS 16-bit PNG/PFM, Marigold 16-bit/npy, Boosting 16-bit, ZoeDepth 16-bit raw, Depth Pro npz float32, VDA/DepthCrafter npz + 32-bit EXR, Shih .npy with log_depth) [all V]. No pipeline stores 8-bit as its working format. Apple Portrait depth: normalised disparity, Float16/32 in memory, 8-bit lossy in JPEG only if filtered, 16-bit lossless otherwise [V WWDC17-507] — the one shipping 8-bit format, and it is disparity-encoded. KSII TIIS "Effects of Depth Map Quantization for Computer-Generated Multiview Images using DIBR": below ~7 bits degrades DIBR; 7+ sufficient for their multiview displays [S] — small-baseline stereo, not our 45°.

## 5. Scale anisotropy and parallax mapping in shipping pipelines
- Shih et al. 2020 [V code]: MiDaS disparity → subtract min, 3×3 box blur, rescale to disp_rescale (10 / 3.0), depth = 1/max(disp, 0.05); intrinsics INVENTED: f = max(H, W) px (~53° FOV), principal point centre; camera motion x/y ±0.015, z −0.05 in normalised units — very small baselines; depth_threshold 0.04 on disparity differences; sparse bilateral filtering = weighted median only at discontinuity pixels excluding edge pixels from the support, re-detecting discontinuities each of 5 passes (windows 7,7,5,5,5; σ_s 4; σ_r 0.5) → sharpens ramps; depth_edge_dilate 10/5; context/background 140/70; ext_edge_threshold 0.002.
- Kopf et al. 2020: only the Tiefenrausch depth net released; LDI/mesh pipeline not open-sourced [V]; edge filtering and camera range [U].
- Google Cinematic Photos (2021): single-image depth CNN, mesh with tears, per-photo virtual camera trajectory optimised against a "stretchiness" loss — parallax amplitude solved per image [S].
- Apple spatial photos (visionOS 2) [V WWDC24-10166]: stereo HEIC with baseline (≈ 64 mm natural; 16–32 mm close-ups; large baselines miniaturise), horizontal FOV ≤ 90°, disparity adjustment as % of width ("even 2–3 percentage points dramatically alter depth perception"), vertical disparity must be zero. The closest published comfort bound: one IPD baseline and a few % of width convergence offset.
- Immersity AI / Leia: a user "depth intensity" dial [S].
- Maximum comfortable eye offset for single-image parallax: no paper found. Shih's defaults are ±1.5 % of the focal-normalised frame; Apple limits to one IPD. Our 45°-of-portal-distance offsets are an order of magnitude beyond anything published for single-image content.

## 6. Depth-edge refinement techniques
Weighted-median at discontinuities (Shih) [V]; multi-resolution merging (Miangoleh) [V]; guided patch fusion (PatchFusion) [V]; learned edge losses (UniDepthV2 edge-guided local SSI [V]; DA-V2 gradient matching [S]; "Monocular Depth Estimation with Sharp Boundary" boundary-aware loss targeting flying pixels [S 2110.05885]); segmentation/matting guidance (3D Ken Burns flattens salient objects and refines edges [S/repo]; US patent 12367585 mask-guided depth refinement [S]); SharpDepth 2024 diffusion sharpening of metric models [S].

## 7. What we should steal (prioritised by the pass)
1. Estimator: Depth Pro primary (metric, focal, native 1536, boundary tooling), MoGe-2 second opinion (focal + sky validity mask); DA-V2-Large relative for speed. Use the estimated f_px to set the x/z aspect: one texel of width at depth Z is Z/f_px world units — the "texel of depth per texel of width" prior becomes measurable, not fitted.
2. Storage: float32 npz/EXR internally; 16-bit PNG of inverse (or log) depth when PNG is required; never 8-bit linear depth.
3. World depth mapping: decide which space is affine (disparity vs depth) before applying the diorama sliders; map through disparity so the sliders act linearly on parallax.
4. Edge handling: Depth Pro's ratio test (Z_far/Z_near > t, t ≈ 1.05–1.25, scale-free) for tear detection instead of a normalised threshold; Shih's discontinuity-aware weighted median to shrink ramps before tearing.
5. Evaluation: port boundary_metrics.py (ratio-based F1 and matting recall) into the synthetic harness.

## Artefacts the synthetic tests must reproduce (degradation model)
- Edge ramp: blur the DEPTH with width ≈ (W_img / W_net) × 1–2 px, then bilinear upsample; W_net ∈ {384, 518, 768, 1536}.
- Thin-structure loss/merging: erase or dilate-to-background structures narrower than ~1–2 network pixels.
- Halos: low-frequency depth bleed within ~1–3 % of width around objects, both signs.
- Flying pixels: the ramp itself, rendered — the tear rule must remove intermediate samples.
- Terracing: 8-bit quantisation of linear depth on slow gradients; compare 8-bit disparity and 16-bit.
- Scale/shift error: random affine in disparity (relative) or depth (Marigold); ±20–30 % focal error for metric models.
- Sky: max range / disparity 0 (MiDaS-style) or invalid mask (MoGe); both must render without a wall at the diorama back.
- Transparent/reflective/mirror/water: surface depth replaced by the reflected/transmitted content's depth.
- Tiling seams: piecewise scale/shift offsets across patch borders.
- Temporal flicker (video): per-frame affine drift.
