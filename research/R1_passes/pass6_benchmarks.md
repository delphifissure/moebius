# Pass 6 — Evaluation of disocclusion quality and synthetic hidden-layer test scenes (agent report, lightly trimmed)

Verification note from the pass: arXiv/CVF/ACM/Semantic Scholar mostly blocked; [verified] = fetched page or snippet quoting the source; [unverified] = memory.

## 1. How the 3D-photo / single-view papers evaluate
- Tucker & Snavely, CVPR 2020 [verified]: RealEstate10K 300 held-out sequences, iBims-1 depth, Flowers, KITTI; source/target 5 or 10 frames apart; LPIPS/PSNR/SSIM whole-frame; "Nobackground" ablation isolates background prediction.
- Shih et al., CVPR 2020 [verified: RealEstate10K, MiDaS depth]: held-out frames; no dedicated hidden-region metric found.
- Kopf et al., SIGGRAPH 2020 [verified: released code is depth-only "Tiefenrausch"; Table 1 depth accuracy].
- SLIDE, ICCV 2021 [verified]: RealEstate10K, Dual-Pixels, Mannequin Challenge; vs SynSin, SMPI, 3D-Photo; no masked metric found.
- AdaMPI, SIGGRAPH 2022 [verified]: COCO via warp-back (warp with DPT depth to a random pose, inpaint holes, warp back → pseudo pair); no explicit depth-noise model documented.
- MINE, ICCV 2021 [verified]: RealEstate10K, KITTI Raw, Flowers LF; PSNR/SSIM/LPIPS.
- 3D Ken Burns, SIGGRAPH Asia 2019 [verified]: own synthetic set (~28–32 game-like environments, RGB + depth + normals, flying/walking camera modes, CC BY-NC-SA 4.0); inpainting judged qualitatively; trajectories give novel-view GT.
- SynSin, CVPR 2020 [verified]: RealEstate10K, Matterport3D & Replica via Habitat; PSNR/SSIM/perceptual; the only paper with an explicit invisible-region split (Vis / InVis).
- Takeaways: default is held-out frame + whole-frame PSNR/SSIM/LPIPS, which dilutes disocclusion error (< 5 % of pixels). Precedents for occluded-region scoring: SynSin InVis; amodal mIoU_occ (PLUG, 2405.16094). FID/KID when no single GT (Infinite Nature 2012.09855; long-term NVS 2304.10700). Temporal/warp consistency: Lai et al., ECCV 2018 — warping error with flow + forward-occlusion masks; with synthetic data use exact GT flow. DIBR-specific metrics (MW-PSNR, MP-PSNR, 3DSwIM): "Quality Assessment of DIBR-synthesized views: An Overview" (1911.07036) [title verified].

## 2. Datasets with occlusion / hidden-layer ground truth
- MPI-Sintel [verified]: 69 sequences, GT occlusion masks, depth/stereo/camera; motion blur, defocus, fog; no hidden-layer colour.
- Middlebury 2014 [verified]: nonocc/all masks, large half-occlusions, structured-light GT; real stereo = true second view.
- Spring (Mehl et al., CVPR 2023, 2303.01943) [verified]: Blender "Spring" film, stereo + flow + disparity, super-resolved UHD GT, evaluation maps for sky, detail (thin structures), unmatched (disocclusion), non-rigid — a region-map design to copy.
- Hypersim (Roberts et al., ICCV 2021) [verified]: 461 scenes, trajectories to 100 views, intrinsics/extrinsics, distance-to-camera depth (convert to planar), normals, semantic/instance, diffuse/illumination/residual split; meshes need Evermotion assets.
- Replica [verified]: 18 scanned scenes, HDR Ptex, semantic/instance, explicit glass and mirror surface files (glass.sur); render via ReplicaRenderer or Habitat.
- Habitat-Sim [verified]: RGB/depth/semantic/equirect/fisheye, arbitrary pose; Replica/HM3D/MP3D/Gibson/HSSD; scans have holes.
- InteriorNet / SceneNet RGB-D [verified]: trajectory renders with depth/instance/flow; Peeking Behind Objects built LDI GT on SceneNet by re-rendering with foreground removed; Shin et al. 2019 used multi-hit ray tracing on SUNCG for multi-layer depth. LayeredDepth-Syn (2503.11633) [verified]: 15,300 synthetic images with multi-layer depth GT for transparent objects + a real benchmark.
- Structured3D [verified]: 21,835 rooms, depth/normals/semantic/albedo/layout; one panorama per room, no offset view.
- TartanAir [verified]: stereo RGB, depth L/R, segmentation, flow with occlusion + out-of-FOV masks, poses. DIODE, MegaDepth: single-view depth only. RealEstate10K/ACID: held-out frames only, no masks, unknown scale. KINS/COCOA: human-imagined amodal masks, shape only.

## 3. Procedural generators
| Generator | Outputs | 2nd-surface depth | Offset eye | Notes |
|---|---|---|---|---|
| Kubric (Greff et al., CVPR 2022) [verified] | rgba, depth (EXR), z, uv, normal, object coords, segmentation, flow, camera | not built in; Blender Cycles underneath | yes (multi-camera static scenes) | Apache-2.0; GSO/ShapeNet/PolyHaven; FlatMaterial holdouts |
| Infinigen (Princeton) [verified via snippets] | RGB, metric depth, normals, occlusion boundaries (2H×2W), panoptic, 3D boxes, flow; OpenGL GT from mesh | not exposed, but foliage/hair are real geometry so peeling is exact | yes (camera rigs) | BSD-3; Infinigen Indoors (CVPR 2024); slow |
| BlenderProc 2 [verified] | colour, depth, distance, normals, instance/class seg, flow, NOCS, stereo; multiple poses | scriptable | yes | best for authoring small element scenes; hdf5/COCO/BOP |
| ProcTHOR / AI2-THOR [verified] | RGB, depth, seg, normals; third-party cameras | no | yes | Unity, game shading |
| Habitat-Sim [verified] | RGB, depth, semantic | no | yes | fast; scans/CAD |
| ThreeDWorld [verified] | img, id, category, mask, depth, normals, flow, albedo | no | yes | Unity |
| Unity Perception [verified] | boxes, seg, keypoints with occluded state, depth, normals, occlusion % | no | yes | terrain trees not labelable |

- k-layer GT from any renderer: (i) multi-hit ray casting on the exported mesh (Shin 2019) — exact; (ii) depth peeling (pass k with z > z_{k−1}; Everitt 2001 [unverified]); (iii) hidden-occluder re-render (Dhamo) — colour AND correct global illumination for the background; the only route that gives correct appearance for glass/mirror/water. For plug evaluation (iii) is primary, (i)/(ii) the geometric check.
- True offset-eye GT: every generator renders a frozen scene from a second camera; none of the 3D-photo papers exploit it. Render the eye at the actual portal geometry: an off-axis (sheared) frustum at ±45° (Blender shift_x/shift_y; Kubric exposes the camera).

## 4. Simulating depth-estimator degradation
Precedents [verified snippets]: per-pixel Gaussian noise + edge erosion (SLAM robustness, 2406.16850); noise/blur/JPEG/quantisation on the INPUT image to a depth net (Sci. Data 2024); procedural scene perturbations (2507.00981, Infinigen-based); DIBR coding literature: quantisation error near edges gives disproportionate rendered-view MSE (USPTO 9307252). No 3D-photo paper documents a depth-corruption protocol. Proposed ladder on GT depth: (a) 16-bit vs 8-bit inverse-depth quantisation; (b) Gaussian edge blur σ ∈ {0,1,2,4} px; (c) affine disparity error (scale/shift); (d) edge erosion/dilation 1–3 px (halo to the wrong layer); (e) low-frequency warp (sky/floor bowing); (f) real MiDaS/DPT/Depth Anything on the render, compared to (a)–(e).

## 5. Proposed synthetic suite (20 scenes)
Each: RGB + GT depth (float EXR) from the portal camera; depth-peeled layers 2–3; hidden-occluder re-render (RGB + depth); instance masks; offset-eye renders at {10,20,30,45}° × {horizontal, vertical, diagonal}; GT flow portal→eye with occlusion mask (exact disocclusion mask).
1 room corner (plane continuation, 8-bit banding); 2 floor under objects (contact); 3 floating objects (touching vs detached); 4 thin pole 0.5–3 px; 5 wire / fence grid; 6 porous canopy (Infinigen tree) against sky, k = 3; 7 hair/fur (particle hair → mesh); 8 stacked occluders (three cards, k = 3); 9 self-occluding limb (posed humanoid); 10 object cut by frame edge (wider-FOV GT); 11 repeated texture behind occluder; 12 text/signage behind occluder; 13 sky + far mountains; 14 glass pane (first-surface vs through-glass GT); 15 mirror (documented failure mode); 16 water with submerged object; 17 strong specular on curved metal (metric noise floor); 18 night with point lights and bloom; 19 motion blur / defocus; 20 painting/illustration style (toon shading of 1, 4, 8). Cross every scene with the degradation ladder.

## 6. Metric suite
Compute on the offset-eye render vs output at each eye offset; report full-frame, disocclusion-only (GT flow has no source), and a ±2 px depth-edge band separately.
1 PSNR/SSIM (full-frame sanity); 2 LPIPS masked to disocclusion regions (primary perceptual; SynSin InVis precedent); 3 DISTS (Ding, Ma, Wang & Simoncelli 2020) for texture-kind on repeated-texture/foliage scenes; 4 disocclusion bad-pixel rate (colour > τ, or rendered depth vs peeled layer-2 depth > δ; Middlebury bad2 analogue) — "did the plug land at the right depth", what a head-tracked viewer perceives as swimming; 5 edge-band PSNR/LPIPS (halos, stretched skin); 6 temporal warping error (Lai 2018) along the head trajectory with GT flow and occlusion mask (flicker/popping); 7 FID/KID on disocclusion patches pooled across the suite for hallucination-only scenes; 8 degradation sensitivity (slope of 2/4/6 against the ladder); 9 failure flags for glass/mirror/water/specular, excluded from aggregates.
Which answers "does the disocclusion look right for a head-tracked viewer": masked LPIPS/DISTS (appearance) + temporal warping error with GT flow along the head path (motion coherence), with layer-2 depth bad-pixel rate as the geometric root-cause diagnostic. Whole-image PSNR is uninformative. No perceptual study on head-tracked disocclusion tolerance was reachable; a small paired-comparison user study remains the only true validation of the metric ranking.

## 7. Generator recommendation
BlenderProc 2 as the authoring/rendering backbone, Infinigen assets for organic content: thin Python over Blender, small element scenes in a few lines, stereo/multi-pose with depth/distance/normals/instance/flow built in; hidden-occluder re-render and depth peeling trivial in the Blender API; Cycles gives correct hidden-region illumination; Infinigen is the only generator whose foliage, hair and terrain are true geometry. Kubric the runner-up (GSO objects). Unity/Habitat fastest but rasterised, no correct hidden-layer shading or glass/mirror physics, harder to bend into off-axis portal frusta; Habitat + Replica worth one pass as a realism check with annotated mirrors.
