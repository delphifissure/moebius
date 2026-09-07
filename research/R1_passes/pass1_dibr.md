# Pass 1 — DIBR / 3DTV hole filling and disocclusion handling (agent report, lightly trimmed)

Coverage note from the pass: citations were located via web search; many publisher pages were blocked by the proxy, so details come from abstracts, snippets and official repos. Unconfirmed constants are marked [unverified].

## Classical pipeline pieces (2004–2012)

- Fehn, "Depth-image-based rendering (DIBR), compression and transmission for a new approach on 3D-TV", SPIE 5291, 2004. Forward warp + uniform Gaussian pre-smoothing of depth so cliffs become ramps and holes shrink. Artefacts: rubber-sheet bowing of background edges, objects glued to background. Constants: sigma per sequence. Verdict: the mechanism of our skirts; not applicable.
- Zhang & Tam, "Stereoscopic image generation based on depth images for 3D TV", IEEE Trans. Broadcasting 51(2), 2005 (precursor Tam et al. SPIE 2004): asymmetric smoothing, vertical ≫ horizontal, because holes from horizontal shifts are vertical strips. Chen et al. ICME 2005 smooth only near depth edges. Verdict: assumes horizontal-only parallax; our head tracking is 2-D; smoothing recreates skirts. Lesson inverted: tear cliffs, never ramp them.
- Vazquez, Tam & Speranza, "Stereoscopic imaging: filling disoccluded areas in depth image-based rendering", SPIE 6392, 2006: compares constant fill, horizontal interpolation, Laplace (membrane) fill, depth-guided extrapolation from the far side, variational inpainting with depth, depth pre-processing. Horizontal interpolation bleeds foreground colour (ghost doubling); depth-blind extrapolation streaks; far-side extrapolation streaks on textured backgrounds. Verdict: "extrapolate only from the far rim" is right; the membrane beats cloning for a moving viewer.
- Müller, Smolic, Dix, Merkle, Kauff & Wiegand, "View synthesis for advanced 3D video systems", EURASIP J. Image Video Proc. 2008: Canny on depth; main layer + foreground boundary layer + background boundary layer (a few px each side of each edge, 7 samples [unverified]); layers warped separately; boundary layers trusted least; far boundary layer dropped where anything else lands, so mixed-colour edge pixels ("corona") never smear. Verdict: highly applicable — our blurred ramp is their unreliable boundary layer.
- MPEG VSRS (Tanimoto, Fujii & Suzuki, MPEG M15836, 2008; Lee & Ho, APSIPA 2009; VSRS 4.2 MPEG M40657): warp depth first with sub-pel upsampling, median filter, back-project colour, boundary noise removal (foreground-side hole-adjacent pixels assumed to be misaligned background wearing foreground colour — erased and retaken), diffusion inpainting per hole from the far side. Constants fixed in config, tuned on MPEG sequences. Verdict: BNR applies as a rim-cleaning rule.
- Zinger, Do & de With, "Free-viewpoint depth image based rendering", JVCIR 21(5–6), 2010; Jantet, Guillemot & Morin, "Joint projection filling", 3D Research 2011; "Reliability-based view synthesis for FVV", Applied Sciences 8(5):823, 2018: warp depth only, fill cracks, inverse-warp colour; pixels at strong discontinuities not warped at all; per-pixel reliability = distance to depth edge + consistency; disocclusion inpainting samples only candidates at or behind the hole's background rim; McMillan occlusion-compatible ordering classifies cracks vs disocclusions during warping. Verdict: a per-texel reliability channel is cheap in a fragment shader and attacks skirts and ghost rims.
- Solh & AlRegib, "Hierarchical hole-filling for depth-based view synthesis in FTV and 3D video", IEEE JSTSP 6(5), 2012: Gaussian pyramid ignoring holes (reduce), expand back down (push–pull membrane); depth-adaptive variant weights far pixels up. Pyramid depth = log2(largest hole). Real-time on GPU. Verdict: a derivable GPU implementation of our far-rim wash.

## Depth-guided exemplar inpainting (Criminisi lineage)

- Criminisi, Pérez & Toyama, IEEE TIP 13(9), 2004: priority = confidence × isophote strength, 9×9 patches.
- Daribo & Pesquet-Popescu, "Depth-aided image inpainting for novel view synthesis", IEEE MMSP 2010: level-regularity priority (flat-depth patches first), depth-SSD in matching.
- Gautier, Le Meur & Guillemot, "Depth-based image completion for view synthesis", 3DTV-CON 2011: structure-tensor priority, one-sided fill from the background side.
- Ndjiki-Nya, Köppel, Doshkov, Lakshman, Merkle, Müller & Wiegand, IEEE TMM 13(3), 2011; Köppel et al. ICIP 2010; EURASIP JIVP 2013: depth hole first, background sprite accumulated over frames, Laplacian membrane, texture synthesis last. Origin of "membrane first, texture only if needed".
- Oh, Yea & Ho, PCS 2009 (background priority); Ahn & Kim, IEEE Trans. Broadcasting 59, 2013 (tensor priority + boundary confidence + background-only candidates); Buyssens, Daisy, Tschumperlé & Lézoray, SIGGRAPH Asia Briefs 2015 and Buyssens et al. IEEE TIP 26(2), 2017 (depth first, colour candidates restricted to the inpainted depth); Zhu & Li, IEEE Trans. Broadcasting 62(1), 2016 (analytic hole location/length: width = baseline × (disparity_near − disparity_far)); Luo & Zhu, IEEE TCSVT 27(10), 2017 (remove foreground, build background video before warping).
- Verdict for the family: seconds per frame, clones texture, empirical weights; three transferable rules — depth first, far rim only, rank rim texels by low depth variance / distance from the cliff.

## Layered representations

- Shade, Gortler, He & Szeliski, "Layered depth images", SIGGRAPH 1998: multiple depth samples per pixel, McMillan ordering, splats; disocclusion handled only where another view supplied the layer.
- Hedman, Alsisan, Szeliski & Kopf, "Casual 3D Photography", SIGGRAPH Asia 2017; Hedman & Kopf, "Instant 3D Photography", SIGGRAPH 2018: two-layer front/back panorama mesh, back layer extended behind silhouettes.

## Temporal consistency

- Köppel 2010 / Ndjiki-Nya 2013 (sprite); Schmeing & Jiang, IEEE TMM 17(12), 2015 (superpixel fill from adjacent frames); Ionescu group ICASSP 2014; GMM background update (Springer LNCS 2012). All need video; our analogue is a pose-independent plug so the fill does not flicker under head motion.

## Learned successors (2017–2024)

- Tulsiani, Tucker & Snavely, ECCV 2018: two-layer LDI from one image with view-synthesis supervision.
- Niklaus, Mai, Yang & Liu, "3D Ken Burns", SIGGRAPH Asia 2019: semantic depth refinement, joint colour+depth inpainting from extreme poses.
- Shih, Su, Kopf & Huang, CVPR 2020 (vt-vl-lab/3d-photo-inpainting): LDI with explicit connectivity, bilateral-median depth sharpening, disparity-difference edge test, edge → depth → colour inpainting. Verified defaults: depth_threshold 0.04, ext_edge_threshold 0.002, depth_edge_dilate 10/5, background_thickness 70, context_thickness 140, edge segments < 10 px removed, synthesis dilated 5 px; 2–3 min per image.
- Kopf et al., "One Shot 3D Photography", SIGGRAPH 2020: mobile LDI inpainting by connectivity traversal; meshed output.
- Tucker & Snavely single-view MPI CVPR 2020; AdaMPI SIGGRAPH 2022 (plane adjustment + colour/density nets, warp-back self-supervision).
- SynSin, Wiles et al. CVPR 2020: feature point cloud, soft z-buffer splat renderer, refinement net.
- SLIDE, Jampani et al. ICCV 2021: soft two-layer split via matting (hair/foliage), depth-aware inpainting.
- Worldsheet 2021; "Real-time position-aware view synthesis" 2024 (arXiv 2412.14005).
- DIBR CNNs: Cai, Fan, Meng & Zhu, J. Electronic Imaging 29(1), 2020; CFFHNet, Wang et al., IEEE TIP 2023.
- Verdict: none runs per frame in WebGL; all hallucinate texture; all tune thresholds. Structural choices transfer: connectivity-torn LDI, depth-then-colour, soft alpha layer.

## What we should steal (prioritised by the pass)

1. Depth first, colour second, always from the far rim; plug depth = planar/linear continuation of the far rim's depth field per hole.
2. Unreliable boundary layer: the measured ramp is untrusted; assign ramp texels to the nearest plateau; exclude from geometry and seeding.
3. Depth-weighted push–pull as the wash; pyramid depth = log2(max hole width).
4. Per-texel reliability channel (distance to cliff, local depth variance) for seeding weights and silhouette alpha.
5. Soft layering for porous silhouettes: alpha from local depth variance where the edge is a noisy band, not a step.
6. Analytic hole geometry to size sweep and plug extent from the maximum eye offset.

## What this literature never solved

Interior self-occlusion of one object (all fill with background); porous/thin structures (SLIDE the one attempt); floor-meets-wall vs object ("far = background" assumed); zero-tuning constants; 2-D parallax at 45°; real-time single-image quality.
