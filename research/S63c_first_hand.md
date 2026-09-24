# S63c: the papers S63's literature agent read, re-read first-hand

Date: 2026-09-24. S63 Part B was written by a literature agent that read these papers through the Hugging Face arXiv
mirror; the user asked that every paper an agent read be read first-hand. Full texts fetched from the same mirror are
kept in `research/papers/s63/`. Each section: what the paper actually says that S63 relies on, what S63 got wrong or
left out, and what it means for moebius. Written paper by paper, in the order of weight in the plan.

---

## ProPainter (2309.03897, ICCV 2023) — read in full, with supplementary

**Mechanism.** Three parts (§3): recurrent flow completion (RFC) on 8× downsampled flow features with deformable
alignment; **dual-domain propagation** — image propagation by warping with completed flow, then feature propagation
with flow-guided deformable alignment; then a mask-guided sparse video Transformer (queries only in windows the mask ever
touched; keys/values from every other frame, alternating) and a decoder.

**The image-propagation rule is the part that matters to us (§3.2, Eqs. 2–4).** A hole pixel p of frame t takes the
warped pixel of frame t+1 only if (C1) the forward–backward flow consistency error ‖F_{t→t+1}(p) + F_{t+1→t}(p + F_{t→t+1}(p))‖²
is below ε = 5, (C2) p is in the hole, (C3) the source pixel in t+1 is *not* in the hole. Filled pixels leave the mask
immediately, so propagation continues across the clip in both directions. Supplementary B.1 / Fig. 10: "image
propagation has filled the majority of the masks and even entirely completed masked regions"; the network only refines.

**Evaluation.** Quantitative scores use *stationary* masks (video completion); object-removal masks are shown only
qualitatively (§4). 432×240, DAVIS 50 clips / YouTube-VOS 508. Table 1: YouTube-VOS 34.43 / 0.9735 / VFID 0.042 /
E_warp 0.974; DAVIS 34.47 / 0.9776 / 0.098 / 1.187; runtime 0.083 s/frame on a V100 (RAFT with only 5 iterations).
E2FGVI E_warp 1.013 / 1.289. Ablation (Table 3): removing image propagation costs 1.10 dB. 480p (864×480): 33.81 dB,
0.249 s/frame (Table 4). Supplementary B.2: the gain is smaller on YouTube-VOS because many of its clips "have almost
stationary scenes without motion", which limits propagation.

**Corrections to S63.**
- S63 §2a table header gives E_warp "(×10⁻²)". The paper's Table 1 caption: "E*_warp denotes E_warp (×10⁻³)". **The unit
  in S63 is wrong by 10×** (the numbers themselves are right).
- S63 does not say that the quantitative evaluation is on stationary masks, not object-removal masks — the case we care
  about is the one only shown qualitatively.
- Memory figures (8 GB / 25 GB) and the licence come from the repo, not the paper — S63 tags them [repo]; correct.

**For moebius.** ProPainter's image propagation is the 2-D version of our "copy what other frames saw": take a pixel from
another frame only where a two-way consistency test passes, never from the other frame's hole, and let filled pixels
become sources. Our 3-D version replaces the flow test with the z-test against that frame's depth; the "never from the
other frame's hole" rule (C3) is one we must keep explicitly. B.2 is the same fact as our gladiator measurement: coverage
comes from motion; a static clip gives nothing to copy.

---

## Depth Anything 3 (2511.10647) — read in full (the mirror serves the 17 Dec 2025 HTML version)

**Mechanism.** One plain DINOv2 ViT; the first ⅔ of layers attend within each image, the last ⅓ alternate between
within-view and cross-view attention over all views' tokens (§3.2). A Dual-DPT head predicts a **depth map and a per-pixel
ray map** (origin + unnormalised direction) for every input; a 3-D point is t + D·d (§3.1). Camera parameters come from
the ray map (DLT homography + RQ) or from a light camera head; known poses can be fed in as camera tokens. Trained with
teacher labels (a synthetic-data monocular teacher, RANSAC scale–shift aligned to noisy real depth, §4.2).

**Numbers that matter for our choice of model.**
- Pose AUC@3 (Table 2): ETH3D — Giant 48.4, Large 32.2, **Base 15.1, Small 8.59**; VGGT 26.3, π³ 35.2, MapAnything 19.2.
  HiRoom — Giant 80.3, Large 58.7, **Base 19.0**; VGGT 49.1. ScanNet++ — Giant 85.0, Large 60.2, **Base 25.1**; VGGT 62.6.
- Geometry F1 without poses (Table 3): ETH3D — Giant 79.0, Large 65.8, Base 49.5, Small 41.6; VGGT 57.2.
- Speed (Table 8, A100, 504×336, 32 images): Large 78 FPS, Base 127 FPS; up to ~1 500 images (Large) on 80 GB.
- Monocular δ1 (Table 10, mono student vs DA2): ETH3D 98.8 vs 86.5, SINTEL 82.3 vs 77.2.
- The monocular models predict **depth, not disparity** (§4.3: "our student predicts depth maps, whereas DA2 predicts
  disparity"); the teacher predicts exponential depth. Our `b_prepare` inverts DA3-Mono output to get disparity — correct.
- Dynamic scenes are future work (§8); the pose benchmark's ground truth itself masks dynamic objects (Fig. 5 caption).

**Corrections to S63.**
- S63 §2b: "It beats VGGT by 44.3 % on pose accuracy and 25.1 % on geometry [abs]." This version's abstract says
  **35.7 % pose and 23.6 % geometry**; §7.1's text says 25.1 % geometry. The 44.3 % is not in this version.
- S63 §8(a) step 1 recommends "DA3-Base/Small if licensing matters". The paper shows **Base and Small are far weaker at
  poses** — Base's AUC@3 is below VGGT on every dataset and roughly ⅓ to ½ of Large's. For a licence-safe pose estimate,
  **VGGT-1B-Commercial** (VGGT's numbers above) is the stronger choice than DA3-Base; DA3-Large/Giant remain best if the
  CC BY-NC licence is acceptable. (Licences themselves are from the repo, as S63 says; the paper does not state them.)

**For moebius.** For the static-world path, poses and consistent depth come from a multi-view model run with people
masked out (the paper's own ground truth does the same). The size matters more for poses than for depth (§7.1: pose
"scales more strongly than depth estimation"), so a small model is a false economy exactly where our copy step needs
sub-pixel reprojection.

---

## Video Depth Anything (2501.12375, CVPR 2025) — read in full (v3 HTML; result tables did not survive the conversion)

**Mechanism.** The Depth Anything **V2** encoder, frozen; the DPT head gets four temporal self-attention layers (attention
along time at each spatial position, at the two lowest resolutions and before the last two fusion layers; supplementary
§4). Loss: scale–shift-invariant spatial loss + a **temporal gradient matching** loss — the frame-to-frame change of
predicted depth at the same pixel should match the ground truth's change, computed only where the true change is below
0.05 (§3.2, Eq. 3). Output is **affine-invariant depth with one scale and shift shared across the whole video** (§3; the
evaluation aligns inverse depth once per video, supplementary §5). Long videos: 32-frame windows = 22 new + 8 overlap +
2 key frames taken every 12 frames back; overlap blended linearly (§3.3, Fig. 3); plain overlap alignment drifts in scale
over minutes (Fig. 7). Trained on 0.55 M synthetic video frames + 0.18 M stereo-labelled wild frames + 0.62 M unlabeled
images (supplementary §4). Temporal stability is measured by TAE, a reprojection AbsRel between consecutive frames
(Eq. 5).

**Evidence I could not check.** Tables 1–7 lost their contents in the mirror's conversion; the text states SOTA on four of
five datasets for accuracy and all five for consistency, ~10 % δ1 over others on KITTI/ScanNet/Bonn, and latency under
10 ms/frame for VDA-S on an A100 at 518×518 (§4.2). Supplementary Fig. 8: DepthCrafter and Depth Any Video "exhibit poor
performance on oil paintings"; VDA matches DAv2 on still images.

**Corrections / additions to S63.** S63 §2b is right on what it says (minutes-long video, 30 fps small model, TAE).
Missing and important for us:
- **VDA is DAv2-based.** Our stills use DA3-Mono, which the DA3 paper reports far ahead of DAv2 on ETH3D δ1 (98.8 vs
  86.5). Using VDA for video means a different depth family from our stills — the layer geometry would change character
  between a still and a video of the same scene.
- **One affine for the whole clip** is exactly what the layers need (a per-frame affine would make plates breathe); but
  it is relative depth, so metric scale and camera poses still come from elsewhere (the paper's own point-cloud demo aligns
  the first frame to metric depth from MoGe, supplementary §6).

**For moebius.** For the moving-person layer, VDA's shared-affine, temporally smoothed depth is the right kind of signal.
For the static world, a multi-view model (DA3-Large/Giant, or VGGT-Commercial) gives poses and depth together. A test worth
running on our synthetic video: DA3-Mono per frame vs VDA vs DA3 multi-view, scored against the truth depth with TAE and
with our own plate-breathing measure.

---

## MegaSaM (2412.04463, CVPR 2025) — read in full (supplementary not in the mirror)

**Mechanism.** DROID-SLAM's learned flow + differentiable bundle adjustment (§3.1), with three changes (§3.2): disparity
initialised from Depth Anything (relative) aligned by UniDepth (metric, which also gives the focal length); an
**object-movement probability map** multiplied into the BA weights so moving things do not drive the camera; and an
**uncertainty-aware global BA**: from the diagonal of the BA Hessian it measures whether disparity and focal length are
*observable* from the video, turns the monocular-depth regulariser on only when disparity is unobservable (little
parallax), and freezes focal length when it is unobservable (Eq. 10, §3.2.2). Optional last stage: consistent video depth
by optimising per-frame disparity and uncertainty with cameras fixed (§3.3).

**Numbers.** Camera ATE (Sintel, calibrated): 0.018 vs CasualSAM 0.036, LEAP-VO 0.041 (Table 1); DyCheck 0.020 vs ACE-Zero
0.062 (Table 2); in-the-wild 0.004 vs LEAP-VO 0.016 (Table 3). Tracking time ≈ 0.7–1.0 s per frame on an A100 (tables'
"Time" = total / frames). Video depth abs-rel: Sintel 0.21 vs DepthCrafter 0.27, DAv2 0.37; DyCheck 0.11 vs 0.20
(Table 4). Depth optimisation 1.3 FPS at 336×144 (§4, implementation). Training: 8 × A100-80 GB, ~4 days.
Ablation (Table 5): without the movement map, RTE 0.127 vs 0.008.

**Corrections to S63.** S63 §2b is accurate ("robust poses and depth on casual dynamic videos, including videos with
little parallax [abs]"; "about 1.3 fps at 336×144 [paper]"). Add: the 1.3 FPS figure is the *optional* depth stage; camera
tracking is ~1 s/frame on an A100 — neither is CPU-practical here. Licence is from the repo, not the paper.

**For moebius.**
- The **observability test** is what our video pipeline needs to choose its branch: when disparity is unobservable from
  the clip (tripod, rotation), the static background cannot be reconstructed from parallax and the copy step falls back
  to the object-motion case (the gladiator clip). The Hessian-diagonal median is a principled, data-derived switch — no
  hand-set "is the camera moving" threshold.
- The movement map is the same idea as masking people before pose estimation, learned.

---

## GEN3C (2503.03751, CVPR 2025) — read in full, with supplement

**Mechanism.** A "3D cache" = an L×V array of point clouds, one per input frame and view, each from that frame's
monocular depth (DAv2), with poses from DROID-SLAM when not given (§4.1). For the target camera path each cache element is
**rendered separately** to an RGB video plus a disocclusion mask (§4.2); each rendered video's latent (masked by
multiplication, not a mask channel — a mask channel generalised worse, suppl. C.1) passes the first layer of an SVD
image-to-video model and the views are **max-pooled** (Eqs. 2–3). The model is fine-tuned to "translate imperfectly
rendered video into a high-quality video, correcting any artifacts … and filling in missing information" (§1). Long
videos: chunks with one-frame overlap; each generated frame's DAv2 depth is scale/shift-aligned to the cache's rendered
depth and appended (§4.5, suppl. A.1). 14 frames ≈ 30 s on an A100; 32 A100 × 4 days training.

**Numbers.** Single view → video (Table 1): RE10K PSNR 19.88 / LPIPS 0.20 / TSED 0.914; Tanks-and-Temples 18.66 / 0.20.
Two views (Table 2): RE10K 24.08 interpolation / 21.56 extrapolation. **Explicit 3-D fusion of the two point clouds
instead of network fusion: 21.81 / 19.87** (Table 6) — the paper's reason: fused clouds suffer "severe artifacts in
misalignment regions" when per-view depths disagree or lighting differs (§5.6, Fig. 10). Depth-noise robustness
(Table 5): PSNR 24.08 → 22.39 at 3 % noise, 18.52 at 30 %. Monocular dynamic NVS on Kubric (Table 4): 19.41 PSNR.
Limitation (§6): dynamic content needs a pre-generated video for the motion.

**Corrections / additions to S63.** S63 §2c/§5 are accurate as far as they go. Two things S63 misses, both important to
our plan:
1. **GEN3C deliberately does not fuse its point clouds in 3-D**; per-view caches are fused by the network, because
   explicit fusion with monocular depth misaligns (−2.3 dB). Our "world-anchored canvas" *is* explicit fusion. It will
   meet exactly this misalignment unless the per-frame depths are made consistent first (multi-view DA3 / MegaSaM depth,
   not per-frame monocular), and unless the copy step's z-test tolerance and robust median absorb the remainder.
2. **GEN3C re-renders every pixel through the VAE**, visible ones included — its "focus on unobserved regions" is a
   tendency of the model, not a guarantee that observed pixels pass through unchanged. For the window, observed pixels
   must be copied exactly, not regenerated.

**For moebius.** Confirms copy-then-generate as the published direction, and hands us a concrete test: on the synthetic
shots, fuse plates across frames explicitly with (a) per-frame DA3-Mono depth and (b) multi-view-consistent depth, and
measure the misalignment against truth. GEN3C's Table 6 says (a) will fail visibly.

---

## Geometric Reciprocity (2607.05354, July 2026) — read in full (v1 HTML; result tables did not survive the conversion)

**The theorem (§3.4).** Under nearest-neighbour depth-image-based rendering, the disocclusion mask for synthesising a
target view R from a source L equals the set of R's pixels that are **lost** when R is warped to L — lost by leaving the
frame (Eq. 18) or by losing the z-test to a nearer pixel landing on the same spot (Eqs. 19–20). The proof removes the
cycle step by step: inpainted content in the intermediate view never maps back; disparity is carried with colour so need
not be re-estimated; and every pixel that survives the round trip returns to exactly where it started (Eq. 17). So any
monocular image, with its own depth, yields a disocclusion mask of exactly the test-time shape **and its own true pixels
as ground truth** (§3.4.2–3.4.3). Soft (bilinear) warping keeps the relation at the level of splatted "renderers", with a
small train–test gap (appendix A9). Limitations (A6): rectified stereo, depth quality at discontinuities, transparent and
reflective surfaces.

**Use.** Fine-tuned LaMa (images) and ProPainter (video) on masks computed this way from ImageNet (1.28 M images) and
Kinetics-400 (240 K videos), depth from DAv2-Large, disparity rescaled to [0, 0.1·W] for training and [0, 0.06·W] for
evaluation (A2); tested on DAVIS-GRT (50 clips, 3 455 frames) and Inria 3DMovie. Stated: best on all metrics, 0.05 s
(image) and 0.24 s (video) per frame at 512² (§4.2); GRT data improves LaMa, SD 1.5/2.1/XL inpainting, ProPainter and
StereoCrafter alike (§4.4). **The numbers themselves are not in the mirror's tables** and cannot be checked from here.
Appendix A7 / Fig. A2: SDXL inpainting "handles large contiguous masks well … but struggles with thin scattered
disocclusion masks along object boundaries". Code, masks and weights promised under Apache-2.0 (A1).

**Corrections to S63.** S63 §2c states the theorem and the ProPainter fine-tune correctly. It misses the two points that
matter most for us:
1. **A ground-truth protocol for our fills on real pictures.** Take a real picture R with its depth; choose a head offset
   inside our envelope; warp R to the virtual eye L (nearest-neighbour, z-buffered). The pixels R loses are exactly the
   background our plates must reconstruct when the viewer moves from L back to R. Fill L's own (unscored) holes with
   anything, build our layers from L, render at R's eye, and score against R **inside the lost set only**. This scores the
   plate fill on the troll, the Vermeer, the paintings and the photos — not only on synthetic scenes — with the mask shape
   the window actually produces.
2. **General inpainters are weak on thin boundary slivers**, and fine-tuning LaMa on masks of that shape helps every
   backbone they tried. Our fills are exactly such slivers; a LaMa fine-tuned on GRT masks (weights promised, Apache-2.0)
   is a cheap candidate painter that runs on CPU.

**For moebius.** Item 1 is the most useful thing in this batch of papers for the stills pipeline: it turns every picture
we own into a test case with ground truth. It should be built next to the synthetic-video stability test.

---

## CogNVS (2507.12646, July 2025) — read in full (mirror; the numeric tables did not survive)

**Method (§3).** Three stages. (1) Reconstruct the clip with MegaSaM (camera + per-frame depth). (2) Render the
co-visible pixels into the novel view; what is left is the hole. (3) Inpaint with CogVideoX-5B fine-tuned as a video
inpainter — the model also sees and may **re-write the visible pixels** (it corrects small reconstruction errors), so the
output is a re-rendered clip, not a fill pasted into a fixed frame. Then **test-time finetuning** (200–400 steps) on the
test clip itself: self-supervised pairs are made by sending the clip along random trajectories (elevation ±15°, azimuth
±30°, radius ±0.15), rendering back, and asking the model to restore the original frames from the resulting holes.

**Cost (stated).** About 5 minutes per 49-frame 480×720 clip on one A6000 Ada, including test-time finetuning.
Pretraining: 8×A6000 for about 3 days on ~10 k videos (SA-V, TAO, YouTube-VOS, DAVIS).

**Ablations (stated in text).** No pretraining: about −5 dB PSNR. No test-time finetuning: about −3 dB. MegaSaM instead of
ground-truth reconstruction: about −3 dB and +45 FID — reconstruction error is as large a loss as the painter. Masks made
by the round-trip render (they call them "structured") beat tube and random masks. **Stacking the static background
across the whole clip** before inpainting adds about +3 dB on DyCheck. Injecting noise at mask edges reduces smearing.

**Checking S63.** S63 cites CogNVS for "test-time 4D optimisation takes on the order of hours"; the paper says this of
the optimisation baselines it compares against, so the citation is accurate. S63 does not mention the two ablations that
bear on us.

**For moebius.**
1. **Background stacking is our static canvas.** Their +3 dB from gathering the static background across the whole clip
   before painting is the same idea as S63's "copy what was seen anywhere first, paint only the never-seen rest", and it
   is measured.
2. **Round-trip masks beat generic masks** for training and for test-time adaptation — the same finding as Geometric
   Reciprocity, from a different group.
3. **Reconstruction error costs as much as the painter.** Our depth and camera must be judged before the painter is.
4. CogVideoX-5B at 5 min per 49 frames on a 48 GB card does not fit our budget as the default path; it is a candidate
   only for the "never seen and changing" class.

---

## MiniMax-Remover (2505.24873, May 2025) — read in full (mirror; Table 2 and 3 cells are empty)

**Method.** Wan2.1-1.3B with the text encoder and cross-attention removed; input is noisy latent + masked-video latent
+ mask latent (48 channels). Stage 1 learns two tokens: a *positive* token trained with **masks borrowed from other
videos** (so the hole never has the shape of what is under it, and the model learns to fill from the surroundings), and a
*negative* token trained with **tight masks on real objects** (so it learns to regrow the object from the mask shape);
CFG from negative to positive then pushes away from regrowth. Stage 2 distils to 6 steps with no CFG on 10 k
hand-picked stage-1 successes (of 17 k), training against "bad" noise — noise nudged by one gradient-sign step towards
reproducing the *original* object (Eq. 9–11). 8×A800, about two days in total.

**The finding that matters to us (App. 7).** "The most challenging issue in object removal is the undesired
regeneration problem, where the model tends to regenerate objects in the masked region that share a similar shape to
the mask itself." That is exactly the starwatcher legs: our hole *is* the leg silhouette, and SD grows something
leg-shaped in it. Their cure is training; the inference-side reading for us is that the painter should not be shown a
hole whose outline is the occluder's outline — see the note at the end of this section.

**Cost (stated).** 24 s per 81-frame 480p clip on an RTX 4090, 14 GB peak (DiT 8 GB, VAE decode 6 GB); most of the time
is in the VAE (§11). Table 1: 0.18 s latency and 8.2 GB for 33 frames at 360p on an A800.

**Checking S63's table.**
- The PSNR/SSIM columns are **background preservation** (§4: "We evaluate background preservation using SSIM and
  PSNR") — they score the pixels *outside* the hole. They say nothing about fill quality; DAVIS removal has no ground
  truth inside the hole. S63 labels the column "DAVIS PSNR" without saying so. Correction recorded.
- The text gives DAVIS SSIM 0.9847 / PSNR 36.66 and success 91.11 % (DAVIS) / 81 % (Pexels); S63's table has 36.56 and
  82.2 %. The table cells are empty in the mirror, so the difference (probably a different step count row) cannot be
  settled from here. S63 also gives MiniMax TC as 0.9770 in the table and 0.9776 in the caveat above it.
- "Success" is GPT-o3's yes/no; "VQ" is GPT-o3's 1–10 score (6.48 vs 5.71). The user study is 64 % vs 42.4 % (DAVIS).
- The latency column is per clip setting in Table 1 (33 frames, 360p, A800), not measured on one machine for S63's
  "per frame" reading; treat as order of magnitude only.
- Licence: S63 says no licence file found; not checkable from the paper.

**For moebius.**
1. **Mask shape invites regrowth.** A hole cut exactly to the occluder's silhouette is the hardest case for a diffusion
   painter — the negative-token training shows the model *learns* that a tight silhouette mask means "an object of this
   shape goes here". This is a direct lead on the starwatcher leg fills (hallucinated object). Things we can test without
   training, all automatic: (a) give the painter a mask that is not the silhouette — the union of the silhouette with its
   dilation along the reveal direction only, or the reveal band rather than the whole occluder; (b) pre-fill the hole
   with our plane wash and let SD run img2img at partial strength inside it (the shape is then carried by the wash, not
   by the mask); (c) LaMa first, SD refine (the `--painter lama+sd` arm already exists). The legs comparison running now
   tests (c); (a) and (b) are the next arms.
2. Their PSNR is not a fill score; our own tests must score inside the hole against truth (kit, GRT protocol).

---

## DiffuEraser (2501.10018, Jan 2025, technical report) — read in full

**Method.** SD 1.5 inpainting UNet + BrushNet branch (masked image, mask, noisy latent) + AnimateDiff-style temporal
attention after self- and cross-attention; the output is blended into the input with a blurred mask. Three sub-problems,
named the way S63 names them: propagate *known* pixels (seen in some frame), generate *unknown* ones (never seen), keep
the result consistent. **Prior injection (§3.2):** ProPainter fills the clip first; that fill is DDIM-inverted and added
into the starting noisy latent. Stated effect: it removes the "meaningless noisy artifacts" (their Fig. 2, sea above the
horizon rendered as noise) and "acts as a weak condition to suppress the generation of unwanted objects"; ProPainter's
blur and mosaic are refined away. **Long clips (§3.3):** 22-frame windows; overlap alone does not fix seams, so they
(i) stagger the window start between even and odd denoising steps, and (ii) run a *pre-inference* pass on frames sampled
across the whole video, then use it to guide frame-by-frame inference; the same pre-propagation is done for the
ProPainter prior. They say plainly that the first and last frames still cannot be made fully consistent.

**Training / cost.** Panda-70M, 3.18 M clips, random masks; 4×A100 then 8×A100. With PCM, two steps: a 10 s 540p 25 fps
video in about 200 s on an L20.

**Evidence.** The report has **no quantitative table** — only side-by-side figures against ProPainter. The numbers S63
quotes for DiffuEraser come from other papers (MiniMax's Table 1/2, FloED's Table) and from the repo, which is fine, but
there is no first-party metric.

**Checking S63.** Mechanism and "ProPainter prior … to suppress hallucinations" are accurate. "Overlap between its
22-frame clips" is incomplete: the paper says overlap does not solve it and uses staggered denoising plus a whole-video
pre-inference. The licence point (ProPainter prior non-commercial) is from the repo and not checkable here.

**For moebius.**
1. **Initialise the painter from our own wash, not from noise.** Their prior injection is exactly the arm (b) proposed
   under MiniMax above: DDIM-invert (or noise to partial strength) the plate's plane wash inside the hole and let SD
   denoise from there. Their stated effect — fewer invented objects, no noise-like fills — is the starwatcher symptom.
2. **Keyframes first, then the rest guided by them** is their answer to long clips, and the same shape as S63's "paint
   the static canvas once, carry it".

---

## PROVE (2605.14534, May 2026, Xiaomi) — read in full (tables survived)

**What it shows (§3, Table 2).** Three biases in how removal/fill is scored:
- *Copy-paste:* full-reference metrics over the whole frame reward keeping the background; computed on the background
  only (as MiniMax does) they can score a failed removal near-perfectly. Background-only PSNR/SSIM/LPIPS correlate
  **negatively** with human rankings (Kendall τ −0.21 to −0.33 on average).
- *Regression to the mean:* fewer diffusion steps give blurrier fills and *better* PSNR/SSIM (their Fig. 2, MiniMax on
  ROSE-Bench).
- *Blur is clean:* the no-reference metrics ReMOVE and CFD score a fill *higher* as it is blurred more (Fig. 3; RORD
  Table 4: they prefer the blurred copy over the original in 40–51 % of cases).
- *Global temporal metrics are blind:* TC (CLIP cosine of adjacent frames) and TF (mean abs frame difference) do not
  fall — sometimes rise — as frames are dropped or replaced (Fig. 5).

Among full-reference scores, **mask-only LPIPS** is the best aligned with people (τ 0.52 avg; m-SSIM 0.43; m-PSNR 0.29).

**RC-S / RC-T (§4).** Crop each hole's box enlarged by a third; DINOv2 features; slide a window (a quarter of the feature
map) and take squared MMD (Gaussian kernel, "size 10") between features inside and outside the hole (RC-S), or between
the same *intersection* of the two frames' holes in adjacent frames (RC-T). Reported as exp(−RC-S/3). RC-S τ 0.59 avg
against 20 people's Borda rankings, best on 5 of 6 benchmarks; RC-T is validated only by monotone response to synthetic
corruption, not by people (they say ranking temporal artefacts by hand is unreliable). Cost on a 4090 at 448²:
RC-S 135 ms/frame, RC-T 184 ms/frame pair. Ablations: no window, cosine instead of MMD, or SAM/DINOv3 features all lose.

**Benchmark.** PROVE-M: 80 real tripod pairs (with / without the object, within two minutes) at 81 frames 1080p, with
**2-D Ken Burns motion** (crop, scale, translate) added — not parallax. PROVE-H: 100 hard videos, no ground truth.

**Checking S63.** S63's one-paragraph summary of PROVE is accurate. Two limits it does not state: RC-T compares
adjacent frames **in image coordinates, with no motion compensation** (union crop, intersection mask) — it measures
distribution drift, so it tolerates small shifts but cannot say whether a fill *moves with the scene*; and PROVE-M's
camera motion is a 2-D transform of a tripod shot, so none of its clips has disocclusion from parallax.

**For moebius (scoring rules for our own tests).**
1. **Never score a fill by PSNR/SSIM over the frame or the background.** Inside the hole against truth: masked LPIPS
   first, masked PSNR only as a secondary number. (Our kit and the GRT protocol give truth inside the hole.)
2. **Blur must not win.** Any no-reference score we use on real pictures must be checked against a blurred copy of the
   same fill — RC-S passes that check, ReMOVE/CFD do not. Our LaMa wash is exactly the blurry case these metrics
   flatter; the user's screen stays the judge.
3. **Temporal stability in moving shots needs geometry, not RC-T.** With exact truth (camera + depth per frame) we can
   warp frame t's fill to t+1 and difference it inside the shared hole — the pixel-true version of RC-T. Use RC-T only
   where there is no truth.
