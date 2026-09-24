# S63b: five papers read in full for the video plan — notes and corrections to S63

Date: 2026-09-24. Read beginning to end (main text, appendix, supplement where present) from the markdown full texts
the user supplied, now in `research/papers/`. The markdown conversion drops most display equations (they appear as
blank lines); where a note depends on an equation, it is taken from the surrounding prose and the tables, and says so.

The five: αDepth (2606.00386), Omnimatte3D (CVPR 2023), SEE4D (2510.26796, Eurographics 2026), Diffusion-VAS
(2412.04623), DepthDirector (2601.10214). In S63 all five were cited from abstracts or search summaries only.

---

## 1. αDepth — soft boundaries as a local two-layer decomposition (Zhang et al., ETH / DisneyResearch|Studios)

**What it does.** Input: an image and a depth map from any monocular model. Output, *only inside soft-boundary
regions*: an alpha, a foreground colour and a background colour, a foreground depth and a background depth. Everywhere
else the input colour and depth pass through untouched (Eq. 4 restricts the layered prediction to the region
Ŝ = [α̂ ∈ [0.02, 0.98]]; §3.2, §A.1). Network: a UNet "detail" encoder plus a DINOv2 "semantic" encoder initialised
from Depth Anything V2, a depth-gradient ("edge extraction") input, and three small decoders (alpha, colour, depth)
(Fig. 4; Table 6: 328.6 M parameters, 319.5 M of them the semantic encoder).

**The circular alpha representation (CAR).** Alpha is trained as (α·sin, α·cos)-style trigonometric components so that
α = 0 and α = 1 map to the same point: every *opaque* pixel, foreground or background, is one class, and only the
transition is estimated (§3.2, Fig. 5). This removes "alpha valleys" where two overlapping foregrounds meet — a global
matte would need a jump from 1 (front object) to 1 (the other object) through a spurious dip (Fig. 3b). Decoding uses
the four-quadrant arctangent, so opaque regions come out as α̂ = 0 (§3.2).

**Two layers suffice locally.** "while complex scenes may theoretically require numerous global layers … local soft
boundaries can be effectively modeled using a two-layer decomposition" (§3.2). Limitation stated in §D: three or more
semi-transparent layers overlapping at one pixel are not captured.

**Warping.** Foreground layer splatted with premultiplied alpha, background layer splatted separately, composited only
on soft regions (§A.1). The warped image keeps the base depth model's geometry elsewhere.

**Evaluation.** Metrics are computed *on soft regions only* (S-PSNR, S-SSIM) because "soft boundaries usually occupy a
small fraction of the image" (§4.2). Warping on Marvel-10K, VDA depth: S-PSNR 26.14 → 28.68, S-SSIM 0.6718 → 0.7636
(Table 2); on the whole image the same change is only 27.04 → 27.38 PSNR (Table 5) — the gain lives in the edge band.
Ablation (Table 4a): alpha alone (A#2) 0.7165 S-SSIM; + CAR 0.7214; + background layer 0.7636 — **estimating the
background colour/depth behind the soft edge is the largest single gain.** Removing the depth-edge input makes training
unstable or diverge and costs 2.54 dB S-PSNR (§C.3, Table 10). Matting quality is comparable to trimap-guided ViTMatte
without any guidance (Table 3). Robust to the depth model used (Table 7: DAv2, Depth Pro, MoGe-2, PPD within 0.13 SAD).

**Compute / code.** Training ~6 days on one RTX A6000; inference 0.0153 s and 608 MB at 448×640 on an RTX 4090
(§4.1, §B.2). **The paper states no code or weight release.**

**Limits the authors state (§D).** Depends on the base depth for global structure; two layers only; image-based, so it
"may produce results with flickering artifacts" in video and "may fail to resolve boundaries at low depth gradients (e.g.,
when two targets move close together in depth)".

**For moebius.**
- This is the right *representation* for our silhouette fringe: at every depth edge, carry α plus a foreground and a
  background colour and depth for a band of a few pixels, and leave the rest alone. It is exactly the "soft cut-out" the
  video discussion arrived at, and it explains the starwatcher's half-transparent legs: a single-layer depth at a mixed
  pixel sends the mixed colour to one side or the other, and the plate inherits foreground colour.
- The largest measured gain is the **background layer inside the soft band** — our plates already are that background;
  what is missing is (a) the alpha, and (b) *un-mixing* the band colour into foreground and background parts instead of
  copying the mixed colour into both.
- We do not need αDepth's main selling point (no manual guidance): our pipeline already knows every depth edge and its
  side, so a trimap is free (edge ± band width). That makes trimap- or mask-guided matting (ViTMatte, MatAnyone 2 — both
  compared in Table 3 and within noise of αDepth) usable today, which matters because αDepth has no release.
- Adopt its evaluation: score soft-edge handling **only inside Ŝ = α ∈ [0.02, 0.98]**. Our synthetic video already
  stores `alpha_thing`, the exact coverage of the blurred image, so Ŝ and the true α are known per frame.
- The low-depth-gradient failure (two things close in depth) is a case to render: two figures near the same depth
  crossing, with defocus.

**Corrections to S63.** S63 §4: "αDepth: estimates layered colour and depth at soft boundaries such as hair and
defocus, to stop background bleeding in stereo conversion [abs]" — confirmed. Add: two layers only, soft regions only,
no stated code release; its gain is concentrated in the edge band (whole-image PSNR +0.34 dB, soft-region +2.54 dB).

---

## 2. Omnimatte3D — a per-frame RGBD background, held together by multi-view consistency (Suhail et al., CVPR 2023)

**What it does.** Input: a video, approximate object masks (Mask R-CNN), and camera poses plus initial depth from
CasualSAM (§4.1). A shared 2-D UNet feature extractor feeds a background network that predicts, **for every frame**, an
inpainted background colour and disparity, and one small network per object that predicts an RGBA layer (§3.1, Fig. 3).
Optimised per video.

**How the hidden background gets filled.** Not by a generative prior: "Unlike prior works that rely on deep priors for
inpainting … our method relies on multi-view consistency losses to steer the inpainting process" (§3). Each batch has
three frames; the backgrounds of two source frames are meshed from their predicted disparity (one vertex per pixel),
rasterised into the target frame, and an L2 loss ties them to the target's background, masked by projected alpha (Eq. 7),
with a matching loss on 3-D coordinates (Eq. 8). Frames are chosen by an **overlap metric**: for each frame, the partner
is drawn from the top 10 frames that maximise static overlap, so "regions that are occluded in one are visible in the
other" (§3.4); random pairing fails to separate shadows (Fig. 8). Without the projection loss the hidden background is
"severe artifacts" (Fig. 9). After optimisation, **detail transfer** reprojects high-frequency detail from frames t−5,
t, t+5 using the background depth (§3.5, Fig. 10).

**Evaluation.** Qualitative only (DAVIS scenes vs Omnimatte and Neural Atlas); no numeric table.

**Limits (§5).** Object layers are not reprojected, so a foreground object is not inpainted where something occludes it
("When an object passes behind the stationary background layer, it is erased from the object layer", Fig. 11).
Scene flow for dynamic elements is left to future work.

**For moebius.**
- It is the closest published system to case (a) of S63, and it **supports "copy what other frames saw"**: the hidden
  background is filled *only* by reprojection between frames, never by a generator, and it works on DAVIS clips with
  real parallax where 2-D atlases fail (Fig. 2).
- Its **frame selection** (partner frames that maximise static overlap so the hidden region is visible in one of them)
  is the right schedule for our copy step: for each hidden plate texel, prefer the frames where it is seen, nearest in
  time.
- It chooses a per-frame background with a soft consistency loss rather than one fixed canvas, to let the background
  "vary slowly over time" (§1). That is a softer design than our "paint once, reproject": it tolerates lighting drift,
  but it cannot guarantee zero flicker in regions no frame saw — there it only has smoothness priors.
- The foreground matte + background depth enabled **re-rendered synthetic defocus** without halo (§4.4, Fig. 7) —
  the same property our soft-edge layers would give: once the layers are clean, defocus can be recomputed per head pose
  instead of baked in.

**Corrections to S63.** S63 §1 lists Omnimatte3D as "an RGBD background video layer built from monocular depth and camera
poses, plus a video layer per foreground object, with multi-view consistency losses [sec]" — confirmed from the text.
But S63 §1 end and §8(a) say the canvas as a textured 3D world surface is "the OmnimatteRF / Omnimatte3D choice". For
Omnimatte3D that is **not accurate**: it keeps **one background per frame** (a per-frame mesh), made consistent by a loss
between frames, not a single world-anchored surface. S63's "paint once in world space" goes further than Omnimatte3D and
is our own choice, justified by exactness, not by this paper. Also S63 says "JAX, in google-research [sec]" — the paper
text does not say; unverified.

---

## 3. SEE4D — render a clip to a fixed bank of virtual cameras by warp-then-inpaint (Lu et al., Eurographics 2026)

**What it does.** From one monocular video, generate videos at a set of fixed virtual cameras ("trajectory-to-camera").
Per-frame depth lifts frames to 3-D; for each target camera a spline of virtual poses is walked in small hops: warp to
the next pose, inpaint the holes with a view-conditional video diffusion model, re-estimate depth, align its scale, repeat
(§3.3.1). Time is handled with sliding windows of length L that reuse the last m clean latents as an anchor (§3.3.2).
Training tricks: "realistic warp synthesis" (forward-project a target frame to a random nearby pose rotated about the
largest foreground object, back-project with pose jitter, so training holes look like real disocclusions, §3.2.2), and
"noise-adaptive conditioning" (more noise on the warp latent when the warp mask is sparse, §3.2.3). Backbone from See3D,
spatio-temporal attention added.

**Compute.** 512×512, 16-frame sequences; 8 × A800-80 GB for ~48 h (§4.1.2). No code or licence stated in the paper.

**Evaluation.** iPhone dataset (5 scenes): PSNR 14.56, SSIM 0.442, LPIPS 0.492, best of all methods; TrajectoryCrafter
14.24 / 0.417 / 0.519; Shape-of-Motion 11.28 (Table 1). VBench on 200 WebVid clips: best on 5 of 6 (Table 2). Ablation:
removing the spatio-temporal backbone drops PSNR to 10.66 (Table 3).

**For moebius.**
- **Calibration that matters:** on held-out real views every method, SEE4D included, scores **10–15 dB PSNR**. Generated
  far-away views are plausible pictures, not the scene. Everything generative should stay confined to what no frame saw.
- The "bank of fixed cameras" is the nearest published analogue of precomputing a grid of head poses — but **each target
  view is generated along its own chain from the source**; the paper claims cross-view coherence from the model but has
  no mechanism that makes two bank views agree texel for texel, and downstream it fuses them into 4D Gaussians
  (§3.3). For a head-tracked window, where the eye moves continuously between such views, independent per-view fills
  would pop. This supports storing one painted layer and reprojecting it (S63 §4 already argued this; SEE4D is the
  concrete counter-design and confirms the risk).
- Worth copying: the **realistic warp synthesis** for any model we train or fine-tune (holes shaped like real
  disocclusions around the main object, with depth noise), and **small hops** when a view change is large.

**Corrections to S63.** S63 §5: "Renders to a bank of fixed virtual cameras instead of one trajectory, with a
view-conditional video inpainter and spatio-temporal auto-regression [abs]. This is structurally the closest to
'precompute a grid of head poses'." — confirmed. Add: absolute accuracy is low (≈14.6 dB PSNR on iPhone), each view is
generated independently of the others, 8×A800 training, no stated release.

---

## 4. Diffusion-VAS — amodal masks, then amodal content, with video diffusion (Chen, Ramanan, Khurana, CMU)

**What it does.** Two stages, both fine-tuned from Stable Video Diffusion (SVD-xt 1.1), 3-D UNet, EDM sampler, 25 steps,
guidance 1.5 (§3, §A.1). Stage 1: modal (visible) mask sequence + **pseudo-depth** (Depth Anything V2) → amodal mask
sequence. Stage 2: the object's modal RGB + the amodal mask → the object's RGB over its whole amodal region. Training
pairs for stage 2 are made by laying random amodal masks over nearly fully visible objects (§3.4, Fig. 3). Trained on
synthetic SAIL-VOS (GTA-V), 8 × RTX 3090 for ~30 h; inference at 256×512 (§4.1).

**Evaluation.** SAIL-VOS mIoU_occ (IoU on the occluded part only) 55.12 Top-1 vs 42.52 for the next best (PCNet-M)
(Table 1) — the "+13 %" is 12.6 points. Zero-shot on real TAO-Amodal (boxes only): AP50 89.25 vs 85.11. Pseudo-depth
beats RGB as a conditioning (Table 3: mask+depth 55.12 vs mask+RGB 53.3 mIoU_occ; adding RGB to depth does not help and
hurts transfer). Content completion has **no quantitative metric** — a 20-sequence user study, 85.6 % preference over
pix2gestalt (§4.2). The two-stage design beats one-stage by 15 points mIoU_occ (Table 7).

**Key statement for us (§2).** "Generic inpainting methods often fail at this task, as they rely on surrounding context,
which often includes occluders." Content completion therefore conditions on the object's own visible pixels, not the
scene.

**Failure cases (§D).** An object occluded for the whole clip (the model cannot tell "fully visible" from "always
occluded"); out-of-distribution objects; wrong height or pose (a sitting person completed as standing). Multiple plausible
completions per seed (Fig. 8: legs in two orientations).

**For moebius.**
- Confirms the occluder lesson from the starwatcher (S62 §12): SD continued the legs because the legs were in its
  context. Taking the occluder out of the painter's input (our `plane_mask_occluder` near pass) is the same fix.
- Applies to **things behind things**, not to background behind a person: H4's half-hidden far figure, and a person's own
  middle surface where an **arm crosses the torso** (the hidden part is torso — an amodal completion of the torso). The
  gap between the legs is background, which the plates already cover.
- Depth as the conditioning signal, not colour, is the same bet our pipeline makes; and seed-dependence (multiple
  completions) means an amodal completion must be made **once and stored**, never re-sampled per frame.

**Corrections to S63.** S63 §6: "Two-stage amodal mask then amodal RGB … up to +13 % amodal segmentation in occluded
regions [sec]. Code at GitHub Kaihua-Chen/diffusion-vas [sec]." — method and the +13 % (12.6 points mIoU_occ on SAIL-VOS)
confirmed; content completion is evaluated only by a user study; the code location is not stated in the paper text
(project page only).

---

## 5. DepthDirector — the "Inpainting Trap" and depth as the camera condition (Chen et al., Tsinghua)

**The argument.** Warp-and-inpaint camera control (GEN3C, TrajectoryCrafter, EX-4D) "fundamentally caps the quality of
the generated content at that of the warped RGB video": depth from monocular video is inaccurate, the warped pixels are
distorted (worst on faces), and the video model learns a shortcut — it inpaints the holes and **keeps the distortion**
(§1, Fig. 2). They call this the Inpainting Trap.

**What they do instead.** Build a per-frame mesh from video depth (DepthCrafter, scale/shift-aligned to π³ poses), render
**depth and an occlusion mask** at the target camera, encode the colour-mapped depth with the VAE and add it to the noise
latent ("view tokens"), and concatenate the **source video's tokens** along the frame axis as the content reference; a
LoRA (rank 32) on Wan 2.2-TI2V-5B is trained on 8 K Unreal Engine 5 multi-camera clips (§3, §3.5). 8 × A100, 4 days;
~4 min per 81-frame 576×1024 video at inference (§4.1). Test trajectories rotate ±30° around the subject (§4.2).

**Evaluation (Table 1).** Warp-based methods are nearly exact in camera (EX-4D RotErr 0.637), DepthDirector 2.542 — **4×
worse camera accuracy** — but better identity preservation (ArcFace RS 0.689 vs 0.627 EX-4D) and more matched pixels
(988.7 vs 947.5). Appendix B2: repainting warped RGB even with multi-camera training still leaves artifacts. Appendix C.1:
with every video depth model tried, including DA3, "the warp results … contain distortion and artifacts without
exception" at these rotations. Limitation: no 360° trajectories — warped depth "loses too much information at large
viewpoint changes" (§E).

**Does the trap apply to us?** Mostly not, and the reason is worth writing down.
- Our visible layer is the source's own pixels, displaced by a few degrees of head motion inside the envelope; the paper's
  regime is ±30° re-shoots. At our offsets the warped pixels are nearly right, and **exactness of what the viewer already
  sees** is the requirement — DepthDirector gives that up (4× camera error, content re-rendered through the VAE). For the
  window, re-rendering the visible picture is the wrong trade.
- What does transfer: a depth error on a sensitive surface (a face) becomes a visible distortion as the offset grows. That
  argues for keeping the envelope where depth error stays sub-pixel, and for better depth on faces — not for replacing
  warped pixels with generated ones.
- The fill is where the trap could bite us: SD conditioned on a **warped** RGB context near a mis-placed edge will copy the
  mis-placement. Our fills are conditioned on the plate (source-anchored, S62), not on a warped view, so the specific
  shortcut they describe does not arise; the soft-edge un-mixing (§1 above) removes the remaining bleed.

**Corrections to S63.** S63 §5: "DepthDirector (arXiv 2601.10214) argues that warp-and-inpaint falls into an 'Inpainting
Trap' and conditions on warped depth instead [abs]." — confirmed; add that it buys identity preservation with 4× worse
camera accuracy, is evaluated at ±30° re-shoots, and that the trap concerns warped *pixels* at large view changes.

---

## What changes in the S63 plan

1. **Soft edges become part of the layer format (αDepth).** At every depth edge carry α, a foreground colour and a
   background colour (and depths) over a band a few pixels wide; un-mix the band colour instead of copying it into both
   sides. The trimap is free from our own edges, so mask-guided matting is usable now; score it only inside
   α ∈ [0.02, 0.98] against the exact coverage in the synthetic video.
2. **Copy-first is supported by the closest published system (Omnimatte3D)**, which fills hidden background only from
   other frames; adopt its partner-frame choice (frames that maximise static overlap / where the texel is seen, nearest in
   time) for the copy step.
3. **S63's world-anchored canvas is our own choice, not Omnimatte3D's** (per-frame background + consistency loss).
   Keep it for exactness, but plan for Omnimatte3D's reason to go per-frame — lighting drift — with the per-frame gain
   already in S63 §8(a) step 6.
4. **Bank-of-views approaches (SEE4D) generate each view independently** — a reason not to bake a grid of head-pose views
   with a generator; one stored layer, reprojected, stays the design.
5. **Generated novel views are far from truth (≈10–15 dB PSNR, SEE4D Table 1)** — keep generation to what no frame saw.
6. **Amodal completion (Diffusion-VAS) is for things behind things** — H4's far figure, an arm over a torso — and must be
   made once and stored (it is seed-dependent). Keep the occluder out of its context, as the paper and our starwatcher
   run both show.
7. **The Inpainting Trap does not argue against our warp of the visible layer** at window offsets; it argues for keeping
   offsets inside the depth-accuracy envelope and for not conditioning fills on warped views.
8. **Re-rendered defocus becomes possible once layers are clean** (Omnimatte3D §4.4): with α and a clean background,
   depth-of-field can be recomputed per head pose instead of baked into the plates.
