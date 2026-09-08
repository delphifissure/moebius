# CODEMAP — moebius.js read end to end (line references, v3.13.63-a228 line 1 banner)

Purpose: replace recall with citations. Every claim about the app in R1/R2/S1 should point here.
Line numbers are for moebiusv2 main at 18e6cef (26,977 lines). Read order = file order; sections
are appended as the read proceeds. "Fact" = read from code; "Note" = my inference, marked.

## 0. Globals and constants (1–1450)

- Fact L18: `mediaLayers` is the source of truth for 2.5D layers; L32 `splatLayers` separate (A223).
- Fact L56: `manualCamDX/DY` manual view offset added to the head-tracked camera; `window.setViewOffset(dx,dy)`.
- Fact L57–69: `contentLensFovDeg = 90` (A65). Comment: head motion measured in focal-plane frame
  widths; "the portal projection absorbs D", gain = tan(fov/2)/tan(45°). Set ONLY by
  `window.setLensFov(deg)` (L25274). Nothing else assigns it (grep, whole file).
- Fact L139: `bgViewFadeStartDeg = 35, bgViewFadeEndDeg = 45`. The fade end sizes the bake's
  envelope ex = D·tan(fadeEnd) (comment L115–120: the live shift is −D·tan(θ)·z/(D−z), the cone
  does not enter it). `window._coneWide` read at module load only.
- Fact L239–255 `bgConeSlopeAtDepth`: k(d) = ex·D/(D−z)²·g(d)·px/m with D HARDCODED 0.2 and pn 0.5
  (A103 says LUT reads live; this function still hardcodes — Note: only used by the cone fill).
- Fact L300–340 `bgShiftLUTFor(pw, ph, exArg)`: layerW = W if pw/ph > W/H else H·(pw/ph);
  pxPerWorld = pw/layerW; D = |camera.position.z − portalPlaneWorldZ| LIVE; ex = exArg or
  D·tan(fadeEnd); z(d) = smoothstep law with live pn, outer, inner; fwd[d] = ex·z/(D−z)·px/m,
  monotone in d; inverse table. Keyed by (pw,ph,fadeEnd,inner,outer,pn,D,ex). Note: because D
  is read live, a bake run while the camera is dollied uses THAT D.
- Fact L341–350 `bgShiftPxAt(L,d)`, `bgDepthAtShift(L,m)`.
- Fact L372–425 `bgDecodeDepth16(url)`: 16-bit PNG decoded to float (A99) for the BAKE path;
  8-bit/interlaced/non-PNG → null → 8-bit canvas path. Consumer: `layer._depth16` (L3827).
  ⇒ the app's bake CAN read 16-bit depth. (The GL render texture stays 8-bit.)
- Fact L426–443 `bgConeSlopePerPx`: 0.0025·(1920/pw) unless `_coneSlopeDerived`.
- Fact L451–462 `bgSourceQuantum(arr,n)`: detects 1/255, 1/4095, 1/65535 grids, else 0.
- Fact L468 `bgRayReproject = true` default (A60); `window._rayReproject` overrides.
- Fact L481–499 device FOV LUT: mac 80×60 (user-measured), iphone 65×50, ipad 105×80, generic 60×40.
- Fact L889–956 `updateViewFade`: virtual angle = atan2(hypot(cam.x,cam.y), |cam.z−portalZ|),
  linear fade 35→45; plus a face-frame fade band 10° inside the learned tracker-loss boundary.
- Fact L1084–1105: `dollyZoomActive=false`, `subjectLockActive=true`, `dollyZoomSpeed=0.0005`,
  `dollyRefEyeZ=null`, `dollyLatGain=1` (A67), `initialFov=75`, `portalPlaneWorldZ=0`,
  `innerVolumeDepth=0.04`, `outerVolumeDepth=0.02`, `subjectFocalPlaneWorldZ=0`,
  `currentNormPortalPlane=0.5`.
- Fact L1128–1144 `volumeZOffForNormDepth(d)` = the ONE CPU copy of the GLSL law (A200):
  d<pn → −outer·(1−smoothstep(0,pn,d)); else (inner+popExtra)·smoothstep(pn,1,d).
- Fact L1149–1170: `terrariumWidth=0.16, terrariumHeight=0.09`; `dollyDistForFocal(f) =
  (W/2)(f/18)`; min 0.08 (18 mm, 90°), max 0.64 (144 mm), rest 0.20 (45 mm).
- Fact L1174–1178: `metricScaleFactor=1`, `physicalScreenDiagonalInches=15.6`.
- Fact L1598–1617 `frameCorners(cam, bl, br, tl)`: generalized off-axis projection from the eye
  through a fixed rect (Kooima); sets quaternion + projectionMatrix.

## 1. Shader material (2301–3101)

- Fact L2302–2424 uniforms: u_portalPlaneDepthNorm, u_worldOuter/InnerVolumeDepth,
  displacementBias, u_embedOffset (A167, 0 by default per A209), u_useRayReproject, u_refEye
  (default (0,0,0.2)), pop-out taper uniforms (A174), aperture crop (A171), u_frameC/u_frameH/
  u_frameZ (A210 in/out-of-frame classification for the SD highlight), u_useBgIslands (A58),
  band-cut uniforms, u_fragTear (A241), u_backTear (A257e), u_restClip (A245), u_pxScale (A189).
- Fact L2494–2800 `unifiedGapLogicGLSL` (fragment): order = A245 plug rest-clip → A257e back-layer
  alpha discard → A241 per-fragment tear (mode 2: vertex fold point vs pose fraction; mode 1:
  texel-density stretch > u_fragTearFactor (2.0) or back-facing, gated by u_sdMask unless
  u_fragTearGate=0) → band-gated stretch cut (uv rate / minor singular value, dithered band,
  contact-ramp exemption, mismatch test) → depth-gradient generator (fwidth(vNormalizedDepth) >
  threshold, default 0.02, RUNG 0.008) → luma/chroma/Sobel/curvature/crease generators →
  inhibitors (uv stretch, grazing angle) → external edge mask. Background layer never discards
  by isGap (L2799).
- Fact L2823–2899 vertex displacement: zOff = displacement(d) + displacementBias + u_embedOffset;
  pop-out taper z* = λ·H·M/(H·tanθ + M) when u_popExtra>0. RAY REPROJECTION (default): the
  vertex is placed on the ray from the FIXED reference eye u_refEye through its portal point, at
  z = portal z + zOff: Sw = refEye + (Pw − refEye)·(H − zOff)/H, H = refEye.z − Pw.z. The live
  camera then projects Sw. Legacy path: view-z push. ⇒ the implied world is built about u_refEye,
  not about the live eye; the truth kit's "photograph from D" corresponds to refEye.z = D.
- Fact L2931–2939 aperture crop: fragments behind the aperture plane are discarded if the
  eye→fragment ray misses the aperture rect (exact window rule); off unless enabled.
- Fact L3004–3037 image mode: vertex reads displacementMap.r as vNormalizedDepth; fragment
  discards alpha<0.01 and (A58/A59b) island-masked plate texels inside [0,1] uv.
- Fact L3091–3100: DoubleSide, transparent, depthWrite, derivatives.

## 2. Layers and mesh (3175–4011)

- Fact L3191–3260 `loadDefaultImages`: defaultImgColor.png + defaultImgDepth.png next to the html.
- Fact L3822–3829: on load, if the depth is a non-video image and `window._noFloatDepth !== true`,
  `bgDecodeDepth16` is AWAITED and stored as `layer._depth16` for the bake.
- Fact L3852–3856: mesh = PlaneGeometry(layerWidth, layerHeight, segmentsW = round(displayW/1)−1,
  segmentsH likewise) ⇒ ONE VERTEX PER SOURCE TEXEL; layer fitted inside the frame
  (layerAspect > frameAspect → width = W, else height = H).
- Fact L3859–3864: missing depth → flat 128 grey (d = 0.5 = portal plane).
- Fact L3879: u_textureSize = (displayWidth, displayHeight). L3892: mesh at portalPlaneWorldZ.

## 3. Scene, renderer, realtime inpainting materials (4402–5760)

- Fact L4402–4516 `setupMeshWithMedia` (legacy single-layer loaders): same one-vertex-per-texel
  plane, same fit rule, plus a "ghost mesh" (flattened, dilated, darkened copy, renderOrder −5).
- Fact L4839–4855 `initializeSceneAndRenderer`: PerspectiveCamera(initialFov 75, W/H, 0.001, 1000);
  camera.position.z = subjectFocalPlaneWorldZ + dollyRestDistance (0.2). Canvas 960×540.
  frameCorners overrides the projection every frame (see updateCameraAndProjection).
- Fact L4861–4906 render targets: sceneRenderTarget with a Float DepthTexture; uvMapRenderTarget;
  screenNormalizedDepthTarget; pyramids; FXAA; sharpen.
- Fact L4984–5000: realtime edge pipeline materials (luma, Sobel, Canny-style NMS/hysteresis,
  temporal stabilise, JFA seed/flood/resolve).
- Fact L5005–5099 `sdGapDepthEstimatorMaterial`: per gap pixel, max depth (= far in normalised
  space? NB comment says "max depth = farthest = background" but the app's convention is bright =
  near; the shader outputs R = maxDepth, G = minDepth; consumers decide) — realtime path only.
- Fact L5104–5177 gap-depth pull/push (background-biased: MIN normalised depth = far).
- Fact L5186–5248 `gapDepthSeedMaterial`: excludes gap pixels and pixels more than
  u_depthEdgeThreshold (0.02) nearer than the local minimum in a 7×7 window (FG exclusion).
- Fact L5256–5339 `maskGeneratorMaterial`, L5340–5454 pull/push (+ depth-aware variants),
  L5456–5461 `layerMaskMaterial` (FG/BG split at u_inpaintingSplitDepth_RAW on HARDWARE depth).
- Note: this whole block is the realtime (non-baked) inpainting path; the quick bake is the
  product path under review. Keep separate in the mind.

## 4. Depth pass, footprint pass, geometric gap pass, FG subtraction (6493–7469)

- Fact L6493–6836 `renderNormalizedDepthPass`: renders every media layer with a depth material
  (clone sharing the uniforms) that writes vNormalizedDepth; clear alpha 0 marks the void. The
  BACKGROUND (plug) layer is HIDDEN from this pass by design unless `_depthPassIncludeBG`
  (L6536–6542), so "holes" are foreground holes. For the BG layer branch (L6602–6626) it applies
  the A245 rest-clip, discards alpha<0.01 texels (A257c) and the back-layer ramp (A257e/g). The
  foreground branch applies the A241/A241b tear (L6627–6639) and the same detector chain as the
  colour pass; TUNNEL_HEURISTICS = false (L6671).
- Fact L7019–7086 `renderMeshFootprintPass`: coverage of the displaced FG mesh with no discard
  (distinguishes interior gaps from out-of-mesh border void).
- Fact L7088–7156 `renderGeometricGapPass` (A120): coverage-only gap buffer, all detectors OFF,
  BG hidden; "holes are made by the cut, not by moving the camera" (an untorn mesh has 0 % holes).
- Fact L7157–7469 `runFGSubtraction` (rim-depth FG mask; realtime path): seed (gap R=1 sentinel;
  border void B=1), 48 rim-flood iterations (min/max rim depth per gap), 64 mark-dilation
  iterations with a parallax budget u_fgReachPx (slider, default 120 px per unit depth) and a
  relative entry threshold u_tauRel 0.35 of the local FG–BG span. Output contract L6994–6999.

## 5. Sweep plug (A232–A236) (7494–7997)

- Fact L7494–7607 `window._plugVisibilitySweep`: renders the plate with a texel-ID colour map and
  the FG black over a 17×5 pose grid, ex = z0·tan(fadeEnd), poses (ex·(2ix/16−1), ex·asp·(2iy/4−1));
  decodes which plate texels reach the screen (seen set, source rows); optional hole→texel
  attribution (holeDemand) using the far field farAt (BFS from the demand set) and a per-pose
  self-calibration of px-per-LUT-shift. Pose sign: camera.position.x = +ex·(...) — a POSITIVE
  eye x is a rightward eye in world.
- Fact L7608–7677 `window._plugSweepBake`: pass 1 full backstop bake → sweep → (optional hole-driven
  demand rebake) → region = reveals (chamfer pad minif+6) ∪ pinholes (pad minif) → pass 2 bake carved
  to the region. Chamfer (5,7).
- Fact L7691– `window._plugCpuSweep` (A236): CPU warp with the a104 ray law; needs `_plugSweepCapture`
  (dQ, plateF, torn). Uses bgShiftLUTFor(pw, ph) with the LIVE D and exRim = D·tan(fadeEnd),
  asp = H/W, grid NX 17 × NY 5 (L7716–7729).

- Fact L7730–7986 CPU sweep body: fx = sign·ex/exRim (sign default −1), FG texels warped by
  sFG·fx (source rows), untorn quads filled as their warped bounding box at the NEAREST corner depth,
  plate quads at the FARTHEST corner depth, ties to FG. A244 reveal demand: every in-frame cell the
  FG does not cover is inverted through the far field (two fixed-point steps) to the plate texel
  that must cover it (L7947–7950) → `revealTex`. A246 "observe": walks each uncovered cell against
  the parallax to the far lip and with it to the near lip; ramp-foot walk (≤ 4·RWD cells, RWD =
  round(4·pw/1200)); two-lip interpolation when |dA−dB| ≤ fgTearStep; A253 object rule classes
  (continuous by slope / interior / extent); pushes (texel, depth, lips, meta) samples.
- Fact L7997–8337 `window._plugGeoBand` (the current band producer used by a257_probe):
  1. pass 1 quick bake (fronts' band names the far rims) → dQ, dis1 (the fronts' band), pF1.
  2. far rims (L8018–8021): non-band texels 4-adjacent to a band texel whose source depth agrees
     with that band texel's plate depth within TOLB = fgTearStep.
  3. a-priori far field (L8025–8042): membrane (bgMembraneSolve, 60 cycles) over all non-rim
     texels with Dirichlet = source depth at the rims, clamped never in front of the source.
     ⇒ THE FAR FIELD IS A GLOBAL MEMBRANE ANCHORED ONLY AT RIMS; under large rim-less regions
     (floor, cave wall) it sags — this is the mechanism of the mega-band.
  4. A253 object rule (L8055–8063, `_plugObjectRule`): object = 4-connected components of texels
     with dQ − farField > TOLB.
  5. A257 backs (L8078–8199, `_plugBack`): medial-ball inflation with measured scale s (least
     squares of front bulge vs envelope height), cliff-edge gating, world-z solve, colour wash.
  6. CPU sweep with revealDemand + observe → observed hidden depth field (median per texel of lip
     samples; L8206–8290), lip bound (A253 B1), re-gate when `_fragTear`.
  7. band = revealTex ∪ pinholes (+1 texel dilation) → `window._bandReplace` (L8304–8310); class per
     texel (`_geoClass`: 1 continuous, 2 interior step, 7 extent step, 3 single lip, 4 fallback,
     5 pinhole, 6 dilation); pass 2 quick bake with the band from the far field.
  ⇒ What `_qbDisocc` (the probe's disocc.u8) IS: the pass-2 band = the union over the 17×5 sweep of
  reveal-demand texels (uncovered cells inverted through the FAR FIELD) plus pinholes and a 1-texel
  dilation. Its precision therefore depends on (a) the tear/cut model producing uncovered cells and
  (b) the far-field depth used for the inversion. 8-bit terraces enter through (a): terraces make
  cells fold/tear (A160 fold + quantum rule) so cells open on slow gradients.

## 6. Debug sheet and SD bundle (8360–9243)

- Fact L8366–8452 panel material modes; mode 9/10 SD inpaint/outpaint masks by the A210 frame-NDC
  rule (inside the source frame = inpaint, outside = outpaint).
- Fact L8455–8846 `exportDebugContactSheet`: refreshes buffers, panels (gap mask, scene depth,
  footprint, FG-sub contract, completed depth, plug depth, deform grid, FG-only / plug-only solos),
  A248 pose strip and flicker stamp (same-pose MAD and 1 %-rim-step MAD over gap pixels).

- Fact L8987–9189 `exportSDBundle`: screen-space color / depth_completed / mask_inpaint (A210
  in-frame demand) / mask_outpaint (outside the source frame) / mask_fg_occluder + meta; then
  source-space files if a BG layer exists (src_band_mask, src_bg_depth_completed,
  src_bg_color_baked), the directional plug set (dir_*), the scene-extension set (out_*), and
  per-plane v2 or per-layer v1 sets. depthConvention 'normalized disparity: 1 = near, 0 = far'.

## 7. Edge bake module, plug port, band/plug globals (9214–10190)

- Fact L9241–9499 inlined `MoebiusEdgeBake`: `bakeEdges` (edge zone = concentration test
  d − boxMin3 > 0.03 and > 0.6·(d − boxMin6), dilated ×4; colour-guided weighted-median snap 5×5,
  σ 0.08, 2 iters; slope-relative edge mask thr = max(0.03, 9·robustSlope)); `parallaxCurve`
  (deltaM·s/(D+s)·px/m with s the smoothstep world offset; NB sign convention here treats behind
  as +s); `buildParallaxLUT`; `deltaMaxForReach`.
- Fact L9503–9564 `MoebiusPlug.buildPlugFromValid`: locally-far anchors (valid & depth ≤ boxMin21 +
  0.08), chamfer nearest-anchor depth, 220 Jacobi sweeps with the ring pinned.
- Fact L9580–9829 globals: bgValidMode 'auto' (Otsu), bgPlugMode 'directional', bgSceneExtend
  true, bgMPIMode true, bgMPIFullPlanes true (v2 default when NOT quick), bgMPIV2Bins 10,
  bgBandMaxGrowPx 28, bgBandStep 0.10, bgCutFGOnPlug true, bgTearAllRubber true,
  `bgQuickBake = false` by default (the harness sets it true), bgBandCutMismatch 0.01,
  bgBandCutMaxGrad 0.04, bgBandCutStretchFrac 0.3, fgPreTear true, `fgTearStep = 0.06`
  (the cliff step used as TOLB throughout the geo band).
- Fact L9853–9901 `bgPullPushFill` (float pyramid, Uint8 out unless wantFloat).
- Fact L9939–10058 `bgDirectionalPlug(depth, W, H)`: band seeds = texels with a 4-neighbour more
  than STEP (bgBandStep 0.10) farther; budget = min(MAXW 28, |pxAt(di) − pxAt(rim)| + 2) with the
  LUT at DELTA = 0.12 m head offset (bgShiftLUTFor(W,H,0.12)); grow into the near side; slope-
  continuing initialisation from 4–8 px behind the rim source; ring anchors; 120 Jacobi sweeps.
- Fact L10059–10182 certified-asset records (defaultBgBand/Valid/DepthBand/Depth_sharpened/
  EdgeMask.png) gated by a 64-sample fingerprint of the certified depth (the troll).

## 8. Live bake of the source depth (applyLiveBake, 10184–11025)

- Fact L10195–10200: the live bake reads the depth through a CANVAS getImageData → 8-bit
  (`depth[i] = dpx[i*4]/255`), regardless of `_depth16`. It then runs `MoebiusEdgeBake.bakeEdges`
  (weighted-median snap in the edge zone), a near-plateau clamp (L10268), SKIN BINARISATION
  (L10273–10276: within a ±2 px window with range > 0.06, a texel more than 0.05 from both
  plateaus snaps to the plateau whose colour it matches), and up to 4 ITERATIVE RAMP-COLLAPSE
  passes (L10288–10313) that march the plateaus over ramps ~2 px per pass. `window._rawPass`
  bypasses; `window._noRampCollapse` disables the collapse.
- Fact L10327–10716 stroke repair (A34–A45): stroke classifier on luma; depth ADOPTION writes are
  OFF by default (A61, `window._strokeAdopt`); wash-ink mask is built for the plate wash.
- Fact L10736–10824 A63 thin-lift: far-flush thin ink attached to a near anchor is lifted to it
  (on unless `_noThinLift`), with the A75 reach bound MAXD = max(60, 150·w/1920) px.
- Fact L10860 ink-seat OFF by default (A61).
- Fact L10974–11007: the sharpened depth becomes the layer's depth texture as a FLOAT DataTexture
  (`L.textures.depth = sTex`, displacementMap rebound) ⇒ the RENDERED foreground uses the
  live-baked (sharpened, ramp-collapsed) depth, not the raw estimator map. `L._rawDepth` keeps
  the pre-bake 8-bit depth for tear decisions. Need: who calls applyLiveBake (see §10).

## 9. v2 full planes (bgBuildFullPlanesCore, 11039–11706) and the backstop sweep (11718–11902)

- Fact L11053–11162: K = bgMPIV2Bins (10) equal-count depth-quantile bins; A49 footing merge of
  small components onto the bin below; A52 farther-only boundary refinement.
- Fact L11191–11231 A58e anamorphic backdrop reach budV: max-plus chamfer seeded with the screen
  displacement across every cliff pair (step > fgTearStep) using the shift LUT.
- Fact L11232–11327: per bin, row/column nearest-anchor continuation; A66 pair validation (anchors
  on both sides, frame edge counts only across strictly-nearer content); the primary's farthest bin
  claims wherever budV > 0 (hole-only backdrop).
- Fact L11335–11380: 2 px weld skirt, masked box blur radius 8 with an edge-aware clamp of
  ±fgTearStep/2; L11381–11491 completion colour = 50/50 row-anchor lerp and quarter-res pull-push
  wash; A193 claim relax (4 Jacobi passes); A136 ordering clamp (claimed depth ≤ visible − quantum).
- Fact L11565–11628: dense mesh over the in-frame bbox; quadtree merge up to 16-texel blocks where
  planar within EPSd = 1.5/255 and not folding (A177 `_v2Tears`: shift span > extent AND depth span >
  quantum); per-cell tears elsewhere; backdrop keeps cliff cells. Margins: coarse 8-px skirt sized
  0.10 world (backdrop) / 0.05 world (frame-cut bins), logged against the a113 law (A139).
- Fact L11718–11902 `bgBackstopSweep` (v1 only): 4 rim poses on the axes at r = D·tan(fadeEnd);
  violations (backstop nearer than FG max over 8 px) are back-projected and flattened to the floor.

## 10. Membrane solver, directional plate, quick-bake preamble (11904–13340)

- Fact L11904–12080 `bgMembraneSolve`: aggregation multigrid Laplace solve for the far field
  (anchors = far rims); this is the a-priori "far field" whose sag under rim-less regions makes
  the mega-band (S1 report §4).
- Fact L12090–12568 `bgDirectionalPlate`: ground segmentation from colour + depth, cliff and
  boundary seeds, cone-envelope flood; A73 farther-value-wins; A78 prominence bound.
- Fact L12570 `bgBuildBackgroundLayerCore(L, …)`; L12580 calls `applyLiveBake(L)` FIRST (so the
  live bake always precedes the quick bake). L12600–12870 defines the GPU materials used by the
  v1/plug path (`srcBandSeedMaterial` u_edgeThresh 0.03 / u_reachPx 120, `bgCombineMaterial`,
  `bgLakeMaterial`, `bgColorSeedMaterial` = one-sided colour sources: a pixel is an invalid colour
  source if the plug replaced depth within 4 px; ink rejected).
- Fact L12886 quick-bake branch (`bgQuickBake`). L12888 the depth image read is
  `L.textures.depth.image2d || .image` → after `applyLiveBake` that is the 8-bit CANVAS COPY of
  the sharpened depth (L10978–10999: `sTex.image2d = oc`, values `round(sharpened·255)`). So on
  the 8-bit path dQ = live-baked depth RE-QUANTISED to 1/255.
- Fact L12896: if `L._depth16` matches the size, `dQ.set(L._depth16.data)` — the RAW 16-bit
  decode (set only at L3828) REPLACES the live-baked depth for the quick bake. Consequence: with a
  16-bit depth PNG the plate/band/plug are computed from the un-sharpened estimator map, and the
  ship-back at L13307 (when `dqDirty`) overwrites the rendered float texture with that dQ (after
  dequantise/despeckle/snap), i.e. the live bake's sharpening is discarded for the render too.
  With 8-bit depth (all probes so far) the live bake's output IS what the quick bake sees. This is
  a real difference between the two probe depth formats, not a precision-only one.
- Fact L12920–12940 A89: source quantum detected from the data (grid 255 / 4095 / 65535, sampled
  every PNq/20000 texels, tolerance 1e-3 level); `window._qbSrcQuantum` = tear noise floor.
- Fact L12949–12997 A127b/A133 log only: k = max(|m0|,|m1|) from `bgShiftLUTFor` (px of shift
  across the depth range at the cone rim); fold limit √2/k; precision 1/k; fgTearStep printed as
  reveal width fgTearStep·k. No behaviour.
- Fact L12998–13042 A86 dequantise (unless `_noDequant`): per axis, adjacent constant runs one
  quantum apart are linearly interpolated between run centres; ≥2 quanta keep the step; axes
  averaged. With a 16-bit source the quantum is 1/65535 so this is effectively a no-op.
- Fact L13043–13090 despeckle (always on): 3×3 range > 0.06 AND < 8 of 25 neighbours within
  0.02 → 5×5 median; 2 passes.
- Fact L13091–13165: cone lower envelope plateQ = min_i(d(i) + sCone·dist), two-pass chamfer;
  sCone = `bgConeSlopePerPx(pw)` = 0.0025·1920/pw (A88) unless `_sConeFixed`.
  `_cellTearStep = bgFoldStepPerCell(pw)` (A91) unless `_noFoldTear`; a102 logs the LUT span.
- Fact L13169–13178 A62 directional plate ON by default (`_dirPlate`), replaces plateQ.
- Fact L13203–13227 A72 smear snap (on when dir plate on, unless `_noSmearSnap`): window
  RS = 2·max(3, round(4·pw/1200)); a texel proud of its plate by > fgTearStep, with a nearer
  surface (rise > fgTearStep) in the window and NO step > fgTearStep in the window, snaps to the
  nearer of (window max, plate). Writes dQ.
- Fact L13241–13302 rigidify OFF by default (`_enableRigidify`).
- Fact L13307–13345 ship-back: if dqDirty, dQ is written into the rendered float depth texture
  (and its image2d); on a fresh load (plain PNG Texture) it is promoted to a float DataTexture.

## 11. Quick bake: SD mask → band → plate depth → plug region → tear → band colour (13351–14600)

- Fact L13357–13359: `disocc` (the SD mask / band seed) = texels where dQ − plateQ > 0.02. The
  0.02 is a hardcoded depth constant (units: normalised depth), used identically at L13243,
  13289, 13866 (near-mask) — NOT scaled with anything.
- Fact L13383–13417 A44 cliff gate runs ONLY when the directional plate is OFF (bypassed under
  A62 by default).
- Fact L13448–13523 A80/A121 viewpoint scan OFF by default (`_vpScan=true` enables): 8 dirs × 4
  magnitudes forward-warp z-buffer test; the log says SKIPPED.
- Fact L13536–13570 A62b ink-adjacency closure: stroke-mask texels 4-adjacent to the mask join it
  (passes = max(3, round(5·pw/1200))) and inherit the min neighbouring plateQ; 2 sandwich passes.
- Fact L13571–13584: `_qbSize`, `_qbDQ` (when `_plugSweepCapture`), A234 `_extraDemand` join.
- Fact L13588–13609 A244 `_bandReplace` (set by `_plugGeoBand`): disocc := the geometric band
  exactly (adds joined, drops restored to source depth); A244i plateQ on band texels := the far
  field `_geoFarField`; A253c lip floor when `_plugObjectRule || _geoLipFloor`.
- Fact L13610: `_qbDisocc = disocc.slice()` captured here (this is the band the probe dumps).
- Fact L13611–13613 plateF (flipped rows) starts as plateQ; maskF = disocc.
- Fact L13644–13722 plateF inside disocc: default (a58c) = `bgPullPushFill` continuation of the
  NON-band depth (isotropic, float); `_plugGroundUp` = column ramps from the ground below at the
  median ground slope; `_plugConeDepth` = plateQ.
- Fact L13732–13736 A244f: with `_bandReplace` + `_geoFarField` (and `_geoDepth !== false`) the
  band's plateF := the far field (overrides the pull-push); L13737–13761 A244d far-rim depth
  membrane is the fallback when only `_geoRef.band` is present.
- Fact L13777–13822 plug region islandF: default (a59c) = disocc exactly (tight silhouette);
  `_bgIslandDilate` px band; `_bgPlugBand` = bud>0 (legacy anamorphic).
- Fact L13840–13897 wash ink mask: reject only ink within RN = max(4, round(4·pw/1200)) dilations
  of NEAR content (dQ − plateQ > 0.02), dilated RD = max(1, round(pw/1200)).
- Fact L13899–13941 the GPU colour wash: `bgColorSeedMaterial` → pull/push pyramid → `bgColorTarget`
  (canvas-res). This is the DEFAULT band colour (A219 verdict) unless a flag below.
- Fact L13944–13953 quick mode removes ring (A245), object backs (A257), prior bgLayerMesh, MPI.
- Fact L13975–14165 FG pre-tear (default; `_qbNoTear` disables): per triangle of the FG grid,
  torn iff shift span across (mn,mx) via `bgShiftLUTFor` > cell extent √(sxT²+syT²) texels
  (A102/A160) AND depth span > source quantum (A160d). Torn texels (`drop`) → `_qbTorn` (capture)
  and are UNIONED into islandF (A160b) so the plug covers the torn footprint. No cap cards (A169).
  a165 logs `_qbStretch` = surviving triangles that still fold (ratio > 1).
- Fact L14188–14294 A70 row-colour plate colours OPT-IN (`_plateRowColor`).
- Fact L14355 band colour arms (all OFF by default; the wash is default): `_bandFillBlend`
  (A215 8-ray Shepard p=1), `_plugMembrane` (A242 Laplace membrane via `bgMembraneSolve`, TOLC 0.5
  8-bit step, 60 cycles), `_plugWashGated` (A247 gated pull-push seeded by far-side texels only),
  `_plugGuided` (A249 mirrored-texture detail over the membrane, feather min(rim dist, RWD)).
  Common domain: BFS from rim seeds gated |plateQ[band] − dQ[src]| ≤ fgTearStep, in-band steps
  |plateQ − plateQ| ≤ fgTearStep (A255 `_geoLipSeed` widens class-1 gaps to their lip spread);
  pockets take resolved colours ungated (never the figure).

## 12. Plate material, ordering clamps, slope limit, carve, margin (14665–15410)

- Fact L14665–14681: plate material `matQ` = clone of the FG material with displacementMap =
  plateDT, map = plateColorTex || the GPU wash; `u_isBackgroundLayer` true; displacementBias
  unchanged (0) unless `_plugZBias`; `u_sdMask` = maskDT uploaded to BOTH plate and FG materials
  (the FG's stretch cut is gated by reveal backing, A84).
- Fact L14743–14749 A161/A216: the island gate is OFF (`u_useBgIslands=false`); the plate is a
  complete backstop rendered with polygonOffset (1,1); visibility is by the depth test alone.
  The SD mask no longer gates the render, only the export.
- Fact L14766–14784: on the plate every discard path is OFF (band net, gradient/sobel/luma/
  chroma/crease/curvature/UV-stretch/grazing cuts, cutSharp); on the FG the band net is armed with
  u_bandCutUvRate = 1/w (cut from ~2× stretch, A52).
- Fact L14792–14797: plate geometry = clone of the FG grid with the FULL (untorn) index.
- Fact L14896–14935 A135 same-texel ordering clamp (unless `_noOrderClamp`): plateF ≤ dQ − eps,
  eps = source quantum (1/255 or 1/65535). Logs strictly-in-front vs flush-setback counts.
- Fact L14977–15036 A162 cross-texel ordering clamp (unless `_noCrossTexelOrder`): min-plus chamfer
  (weights 1/1.0396, √2/1.0396) of the source shift field F = shift(dQ); a plate texel whose
  shift exceeds F is pushed back to depthAtShift(F). `_plateFlushExempt` exempts |plate − src| ≤ 2q.
  ⇒ NOTE for the band: this clamp pushes ANY plate texel that could occlude any source texel from
  any eye in the cone, so an interior fill nearer than the neighbouring backdrop is pushed to the
  backdrop unless the A253 lip floor (object rule) re-raises it (L15130–15137).
- Fact L15049–15118 a126 slope limit (default; `_legacyPlateTear` reverts to the a87 tear):
  plateF ≤ min(neighbour) + step, step = `bgConeSlopePerPx(pw)` = 0.0025·1920/pw, NOT 1/k
  (`_envelopePlateStep` selects 1/k; measured worse at 32–38°). Diagonal step ×√2.
- Fact L15130–15137 A253 lip floor after a126 (with `_geoLipFloor` or `_plugObjectRule`):
  plateF ≥ min(lipBound − q, dQ − q) on band texels (mode 2 = observed classes 1/2/3/7 only).
- Fact L15249: `_qbPlateF = plateF` captured for the CPU sweep (final plate depths, flipped rows).
- Fact L15250–15372 A217 carve OFF by default (`_plugCarve`): keep triangles touching demand +
  displacement collar + A229 rim demand; `_plugRegion` (from the sweep) supersedes.
- Fact L15386–15410+ A245 plug margin ring OFF by default (`_plugMargin`): four strips of M texels,
  M = max border shift of FG or plate texels (+ letterbox bar in texels, A253b), ClampToEdge UVs.

## 13. Plate mesh, object back layer, FG tear arms, quick-bake return (15429–15671)

- Fact L15429–15433: `bgLayerMesh` = plate; same transform as the FG mesh, renderOrder FG − 1.
- Fact L15451–15510 A257 object back layer (`_plugBack`, needs `_geoBackDepth` from
  `_plugGeoBand`): back depth per texel, BFS-filled outside objects (alpha 0 there), colour =
  `_geoBackColor` wash if present else raw texels; A257f index keeps quads whose four corners carry
  a back within fgTearStep of each other. Sits between FG and plug in depth.
- Fact L15512–15519: the a149 quick skirt is REMOVED; beyond-frame is transparent by design
  (outpaint demand, not disocclusion).
- Fact L15525–15526: `window._sdMaskTex = maskDT`; `_bgQuickBaked = true`.
- Fact L15553–15622 A241 per-fragment tear (`_fragTear`): mesh stays whole; `u_fragTear` 1 or 2
  (mode 2 = per-vertex fold points aFoldAt = min over incident cells of extent/rim-shift-span,
  gated by "source deeper than the far field by > 2 quanta" when `_geoGateField`/`_geoFarField`
  exists, else by disocc); `u_texelsPerPxRest = pw / plate screen px at rest`; factor 2.0
  default; an unflagged bake disarms it.
- Fact L15623–15667 A212 baked FG pre-tear (default when `fgPreTear` and not `_fragTear`):
  triangle torn iff it touches disocc (or `_a212Ungated`) AND depth span > quantum AND rim shift
  span > its texel extent. NOTE this is a SECOND tear after the L13975 one on the same geometry
  (`_fullIndex` is the source both times, so the second REPLACES the first: the first tear's
  index is overwritten by this one, which is gated by disocc; the first was ungated). The torn
  texels → `_qbFgTorn` (capture).
- Fact L15668–15670: quick bake returns true here. Everything from L15673 to the end of
  `bgBuildBackgroundLayerCore` is the v1 path (UI-disabled since a129; `bgQuickBake` false).

## 14. v1 path (15673–18660) — not the shipped default; read for completeness

- Fact L15673–15829 v1 pass 0: GPU rim flood with unlimited budget, FULL_FLOOD_ITERS =
  ceil(min(w,h)/2) (A155), lake closure (256 flag + 128 lake iterations), harmonic (96 Jacobi) or
  min relax; combine → `bgDepthTarget`. Runs at CANVAS resolution w×h (not source).
- Fact L15831–15867 v1 pass 1–2: seed at discontinuities (u_edgeThresh = max(slider, 0.03), reach
  slider default 120 px), 64 dilation iterations.
- Fact L15872–15923 v1 pass 4: GPU pull-push wash against `bgDepthTarget`.
- Fact L15949–16032 v1 CPU plug: depth read at NATIVE res from image2d / img / DataTexture
  readback (8-bit); `L._plugBaseDepth` restores the pristine input on rebuild (A180 idempotence).
- Fact L16060–16143 v1 despeckle/glow-attach: raised soft blobs vs a 24-px local floor; attach to
  thin carriers or flatten; `bgGlowAttach` OFF by default (L16161).

- Fact L16291–16350 v1 ramp collapse (binarise ±2 px window spans > fgTearStep) and display-side
  shallow closing (radius 5, 0.008 < up ≤ 2·fgTearStep); L16352–16372 installs the cleaned depth
  as the FG texture tagged `_isBakeDerived`.
- Fact L16385–16485 v2 full planes branch (`bgMPIFullPlanes`): calls `bgBuildFullPlanesCore`
  per media layer and returns (skips the v1 plug).
- Fact L16486–16525 v1 plug: `bgPlugMode==='directional'` → `bgDirectionalPlug`; else band PNG +
  Otsu valid + `MoebiusPlug.buildPlugFromValid` (220 iterations).
- Fact L16534–16610 v1 thin-feature halo: near class by band-excluded Otsu; thin = near not
  geodesically reachable from a 2-px-eroded core in 3 passes; halo = 5×5 max of thin depth onto
  neighbours (+0.004 gate) into the DISPLAYED depth only.
- Fact L16640–16970 v1 plug completion: standing-content mask (above local floor over 4×
  bgBandMaxGrowPx AND geodesic from a cliff seed), nearest-rim-first bucket flood (gate +0.02),
  floor rind, pull-push depth diffusion under occluders, membrane correction (one-sided: farther
  only, within fgTearStep nearer), plate ceiling (source or local floor), A41 cone clamp
  (sCone = bgConeSlopePerPx), A43 near-edge erosion E = max(3, round(3·pw/1200)).
- Fact L17018–17076 v1 band-gated FG cut mask (`bgBandCutDilatePx`), `u_useBandCut =
  bgCutFGOnPlug`, discards off under fgPreTear.
- Fact L17091–17275 v1 FG pre-tear: far-side match (plate carries the cliff's far side within
  fgTearStep) OR under-sheet OR soft-cliff core (NMS); halo-edge tear; adopted ink exempt.
- Fact L17286–17460 MPI slice 1 (`bgMPIMode`): components split at cliffs, K = bgMPIMaxLayers
  largest, per-layer meshes sharing attributes, quadtree decimation EPS 1.5/255.

- Fact L17471–18157 v1 fill colour: fillSrc = non-band, non-rind, luma ≥ 45; pull-push base;
  MPI slice 3 per-layer strips (`bgMPIStrips`); A43 backstop contract (plate near content with no
  surviving FG within 4 px flattens to the floor); A137 v1 ordering clamp; ink scrub; directional
  reflection fill (8 dirs, 400 px); `bgFillMode==='smooth'` rim colours; depth-consistent
  row/column continuation (tolD 0.06, REACH 400); 24 Jacobi passes; bleed BLEED = max(3,
  bgBandCutDilatePx+1); fill alpha = band reach fade (`bgFillSolid` → 255), full-frame opaque.
- Fact L18169–18351 v1 scene extension (`bgSceneExtend`): margin = pillarbox/ax + isotropic
  parallax px `max(|m0|,|m1|)` from the LUT (A113), ×1.15; margin colour+depth by pull-push
  diffusion seeded from SOURCE colour and FRONT depth; 3-texel weld ring; `bgExtendExport`.
- Fact L18368–18410 v1 hole-only islands (sConeB = 0.0025 hardcoded here, unlike the quick
  path): island = disocc (depth − plug > 0.02) unless `_bgPlugBand`; bound to `u_useBgIslands`
  = TRUE on the v1 plate (L18425–18428) — the v1 plate IS island-gated, unlike quick (A216).
- Fact L18449: v1 plate displacementBias −0.004; under-sheet −0.002; strips −0.0025.
- Fact L18626: v1 runs `bgBackstopSweep()` unless `_bsNoSweep`.
- Fact L18660–18690 `buildBackgroundLayer()` wraps the core and claims
  `window._bgLastBuiltDepthKey` = depth texture uuid on completion (A115).
- Fact L18697–18730 `_wireDebugSheetControls`: debug sheet button, SD bundle button, bake mode
  select (v1 disabled in the dropdown, A129).

- Fact L18733–18738 `applyBakeMode`: 'quick' → bgQuickBake; 'v2' → full planes + MPI; else v1.
- Fact L18755–18772 A253 gap-rule select (`bgGapRuleSel`): 'default' clears
  `_plugObjectRule/_plugExtent/_geoLipSeed/_plugBack/_bandReplace/_geoFarField/_geoGateField`;
  any other value sets object rule + extent + lip seed (+ back for 'back') AND `_plateFlushExempt`,
  `_plugMembrane`, `_plugGuided`, `_fragTear=2`, `_plugMargin=1`, then runs
  `_plugGeoBand({flush:true, observed:true, gateAPriori:true})`. This is the "experiment recipe";
  it is not the default and does not persist across a 'default' bake.
- Fact L18794–18823: no auto-build; the 800 ms watcher resets baked state on a new depth
  texture uuid (A112) and claims the key without baking.
- Fact L18988–19350 depth peeling (primary/secondary/fidelity passes): the realtime gap-mask
  machinery; `secondaryDepthFragmentShader`, GEQUAL depth func; not part of the bake.

## 15. updateCameraAndProjection (19365–19798) — THE camera facts

- Fact L19368–19375: `u_poseFrac` = max(|ex|/exR, |ey|/(exR·asp)), exR = D·tan(fadeEnd), D = live
  |camera.z − portal|, asp = terrariumHeight/terrariumWidth. So the vertical envelope of the
  per-fragment tear is the horizontal one × the WINDOW aspect (matches the CPU sweep rule).
- Fact L19378–19410 dolly: `dollyRefEyeZ` frozen at engage (A208); phase synced to the current
  distance (A209); `camera.position.z = subjectFocalPlaneWorldZ + dist`, dist ∈ [dollyMinDistance,
  dollyMaxDistance] on a sine. The dolly moves ONLY camera z. Nothing here touches
  `contentLensFovDeg` (confirmed: that is set only by `window.setLensFov`, L25274).
- Fact L19443–19474 subject pin: only when `subjectLockActive` AND the RENDERED subject plane
  (picked z + embed offset) is off the portal: `dollyLatGain = (e − qr)/(e0 − qr)`. For a subject at
  the portal (zeta = 0, the default click) `dollyLatGain = 1` (L19482–19485).
- Fact L19489–19518 head → eye: `scalarVal` = facetrackingScalarSlider (default 1.0),
  `camOff = 0.2`, `lensGain = tan(contentLensFovDeg/2)` (90° → 1.0);
  `faceTrackCamX = −(deviationX) · 0.2 · scalar · lensGain`, where deviationX is the face-tracker
  normalised position (0..1 frame fraction, minus 0.5, plus the window-on-screen offset, minus the
  baseline). Units: eye metres per unit of normalised face offset = 0.2·lensGain·scalar.
  Gyro: `gyroCamX = −pitchDeg · gyroSensitivityX · lensGain` (L19541–19542).
- Fact L19546–19547: `camera.position.x = (face + gyro + manualCamDX) · dollyLatGain`; y likewise.
  NOTHING divides by D or multiplies by D: the eye displacement in metres is independent of the
  dolly distance ⇒ the window angle shrinks as 1/D during a dolly-out (convention (c) in the S1
  report / dolly.py), unless the A67 pin (subject off-portal) scales it by (e − qr)/(e0 − qr).
- Fact L19560–19578: with the simulated viewer (`_svEyeLock`) the eye is `_svEyeBase · dollyLatGain`.
- Fact L19610–19634 frustum: the rect half-extents are terrariumWidth/2 × terrariumHeight/2 at
  z = portalPlaneWorldZ; ONLY during a dolly with the subject pin engaged (`_dzLat`, zeta ≠ 0) is
  the rect scaled by k = h·(h0−ζ)/(h0·(h−ζ)) and re-centred (A208 corner adjustment). Then
  `frameCorners(camera, pbl, pbr, ptl)`.
- Fact L19677–19693 per-layer uniforms every frame: portal norm, outer/inner depth, peek, metric
  scale, `u_useRayReproject = _rayReprojectNow()`, `u_embedOffset = bgEmbedOffsetNow()`,
  `u_refEye = (0,0,bgRefEyeZNow())`, aperture uniforms.
- Fact L19738–19768: the plug / MPI meshes get the SAME uniforms (A59f) plus the frame rect
  `u_frameC/u_frameH/u_frameZ` (A210 inpaint/outpaint classification); `bgEnsureSDDemandBackdrop`
  and `bgEnsureFishtank` refreshed here every frame.

## 16. Legacy sweeps, hole patch, SD import, embed/fishtank, simulated viewer (19804–22580)

- Fact L19804–20224 legacy texture-space atlas sweeps (`runAutomatedSweep` 5×5 grid,
  `runContinuousSweep` 180 frames): eye offsets = slider/400 (h default 45 → 0.1125 m, v default
  20 → 0.05 m) — a UI-unit convention unrelated to the fade cone; `bakeInfillAtlas` fills by
  flood/pyramid/planar. Legacy, not the quick bake.
- Fact L20233–21053 hole-patch system (screen-space gap capture → UV accumulation → patch mesh);
  legacy. L21055–21068 old SD pipeline stubs (deprecated).
- Fact L21079–21189 per-layer / v2-plane SD reimport (colours only; depth stays).
- Fact L21190–21310 `importSDInpaintedPatch` / `createInpaintPatchMesh` (legacy patch mesh).
- Fact L21427 `bgEmbedVolume = false` (A209: embed OFF by default, user decision) ⇒
  `bgEmbedOffsetNow()` = 0 and the fishtank / outer matte / aperture crop are all OFF
  (L21682 early return). `bgRefEyeZNow()` = frozen dolly eye or live camera z (L21428).
- Fact L21506–21524 `bgSyncApertureUniforms`: with `bgAperture` null the crop is 0.
- Fact L21558 `bgPopOut = false` (A174c OFF). L21577–21592 pop-out derived from the a165 fold
  ratio; dormant.
- Fact L21619–21666 A210 SD demand backdrop: visualisation only (`_sdHighlightOn`), placed at
  portal − max(outer, 0.01) − 0.005; orange outside the frame rect, cyan inside.
- Fact L21667–21797 `bgEnsureFishtank`: walls flare along reference rays s = (eZ − zF)/H; only
  when `bgEmbedVolume`.
- Fact L21877–22076 simulated viewer (a130): pass 1 supersampled ×1.75 (capped by 16 Mpx / max
  texture), pass 2 real quad at the panel rect viewed from the eye on a sphere of radius
  refD·dollyGain, lens locked to the head-on vertical FOV 2·atan(H/2/refD); yaw/pitch limits 90°.
  `svRecordPose` logs the real head angle θ = atan(hypot(x,y)/D) at ≤ 8 Hz (`svPoseStats` p50/95/99).

- Fact L22112–22138 `svKAt`: k "needed here" = LUT at the current lateral offset; k "budgeted"
  = LUT at D_ref·tan(fadeEnd) with the camera temporarily at the reference distance (because
  `bgShiftLUTFor` reads D live from camera.position.z).
- Fact L22146–22326 `svRenderFrame`: pass 1 renders `renderPortalFrame()` into the supersampled
  buffer with the eye at `svEye()` (+ optional perturbation), `_svEyeLock` set, the fade disabled,
  `bgPxScaleMul = S`; pass 2 photographs the panel quad from E with the locked lens; Lambertian
  falloff bound Ez/r³·D_ref². The live camera is LEFT at the pass-1 eye.
- Fact L22436–22556 SV acceptance test (A1 frame agreement, anchor drift sweep, A2 perturbation
  closed form drift = δ(1−t)·viewportH/H); pass criterion drift < 0.5 px and A2 ratio within 5 %.

## 17. renderPortalFrame (22584–24611)

- Fact L22590 `bgSyncPxScale()` every frame (band-cut thresholds vs canvas width).
- Fact L22625–22672: any non-final debug view (or inpainting off on an un-baked scene) hides the
  baked meshes and the fishtank for that frame.
- Fact L22675 `updateCameraAndProjection()` is called HERE, once per frame, before rendering.
- Fact L22752–22805 `sd_gap_mask` / `sd_gap_depth` views: realtime geometric gap pass + FG
  subtraction; interior gap predicate `(a.a>0.5 && a.b<0.008 && b.a<0.5)` (mode 9), identical
  to the export.
- Fact L22944–22977 static atlas path (legacy `useStaticInfillAtlas`).
- Fact L23067–23119 BAKED-DIRECT path: after a quick bake (`_bgQuickBaked`) or with inpainting
  off, the scene renders in ONE pass with every per-fragment gap generator OFF in a baked scene
  (A52; `_qbForceDiscards` diagnostic re-arms depth-grad only). `window._framePath`.
- Fact L23122+ PIPELINE path (realtime): clean pass → UV map → layer mask (split depth) → gap
  pass with the UI-armed discards → debug views (`layer_mask`, `plug_error` seam metric …).

- Fact L23351–23763 realtime debug views (`fg_exclusion_*`, `depth`, `gaps`, `jfa*`,
  `pull_coarsest`, `push_final`, `fg/bg_inpainted`): all read the realtime pipeline buffers.
- Fact L23777–24137 realtime inpainting methods: `jfa` (seed/flood/resolve with a background-
  biased gap target depth, `bgMaxBiasSlider` default 0.7), `pullpush` (the default realtime
  fill: FG subtraction `runFGSubtraction` → depth-aware pull/push per layer-mask channel → final
  composite), `dilation`, `cutoff/displacement` (no fill).
- Fact L24142–24556 `inpaint_only`, `inpaint_only_depth`, `gap_target_depth`, `scene_depth`,
  `scene_depth_composite` views.
- Fact L24558–24608 final post: FXAA (`useAntiAliasing`) → sharpen → dither → screen.

## 18. UI wiring, click handlers, metric scale (24610–26030)

- Fact L24641 gyro sensitivity slider range 0.0001–0.005 (deg → metres·lensGain).
- Fact L24770–24809 slider map: `innerDepthSlider → innerVolumeDepth`, `outerDepthSlider →
  outerVolumeDepth`, `portalPlaneZSlider → portalPlaneWorldZ`, `subjectFocalZSlider`,
  `depthMidpointSlider → currentNormPortalPlane`; `autoSweepAngle*` sliders are read directly by
  the legacy sweeps only. `facetrackingScalar` clamped 0–50 (L24945), default 1.
- Fact L25084–25102 dolly button toggles `dollyZoomActive` (and resets camera.fov to initialFov
  when off; fov is irrelevant because frameCorners overwrites the projection); subject-lock button
  toggles `subjectLockActive`.
- Fact L25133–25178 camera intrinsics inputs set `camera.fov` / `initialFov` (default 27) — again
  overwritten by frameCorners every frame; only `initializeSubjectLockConstant` reads it.
- Fact L25199–25256 manual view drag: ctrl/cmd/shift-drag adds `manualCamDX/DY` in metres
  (full canvas width ≈ 2 frame widths of travel); in SV mode a plain drag scrubs yaw/pitch.
- Fact L25273–25274 `window.setViewOffset(dx,dy)` and `window.setLensFov(deg)` (clamped 5–170;
  the ONLY writer of `contentLensFovDeg`).
- Fact L25401–25519 `get3DPointFromUV`: reads the 8-bit depth PNG through a canvas (`> 5` = hit),
  z = portal + `volumeZOffForNormDepth(d)` (the shader's smoothstep law, A200).
- Fact L25740–25814 `handleCanvasClick` (plain click = "set subject"): runs the depth-peek reveal
  animation AND SETS `currentNormPortalPlane = clicked 8-bit depth`, `subjectFocalPlaneWorldZ =
  portalPlaneWorldZ`, `outerVolumeDepth = 0.01`. ⇒ a plain click on the canvas CHANGES THE DEPTH
  LAW (pn and outer) — this is the "sweet spot" behaviour and it is why a probe must set
  `DEPTH_OUTER/INNER/PN` explicitly (a257_probe env) rather than trust the load-time defaults
  after any click.
- Fact L25831–25852 shift-drag = split-plane readback (`currentInpaintingSplitDepthNorm`);
  plain drag = depth-peek drag.

- Fact L25880 click-vs-drag slop 4 px (OS convention).
- Fact L25937–26025 set-scale: `metricScaleFactor = real/virtual` from two clicked 3D points;
  also sets the face-tracking scalar = (0.7 m / estimated viewing distance) × 3.0 — two
  hardcoded constants (NATURAL_INTERACTION_DISTANCE_M, BASE_PARALLAX_SENSITIVITY) that scale the
  head → eye gain. Only runs when the user uses Set Scale; the probe never does.
- Fact L26034–26220 `onOpenCvReady`: scene/renderer init, controls, resize observer (canvas
  keeps `camera.aspect`), `render()` loop, `loadDefaultImages()`, then webcam + FaceMesh.
- Fact L372–420 `bgDecodeDepth16(url)`: returns a Float32Array ONLY for a 16-bit PNG (bd === 16);
  8-bit PNGs return null and the layer keeps the 8-bit path. So every probe so far
  (`rest_depth8.png`) ran the 8-bit / live-bake path; a `rest_depth16.png` probe runs the float path.
- Fact L26235–26977 A227 embedded splat support (fzstd, .splat/.ply/.spz/.splatv parsers, EWA
  renderer); splats ride the same camera and are hidden in pipeline debug views.

## 18b. The CPU sweep's hole rule (7691–7930), read after the 16-bit reruns

- Fact L7699–7708: the sweep's `torn` set defaults to `_qbFgTorn` (the A212 disocc-gated tear);
  `_qbTorn` (the first, ungated fold tear) is NOT applied to the sweep's foreground ("including it
  over-covers by 45 %"). With `_fragTear` the per-pose fold points `_qbFoldTex` replace it.
- Fact L7845: `if (torn && torn[i]) continue;` — a torn texel is neither splatted nor quad-filled.
  The screen cells it would have covered are "uncovered" unless another texel lands there.
- Fact L7848–7856: untorn texels are drawn as QUADS over the warped bounding box of (i, i+1,
  i+pw, i+pw+1) when the two edge lengths are ≤ cutLen = 1/bgBandCutStretchFrac; so an untorn
  stretched surface stays covered. Compression never opens a hole under any splat rule.
- Fact L7858–7862 / L7876+: every in-frame cell not owned by the FG is a reveal cell, inverted
  through the far field to the plate texel that covers it → band demand along the pose's shift
  direction (one streak per pose).
- Consequence (measured on S2's dumps, see S1 report §5 correction): the fold criterion
  (shift span over the cell > extent, directionless) tears ~90 % of a grazing ceiling/floor, so the
  sweep sees holes where a continuous surface was, and the band takes the whole plane. The
  A212 quantum gate hides this on 8-bit sources (one-level treads exempt), exposing only risers
  (the stripes); on 16-bit sources the whole plane goes.

## 19. What this read changed (facts that contradict or sharpen earlier notes)

1. **Two depth paths, not one.** With an 8-bit depth PNG the quick bake consumes the LIVE-BAKED
   (sharpened, ramp-collapsed, thin-lifted) depth re-quantised to 1/255 via the canvas copy. With a
   16-bit PNG it consumes the RAW decode and, when dequantise/despeckle/snap touch anything, writes
   that raw-derived field back over the rendered texture — the live bake's sharpening is discarded.
   All probes to date were 8-bit. (§10; L10999, L12888, L12896, L13307.)
2. **The dolly does not touch the lens gain.** `contentLensFovDeg` has one writer
   (`window.setLensFov`); the dolly changes only camera z; the eye displacement in metres is
   D-independent unless the A67 pin is engaged (subject off the portal). (§15.)
3. **A plain click changes the depth law**: pn := clicked depth, outer := 0.01, subject := portal.
   Any probe or experiment that has clicked the canvas is no longer at the load-time defaults.
   (§18; L25795–25797.)
4. **The FG is torn twice on the quick path** and the second (A212, disocc-gated) tear REPLACES
   the first (L13975, ungated fold tear) because both start from `_fullIndex`. The torn footprint
   handed to the plug (`islandF`, a160b) comes from the FIRST tear; the rendered FG index comes
   from the SECOND. (§11, §13.)
5. **The plate is not island-gated on the quick path** (A216: complete backstop + polygon offset +
   depth test); it IS island-gated on the v1 path. The SD mask gates nothing in the render.
   (§12, §14.)
6. **The band's plate depth on the geometric path is the far field itself** (A244f overrides the
   pull-push continuation), then clamped by a135/a162 (never nearer than any source texel that
   could land on it) and slope-limited by a126 with the stale 0.0025·1920/pw step, then re-raised
   by the A253 lip floor only under the object rule. (§11, §12.)
7. **The constant 0.02 (depth units)** appears at L13359 (band seed), L13243/13289 (rigidify),
   L13866 (wash near-mask), L16753/16764 (v1 flood gate), L16964 (v1 cone clamp), L18371 (v1
   islands): an uncited threshold in normalised depth, invariant to nothing the scenes vary.
8. **The vertical envelope** everywhere (u_poseFrac, the CPU sweep) is the horizontal one ×
   terrariumHeight/terrariumWidth — window aspect, not a measured head range.
9. **Embed/fishtank/pop-out are OFF by default** (`bgEmbedVolume=false`), so `u_embedOffset=0`
   and the aperture crop is off; the S1 kit's assumption (portal at z=0, nothing in front) matches
   the shipped default.
10. The legacy sweeps' `slider/400` eye units, the v1 path, the hole-patch system and the
    depth-peeling passes are all dead or non-default code; none of them touches the quick bake.
