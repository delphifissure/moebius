# Pass 4 — Priors and predictors for geometry hidden behind a single view's silhouettes (agent report, lightly trimmed)

Verification note from the pass: paper hosts were blocked by the proxy; first-hand details come from code/READMEs (Monster Mash, TRELLIS, Hunyuan3D-2, TripoSR, InstantMesh, Wonder3D, One-2-3-45, zero123, ECON, Depth Pro, UniDepth, MoGe, pix2gestalt, deocclusion, Amodal-Depth-Anything, Amodal3R); internals marked [unverified] are from memory.

## 1. Layered / multi-layer depth from one image
- Dhamo, Tateno, Laina, Navab & Tombari, "Peeking Behind Objects: Layered Depth Prediction from a Single Image", Pattern Recognition Letters 125, 2019 (arXiv 1807.08776): two-layer LDI (front + background behind foreground objects), synthetic indoor training; external occlusion only; nothing on thickness.
- Shin, Ren, Sudderth & Fowlkes, "3D Scene Reconstruction with Multi-layer Depth and Epipolar Transformers", ICCV 2019 (arXiv 1902.06729; repo daeyun/single-view-3d-scene-recon, weights apparently never released): viewer-centred multi-layer depth including the EXIT (back) surface of the first object along each ray [layer count unverified; ~5 on SUNCG], epipolar feature transformer for the floor extent. The only scene-level work predicting per-pixel object thickness (entry–exit); synthetic indoor; back less accurate than front. Its representation (entry + exit depth per pixel) is the target format for any thickness prior.
- Tulsiani, Tucker & Snavely, "Layer-structured 3D Scene Inference via View Synthesis", ECCV 2018: LDI via view-synthesis loss; background-behind-object.
- Shih et al. CVPR 2020; SLIDE ICCV 2021: cut at cliffs, inpaint colour and depth of the hidden background from the background side; the object is a zero-thickness sheet, seen cardboard side-on at large offsets. Discipline to keep: plug depth inpainted from the far side, never a blend with the foreground.

## 2. Amodal depth (2024–2026)
- Li et al., "Amodal Depth Anything", ICCV 2025 (arXiv 2412.02336): RGB + amodal mask → relative depth of the object's parts hidden behind an external occluder; Amodal-DAV2 and Amodal-DepthFM; ADIW composited dataset. Not the back surface.
- Jo, Lee & Rhee, IEEE Access 2024: iterative amodal mask → amodal depth; same scope.
- No 2020–2026 work found that predicts dense back-surface depth for arbitrary in-the-wild scenes; backs exist only for humans (§5) and via object generators (§6).

## 3. Amodal segmentation / completion
- Zhu, Tian, Metaxas & Dollár, "Semantic Amodal Segmentation", CVPR 2017 (COCOA). Zhan et al., "Self-Supervised Scene De-occlusion", CVPR 2020 oral (PCNet-M/PCNet-C). Ozguroglu et al., pix2gestalt, CVPR 2024 (22–28 GB VRAM, seconds per object). Wu, Zheng, Guan, Vedaldi & Cham, Amodal3R, ICCV 2025 (TRELLIS conditioned on visible/occluded masks). All complete a silhouette hidden by ANOTHER object; our silhouette is complete and we need depth extent; only the ordering cue transfers and the depth map already gives it.

## 4. Silhouette inflation
- Igarashi, Matsuoka & Tanaka, Teddy, SIGGRAPH 1999: chordal-axis spine, height from distance to the silhouette, quarter-oval sewing, mirrored back [from memory]; thickness ∝ local width, ratio ≈ 1.
- Dvorožňák, Sýkora, Curless, Jamriška, Kopf et al., Monster Mash, SIGGRAPH Asia 2020 (repo google/monster-mash). Verified from src/reconstruction.cpp: inflation is a Poisson solve Δz = −c inside each region, z = 0 on the outline, then z ← sgn(z)·√|z|; front and back solved separately with ±c; defaultInflationAmount = 2 (commonStructs.h); overlapping parts pushed apart in z by the layered ARAP-L deformer. No explicit scaling by region size and none needed: for a disc of radius R the Poisson solution is c(R² − r²)/4, so after the square root the profile is a hemi-ellipsoid with peak height R·√c/2; with c = 2 that is 0.71 R per side — total thickness ≈ 0.71 × local width, self-scaling, resolution-independent (mass-normalised operator). Real-time in the browser. Verdict: the best-justified zero-tuning thickness rule in the literature; smooth (no crease at the spine) unlike the medial-axis envelope; and the pass's judgement on our A257d scale fit: a normalised, blurred 8-bit depth map cannot resolve a bulge of a few centimetres inside a scene spanning metres, so a scale fitted to the front bulge will always come out near zero.
- Weng, Curless & Kemelmacher-Shlizerman, Photo Wake-Up, CVPR 2019 (arXiv 1812.02246): SMPL fit, template silhouette warped to the person's silhouette, front and back depth maps from the warped SMPL renders; arm-over-torso self-occlusion handled with body-part label maps so parts get separate layers; background inpainted. Thickness from the body model (~0.25–0.35 of shoulder width for a torso); correct treatment of internal self-occlusion = separate layers per part, not a tunnel.

## 5. Human / animal body priors
- SMAL (Zuffi, Kanazawa, Jacobs & Black, CVPR 2017) and SMPL fitting: closed body from keypoints + silhouette; seconds to minutes; fails on unusual species/poses.
- PIFuHD (Saito et al., CVPR 2020): front AND back normal maps into a pixel-aligned implicit function; ≥ 8 GB GPU.
- ECON (Xiu, Yang, Cao, Tzionas & Black, CVPR 2023 highlight, arXiv 2212.07422): front/back normals conditioned on SMPL-X, d-BiNI integrates them into two depth sheets whose gap is anchored to the SMPL-X depth; ~1.8 min per image. "Thickness = body-model thickness, detail = normals"; an offline oracle for people.

## 6. Single-image object generators
Zero-1-to-3 (~22 GB), One-2-3-45 (40 s A6000), Wonder3D (2–3 min; "front-facing images always lead to good reconstruction"), TripoSR (< 0.5 s A100, 6 GB), InstantMesh (Zero123++ + sparse-view LRM), Hunyuan3D-2 (6 GB shape / 16 GB textured; 10–25 s), TRELLIS (1.2 B, ≥ 16 GB, ~16 s H800; Amodal3R builds on it). All assume a segmented, centred object; the back is hallucinated (Janus failures: Dehallu3D 2603.01601, AR-1-to-3 2503.12929). Verdict: offline per-object pre-pass at most, using only a low-frequency thickness field (re-projected entry/exit depth), never its texture; at 45° you see the side, never the true back.

## 7. Symmetry priors
Wu, Rupprecht & Vedaldi, unsup3d, CVPR 2020 best paper; Zhou et al. 2020 (2006.10042); Sym3DNet 2022; "Symmetry Strikes Back" 2024 (2411.17763). Bilateral symmetry yields the far half only when the symmetry plane is not parallel to the view; head-on it says nothing about depth extent. Not applicable.

## 8. Thickness from perspective / ground contact / shadows
"Floating No More: Object-Ground Reconstruction from a Single Image" (ORG, 2024, 2407.18914); pixel-height maps (Sheng et al., 2207.05385): ground plane and contact points per object; OutCast: "a thin box will cast a thin shadow" — shadow footprint is the only image cue to depth extent and needs a light direction. Verdict: ground contact is the cheap justified constraint — the inflated side must terminate on the ground plane at the silhouette's bottom edge.

## 9. How deep is the scene relative to its width?
A silhouette w px wide at metric depth z has world width z·w/f: thickness-vs-width ratios are meaningless in an affine-invariant depth map and require f. Depth Pro (Bochkovskii et al., ICLR 2025, arXiv 2410.02073): metric depth + focal length in pixels, 0.3 s per 2.25 MP. UniDepth/V2 (Piccinelli et al., CVPR 2024/2025): predicts or accepts intrinsics. MoGe / MoGe-2 (Wang et al., CVPR 2025 oral / NeurIPS 2025): affine-invariant point map with recoverable FOV, 60 ms A100; MoGe-2 adds metric scale. Focal benchmarks not retrieved [unverified]; consensus: Depth Pro lowest metric error, UniDepthV2/Metric3Dv2 most stable; a wrong focal distorts geometry even with correct depth. Rule: convert silhouette width to world width once, offline, with the predicted f; derive thickness from that, never from the 8-bit depth range.

## What we should steal (prioritised by the pass)
1. Poisson inflation with c = 2 (Monster Mash): thickness ≈ 0.71 × local silhouette width, smooth, self-scaling; offline per foreground component.
2. Metric width via predicted focal (Depth Pro / MoGe / UniDepth) so thickness is in world units; drop the front-bulge fit.
3. Ground-contact clamp (ORG / pixel-height): the side ends on the ground plane at the silhouette's lower edge.
4. Per-part layering for internal self-occlusion (Photo Wake-Up, Monster Mash ARAP-L): each part its own inflated back and z offset where the depth map shows an internal cliff.
5. Background-side inpainting discipline for the plug (Shih / SLIDE); soft alpha at cliffs.
6. If budget allows: offline TripoSR/Hunyuan-mini per object, only for a thickness field in Shin et al.'s entry/exit representation.

## What the literature says about filling a self-occlusion when the back is unknown
Nobody fills at the object's own depth. Layered methods treat the reveal as background at background depth; inflation and body methods give the object a closed side of thickness proportional to its width and let the background appear beyond it. The principle "a gap inside the head-on silhouette must never show distant background" is stronger than the literature supports: the correct picture is side first, then background. Whether background appears depends on thickness × parallax: at an eye offset ≈ portal distance the revealed band ≈ thickness, so a 0.7-width side covers most of the reveal for compact objects and, correctly, not for thin ones. Tunnelling violated both rules; the thin band came from a thickness underestimated by fitting to an 8-bit blurred depth map, not from the approach.
