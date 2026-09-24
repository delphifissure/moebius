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

---

## StereoCrafter (2409.07447, Sept 2024, Tencent) — read in full

**Method.** Video depth (DepthCrafter preferred over DAv2 for temporal stability) → forward splat left→right → occlusion
mask = target pixels nothing landed on → SVD fine-tuned as a stereo inpainter (condition = warped frames instead of an
image; one extra zero-initialised mask channel, 8→9). Only the spatial UNet layers are fine-tuned (8×A100, 26 k
iterations, 25×576×1024 clips, frame stride 1–6). **Long clips:** during training the first n frames (random 0…N) are
replaced by ground truth; at inference the last frames of the previous window (n = 3 in the ablation) are fed in with
the next window. **High resolution:** spatial tiles, blended linearly in latent space across the overlap.

**The splat (§3.2).** Each source pixel is splatted bilinearly to its four nearest target pixels; overlaps are resolved by
a **soft** weight w = √2^disp, so a pixel 2 px nearer counts twice as much, not infinitely more. That is a soft z-buffer:
at small disparity steps foreground and background colours are *blended*, not ordered. (Our warp uses a hard z-test.)

**Data.** Stereo films/videos cut by shot, disparity from a video stereo matcher after shifting the pair so all
disparities are ≤ 0, warped by the same splat, kept only if warped-left vs real-right PSNR > 25 dB: ~180 k clips,
~25 M frames.

**Evidence.** **No quantitative table.** Comparisons are figures only (Deep3D, Owl3D, Immersity; FuseFormer, E2FGVI,
ProPainter "blurry"), plus a stereo matcher run on the result to show left/right consistency. Ablations (overlap, tiling)
are figures.

**Checking S63.** Mechanism, 25-frame SVD windows, auto-regressive + tiled, the real-time GPU splat, and the quote about
dynamic reconstruction ("cannot address the occlusion that does not appear in the neighboring frames") are all accurate.
S63 does not say the paper has no numbers, and it does not mention the soft z-buffer.

**For moebius.**
1. The overlap-window scheme (feed the last three filled frames into the next window) is the cheap version of
   "copy what was already filled"; with a world-anchored canvas we get it exactly instead of approximately.
2. Their soft splat weight is a design choice we should not copy: it trades crisp occlusion for fewer cracks. Our hard
   z-test plus explicit hole mask is the right call for layers that must stay clean.
3. Their training-data recipe (real stereo pairs → warp → mask → the other eye is truth, filtered by warp PSNR) is the
   stereo twin of the GRT protocol; we already have truth from the kit, so we do not need it.

---

## SVG — stereo video by denoising a frame matrix (2407.00367, ICLR 2025) — read in full (Table 1–2 cells missing)

**Method.** Generate (or take) the left video; video depth (DAv2-class, flow-aligned and Gaussian-smoothed in time;
normalised to 1–10) → warp into **8 evenly spaced views** along a 0.08 baseline (MPI-style projection to remove isolated
pixels and cracks) → a matrix of views × time. Inpainting is RePaint-style with a frozen text-to-video model
(Zeroscope): at each noise level the known pixels are re-noised from the warp and pasted outside the mask; rows (fixed
time, sweeping view) and columns (fixed view, sweeping time) are denoised **alternately**, with noise added back between
resamplings — 8 resamplings per step for steps 50→25, then 4 and right view only. DDPM, 50 steps. **16 frames** only
(Zeroscope's limit). One A6000; no runtime is given, but 9 views × 16 frames × 8 resamplings × 50 steps is heavy.

**Disocclusion boundary re-injection (§3.3).** A latent model sees the black hole through its VAE, and the 8× encoder
spreads the black past the latent mask, corrupting the "known" latents along the boundary. Fix: at each step decode the
current x̂₀, paste the warped pixels back outside the hole, re-encode, and use that as the new known latent.

**Evidence.** A 20-person VR user study (7-point Likert, 5 methods; table cells lost in the mirror, text says ours best
on all four axes, p < 0.001) and a left/right CLIP similarity: **96.44** full, **95.81** without the frame matrix,
**95.60** without re-injection. Baselines: ProPainter, E2FGVI (blurry), RoDynRF, DynIBaR (pose failures). Fails beyond a
20 cm baseline at their depth normalisation; thin structures limited by depth.

**Checking S63.** S63 calls this "the one method that makes a fill consistent across both time and viewpoint, which is
what a head-tracked window needs". **Correction:** the frame matrix *encourages* consistency — views are tied only by the
denoiser's smoothness along the row, not by geometry; nothing reprojects one view's fill into another. The measured
benefit is 0.6 CLIP points. It covers a 2-view baseline with 7 in-between views and 16 frames; our window needs a
continuous 2-D range of views. For static content a world-anchored layer painted once is consistent across every view
*by construction* and costs one paint; SVG's scheme is only a candidate for the "never seen and changing" class, and even
there it is heavy.

**For moebius.**
1. **Never hand a latent painter a black hole.** Their re-injection result says the VAE smears the hole's black into the
   known ring. Our SD path feeds `plane_plate_color.png`, where the hole already holds our wash — check that this is so
   for every class we send (plate 2, sky, carriers), and that no mask-black survives into the image we encode.
2. The alternating row/column denoising is a neat general trick for coupling two axes with a 1-D video model; park it
   for the dynamic-content class.

---

## CoDeF (2308.07926, CVPR 2024) — read in full

**Method.** A 2-D hash-grid canonical image C(x, y) and a 3-D hash-grid deformation field D(x, y, t) → canonical
position; colour = C(D(x, y, t)), fitted by L2 to the frames. Regularisers: **annealed** hash levels on the deformation
(coarse first, fine added between steps 4 000 and 8 000 of 10 000; without it the canonical image grows "multiple
hands"), and a flow-consistency loss on RAFT flow where forward–backward agrees. For big occlusions, optional *grouped*
fields per SAM-track segment, with an extra loss that trains each group's canonical *outside* its mask to the frame colour
— because unsupervised hash cells otherwise fill with "random and unstructured patterns". Image tools (ControlNet, SAM,
R-ESRGAN) run on the canonical image; the result is warped to every frame.

**Cost / evidence (stated).** About 5 minutes for 100 frames on one A6000 (1–10 min depending on clip); LNA "more than
10 hours". Reconstruction PSNR **+4.4 dB** over LNA on unnamed "collected videos"; positional encoding instead of the 3-D
hash: −3.1 dB. Everything else is figures and project-page videos — the authors say there is no accurate metric.
Limitations they name: per-scene optimisation, **extreme viewpoint changes**, large non-rigid deformation.

**Checking S63.** Accurate: mechanism, ~300 s vs >10 h, "cannot un-occlude anything". S63 says "large camera translation
… which CoDeF names as a known flaw of prior atlases"; CoDeF actually names *distorted atlases* as the prior flaw and
*extreme viewpoint change* as its own open problem — same substance, attribution loosened. S63 omits that CoDeF gives
only one number against LNA.

**For moebius.** CoDeF confirms the "edit the canonical image once, warp everywhere" pattern and its price: the canonical
image is only as natural as the deformation is smooth, and regions never observed are *noise*, not a fill. It has no
depth, so it does not help a head-tracked window. Our world-anchored layer is the 3-D version; the useful borrowing is
their trick for unobserved cells — supervise them with something (for us: the plane wash) so a painter never sees
garbage there.

---

## OmnimatteRF (2309.07749, ICCV 2023) — read in full (tables survived)

**Method.** Omnimatte's 2-D RGBA foreground layers (a U-Net per object, fed a coarse mask, RAFT flow and an (x, y, t)
encoding) over a **static TensoRF radiance field** for the background, rendered from each frame's pose (COLMAP, or
RoDynRF poses where COLMAP fails). Losses: reconstruction, Omnimatte's alpha/flow terms, TV on the field, a
scale-invariant MiDaS depth loss (needed when the camera only rotates; it breeds floaters, so a Mip-NeRF-360 distortion
loss is added). **Masked retraining (§3.3):** joint training lets the field model shadows as holes/floaters that
correlate with view direction; so after joint training the field is retrained *from scratch* on pixels where the
foreground alpha is low (~30 min).

**What it does not do.** Nothing fills background that was never seen: the field is only trained on observed pixels,
and the background is evaluated only **at the input views** ("novel view synthesis is not the focus"). Foreground
layers do not hallucinate their own occluded parts (limitation 3). A region under a shadow in nearly every frame keeps
the shadow (limitation 1); unrelated motion (trees, cars) lands in the foreground layer (limitation 2); results depend on
the random seed (App. B, seed 3).

**Evidence.** Background PSNR on Kubric **39.1–43.6 dB** (D²NeRF 33.3–38.8, Omnimatte 21.2–31.2) and on their new
**Movies** set **27.7–39.1 dB** (Omnimatte 19.1–23.9, LNA 18.8–26.5; D²NeRF fails on 2 of 5). Cost on one RTX 3090 at
480×270: 3.8 h training, 3.5 s per rendered image (Omnimatte 2.7 h / 2.5 s; LNA 8.5 h). Masks: Mask R-CNN picks or
After-Effects Roto Brush, ~10 min of manual work per 200 frames.

**Checking S63.** S63's summary (2-D foreground + 3-D radiance-field background, masked retraining, static background,
known or estimated poses) is accurate. S63's Omnimatte line "3–8.5 h per video and ~2.5 s per frame" (cited via
OmnimatteZero) blends two rows of this paper's Table A2: Omnimatte is 2.7 h and 2.5 s/frame; 8.5 h is LNA.

**For moebius.**
1. This is the "copy what was seen anywhere" half of S63's plan, done with a radiance field; it confirms that a static
   3-D background gathered over the clip is clean where observed, and says nothing about the never-seen rest — that is
   still our plate fill.
2. **Masked retraining is our rule too:** build the static layer only from pixels the foreground does *not* cover, after
   the foreground is known. Their failure (shadow baked where it is present in nearly every frame) is the lighting case
   S63 assigns to a per-frame gain.
3. **The Movies dataset is a ready truth set for our video work:** Blender Studio clips re-rendered with and without the
   actors, with camera poses, released by the authors. It complements our ray-cast shots with real production lighting
   and non-rigid actors — the Blender-realism check we planned, already rendered. (Licence to be checked before use.)

---

## Generative Omnimatte (2411.16683, CVPR 2025) — read in full (main Table 1 cells lost; appendix tables survived)

**Method.** Stage 1: **Casper**, Lumiere's inpainting model fully fine-tuned (20 k iterations, batch 32) to remove an
object *and its effects*. Condition = input video + **trimask** (0 remove, 1 keep, 0.5 "background that may hold effects")
+ noise; unlike ordinary inpainting the RGB inside the removal region is **kept** in the condition (after ObjectDrop), so
the model can tie a shadow outside the mask to the object inside it. One clean-plate run plus one "solo" run per object.
Stage 2: per object, optimise RGB + alpha (U-Net for alpha, sparsity L0/L1, mask loss decayed) so that
alpha·fg + (1−alpha)·clean-plate = solo video; the clean plate is fixed. Layer order for recomposition from DepthCrafter.
Training data: 31 omnimatte results, 15 tripod web videos (Ken-Burns motion added), 569 Kubric scenes, 1024 object-paste
clips — about half real, half synthetic.

**Resolution and cost.** Casper runs at the **Lumiere base resolution, 128 px high (e.g. 224×128)**, 80 frames, 256 DDPM
steps, no CFG — ~12 min on a 96 GB TPU; Lumiere SSR to 640×384 (~15 min) *hallucinates high-frequency detail*, so alpha
is bootstrapped at 128 px and detail is transferred back only where layers are fully opaque. Whole clip, 3 objects:
35–49 min. A CogVideoX re-fine-tune: 66 s for 85 frames at 384×672 on an A100 (50 DDIM steps).

**Evidence.** On OmnimatteRF's 10 synthetic scenes (5 Kubric + 5 Movies): **38.38 dB / LPIPS 0.020** with all data
(Table 3); Omnimatte-only data 37.06. For scale, OmnimatteRF's own per-scene numbers average ≈ 37.4 dB — the generative
method is about **1 dB** better on average on backgrounds that are mostly *observed*; its advantage is qualitative, on
real clips where pose/depth fail and on content never seen (the occluded horse). Limitations: deformation effects
(bending poles, trampolines), many similar objects, unrelated background motion assigned to an object; fixed seed 0.

**Checking S63.** Accurate: Casper/trimask, "no static scene, poses or depth", 12 min / 80 frames at 128 px then 640×384,
the limitations list. Not stated in S63: the 128-px working resolution means every fine detail in the fill comes from an
upsampler the authors themselves say invents detail; and the quantitative margin over OmnimatteRF is about 1 dB.

**For moebius.**
1. **Amodal completion by removing the occluder (App. A, Fig. 14):** to recover a dog hidden behind poles they mark the
   *poles* for removal and let the model complete the dog in the solo video. That is the middle-surface class (a leg
   behind a leg, the starwatcher's hidden body) posed as a removal problem — useful framing for the "never seen and
   changing" class.
2. **Keeping the occluder's pixels visible to the model** helps *effect* removal (shadows follow the object). For our
   disocclusion fills the occluder is not inside the hole, and Diffusion-VAS/our S62 finding says keep it out of context;
   the two are consistent once you separate "remove an object and its effects" from "fill behind an object that stays".
3. At 128 px the model is a planner, not a painter; any use for us would be as a low-resolution prior with our own
   texture carried from observed pixels.

---

## OmnimatteZero (2503.18033, SIGGRAPH Asia 2025) — read in full (Table 1 survived)

**Method.** Training-free, inside a frozen video DiT (LTX-Video or Wan2.1). **Temporal Attention Guidance:** TAP-Net
tracks each masked point to other frames; tracks landing in the mask are discarded; the attention from the masked token to
its background correspondences is set to the mean attention among those correspondences — i.e. the model is steered to
*copy what other frames saw*. **Spatial Attention Guidance** does the same within the frame for points with no
correspondence. Effects (shadows, reflections) are found from the object's self-attention after one noise/denoise step,
Otsu-thresholded into an enlarged mask. Foreground layer = latent(object+bg) − latent(bg), with the object's own pixels
pasted back from the input; alpha from the soft attention mask decoded by the VAE's upsampling path.

**Evidence (Table 1, background reconstruction on OmnimatteRF's Movies + Kubric, A100).**

| Method | Movies PSNR | Kubric PSNR | Avg PSNR | s/frame |
|---|---|---|---|---|
| ProPainter | 27.44 | 34.67 | 31.06 | 0.083 |
| DiffuEraser | 29.51 | 35.19 | 32.35 | 0.8 |
| Lumiere inpainting | 26.62 | 31.46 | 29.04 | 9 |
| ObjectDrop (per frame) | 28.05 | 34.22 | 31.14 | – |
| Video RePaint [LTX] | 20.13 | 21.15 | 20.64 | 0.4 |
| OmnimatteRF | 33.86 | 40.91 | 37.38 | 3.5 (+6 h fit) |
| Generative Omnimatte | 32.69 | 44.07 | 38.38 | 9 |
| **OmnimatteZero [LTX]** | **35.11** | 44.97 | **40.04** | **0.04** |
| OmnimatteZero [Wan2.1] | 34.12 | 45.55 | 39.84 | 3.2 |

Limitations they state: VAE round trip gives "slight deviations" from the input; TAP quality under heavy occlusion or low
resolution; bounded by the base model.

**Checking S63.** Mechanism, real-time claim and the VAE caveat are accurate. S63's Omnimatte line ("3–8.5 h per video,
~2.5 s per frame", cited via this paper) is this paper's sentence about *LNA and Omnimatte together*; Omnimatte alone is
~3 h (see OmnimatteRF note).

**For moebius — the table is the strongest evidence yet for the S63 plan.** On backgrounds that are mostly *observed
somewhere in the clip*, the methods that gather observations geometrically (OmnimatteRF's static 3-D field: 37.4 dB)
beat the 2-D video inpainters (ProPainter 31.1, DiffuEraser 32.4) by about 5 dB, and the best method wins by *steering a
generator to copy corresponded pixels* (TAG). Per-frame generation (Video RePaint, 20.6 dB) is the worst by far. That is
exactly the ordering S63 proposed: copy what was seen (by 3-D reprojection, with a z-test), paint once only what was never
seen. The 0.04 s/frame is for 2-D correspondences from a tracker; we get correspondences from depth and pose instead, at
no model cost.

---

## EasyOmnimatte (2512.21865, Dec 2025) — read in full (Tables 1–2 cells lost)

**Method.** Start from the Gen-Omnimatte public video inpainting model (Wan2.1). Duplicate the input tokens; the
original tokens go through the **frozen** inpainter and give the background B; the copy goes through LoRA "branch"
blocks and predicts the alpha matte. Foreground colour is then solved analytically, **F = (I − (1−α)·B)/(α+ε)**. A
block-wise attention analysis finds three stages — context, *effect perception* (middle), *effect suppression* (late) —
so the **Effect Expert** puts LoRA (rank 128) only on the late blocks, the **Quality Expert** (rank 64) on all blocks;
sampling switches from the first to the second at τ = 0.5. Trained 8 k iterations on 2×H100 on synthetic composites
(VideoMatte240K foregrounds over captioned background videos, with programmatic shear-and-blur shadows and
affine-eased "camera motion").

**Evidence.** Tables are empty in the mirror. The text: under 10 s per clip against minutes per layer for
Gen-Omnimatte's optimisation; a user study (28 people, 20 videos, 0–5 scale on foreground integrity, effect harmony,
temporal consistency); recomposition PSNR/SSIM/warp loss and FVD on new backgrounds. Fine-tuning a general Wan-Fun model
instead of the inpainter fails to learn effects at all (App. E). Failures inherit the inpainter's (App. F).

**Checking S63.** Accurate as far as it goes ("LoRA effect expert plus quality expert on the Gen-Omnimatte Wan model;
under 10 s"). The background layer is not EasyOmnimatte's contribution — it is the frozen inpainter's output — so it
brings nothing new to *filling* holes.

**For moebius.** The piece we can use is the analytic un-compositing **F = (I − (1−α)B)/α**: once the layer behind a
soft edge is known (our plate, filled once), the foreground's own colour at a hair/bokeh/motion-blur edge follows from
the observed pixel and α. That is the known-background matting idea (BGMv2 is their baseline) and it fits the αDepth
soft-edge plan: fill the plate first, then solve α and F at the edge against it, so the edge carries no background colour
when the head moves.

---

## FloED (2412.00857, v Mar 2025) — read in full (tables survived)

**Method.** SD-inpainting UNet + AnimateDiff-v3 motion modules (stage 1: motion modules fine-tuned for inpainting).
Stage 2 adds a time-independent **flow-completion branch** (RAFT flow of the masked frames, completed) feeding
**multi-scale flow adapters** (IP-Adapter-style cross-attention) into the up-blocks, with an L1 flow loss (λ = 0.1).
**Anchor frame:** one extra frame is inpainted first by an *image* inpainter and prepended as guidance, then dropped.
**Speed-up:** for denoising steps 2–6 of 25, only half the frames are denoised per step and the other half are warped
from them by the completed flow (warping x̂₀, not the noise — warping the noise blurs); flow K/V cached after step 1.
Training: Open-Sora-Plan, 421 k clips, 16 frames at 512, 8×A800.

**Evidence (Table 1, their own 100-clip Pexels/Pixabay benchmark at 512×512).** Background restoration (synthetic
random masks): FloED PSNR 29.17 / E_warp 2.83 / TC 0.994; DiffuEraser 24.23 / 2.98 / 0.984; CoCoCo 23.08 / 3.73 / 0.991;
VideoComposer 22.81 / 3.43 / 0.987. Ablation (Table 2): no flow adapter and no anchor 21.30 dB → anchor only 25.34 →
flow adapter only 27.05 → both 28.71 → longer training 29.17. Timing (Table 3/4, H800, 25 steps, CFG): 0.13 s/frame at
432×240 and 0.34 s at 512²; the flow machinery costs +16 % and the interpolation + cache win back 13.4 %, so net it is
about the cost of the plain model. User study: 15 annotators, preferred 62 % (BR) / 56 % (OR).

**Checking S63.** The FloED table in S63 matches the paper. **Correction:** S63 says latents are "warped by flow to skip
half the denoising work"; the paper interpolates only in steps 2–6 of 25, and the whole speed-up is 13.4 %, roughly
cancelling the flow branch's own cost. S63 does not say that the benchmark is the authors' own and that PSNR here is
over random background masks (the "BR" task), not object removal.

**For moebius.** The ablation is the useful number: of the 7.9 dB FloED gains over its plain baseline, **propagated
motion (flow) is worth about 5.8 dB and an image-inpainted anchor frame about 4 dB**, together ~7.4 dB. Both are cheap
stand-ins for what we get exactly from geometry: correspondences from depth + pose instead of completed flow, and a
painted world-anchored layer instead of one anchor frame.
