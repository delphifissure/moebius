# R8 supporting file — per-paper first-hand reading notes (2026-09-22)

Every paper in the supplied corpus, read beginning to end. Quotations are verbatim; numbers are from the tables named.
The synthesis drawn from these is `R8_corpus_first_hand.md`.


Order = order read. Every entry is from a beginning-to-end read of the file, not an abstract.

## 1. 1909.00915v1 — Counterfactual Depth (Dhamo? / "Peeking behind objects") [505 lines] DONE
- Task IS ours: "a depth map that describes the scene when a masked object is removed".
- **Inpaint-then-redepth LOST**: "Inpainting method does not work". Beats Poisson fill too.
- Uses a do-nothing baseline. R7's .310-vs-.425 checks out. Mask dropout load-bearing (.425 -> .762 without).
- Indoor only, 128x160 output, NO WEIGHTS available.

## 2. 2412.02336v1 — Amodal Depth Anything (Li et al.) [1246] DONE
- Task NOT ours: "depth of invisible parts of objects" = occludee amodal depth.
- ADIW 564K imgs; GT is itself a DAV2 ViT-G prediction -> capped by DAV2 (R7 right).
- Amodal-DAV2-L RMSE 3.418; Amodal-DepthFM 5.410.
- **Tab.2 ablation: alignment HURTS Amodal-DAV2** (Full 3.682 vs w/ align 3.878); helps DepthFM (5.410->4.645).
  => our amodal_probe.py / s52_depth.py min-max rescale runs the model in its degraded config.
- w/o Do,Ma 7.549; w/o Ma 4.369 (mask conditioning is most of the model).
- They benchmark inpaint-then-depth (Invisible Stitch, pix2gestalt): "cascade errors due to inaccurate inpainting".
- Limits: mask errors propagate; detail capture DECLINED after SAM-dataset fine-tuning.

## 3. 2406.07706v1 — PACO, Object-level Scene Deocclusion (SIGGRAPH'24) [682] DONE
- Task = deocclude the OCCLUDEE (album behind teddy bear). Not our band.
- Fig.8 three SD-inpainting strategies (a) hole only -> completes occluder; (b) grey occluder -> colour leaks;
  (c) mask over whole occluder -> invents new objects. Supp S7: they USE (c) for all comparisons,
  "its superiority over the other two strategies in most scenarios".
- **NEW / load-bearing: PACO delegates the BACKGROUND to LaMa, by name, twice.**
  S4.3: "we can seamlessly leverage recent image inpainting models such as LAMA to help us to deal with
  occluded background regions."  Limitation (iv): "Background deocclusion is limited by the inpainting
  models ... leaving background processing to inpainting models like LAMA."
  => S52 arm A is PACO's own prescription for our half. Not an analogy.
- S4.4: the invented-object failure is blamed on TRAINING DATA ("avoids the tendency of generating novel
  objects based on contextual information, a common characteristic of existing inpainting models"),
  not on inpainting as such. So LaMa's speckled patch is contingent, not a law.
- Limitation (iii): objects crossing the image boundary are NOT handled; proposed fix = pad the border.
  == our S48 "unbounded" class; supports the app's margin strips.
- Inference S4.3: uses MiDaS depth to order objects into DEPTH LAYERS, occlusion relation from relative
  depth across the shared boundary; deocclude a whole layer in one pass.
- Fig.14c: LaMa + GT amodal mask is BLURRY "due to limited generative capabilities" == our caveat 2.
- Tab.1 COCOA val: PACO IoU 89.52 / FID 13.93 / order acc 90.0 vs SSSD 87.59 / 15.05 / 89.4 (small margins).
- Tab.2 strategies: one-by-one FID 13.79 (7.19 diffusions/img), layer-wise 13.93 (2.50), once-for-all 14.56 (1).

## 4. 2406.06679v1 — PatchRefiner (Li/Bhat/Wonka, KAUST) [588] DONE
Same first author as Amodal-DAV2 and PatchFusion. Not about occlusion at all; about high-res metric depth.
Four things transfer directly:
- **Residual beats direct.** Frozen coarse model + refiner predicting a RESIDUAL. Tab.3: residual on D_c
  RMS 0.892 vs direct prediction 0.925, same features. Independent corroboration of S48's finding that the
  pure-gradient return beat the absolute return 2.57x: when you already hold a trustworthy coarse field
  (our plate / the observed rim), ask the model for the DIFFERENCE, not the value.
- **Scale error and boundary error are separable and must be supervised separately** (DSD loss):
  L_silog against real GT for scale, L_rank + L_ssi against a synthetic-trained teacher for detail.
  Tab.4 CityScapes: L_rank alone F1 26.12, L_ssi alone 26.39, BOTH 26.84 -> "orthogonal strategies".
  Baseline real-only 23.68. Naively using L_silog on the pseudo-label wrecks scale: d1 95.4 -> 82.6.
  => exactly our failure: the per-component absolute shift wrecked the field; gradients preserved it.
  => and it says gradients/ssi ALONE are not the ceiling: ordinal ranking supervision (tau = 0.03) adds.
- **The synthetic teacher's profile is "great boundaries, useless scale"**: zero-shot d1 = 5.705 %,
  RMS 12.203, but the best boundary recall in the table (51.28 vs 37.59 baseline). That is the profile of
  any learned prior dropped into our band, and the reason the return contract must take only structure.
- **S.B / Fig.9: GT depth near edges is systematically wrong**, so scale metrics computed near boundaries
  are unreliable; they report non-boundary scale separately. Our S45/S48 scoring is ENTIRELY in the band,
  i.e. entirely near boundaries — a caveat on our own numbers that we have not stated.

## 5. 2309.06547v2 — AmodalSynthDrive (Sekkat, Mohan, ... Valada) [547] DONE
This is the paper that INTRODUCED the amodal depth estimation task, and the dataset our own code path is
named after: s52_depth.py imports `src.models.amodalsynthdrive.dav2.AmodalDAv2`.
- **THE DECISIVE QUOTE, and it is a third independent confirmation that S39/S40/S43 used the wrong model.**
  S.III-C1: "We limit depth estimation for amorphous regions to directly visible portions only, as these
  regions lack the structure or identifiable features necessary for amodal prediction."
  Amorphous = "stuff" = road, building, wall, vegetation, terrain, sky. i.e. THE BACKGROUND BEHIND AN
  OCCLUDER IS EXPLICITLY EXCLUDED FROM THE AMODAL DEPTH TASK, by its definition paper, ON THE GROUND THAT
  IT IS NOT PREDICTABLE. Stronger than 2412.02336's phrasing: that one says the task is about objects;
  this one says background stuff was deliberately ruled out.
- Output is a STACK of depth maps D_0..D_{N-1} by relative occlusion order, N=8. Level 0 = all amorphous
  regions + unoccluded objects; level n = objects occluded by >=1 object of level n-1. Objects within a
  level never occlude each other. Most scenes 2-4 levels (Fig.4d).
- Metric ADErr = occurrence-weighted mean of per-level RMSE.
- Tab.IV baselines: Amodal-DORN ADErr 23.9 / RMSE_vis 10.13; ADB-DeepLab 23.2 / 9.59; AD-DeepLab 21.6 / 7.93.
  "the significant disparity between ADE and RMSE_vis errors indicates the network's difficulty in learning
  the delineated multiple depth maps directly." Even with perfect synthetic GT the amodal depth task scores
  ~2.5x worse than modal depth. A ceiling on what any such model could give us even if the task DID match.
- Also: improving amodal depth improved MODAL depth (RMSE_vis 10.13 -> 7.93) -- occlusion reasoning helps
  the visible field too. The one encouraging line for us.
- Synthetic (CARLA), 60k imgs 1080x1920, 150 seqs, non-commercial licence. Driving only.
- Pretraining on it improves real amodal seg by ~2 points (Tab.V/VI).

## 6. 2603.05908v1 — Pano3DComposer (Qiu & Wu, SYSU, 2026) [497] DONE
Panorama -> compositional 3D scene, feed-forward. Mostly off-task. Two things.
- **S3.3 IS INPAINT-THEN-REDEPTH FOR THE BACKGROUND, USED WITHOUT COMMENT IN 2026:**
  "We merge all instance masks and apply an inpainting model (LaMa [34] or DiT360) on the panoramic image
  to obtain a clean background panorama I_bg. A feed-forward Gaussian reconstruction network, following
  Flash3D, predicts background depth with Depth-Anywhere and generates a background Gaussian set G_bg."
  => merge ALL object masks, LaMa, then run a monocular depth model on the INPAINTED image.
  That is S52 arm B followed by DA3/MoGe.
  **DIRECT CONFLICT with 1909.00915 ("Inpainting method does not work").** 7 years apart; the inpainter
  changed. Record as an open disagreement, and note that it names a depth path WE HAVE NOT TRIED and can
  try today with assets already on disk (occluder-removed inpainted plate from S52 + DA3/MoGe in-session).
  This is NOT the amodal path that failed for a task-definition reason. Different construction.
- Tab.1 carries a "Pseudo Geometry" row = the offline differentiable-optimisation oracle, as an explicit
  upper bound in the results table (CD-S 0.0119 vs their 0.0784; F-Score-S 0.8695 vs 0.6930).
  Same device as S51's oracle bound. Confirms it as normal practice, not a peculiarity of ours.
- Failure case (a): "When backgrounds exhibit complex geometry, clutter, or heavy occlusions, the inpainting
  network may fail to recover a clean room structure"; and Flash3D background "affected by the quality of
  depth estimation; inaccurate depth may lead to distorted backgrounds".
- Tab.3 ablation: Chamfer alone is useless (CD-S 0.8688); + direct parameter regression 0.1266; + mask
  (silhouette) loss 0.1120. Silhouette consistency is worth ~12% -- our equivalent is the seam/rim exactness.
- Uses Amodal3R optionally for severely occluded instances. Another amodal-completion reference.

## 7. 3746027.3755176 — MLGS, Multi-Layer Gaussian Splatting (Diao et al., ACM MM'25) [421] DONE
Single image -> feed-forward 3DGS -> novel view. THIS IS OUR TASK in another representation, and it is the
most directly transferable paper so far.
- **Their thesis is our S51/S52 conclusion stated as architecture:** "visible surfaces and occluded regions
  demand fundamentally different optimization strategies. While visible geometry can be directly learned
  from image data and supervised through photometric constraints, occluded areas require geometric
  reasoning driven by physical plausibility and structured prior knowledge."
  So they DECOUPLE: separate decoders (D_vis vs D_occ), separate losses (L_rec vs L_occ). Our app has one
  plate and one far-side law doing both jobs.
- **Context for filling layer m is ONLY what is BEHIND it.** S3.2: agglomerative clustering in depth space
  into P=8 layers; contextual region M_m^c = union_{j=m+1..P} M_j. "This design allows the network to
  utilize information from deeper layers for reconstruction."
  == S45's fix of filtering the rim through rl.joined to the FAR side, which was worth 5.1x (0.1776->0.0349).
  Independent confirmation that far-side-only context is the correct rule, not a hack.
- **Gated convolution exists to SUPPRESS the near-side context:** "features derived from areas outside the
  contextual mask M_m^c introduce harmful artifacts when processed indiscriminately, as they lack reliable
  semantic information for occlusion inpainting."
- **Tab.4 ablation is the punchline.** LPIPS on RealEstate10K (lower better):
    Ours                                   0.148
    w/o L_occ                              0.150
    GCB -> plain Conv3x3                   0.151
    reduce clusters 8 -> 4                 0.153
    w/o mask-guided AND GCB->conv          0.156
    w/o occlusion GS layers (= Flash3D)    0.157
  Their total margin over Flash3D is 0.160 -> 0.148 = 0.012. Of that, ~0.008 is mask-guidance + gating,
  i.e. ESSENTIALLY THE WHOLE IMPROVEMENT IS "restrict the context to the far side and gate out the near
  side". Architecture second, context rule first.
- They deliberately DO NOT inpaint behind the farthest layer: "due to the lack of subsequent layers to
  provide reliable sources ... and the final layer typically represents distant background elements, which
  are rarely exposed to occlusion." Bears on our sky layer / _skyInf.
- MPI baselines show "stack of cards" artifacts = "discontinuous depth transitions". Our streak/step problem
  in another representation; a layered representation does not escape it.
- **METHODOLOGICAL: LPIPS is where they win and they say so.** Tab.1 PSNR 24.93->25.17 (+0.24, negligible),
  SSIM 0.833->0.834 (nil), LPIPS 0.160->0.148 (-7.5%). "the proposed method achieves a significant
  improvement in the LPIPS metric, which demonstrates the ability of MLGS to generate visually realistic
  results in disoccluded regions, aligning more closely with human perceptual expectations."
  => EVERY metric this project uses (placeholder %, hole %, wall length, pixels-differing, mean abs diff) is
  of the PSNR/SSIM family -- area and magnitude. S51 measured a 21% cut in wall length and saw nothing;
  S52 measured "4.24% of pixels differ" and could not say whether it was better. LPIPS is the instrument
  built for exactly that gap and we have never used it. This is an actionable defect in our harness.

## 8. Mohan & Valada — Amodal Panoptic Segmentation (CVPR 2022) [372] DONE
Introduces the APS task + KITTI-360-APS / BDD100K-APS + APSNet. Segmentation only, no depth, no colour.
Low direct relevance; three things worth carrying.
- **The occluded half is ~2.4x worse than the visible half, again.** Tab.2, APSNet (M6): APQ^V_T 44.1 vs
  APQ^O_T 18.6; APC^V_T 62.2 vs APC^O_T 25.8. Same ratio as AmodalSynthDrive's ADErr 21.6 vs RMSE_vis 7.93.
  Across segmentation and depth, on synthetic and real data, hidden-region quality sits at ~40% of visible.
  A sober prior for what ANY learned prior can give our band.
- **Explicit occluder modelling is what buys the gain.** Their amodal head splits the box into three masks:
  visible / occluder (what covers the target) / occlusion (the hidden part of the target). Ablation M2->M3
  adds the OCCLUDER head and lifts APQ_T 33.7 -> 34.6, with "the larger increase in APC^O_T". "The occluder
  features that are incorporated enable the amodal mask head to discern the boundaries of the occluded
  regions." We already export plane_object_ids (the occluder footprint) -- this says naming the occluder
  explicitly, as a separate input channel from the hole, is worth real points. S52's arms differ only in
  whether the occluder is inside the mask; nothing tells the model "this is the occluder".
- Amodal reasoning improved the MODAL result too (KINS Tab.3: inmodal AP 29.7 -> 32.7). Second sighting of
  this effect (AmodalSynthDrive had it for depth).
- Residual limitation: "segmentation quality near the boundaries of moderately to heavily occluded regions
  of non-rigid classes such as pedestrians tends to be poor."

## 9. 2406.11824v1 — Infinigen Indoors (Raistrick, Mei, Kayan et al., Princeton) [2700] DONE
Procedural Blender generator of photorealistic indoor scenes. BSD licence, 100% procedural, no external
assets, unlimited scenes. Not a disocclusion method. Relevance is as a TRUTH-KIT SOURCE and one methodology
point.
- Emits per-image: RGB, mesh, **depth, surface normals, OCCLUSION BOUNDARIES, segmentation, bounding boxes,
  optical flow, albedo** (Fig.2). 79 object generators / 741 params; 30 material generators / 120 params;
  40k LoC. Multi-room multi-floor houses. Exports to USD/Omniverse/UE5.
  => a drop-in replacement/extension for our hand-built truth kit (S1-S32, P1-P6) if we ever want scale and
  indoor variety. It does NOT give amodal/hidden-surface GT directly, but the full mesh is there, so our
  own multi-hit ray-caster would run on it.
- **Occlusion boundary estimation is a named task with standard metrics.** S4.3 / Tab.4 reports ODS (optimal
  dataset-scale F), OIS (optimal image-scale F) and mAP -- the BSDS boundary protocol.
  Infinigen-Nature 14.38 / 19.43 / 10.80; Hypersim 26.02 / 19.44 / 15.69; Infinigen Indoors 29.47 / 30.29 /
  19.09. Note how LOW these are in absolute terms: best ODS 0.29. Occlusion boundaries are a hard task.
  => S33's "visible wall length" and bend classes are a home-grown occlusion-boundary metric. There is a
  standard one. If we want a number other people can read, ODS/OIS/mAP is it.
- **G.2, and this one is in our favour:** "Due to the absence of ground truth occlusion boundaries in
  Hypersim (or any other photorealistic dataset), we approximate them by thresholding the gradient of the
  provided depth maps. We carefully tuned this threshold on Hypersim to give the best results."
  That is precisely S33's construction (a bend = adjacent samples differing by more than a threshold) --
  and the field does it with a HAND-TUNED threshold. S48's reveal field derives the threshold from the
  viewing envelope in screen pixels with no tuning. On this narrow point our instrument is better than the
  published practice, and the R7 synthesis should say so.
- F.2 camera placement: "we sample at random, reject near walls, and maximize depth variance." A cheap,
  principled rule for choosing test poses; our kit picks poses by hand.
- Solver detail (simulated annealing over a constraint DSL, DOF-restricted moves, cardinality bounds,
  3x speedup from BVH caching + plane hashing) is irrelevant to us.
- Tab.2 shadow removal: synthetic data slightly HURTS in-domain (ISTD PSNR 31.96 -> 31.72) and clearly helps
  zero-shot (SRD 22.83 -> 24.56). The standard synthetic-data trade, stated cleanly.

## 10. InpaintFusion (Mori, Erat, Broll, Saito, Schmalstieg, Kalkofen; IEEE TVCG 26(10) 2020) [654] DONE
Diminished Reality: remove a real object from a live RGB-D view and show what is behind, with JOINT COLOUR
AND DEPTH inpainting, fused into a surfel map, 6-DoF, real time. **The closest published system to what this
project is building**, and it predates everything else in the pile by years. Four findings, all load-bearing.

1. **THEY INPAINT DEPTH IN THE GRADIENT DOMAIN WITH A POISSON SOLVE. INDEPENDENT ARRIVAL AT S48's CONTRACT.**
   S3.7: "Since we cannot simply copy view-dependent depth values, we use the normal map N-hat for inpainting
   3D structure. The normals at reference pixels can simply be copied like color values." and "For the depth
   values in the ROI, we compute grad-D-hat, a gradient field [Perez, Poisson image editing] (depth gradient
   map) of the sampled depth values. We minimize [...] to calculate the inpainted depth map."
   Their stated reason is ours: absolute depth is "perspective and view-dependent", gradients are not.
   S48 found the pure-gradient return beat the absolute return 2.57x and treated it as a local discovery.
   It is the published construction, from 2020, in a shipping real-time system.

2. **BI-DIRECTIONAL GRADIENT AVERAGING -- a concrete defect in our exporter.**
   S3.7: "directly sampling pixels from f* will introduce inconsistencies: Consider a pixel at u and its right
   neighbor at u+v. A naive horizontal gradient will usually not match the sampled depth gradient of the
   adjacent pixel, d(f*(u+v)) - d(f*(u+v) - v). Therefore, we minimize [...] where E-hat is the mean
   bi-directional depth gradient sample."
   Our export (moebius.js and harness/s52_depth.py) writes ONE-SIDED forward differences:
   gx[:, :-1] = d[:, 1:] - d[:, :-1]. When the return's gradients come from copied/sampled sources the forward
   and backward estimates disagree and the fix is to average them. ACTIONABLE.

3. **MULTIPLICATIVE, NOT ADDITIVE, COMBINATION -- to avoid tunable weights.**
   S3.7: the geometric term "modulates the texture similarity rho_t, acting like a weight that forces both
   texture and normals to agree. Adding rho_g as another linear term to sum of rho_t and rho_s works as well,
   but it introduces two more additional weighting parameters that must be adjusted." (Fig.12: 3 params vs 1.)
   A published instance of our own "zero per-image tuning" principle deciding an architectural choice.
   Also: "rho_g provides a geometrical labeling that limits pixel search to geometrically similar surfaces,
   overcoming the need for manual labeling used in previous work" -- normals as a free surface-segmentation,
   cf. our sheets (S35) and far-side-only context.

4. **THE SECOND INSTRUMENT DEFECT, AND IT IS BIGGER THAN THE LPIPS ONE: WE MEASURE ON STILLS.**
   S4.1: "As inpainting has no ground truth, previous work ... does not present quantitative measures and
   typically relies on the authors' subjective preference. In fact, quantitative assessment in inpainting is
   an open research problem ... Such automated quality assessment, however, will not be able to truly reflect
   human judgement. In addition, SPATIO-TEMPORAL CONSISTENCY CANNOT BE JUDGED FROM INDIVIDUAL IMAGES."
   So they ran 55 subjects x 9 scenes x 3 methods = 1485 ratings, for stills AND for video. Result (Fig.9):
       median score   stills   video    delta (sV - sI)
       Single Plane      5       3        -1
       Multi-Plane       5       2        -2
       InpaintFusion     6       7        +1
   On STILLS the three methods are nearly indistinguishable (6/5/5). IN MOTION they separate by 4-5 points.
   The planar proxies get WORSE in motion; only the one with correct depth improves. Fig.14 caption:
   "static images do not clearly show the advantages of our method. Therefore, we strongly recommend readers
   to watch the results in motion."
   => S51's A/B was two still frames and concluded "the frames are indistinguishable". S52's arms were
   compared at fixed poses. OUR ARTEFACT IS A PARALLAX ARTEFACT -- "streaky as hell" is a motion percept.
   Measuring on stills is measuring in precisely the regime this paper demonstrates is blind to the
   difference. Every "measured improvement, no visible improvement" verdict in S51 is suspect on this ground.
   Their H1 was that stills would show nothing; they rejected it only because IF still won by 1 point.

Other:
- Mask ratio 17.02 % (Tab.3). Our band is ~16 % of the picture at 45 deg. Near-identical regime.
- Runtime: 31 Hz main thread; first keyframe inpaint 4.4 s on a background thread, cheaper after propagation.
- Limitation that is our seam requirement: "in case a real background is observed after inpainting, that
  inpainted depth and real depth may disagree, leading to discontinuities at the ROI border."
- Blending prefers OBSERVED pixels over inpainted ones by weight (S3.9) -- "combines inpainting-based DR with
  observation-based DR, while minimizing the inpainting area". Our plate-2 / carriers do the same thing.
- They cite Dhamo et al. "Peeking behind objects: Layered depth prediction from a single image" [38] -- the
  same group as the counterfactual-depth line.

## 11. 2503.13439 — Amodal3R (Wu, Zheng, Guan, Vedaldi, Cham; S-Lab/NTU + VGG Oxford) [669] DONE
Amodal 3D reconstruction: occluded 2D image -> complete 3D asset. TRELLIS + two new attention mechanisms.
Task is the OCCLUDEE again, not our background. Three transferable findings.
1. **THIRD PAPER TO SAY: GIVE THE OCCLUDER ITS OWN CHANNEL -- and here it is specifically GEOMETRY that gains.**
   S3.2: "if a pixel is denoted as invisible in the mask M_vis, this might be because there is an occluder in
   front of that pixel (so the pixel COULD HAVE contained the object except due to occlusion), or because the
   pixel is entirely OFF the object. This information is encoded by the mask M_occ."
   Tab.3 (GSO, single view):        FID    KID%   COV%   MMD(per-mille)
     naive concatenation           31.96  0.49   37.96  3.61
     w/ only mask-weighted attn    30.53  0.38   36.90  3.69   <- best appearance
     w/ only occlusion-aware layer 31.77  0.57   40.19  3.51   <- best GEOMETRY
     full                          30.64  0.35   39.61  3.62
   Fig.7: "Mask-weighted attention alone extends geometry into background regions, while occlusion-aware
   attention alone cannot guarantee photorealistic appearance."
   With PACO (Fig.8 strategies) and APSNet (occluder head, M2->M3) that is three independent papers saying the
   occluder must be named separately from the hole. Our bundle HAS this (plane_object_ids) and S52 never used
   it as a distinct input -- the three arms differ only in whether the occluder falls inside the mask.
2. **ONE-STAGE BEATS 2D-COMPLETE-THEN-3D, and inconsistent per-view completion is WORSE THAN ONE VIEW.**
   Tab.1 GSO FID: TRELLIS 1-view + pix2gestalt 58.82; TRELLIS 4-view + pix2gestalt 65.69 (WORSE with more
   views); + Zero123++ to force consistency 60.37; Amodal3R 1-view 30.64, 4-view 26.27.
   "inconsistent 2D completion does confuse reconstruction models to the point that using a single view is
   preferable."
   => Direct support for our pipeline shape: inpaint ONCE on the plate grid and reimport, rather than
   inpainting per pose. Per-pose fills would be mutually inconsistent and this says that is worse than one.
3. Mask ratio at inference 0.4-0.6 (much larger than our band). Trained on only 20,627 synthetic assets,
   mostly furniture; "trained exclusively on synthetic data ... cannot leverage environmental cues and must
   rely solely on the visible portions of occluded objects" -- a limitation vs pix2gestalt, which can.
- Cites 2411.13019 (Open-world amodal appearance completion), also in this pile.
- Random occlusion masks for training: 1-3 lines/circles/ellipses plus 3-7 dilated rectangles, unioned, "to
  ensure these regions connect -- thereby better simulating real-world occlusions, where mask regions are
  typically not highly fragmented". Our band IS highly fragmented (261 components on the troll). Worth noting
  as a distribution mismatch for any off-the-shelf inpainter we feed it to.

## 12. 2411.13019v1 — Open-World Amodal Appearance Completion (Ao, Jiang, Ke, Ehinger; Melbourne/Monash) [1453] DONE
Training-free pipeline: text query -> LISA-13B visible mask -> RAM++ tags -> GroundingDINO + SAM all objects
-> InstaOrderNet occlusion ORDER -> auto CLIP-chosen prompt -> SD2-inpaint, iterated -> RGBA output.
Occludee task again. Four things carry, one of them big.

1. **BACKGROUND SEGMENTS AS OCCLUDERS -- the only paper in the pile that treats amorphous "stuff" as a
   first-class occluder, and it is worth a lot.** S3.1 "Handling Background Regions and Unknown Objects":
   "Traditional segmentation methods may overlook these regions because they aren't associated with object
   category labels, but these unlabelled (or 'background'-labelled) regions can be occluders of a target
   object." They take I minus the union of all object masks, erode to separate loosely connected areas,
   dilate to re-consolidate, and get a set of background segments B_1..B_k that enter occlusion reasoning
   alongside the object masks.
   Tab.4 ablation (full dataset): with background segments LPIPS 0.320 / FeatSim 0.646 / SSIM 0.731;
   WITHOUT 0.333 / 0.620 / 0.713. Fig.6, Fig.7: foliage, ground, undergrowth as occluders.
   => Our object map comes from SAM 2.1 clicks on NAMEABLE objects. The troll's cave wall, foliage, rock --
   the things that actually occlude in our scenes -- are exactly the "ambiguous background" this paper says
   the object-centric pipeline drops. The erode-then-dilate partition of the unsegmented remainder is cheap
   and we do not do it.

2. **BOUNDARY-AWARE OCCLUSION: when the target touches the image edge, DILATE THE OCCLUDER MASK ALONG THAT
   EDGE.** Eq.3. "amodal completion requires image expansion". Applied iteratively until the mask stabilises.
   That is S48's "unbounded" class handled as a rule rather than a caveat, and it agrees with PACO's
   limitation (iii) that the fix for boundary-crossing objects is to pad.

3. **EVALUATION: they say plainly that the metrics are a formality and the humans are the measurement.**
   S4.2: "Evaluating amodal completion on natural images with real-world occlusions presents unique
   challenges, as the ground-truth appearance of occluded regions is inherently unavailable. Thus, we use a
   combination of human evaluation and quantitative metrics. WE CENTER OUR EVALUATION ON HUMAN ASSESSMENT."
   And S4.3 Tab.3 footnote: "these appearance quantitative metrics provide insight, they are provided for
   reference only, as the amodal appearance ground-truth is not available."
   180 participants on Prolific, 4-way forced choice, randomised order, 10% gold-standard trials, only raters
   passing 75% of checks retained. Preference: Ours 41.86%, Pix2gestalt 27.95%, PD w/o MC 15.78%, PD-MC 14.41%.
   Fleiss' kappa 0.319 overall (0.275 VG .. 0.374 LAION) -- only "fair agreement". **Even with 180 people,
   agreement on which disocclusion looks better is only fair.** Third paper in the pile (with InpaintFusion
   and MLGS) whose headline evidence is a human study. Our project has exactly one human rater and he is the
   stated authority; that is not a weakness of the project, it is the field's own standard practice.
   Their proxy metrics are computed by comparing the VISIBLE part to the completed version -- LPIPS 0.320,
   FeatSim 0.646, SSIM 0.731. A self-consistency check, not an accuracy check. We could do the same on the
   band: compare the filled band against the rim-adjacent visible surface.

4. **Complete-failure rates (Tab.5) are a metric we do not have.** PD w/o MC 44.9%, PD-MC 45.5%, theirs 4.1%,
   pix2gestalt 0.0% -- but "Pix2gestalt achieves a 0% failure rate due to its supervised design, it sometimes
   minimally alters the input without meaningfully addressing occlusion". A method that always outputs
   something and a method that outputs nothing 45% of the time are both bad, differently. Our S52 arm A
   changed 4.24% of pixels; that number alone cannot distinguish "filled well" from "barely touched it".

Other: SD v2 inpainting, max 3 iterations, A100. Dataset 2379 images / 2565 instances / 553 classes from
VG(51.9%) COCO-A(31.6%) free(9.6%) LAION(7.0%). COCO-A filtering removed images where "background elements
were occluded but primary objects were not" -- i.e. they explicitly discarded OUR case as out of scope.
Alpha blending with a graded transition region at the visible boundary (Eq.8) = our seam feather.

## 13. Zhu, Tian, Metaxas, Dollar — Semantic Amodal Segmentation (CVPR 2017) [1028] DONE
The foundational paper: COCOA dataset, 500 BSDS images x 5-7 annotators + 5000 COCO images. Segmentation and
depth ORDER, no appearance. Old, but it is the one that establishes whether any of this is well posed.
Five findings, two of them directly usable.

1. **AMODAL ANNOTATION IS MORE CONSISTENT BETWEEN HUMANS THAN MODAL ANNOTATION.**
   Region consistency (pairwise F at IoU 0.5): amodal median 0.723 vs original modal BSDS 0.425.
   Their own modal annotations 0.756. Edge consistency: amodal 0.795 vs BSDS 0.728.
   "our data has higher region and edge consistency than the original BSDS labels."
   Set against 2411.13019's Fleiss kappa = 0.319 for "which completion looks best", the split is clean:
   **people agree on the SHAPE of what is hidden and disagree on its APPEARANCE.** Geometry of the hidden
   region is a well-posed target; its texture is not. That is an argument for scoring our band's geometry
   against human-stable criteria and its colour only by preference.

2. **AMODAL SEGMENTS ARE SIMPLER THAN MODAL ONES -- a parameter-free prior we could actually use.**
   Tab.1:            simplicity        convexity
     BSDS modal        .718              .616
     BSDS amodal       .834              .643
     COCO modal        .746              .658
     COCO amodal       .856              .685
   with simplicity(S) = sqrt(4*pi*Area)/Perimeter and convexity(S) = Area/Area(ConvexHull); both = 1 for a
   circle. "amodal segments have simpler shapes than the modal segments ... independent of scene geometry and
   occlusion patterns."
   AmodalSynthDrive Tab.II replicates it on three more datasets (KINS .709->.830, KITTI-360-APS .778->.884,
   BDD100K-APS .697->.821, theirs .585->.633). Universal.
   => S33's "visible wall length" is a perimeter measure. A far-field construction that RAISES the simplicity
   of the completed surface (less perimeter per unit area) is doing the amodally-correct thing, and simplicity
   needs no tuning and no truth. This is a candidate objective to replace/augment wall length, and unlike wall
   length it has a published prior saying which direction is right.

3. **Depth layers needed grow only LOGARITHMICALLY with the size of a connected component** (Fig.7), and most
   components need just a few (Fig.6d). Retroactive support for the app's plate-1 + plate-2 design being
   nearly enough; MLGS chose 8 and found 8 > 4.

4. Occlusion statistics: 62% of regions are partially occluded; mean occlusion 21% of region area;
   most regions lightly occluded with a small heavily-occluded tail (Fig.6a).

5. **The human-machine gap is the paper's point, and it is a caution about saturated metrics.**
   On the ORIGINAL BSDS edges, HED ODS .79 against human F .81 -- a gap of .02, i.e. the metric is used up.
   On the AMODAL annotations, HED drops to .69 while human rises to .90 -- gap .21.
   A metric can look healthy and be measuring nothing left to win.

Baselines (Tab.3a, COCO val, average recall): DeepMask .378 / SharpMask .396 (modal, state of the art then)
vs ExpandMask .417 / AmodalMask .434. Under HEAVY occlusion the gap widens: SharpMask AR_H .242 vs
AmodalMask .364. On STUFF only: SharpMask .246 vs AmodalMask .366. Synthetic amodal training data (random
overlays) helped over modal but lagged real amodal data (AmodalMask_S .395 vs AmodalMask .434).

Depth ordering (Tab.3b): naive "smaller mask in front" .696, "closest to top is back" .711 -- i.e. **trivial
heuristics already get ~70%**; OrderNet_M+I reaches .814 on generated masks and .883 on ground truth.
We read occlusion order straight off a depth map, which should beat all of this; worth remembering that
"who is in front" is a task people publish models for and we get for free.

The four annotation guidelines (S2) are a checklist our SAM object-map workflow does not follow:
(1) only nameable, semantically meaningful regions; (2) DENSE -- "if an annotated region is occluded, the
occluder should also be annotated"; (3) every region ordered in depth; (4) shared boundaries marked
explicitly so they carry no figure-ground side. (2) is the discipline our object map lacks, and (4) is our
"is this bend a real step or two surfaces meeting" question stated as an annotation rule.

## 14. 2207.02062v3 — Image Amodal Completion: A Survey (Ao, Ke, Ehinger; CVIU 2023) [829] DONE
The field map, to 2022. Three subtasks: amodal SHAPE, amodal APPEARANCE, ORDER perception. Tables 1-7 give
the method/dataset/metric landscape. Six things matter to us, one of them decisive.

1. **THE SURVEY'S OWN DEFINITION PUTS OUR TASK OUTSIDE THE AMODAL LITERATURE.** S2.2, first sentence:
   "General image inpainting methods restore a user-selected missing area in an image to create a
   visually-reasonable output, WITHOUT CONCERN FOR WHICH OBJECT(S) THE MISSING REGION BELONGS TO. In contrast,
   amodal appearance completion algorithms AUTONOMOUSLY IDENTIFY the partially-occluded objects and their
   hidden regions that need to be reconstructed."
   We compute our mask from geometry, we do not care which object the band belongs to, and we want plausible
   background. **By the survey's definition we are doing general inpainting, not amodal completion.**
   This retires a large fraction of R7 in one line: the amodal-completion literature was never addressing our
   problem, and the fault was in the framing, not in the reading.

2. **The discriminative/generative split, stated by the survey, matching Zhu-2017 vs the Fleiss kappa.**
   Conclusion: "shape completion and order perception generally using DISCRIMINATIVE models (assuming only
   one ground truth shape and correct ordering) and appearance completion typically using GENERATIVE models
   (ALLOWING MANY POSSIBLE APPEARANCES)."
   Hidden shape: one answer, humans agree, score it. Hidden colour: many answers, humans only fairly agree,
   judge it. Our band has both halves and they need different treatment -- which is exactly what the S45/S48
   return contract does (depth solved against a boundary condition, colour merely written on the mask).

3. **NOVEL VIEW SYNTHESIS IS CALLED OUT AS A STRICTLY EASIER NEIGHBOUR, AND THAT IS US.** S2.3.2:
   "Similar to amodal completion, the task of novel view synthesis also requires predicting what lies behind
   the visible object. The difference is that, depending on the angle of the novel view relative to the
   original view, it may not be necessary to predict much-hidden information. FOR SMALL SHIFTS IN VIEW,
   USUALLY ONLY A FEW PIXELS NEAR THE EDGES OF THE VISIBLE OBJECTS NEED TO BE PREDICTED."
   That is the band, described exactly, and it says our problem is the smaller one. Encouraging, and it is
   the reason the amodal models underperform on it: they are built for a harder, differently-shaped task.

4. **S5.3 names our far-field rule as a future direction.** "One potential future approach is to build a 2.5D
   or 3D representation using additional information (such as the predicted layer order of the objects and
   the structure of the background) or using a hypothetical spatial layout (SUCH AS TREATING THE BACKGROUND
   AS MULTIPLE PLANES and the objects as simple volumes)."
   window._farRule='plane' is a 2023 survey's open suggestion, built.

5. **S5.1 names our truth kit as a gap in the field.** "a real dataset that provides visually complete ground
   truth about the appearance of the invisible parts of objects or backgrounds IS CURRENTLY UNAVAILABLE. The
   next step could be to create real datasets with the ground-truth appearance in some simple scenes. For
   example, use a robotic arm to sequentially remove objects from the table."
   Our multi-hit ray-caster truth kit is that, in simulation. Worth stating in the synthesis that the
   instrument the project built in Sprint 1a is one the field says it lacks.

6. **S5.5 "Consistent Performance Metrics": the field admits it has none.** "there are no consistent
   performance metrics for associated tasks at this time ... Inconsistent evaluation metrics lead to
   difficulties in comparing multiple approaches for the same task."
   Combined with InpaintFusion S4.1 and 2411.13019 S4.2, the position is settled: nobody has a working
   automatic metric for hidden-appearance quality, and the ones who try say so in print.

Numbers worth keeping:
- Tab.2 average occlusion rates: COCOA 18.8%, COCOA-cls 10.7%, D2S 15%, KINS 19.8%, DYCE 27.7%, CSD 26.3%,
  SAIL-VOS 56.3%. Our band is ~16% of the picture at 45 deg -- squarely in the normal range.
- Tab.3 amodal instance segmentation mAP on COCOA: best is Shape Prior 35.4; ORCNN 33.2, ASN 34.0, PCNet 30.3,
  BCNet 32.7, CSDNet 34.1. **Nothing is above 36 %.** The whole subfield sits in the low thirties.
- Tab.4 amodal SEMANTIC segmentation, Amodal Cityscapes: MIoU visible 62.7 vs MIoU INVISIBLE 23.6. The 40%
  ratio again (fourth sighting).
- Tab.6 amodal appearance on CSD: CSDNet RMSE 0.06 / SSIM 0.91 / PSNR 35.24 -- but CSD is synthetic with
  rendered ground truth, which is why numbers exist at all.
- Tab.7 occlusion ORDER is nearly solved: InstaOrderNet on KINS recall 98.7 / prec 94.5 / F1 96.0;
  ASBU accuracy 92.6 on KINS, 90.3 on COCOA. Order is the one subtask that works -- and we get it free from
  the depth map.
- S4.1: model-generated amodal masks are already competitive with human ones, and "human observers even
  PREFER the automatically-generated masks" (Ling et al. 2020).
- S2.3.2 two-layer scheme (Dhamo 2019b): predict the FG mask, discard ALL foreground pixels, GAN-fill the
  background -- "the subsequent background completion task will not be fooled by the appearance of objects
  in the foreground layer." That is the principled justification for S52 arm B / PACO (c).
- S4.3 lists Diminished Reality as a headline application and cites PanoDR and Pintore's "Instant automatic
  emptying of panoramic indoor scenes". The DR line (InpaintFusion et al.) is the one adjacent to us.

## 15. 2503.20211v1 — Synthetic-to-Real Self-supervised Robust Depth (Yan et al., NUS) [1101] DONE
Self-supervised monocular depth in rain/night/fog for driving. No occlusion content at all. Off-task, but it
contributes two instrument ideas and one general lesson.

1. **CONSISTENCY REWEIGHTING: a confidence map built from the DISAGREEMENT OF TWO ESTIMATORS, with no truth.**
   Eq.9-11: C_cst = exp(-beta * |D_syn - D_day| / D_syn); W_cst = C_cst + eps; then the pseudo-label loss is
   weighted by W_cst. "assigning higher weights to consistent regions and lower weights to highly inconsistent
   areas". Fig.5 visualises it: dark distant regions at night and blurry rain regions come out low-confidence.
   => We have two independent estimates of band depth whenever we run anything alongside the plane law. Where
   they agree, trust; where they disagree, fall back. Our only current uncertainty is _geoFarAxS, derived
   inside one law (half the rim tolerance + slope uncertainty x distance). This is a free second source and
   it needs no ground truth. Cheap to add to the return contract as a per-texel lambda in the screened
   Poisson rather than the single global lambda we use.

2. **STRUCTURE PRIOR AS A DISTRIBUTION MATCH -- a scoring idea we do not have.**
   Eq.12-15: compute the depth histogram over the WHOLE daytime training set with a differentiable histogram
   (two sigmoids per bin, bandwidth a), then constrain adverse-condition predictions to match it by KL
   divergence. Fig.3(c)(d): night predicts too many near planes, rain predicts too many far ones.
   => Applied to us: **the filled band's depth distribution should resemble the visible far field's depth
   distribution.** That is a global, parameter-free, truth-free check on a return, and it catches exactly the
   failure S52's depth half hit -- a prediction that tracked the occluder would have an occluder-shaped
   histogram, not a background-shaped one. Our guard there was a hand-written median comparison; the
   histogram/KL version is the principled form of the same idea and generalises to any return.

3. **General lesson from Tab.4: transferring a FILTERED, STRUCTURAL representation beats transferring a rich
   one.** Distilling raw features (L_feat) is WORSE than no distillation at all (night AbsRel 0.1911 vs
   baseline 0.1865); distilling the COST VOLUME helps (0.1809). Their reason: "the cost volume inherently
   filters extraneous information and retains motion-structure features", whereas features carry "abundant
   information ... heterogeneous visual cues across conditions".
   Same shape as the gradient-vs-absolute finding: pass the structure, not the values.
   Also: "applying RA alone without additional strategies does not guarantee improved performance on real
   data, as not all supervisions are valid" -- naively adding the real-data stage barely moved it; the gain
   came from reweighting + the distribution prior.

4. Fig.3(a): the synthetic-to-real drop on the SAME condition is 70% in AbsRel, 28% RMSE, 17% delta1. Blunt
   evidence for how far a model trained on rendered data is from a photograph -- relevant every time we score
   on the kit and then look at the troll.
Results for the record: nuScenes-night AbsRel 0.1713 (prev best 0.1865); Robotcar-night 0.1103 (prev 0.1219);
zero-shot DrivingStereo-rain 0.1707 (prev 0.1822).

## 16. 2504.19506v1 — SynergyAmodal / DeoccAnything (Li et al., Xiamen Univ.) [1114] DONE
Data-human-model co-synthesis -> SynergyAmodal16K -> a text-controllable deocclusion diffusion model.
Occludee task. Five findings, two of them directly actionable.

1. **FOURTH INDEPENDENT PAPER PUTTING THE OCCLUDER IN ITS OWN CHANNEL -- and they go further: THE BACKGROUND
   IS ALSO ITS OWN CHANNEL.** Eq.4 conditions the denoiser on m_occluder (downsampled), E(x_{n+1}),
   **E(x_background)**, and the TRIPLE mask stack (m_deoccluded || m_occluder || m_n+1), through a
   zero-initialised conv.
   x_background,i = x . (m_deoccluded,i AND m_occluder,i AND m_i) -- the visible background passed separately
   rather than composited in.
   => PACO's objection (b) was that the replacement colour leaks into the fill. Passing the background as its
   own channel is how this paper avoids that, and it is a cheaper fix than S52's harmonic continuation.
   Running tally on "name the occluder explicitly": PACO (Fig.8), APSNet (M2->M3 occluder head), Amodal3R
   (occlusion-aware layer, best geometry), SynergyAmodal (triple mask + background channel). Four for four.

2. **PERFORMANCE SPLITS BY OCCLUSION FRACTION, AND IT TELLS US WHICH TOOL FOR WHICH PART OF OUR BAND.**
   Fig.6: SDAmodal (a regression trained on COCOA) has the highest mIoU in the 0-10% occlusion bucket;
   generative methods (Pix2Gestalt, theirs) take over at 10-50%, 50-90% and 90-100%.
   And S4.3: "regression-based methods tend to produce results resembling an 'AVERAGE' outcome. While they
   often achieve DECENT IoU SCORES, the actual shapes do not meet the requirements of the deocclusion task."
   => Our plane far-side law IS a regression producing an average, and our metrics (placeholder %, hole %,
   coverage) ARE the IoU family. This is the trap named exactly.
   => And the split is actionable: S48 measured the reveal field as p50 0.116 screen px, p90 0.544, p99 4.641,
   max 45.2. **Most of our band is a tiny disocclusion where a regression is the right tool; the heavy tail
   is where a generative model earns its place.** A reveal-thresholded hybrid is justified by this figure,
   and the threshold is the reveal field we already compute -- no new parameter.

3. **Global-to-local inference is worth ~13% FID for free.** S3.4 / Fig.4 / Tab.2: run the whole image first
   (resized, padded) to get a blurry amodal result; then crop the ROI guided by the predicted mask and
   re-denoise at reduced noise strength, initialised from the blurry result.
   COCOA FID: w/o G2L 10.9 -> with 9.5. BSDSA: 37.4 -> 34.3. mIoU essentially unchanged (90.1 -> 90.3).
   Only matters if we move off LaMa to a latent diffusion inpainter with a fixed 512 input; then it is the
   recipe for our 851x1023 plate.

4. **Dual-occlusion ambiguity (Appendix A) -- a warning about self-supervised occlusion synthesis.**
   If you paste a random occluder C over a region already occluded by B, the model learns that A's amodal
   shape is "A as partially occluded by B", i.e. the wrong target. Their fix is to subtract B's occluding
   region from C. "the dual-occlusion ambiguity severely impacts the success rate of SSSD."
   General form: synthetic occlusion has to respect the occlusion order already in the image, or it teaches
   the wrong answer. Bears on the truth kit's degradation ladder and on any paste-based augmentation.

5. Numbers. Tab.1 COCOA mIoU/FID: Ours 90.3/9.5, SDAmodal 87.3/11.0, Pix2Gestalt 85.8/13.6, SSSD 81.3/12.8,
   **naive "InternVL + SD2-inpaint + ZIM" 58.5/15.1**. On the domain-shifted BSDSA, SSSD collapses to
   34.1 mIoU / 92.9 FID while the others hold.
   The naive VLM+inpaint+segment stack at 58.5 is "primarily attributed to its lack of explicit occlusion
   reasoning mechanisms" -- an off-the-shelf pipeline with no occlusion model in it loses by 30 points.
   They sample 8 variations and take the best: "highlights the necessity of calculating the mIoU across
   different variations". Best-of-N is the standard evaluation for generative completion.
   Cost: 3 expert annotators x ~200 hours total for 16K pairs; training 50K steps, 4 days on 4xA100.
   Failure cases (Fig.10): meaningless text glyphs, and **shadows of the removed occluder remain**.

## 17. 08418.md — DUPLICATE of #4 (PatchRefiner, 2406.06679v1) [1058] DONE (read, verified)
Same paper, ECCV camera-ready rendering. Read beginning to end and compared against the arXiv file:
identical Abstract, S1-S5, Fig.1-7, Tab.1-4 and all numbers (UnrealStereo4K RMSE 0.892 vs PatchFusion 1.088;
CityScapes DSD boundary F1 26.84; zero-shot PR.S delta1 5.705 / boundary recall 51.28; ranking tolerance
tau = 0.03; lambda1 = lambda2 = 0.1).
**08418 is a strict SUBSET**: it stops at the references, whereas 2406.06679v1.md also carries the
supplementary (A Boundary Evaluation Protocol with the DBE/chamfer metric and Tab.5, B Challenges in Scale
Evaluation with Fig.9 and Tab.6, C More Results). Nothing in 08418 that is not in #4.
So the pile is 20 distinct papers, not 21.

## 18. 2601.04090v2 — Gen3R: 3D Scene Generation Meets Feed-Forward Reconstruction (Huang et al., ZJU+ByteDance) [1178] DONE
VGGT recast as a geometry VAE; its latents aligned by KL to a video-diffusion RGB latent space; the two
generated jointly by a fine-tuned Wan2.1 DiT. Not an occlusion paper, but five findings land on us.

1. **THEIR "2-STAGE" ABLATION IS THE SHAPE OF OUR PIPELINE, AND IT LOSES.**
   S4.4: "a video diffusion model ... generates only RGB under camera control, while geometry is predicted
   separately using VGGT from the generated images ... our joint generation approach outperforms the 2-Stage
   pipeline in both appearance and geometry. This is because the 2-Stage approach NAIVELY CONNECTS 2D
   GENERATION WITH 3D RECONSTRUCTION, LEADING TO ACCUMULATED ERRORS."
   Tab.4, 1-view: 2-Stage PSNR 17.38 / LPIPS 0.3412 / CD 1.6223 against joint 20.51 / 0.2281 / 1.1047.
   => Third data point on the inpaint-then-redepth question. Tally: AGAINST = 1909.00915 ("Inpainting method
   does not work") and Gen3R (accumulated errors); FOR = Pano3DComposer (uses it without comment).
   Caveat that keeps it open: Gen3R's 2-stage generates NOVEL VIEWS then reconstructs, which is much harder
   than inpainting a hole in a fixed view and re-running depth on it.
   => Also a point in favour of our return contract's shape: it asks for colour AND depth in one return.

2. **GEN3C IS OUR ARCHITECTURE, AND ITS STATED FAILURE MODE IS OUR STREAKS.** S4.2: Gen3C "combin[es]
   depth-based warping and inpainting, but its quality HEAVILY DEPENDS ON DEPTH ACCURACY, LEADING TO
   MISALIGNED BOUNDARIES WHEN THE DEPTH ESTIMATES ARE INACCURATE. In addition, it sometimes exhibits color
   differences from the input image."
   Warp by depth, inpaint the holes, get misaligned boundaries where the depth is wrong. That is the plate,
   the band and the streaks, described by someone else.

3. **VGGT's PROFILE IS OUR PLATE'S PROFILE: best accuracy, worst completeness.** Tab.2, 1-view Co3Dv2:
   VGGT Accuracy 0.3291 (best of all) / Completeness 4.3830 (worst of all) / CD 2.3561;
   Gen3R Accuracy 0.8284 / Completeness 1.3811 / CD 1.1047. "it suffers from lower completeness since it does
   not generate geometry for novel views."
   Accurate where it can see, empty where it cannot. **Accuracy / Completeness / Chamfer is a cleaner and
   standard statement of what we call precision / recall / holes**, and it makes the trade explicit in one
   number (CD) instead of two we have to read together.

4. **A GENERATIVE PRIOR CLEANS UP A GEOMETRIC ESTIMATOR'S NOISE.** S4.3: "VGGT occasionally exhibits floaters
   in its predicted geometry, and our adapted VAE inherits these artifacts. HOWEVER, OUR GENERATIVE MODEL
   CORRECTS THE ERRORS and produces cleaner depth." Tab.3 Co3Dv2 CD: VGGT 0.9632 -> Ours 0.9625; TartanAir
   1.5957 -> 1.5101. Tab.10 zero-shot ScanNet++: VGGT completeness 0.1162 / CD 0.1279 vs Ours 0.0963 / 0.1209.
   Modest, but it is the effect we would want against our speckle and streaks: not "fill the hole" but
   "regularise the whole field through a learned prior".

5. **Tab.11 is a sharp warning against asking one model for both modalities.** They trained an RGB head on
   VGGT's geometry tokens: RealEstate10K PSNR 23.39 against the RGB VAE's 37.58.
   "VGGT is designed primarily for geometry modeling and LACKS SUFFICIENT CAPACITY FOR RGB FEATURE EXTRACTION
   and high-fidelity appearance reconstruction. This observation also motivates our choice to DECODE
   APPEARANCE AND GEOMETRY SEPARATELY."
   => Our return contract keeps colour and depth as separate files from (potentially) separate models. Right
   shape. The thing Gen3R adds is that the two should still be ALIGNED before being generated -- their KL
   alignment is load-bearing: without it, 1-view PSNR 20.51 -> 16.31 and camera AUC@30 0.7443 -> 0.4100.

Other: DepthSplat (pure reconstruction) "leaves holes in occluded regions ... In contrast, our method can
plausibly complete these regions using diffusion-based generation" -- reconstruction leaves holes, generation
fills them; the same trade as our plate vs the inpaint.
Trained on 300k scenes across 10 datasets, 24 H20 GPUs. 560x560, 49 frames.

## 19. 2406.09414v2 — Depth Anything V2 (Yang, Kang, ... Zhao; HKU + TikTok, NeurIPS 2024) [1229] DONE
The family our depth maps come from. Not about occlusion at all, and yet it contains the single most direct
statement of our S51 problem in the whole pile, plus two things we can act on this week.

1. **"BETTER MODEL BUT WORSE SCORE" -- S51's verdict, reached by someone who concluded the METRIC was wrong.**
   Tab.2 caption: "Solely from the metrics, Depth Anything V2 is better than MiDaS, but merely comparable with
   V1. But indeed, the focus and strengths of our V2 (e.g., fine-grained details, robust to complex layouts,
   transparent objects, etc.) CANNOT BE CORRECTLY REFLECTED ON THESE BENCHMARKS. Similar results (i.e.,
   BETTER MODEL BUT WORSE SCORE) are also observed in [7, 28]."
   S6.1: "Such frequent label noise makes the reported metrics of powerful MDE models not reliable anymore."
   Fig.8 caption: "The noise will cause better models instead achieve lower scores."
   => S51 measured a 21% cut in wall length, saw nothing on screen, and concluded the construction was not
   worth shipping. DAv2 hit the same wall and concluded THE BENCHMARK WAS AT FAULT, then built a new one.
   Given MLGS (LPIPS) and InpaintFusion (stills vs motion) saying the same thing from two other directions,
   the S51 conclusion should be reopened as a measurement failure, not a construction failure.

2. **DA-2K IS A TEMPLATE WE CAN COPY CHEAPLY, AND IT IS THE RIGHT SHAPE FOR THE BAND.**
   S6.2 / Fig.9: sparse ORDINAL pairs. Pick two pixels, decide which is nearer. 1K images, 2K pairs.
   Selection: SAM key points; four expert models vote; disagreements go to human annotators; plus a manual
   pipeline for pairs all models get wrong together. C.3: only pop pairs whose predicted depth ratio > 3
   (avoid hard calls). Triple-checked by two further annotators. Organised into 8 scenarios so results are
   readable per scenario.
   => For the band: sample pixel pairs straddling it and ask "which is nearer". Scores a far-field
   construction on ORDINAL correctness. No dense truth needed; it is the thing humans demonstrably agree on
   (Zhu 2017); it is cheap; and it is exactly the "ranking supervision" PatchRefiner found ORTHOGONAL to
   scale-shift invariance. This is the most concrete new instrument in the whole read.
   Tab.3 DA-2K accuracy: Marigold 86.8, Geowizard 88.1, DepthFM 85.8, DAv1 88.5, DAv2-S 95.3 ... -G 97.4.
   The benchmark separates models that the conventional metrics rank as equal.

3. **TEST-TIME RESOLUTION SCALING UP -- free sharpness, and we are leaving it on the table.**
   B.8: "we surprisingly find that our model has the property of 'test-time resolution scaling up' ... we can
   almost freely increase the image resolution at test time to produce more fine-grained depth maps." Fig.11
   shows 1x / 2x / 4x of the 518 base resolution with steadily improving sharpness.
   => Our plate is 851x1023 and we run DA at its native short-side 518. Running at 2x should sharpen exactly
   the depth boundaries that every streak in this project originates from. One flag, no training.

4. **Real depth labels are noisy AT BOUNDARIES, and mixing them in actively harms detail.**
   S2: two disadvantages of real labels -- label noise (sensors fail on transparent surfaces, stereo fails on
   repetitive patterns, SfM fails on dynamic objects) and IGNORED DETAILS: "These datasets struggle to provide
   detailed supervision at object boundaries or within thin holes, resulting in OVER-SMOOTHED depth
   predictions."
   B.9: adding HRWSI (V1's best real dataset) at only 5% of training images "has a huge negative impact on
   the original fine-grained predictions" (Fig.12).
   => Our truth kit is synthetic and exact. This is the strongest possible endorsement of that choice for
   boundary work -- and a warning against ever "validating" it against noisy real depth.

5. **The gradient matching loss is what buys sharpness, and only works when labels are precise.** B.7: L_gm
   (from MiDaS) "fails to bring evident improvement when the model is trained on labeled real datasets";
   on synthetic labels, raising its weight 0.5 -> 2.0 -> 4.0 steadily improves sharpness. Final ratio
   L_ssi : L_gm = 1 : 2, i.e. **the gradient term is weighted twice the value term.**
   Fourth independent vote (with InpaintFusion, PatchRefiner, S48) that depth detail lives in the gradients.

Other:
- B.5 / Tab.12 NTIRE 2024 Transparent Surface Challenge delta1: MiDaS 0.259, DAv1 0.535, DAv2 0.836 zero-shot,
  0.912 fine-tuned (first place 0.917). Transparent and reflective surfaces are a real measured weakness of
  the depth models we depend on.
- B.6 / Tab.13: only DINOv2 transfers synthetic->real. SAM-L NYU-D AbsRel 0.186 against DINOv2-L 0.048;
  SynCLR collapses (0.344). And DINOv2-G WITH registers is much worse than without.
- S5.2: they ignore the top-10%-largest-loss regions per sample during training as "potentially noisy pseudo
  labels" -- a cheap robust-loss trick.
- Data: 595K precise synthetic (BlendedMVS, Hypersim, IRS, TartanAir, vKITTI2) + 62M pseudo-labelled real.
  B.4: diversity of unlabelled sources matters more than volume -- SA-1B alone at 11M for the same iterations
  loses to eight sets at 62M.
- B.2/Tab.9: the two purely INDOOR synthetic sets (Hypersim, IRS) "surprisingly fuel the most generalization
  ability"; vKITTI2 has poor metrics but is "highly beneficial to the prediction sharpness, due to the large
  number of fine-grained structures (e.g., leaves)". Fine structure in training data buys sharpness.
- Speed: ViT-S 60 ms / 25M params, ViT-L 213 ms / 335M, against Marigold-LCM 5.2 s / 948M.

## 20. 2312.00532v1 — DeepDR: Deep Structure-Aware RGB-D Inpainting for Diminished Reality
##     (Gsaxner, Mori, Schmalstieg, Egger, Paar, Bailer, Kalkofen; TU Graz) [1601] DONE
Same group as InpaintFusion, four years on. **The second most important paper in the pile.** Joint colour+depth
inpainting for DR, structure-conditioned, temporally coherent, real time. Their Tab.1 is literally our
requirements list: Color / Depth / Structure / Temporal, and they are the first to tick all four.

1. **THEY STATE OUR PROBLEM IN THEIR INTRODUCTION.**
   "image space inpainting is not sufficient for DR applications -- depth information needs to be coherently
   inpainted as well." And: "DR has strict requirements in ADHERING TO THE STRUCTURAL BOUNDARIES of the
   underlying scene. This is conflicting with the tendency towards producing BLURRY RESULTS AT AMBIGUOUS
   OBJECT BOUNDARIES AND REGIONS WITH MIXED SEMANTICS, which is commonly seen in image inpainting CNNs."

2. **THE DECISIVE EVIDENCE ON INPAINT-THEN-REDEPTH: JOINT INPAINTING ROUGHLY HALVES DEPTH ERROR.**
   Their baselines are exactly the construction in question: RGB inpainting (DeepFillV2 / PanoDR / E2FGVI)
   followed by a state-of-the-art depth-completion network (InDepth / NLSPN / DM-LRN) run on the inpainted
   colour. Depth RMSE:
     InteriorNet: DeepFillV2 0.572, PanoDR 0.564, E2FGVI 0.563  ->  **DeepDR 0.278**
     DynaFill:    7.92, 8.12, 7.83, and DynaFill's own model 7.78  ->  **DeepDR 4.51**
     ScanNet:     0.508, 0.536, 0.512  ->  **DeepDR 0.484**
   S4.4: "sequential approaches suffer from the LOSS OF DETAIL AND SHARP FEATURES in inpainted images", and
   "the baseline depth completion fails at filling complex depth regions with sharp edges (e.g. between floors
   and walls), in particular FOR STRUCTURES FAR AWAY FROM THE CAMERA."
   => Running tally on inpaint-then-redepth: AGAINST = 1909.00915, Gen3R, **DeepDR (quantified, ~2x)**;
   FOR = Pano3DComposer (uses it, no ablation). The question is settled: **do not fill colour and then run a
   depth model on the fill.** If we want depth in the band, it must come from a joint solve or from the
   contract's own gradient/Poisson path -- which is what S45/S48 already built.

3. **PIXEL METRICS REWARD BLUR, AND THEY SAY SO AND THEN DEMONSTRATE IT.**
   S4.3: "these metrics only measure pixel-wise concordance and TEND TO FAVOR BLURRY OVER PERCEPTUALLY SIMILAR
   IMAGES, which is problematic for DR. Measures computed on deep features better mirror human perception and
   are, thus, considered more meaningful for our evaluation." They use LPIPS + FID for frames and **VFID
   (video FID)** for sequences.
   The demonstration: DeepDR comes SECOND in PSNR (41.9 vs E2FGVI's 43.2) while winning LPIPS (0.0104 vs
   0.0131) and FID (0.218 vs 0.363). On ScanNet E2FGVI's PSNR lead grows to 46.7 vs 42.4 -- "we attribute that
   to its TENDENCY TO PRODUCE OVERLY SMOOTH RESULTS, which matches the blurry images recurrent in ScanNet."
   => S52 reported "mean abs difference 85.1" and "4.24% of pixels differ". Those are PSNR-family numbers.
   This paper is the proof that a blurrier fill can score better on them. Third independent source (with MLGS
   and DAv2) saying our metric family is the wrong one.
   And with InpaintFusion's stills-vs-video result, the pair is named: **LPIPS per frame, VFID per sweep.**

4. **THE GRADIENT TERM DOMINATES THEIR DEPTH LOSS.** S3.4: L1 on depth "does not take the local pixel
   neighborhood into account, which can lead to BLURRY EDGES AND DISCONTINUOUS SURFACES in reconstructed depth
   images. Hence, to encourage smooth depth predictions with sharp steps, we use a gradient-based loss term"
   (Sobel). Supplementary S6.2 weights: lambda_rec 10, lambda_per 10, lambda_sty 250, **lambda_grad 100**,
   lambda_seg 10, lambda_t 10. The depth gradient term is weighted TEN TIMES the depth value term.
   Fifth independent vote (InpaintFusion, PatchRefiner, DAv2, S48, DeepDR) that depth detail lives in the
   gradients. Our contract is on firm ground.

5. **STRUCTURE CONDITIONING: predict a segmentation at every decoder scale and use it to modulate BOTH the
   colour and the depth features, with SHARED parameters.** RGB-D SPADE. The premise: "the RGB and depth
   inputs share the same underlying semantics." Ablation Tab.6: no RGB-D SPADE gives LPIPS 0.0143 vs 0.0104
   and depth RMSE 0.374 vs 0.278. Cost: inference 2.41 -> 4.43 ms (Tab.11), i.e. it nearly doubles the model.
   => We already compute an object map (SAM 2.1, Sprint 20/21). It is currently used for highlighting and for
   plane_object_ids. This says it should also be the thing that keeps the band's colour and depth boundaries
   agreeing with each other -- the single shared structure both modalities are conditioned on.
   S8.5: segmentation quality matters and FEWER CLASSES SEGMENT BETTER (DynaFill 12 classes segments more
   accurately than InteriorNet's 40); they propose "reducing the number of semantic classes by merging similar
   classes". Our object map is already coarse, which is an advantage here.

6. **SEPARATE ENCODERS, FUSED DEEP.** S3.1: "deep features in a CNN contain the majority of structural
   information, while shallow layers contain textural information. Since RGB and depth inputs are TEXTURALLY
   DIFFERENT, BUT REPRESENT THE SAME UNDERLYING STRUCTURE, we encode RGB and depth in two separate but
   parallel streams." Ablation: joint encoder LPIPS 0.0121 vs separate 0.0104, with MORE parameters.
   Same conclusion as Gen3R Tab.11 from the opposite direction.

7. **MASKING MORE BEATS MASKING LESS -- measured.** Supplementary S7.3: they manually added the object's
   SHADOW to the mask. "results with masked shadows OFTEN LOOK BETTER than without. The reason for that is
   that our model does not need to hallucinate the very ambiguous shadow borders, leading to a more realistic
   color with fewer artifacts." Conversely, ScanNet's automatic instance masks "sometimes do not cover the
   entire diminished object. In such cases, ARTIFACTS AND FLICKERING between consecutive frames can appear."
   => Empirical support for PACO strategy (c) / S52 arm B, and a rule: **an over-generous mask beats a tight
   one.** Our band mask is computed to be exactly the revealed set. Dilating it into the occluder may help.
   (Also the third paper to name leftover shadows as a failure, after SynergyAmodal and PACO.)

8. **HOW MUCH HARDER IS HIDDEN DEPTH THAN VISIBLE DEPTH? ~1.85x.** Supplementary S7.4 / Tab.10: the same model
   on depth-from-RGB (filling depth in regions VISIBLE in colour) scores RMSE 0.262 on ScanNet, against 0.484
   for the hidden-structure task in Tab.4. A clean quantification of the gap our band lives in.

9. **A fourth human study, and the largest gap in it.** 64 participants, 7-point scale, 12 scenes x 50-200
   CONSECUTIVE FRAMES, shown as video beside the input, with 3D-reconstructed meshes re-lit and re-furnished.
   Median: DeepDR 5.3, DeepFillV2 2.0, PanoDR 2.2, E2FGVI 2.2. Friedman chi2(3) = 133.3, W = 0.7, p < 0.001.
   **The perceptual gap (5.3 vs 2.2) is enormous next to the metric gaps (LPIPS 0.0104 vs 0.0131).**

Other:
- Real time: 4.43 ms / 184.3 G MADs / 69.9 M params on a 1080 Ti, ~9x faster than E2FGVI (40 ms) because no
  optical flow at inference. Flow (MaskFlowNet) is used only in the TRAINING temporal loss.
- Temporal coherence without future frames: ConvLSTM + short-term and long-term warped losses against the
  previous and the FIRST frame. Ablation: no temporal -> VFID 0.0487 vs 0.0257.
- Failure cases (Fig.8): irregularly textured objects (a carpet) produce structural artifacts; ambiguous
  object borders (a curb) produce colour bleeding.
- S4.1: "DynaFill is the SOLE DATASET that offers ground truth by presenting scenes both with and without
  individual objects that need to be removed" -- i.e. the dataset the amodal survey (S5.1) said did not
  exist, does, for outdoor driving. Everything else simulates removal with random object masks over an
  unmodified image, using the original as ground truth. **That is a truth protocol we could adopt directly
  for the band: paste a synthetic occluder into a kit scene, and the untouched render is the truth.**
- Trained at 256x256, T=5 frames, 1M iterations, batch 4, Quadro RTX 8000.

## 21. 2306.09310v2 — Infinigen: Infinite Photorealistic Worlds using Procedural Generation
##     (Raistrick, Lipson, Ma et al., Princeton, CVPR 2023) [1558] DONE
The natural-world predecessor of #9 (Infinigen Indoors). Same role: a truth-kit source. Four things, two of
which validate choices our truth kit already made and one of which is an honest negative result.

1. **"REAL GEOMETRY" AS A STATED DESIGN CONSTRAINT -- and a trap our porous-silhouette scenes could fall into.**
   S1: "unlike in video game assets, which often use texture maps to fake geometrical details (e.g. a surface
   appears rugged but is in fact flat), ALL GEOMETRIC DETAILS IN INFINIGEN ARE REAL. This ensures accurate
   geometric ground truth."
   S3 Material Generators: "The ability to produce accurate ground-truth geometry is a key feature of our
   system. THIS PRECLUDES THE USE OF many common graphics techniques such as BUMP MAPPING AND PHONG
   INTERPOLATION. Both manipulate face normals to give the illusion of detailed geometric textures, but do so
   in a way that CANNOT BE REPRESENTED AS A MESH. Similarly, artists often rely on image textures or ALPHA
   CHANNEL MASKING to give the illusion of high res. meshes where none exist. All such shortcuts are excluded."
   Fig.4 illustrates fake vs real geometry.
   => Our truth kit's multi-hit ray-caster hits real geometry, so its truth is only as honest as the scenes.
   **P1-P6, the porous-silhouette set (foliage, hedges), is exactly where alpha-masked cards would silently
   corrupt the hidden-surface truth** -- a ray passes through an alpha hole that the renderer treats as
   transparent but the caster treats as solid, or vice versa. Worth an explicit check.

2. **COMPUTE TRUTH FROM THE MESH, NOT FROM THE RENDERER -- they say it, we already do it.**
   S4 / C.2: "Prior datasets rely on blender's built-in render-passes to obtain dense ground truth. However,
   these rendering passes are A BYPRODUCT OF THE RENDERING PIPELINE AND NOT INTENDED for training ML models.
   Specifically, they are incorrect for translucent surfaces, volumetric effects, or when motion blur, focus
   blur or sampling noise are present. We contribute OpenGL code to extract surface normals, depth,
   segmentation masks, and OCCLUSION BOUNDARIES FROM THE MESH DIRECTLY."
   Fig.K shows Blender's depth pass going noisy on water/fog/semi-transparent surfaces.
   And: "Blender does not natively produce occlusion boundaries, and WE ARE NOT AWARE OF ANY OTHER SYNTHETIC
   DATASET OR GENERATOR WHICH PROVIDES EXACT OCCLUSION BOUNDARIES."
   => Sprint 1a's exact multi-hit ray-caster is the same decision, made independently, for the same reason.

3. **THE HONEST NEGATIVE RESULT, and it is about train/test composition.** Tab.3/B: RAFT-Stereo trained on
   30K Infinigen pairs, evaluated on Middlebury (indoor, cluttered): average Bad 3.0 error 29.7 against
   SceneFlow's 25.0. **They lose on average.** Best on the one natural-object scene, Jadeplant (35.2 vs
   next-best 41.3) and Pipes (24.7); worst on Shelves (55.1) and Vintage (46.9).
   Caption: "natural objects contain VERY FEW PLANAR OR TEXTURELESS SURFACES; models trained exclusively on
   natural objects generalize less well on Middlebury's indoor scenes."
   But on their OWN held-out set (Tab.A, 400 independent scenes, no shared assets) they win handily:
   5.527 vs TartanAir 6.504, SceneFlow 7.837, and up to InStereo2K's 25.282.
   => Two lessons for us. (a) A construction tuned on a kit of geometric primitives and hedges may not
   transfer to a painted troll, and the failure will be in the surface STATISTICS (planar, textureless) not
   the geometry. (b) Winning on your own held-out set proves the model learned your distribution, not the
   world -- which is precisely what "score on the kit, then look at the picture" is guarding against.

4. **Camera selection heuristics (F.1)** -- four rules, all cheap, and we choose our poses by hand:
   height above ground sampled from a Gaussian to match a creature's eye line; a minimum distance to all
   objects; a coverage requirement that a named component be visible within a pixel range; and
   **"Standard Deviation of Depth: we compute the variance of pixel-wise depth values, and choose the
   viewpoint out of TEN RANDOM SAMPLES with the largest variance to favor more interesting content."**
   Depth variance as an automatic "is this pose interesting" score is directly usable for picking the poses
   we render our A/Bs at -- and it is close to what our reveal field already computes.

Other:
- Fig.2: emits RGB, depth, surface normals, OCCLUSION BOUNDARIES, instance segmentation, 2D/3D boxes,
  optical flow, albedo, lighting intensity, specular reflection. BSD licence, no external assets.
- Scale: 182 generators, 1070 interpretable DOF, 40,485 lines of code; average scene 16M polygons.
- **Cost: 3.5 hours wall time and ~24 GB memory per stereo 1080p pair** (2 Xeon CPUs + 1 GPU, 1000 trials).
  Procedural truth at photorealistic quality is not cheap.
- Dynamic resolution scaling: evaluate every asset so each face is < 1 px on screen; Spherical Marching Cubes
  for terrain (uniform in theta/phi, LOGARITHMIC in r) so density follows the camera.
- Surface normals are computed by fitting a plane to the LOCAL DEPTH MAP around each pixel, not by sampling
  geometry, "as [sampling] can lead to aliasing on high-frequency surfaces (e.g. grass)"; and samples that
  cannot be reached from the plane centre WITHOUT CROSSING AN OCCLUSION BOUNDARY are excluded, with planes of
  fewer than 3 samples marked invalid. That is a careful, occlusion-aware local estimator -- the same shape
  as our run/sheet logic, applied to normals.
- B: "there does not exist a real-world benchmark that evaluates depth estimation for natural scenes ... it
  is challenging to obtain 3D ground truth for real-world natural scenes, because [they] are often highly
  complex and non-static (e.g. moving tree leaves), making high-resolution laser-based 3D scanning
  impractical." So for natural scenes they fall back to qualitative evaluation on ZED-2 stereo photographs.

=== ALL 20 DISTINCT PAPERS READ BEGINNING TO END (21 files, one duplicate). ===
