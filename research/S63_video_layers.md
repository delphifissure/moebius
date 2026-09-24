# S63: video input — keeping the layers and their painted holes continuous over time

Date: 2026-09-24. Question (user): with a moving camera, keep the layers continuous — paint each static layer once with
SD and composite, instead of an SD pass per frame — or is there another way? Part A is our own first measurement on the
one clip in the app repo; Part B is the literature pass (report written for this note, evidence-tagged per claim).

## Part A — the coverage measurement on the gladiator clip

**What it asks.** Of what is hidden behind the moving foreground at frame t, how much is *seen* in some other frame?
Anything seen can be copied from real footage; only the rest ever needs painting.

**Clip.** `gladiator-video-rgb.mp4` + `gladiator-video-depth.mp4` (moebiusv2 root): 681 frames, 24 fps, 1080×608,
letterbox rows 74–534. The depth video is matplotlib *inferno* colour; decoded exactly by nearest LUT entry. A hand
moves through wheat; the camera follows loosely.

**Method** (`harness/video_observed.py`, half resolution 540×230):
- foreground = decoded depth above the per-frame Otsu split (median split 0.475; the foreground covers 30.6% of the frame);
- background motion between consecutive frames = a RANSAC homography fitted to Farneback flow on background pixels,
  chained to carry a pixel of frame t into frame s;
- hidden sets at frame t: **band** = foreground pixels within 2% of the width (11 px at half resolution) of the
  silhouette — what head motion inside the window reveals — and **whole** = the whole foreground footprint;
- a hidden pixel counts as seen at s if it lands inside frame s on background (foreground at s dilated 3 px);
  sampled every 10th frame.

**Result.**

| hidden set | seen within ±6 f (¼ s) | ±24 f (1 s) | ±72 f (3 s) | anywhere in the clip |
|---|---|---|---|---|
| band (what the window reveals) | 56.6% | **86.1%** | 96.7% | **99.1%** |
| whole footprint | 27.8% | 68.4% | 91.0% | 97.5% |

The background moves a median 0.08 px per frame (half-res), 162 px of path over 28 s: the camera is nearly still, so
the coverage comes from the **hand moving**, not the camera. This clip is case (b) of Part B §8.

**What it says.** On this clip, 99% of what the window would ever need to reveal behind the hand is real footage
somewhere in the clip, and 86% within one second. Painting is needed for about 1% of the band — once, in the static
background's frame. The user's "paint the static layer once, composite" is right, and most of the static layer should
be *copied*, not painted.

**Limits of this first cut.**
- 2-D homography, not 3-D reprojection with poses and depth: right for a near-still camera; a translating camera needs
  the §8(a) route (DA3 multi-view poses, z-test).
- The wheat sways: a pixel "seen" at another time shows the same place but not the same wheat pose. Copied pixels are
  real texture, but they need a temporal blend or a video fill where the motion is visible.
- Decoded 8-bit colour-mapped depth, one Otsu split: near wheat can join the foreground mask.
- One clip. The Experiment 1 of §9 on 4–6 clips (handheld walk-past, pan, tripod + person, handheld + person) is still
  the deciding measurement.

## Part B — literature: every credible route, with evidence

Research date: 2026-09-24. Scope: work up to September 2026, weighted to 2024–2026.

### How to read the evidence tags

arXiv and project pages were blocked from this sandbox. Full paper texts were read through Hugging Face's mirror of the arXiv HTML (`huggingface.co/papers/<id>.md`). Code licences and compute tables were read from the raw GitHub README and LICENSE files. Each claim carries one of these tags:

- **[paper]**: checked in the paper's full text.
- **[abs]**: checked in the abstract only.
- **[repo]**: checked in the GitHub README or LICENSE file.
- **[sec]**: from memory or a search-engine summary, not re-checked. Treat these as leads.

"No licence file" means that no LICENSE file was found at the repo root on `main`. It does not mean the code is permissively licensed.

---

### 0. TL;DR

1. **Most hidden pixels need no painting at all.** Only one kind of pixel has to be generated: one that was never seen in any frame. With a moving camera, much of what the head-tracked window reveals was visible in some other frame. Copy those real pixels in through 3D reprojection. Only the remainder needs an inpainter.
2. **The pixels that do need painting should be painted once, in a coordinate frame that does not move.** That is world space for static content, or the object's own frame for a rigid object. Every frame and every head pose then reprojects that one painting, so it cannot flicker, because nothing is re-sampled. For static content this is exactly the user's proposal, with one change: the "layer" must be a **3D surface anchored in the world, not a flat image per frame**. A per-frame 2D plate re-inpainted each frame will flicker, because its mask and context move every frame.
3. **Anything that truly changes over time needs a video model rather than an image model.** That includes a walking person's self-occluded middle surface, water, foliage and shadows. SD/LaMa run per frame is the known failure mode. The 2025–26 video inpainters are good enough to try on the moving layers: MiniMax-Remover, DiffuEraser, VACE/Wan, ROSE, SVOR, and the Omnimatte-style decomposers. They still invent content, and their licences vary.
4. **The published problem closest to ours is 2D-to-stereo conversion.** It uses warp-by-depth, then fills with a video model. Its temporal consistency comes from video diffusion with overlapping windows (StereoCrafter), or from denoising all views and times jointly (SVG "frame matrix"). It does not come from a world-anchored canvas, because a stereo pair only needs one fixed extra view. We need a continuous range of views, which favours the canvas.
5. **Full 4D reconstruction is heavier than we need for now.** Shape-of-Motion/MoSca combined with generative gap-filling (CogNVS, Vivid4D, World-from-Motion) is the most general answer. It costs minutes to hours per clip and is fragile on casual video. A layered 2.5D scene built from reprojection is cheaper and fits the app's renderer.
6. **Depth and masks cause flicker too, not only paint.** Monocular DA3 run per frame will make the geometry itself shimmer. Use DA3 multi-view/pose mode (static scenes) or MegaSaM or Video Depth Anything (dynamic scenes).

---

### 1. Static background as a single canvas: atlases and the Omnimatte family

These methods write a video as a small number of layers, each with one canonical texture, plus a per-frame mapping into the frames. If the canonical texture is edited or inpainted once, the edit propagates to every frame with no flicker by construction. The weakness is the mapping. A 2D atlas cannot represent parallax inside a layer, because two points at different depths inside one layer move differently in the image.

**Layered Neural Atlases (LNA)**: Kasten et al., SIGGRAPH Asia 2021, arXiv 2109.11418.
- *Mechanism:* per-layer MLPs map each pixel (x,y,t) to a UV coordinate in a 2D atlas, plus an opacity. Editing the atlas edits the whole video.
- *Assumes:* each layer unwraps onto one 2D plane, with roughly two layers (foreground and background).
- *Evidence:* optimisation takes "more than 10 hours" per video, per the CoDeF paper [paper].
- *Code:* MIT [repo].
- *Breaks on:* strong background parallax and self-occluding foregrounds [sec]. Neural Atlas Graphs (below) also calls out multi-object occlusion as a failure [abs].

**Deformable Sprites**: Ye, Li, Tucker, Kanazawa, Snavely, CVPR 2022 [sec].
- *Mechanism:* each scene element is a 2D texture for the whole video, plus per-frame masks and non-rigid deformations. Optimised per video, with no masks needed.
- *Assumes:* the same 2D-texture limit as LNA.

**Hashing Neural Video Decomposition**: Chan et al., arXiv 2309.14022 (ICCV 2023) [sec for venue].
- *Mechanism:* per layer, a 2D texture plus a mask plus a **multiplicative residual in space-time for lighting changes** [abs]. The residual idea matters to us: it is how an atlas copes with changing illumination.
- *Compute:* 25 s per frame to fit at 1080p; renders at 71 fps [abs].

**INVE**: arXiv 2307.07663.
- *Mechanism:* LNA with hash grids plus bidirectional atlas↔frame maps. Learning and inference are 5× faster than LNA [abs].

**CoDeF**: arXiv 2308.07926 (CVPR 2024) [sec for venue].
- *Mechanism:* a 2D hash-grid canonical image plus a 3D hash-grid deformation field. Image algorithms run on the canonical image and results are warped to every frame.
- *Compute:* about 300 s to fit, against >10 h for LNA [paper].
- *Assumes:* one canonical image per layer. A deformation field can absorb some parallax by warping, but it cannot un-occlude anything.
- *Code:* GitHub qiuyu96/CoDeF; no licence file found.

**StableVideo**: arXiv 2308.09592 (ICCV 2023) [sec for venue]. Diffusion editing done in LNA atlases, then propagated [abs]. It shows the "edit once in canonical space with SD" pattern, and it inherits the atlas limits.

**Neural Atlas Graphs (NAG)**: arXiv 2509.16336, Sept 2025.
- *Mechanism:* a scene graph whose nodes are view-dependent neural atlases, so 2D-editable textures carry 3D ordering and placement. It explicitly targets the case where "neural atlases … break down when multiple objects occlude and interact" [abs].
- *Evidence:* reports +5 dB PSNR on Waymo and +7 dB on DAVIS against matting and editing baselines [abs].
- *Takeaway:* this is the most recent sign that "atlas per layer, with 3D ordering" is being revived.

**Omnimatte**: Lu et al., CVPR 2021.
- *Mechanism:* RGBA layers per object plus their effects (shadows, reflections), with a background modelled by homographies.
- *Assumes:* a **planar background or rotation-only camera** [paper, via the OmnimatteRF text].
- *Compute:* 3–8.5 h per video and ~2.5 s per frame to render [paper, via the OmnimatteZero text].

**Omnimatte3D**: Suhail et al., CVPR 2023 [sec].
- *Mechanism:* an RGBD background video layer built from monocular depth and camera poses, plus a video layer per foreground object, with multi-view consistency losses.
- *Code:* JAX, in google-research [sec].

**OmnimatteRF**: arXiv 2309.07749, ICCV 2023.
- *Mechanism:* 2D foreground layers plus a **3D radiance-field background**. It "retrains" the background with the object masks to get a clean static 3D reconstruction [paper].
- *Assumes:* a static background and known or estimated poses. This hybrid is the closest in spirit to our case (a) below.

**Generative Omnimatte**: arXiv 2411.16683, CVPR 2025.
- *Mechanism:* the "Casper" video diffusion model, fine-tuned from Lumiere inpainting, takes a *trimask* (remove / keep / maybe-effect). It produces clean-background and single-object videos, then test-time optimisation extracts the RGBA layers.
- *Assumes:* no static scene, poses or depth [abs]. It completes occluded *dynamic* regions.
- *Compute:* Casper takes about 12 minutes for 80 frames at 128 px base resolution, then Lumiere upsampling to 640×384 [paper].
- *Public code:* Apache-2.0, a re-implementation on CogVideoX-Fun-5B and Wan2.1-Fun that the authors say is "close to, but does not match" the Lumiere model. It takes 1–2 min on an A100 and 4–5 min on a 48 GB A6000, with 85-frame windows and up to 197 frames via temporal multidiffusion [repo].
- *Limitations:* bending and deforming objects not seen in training, similar-looking multiple objects, and unrelated background effects getting assigned to an object [sec, from the paper's limitations section as summarised].

**OmnimatteZero**: arXiv 2503.18033, 2025.
- *Mechanism:* training-free. It uses off-the-shelf video diffusion (Wan2.1, LTX) with attention-guided effect removal and latent arithmetic for layers. It claims real-time speed [abs].
- *Caveat:* output passes through the VAE, so reconstructed video "may exhibit slight deviations" from the input [paper].

**EasyOmnimatte**: arXiv 2512.21865, Dec 2025.
- *Mechanism:* LoRA "effect expert" plus "quality expert" on a Wan-based inpainting model (the Gen-Omnimatte public one). Omnimatte "in under 10 seconds" against minutes per layer for Gen-Omnimatte [paper].
- *Code:* none linked [abs].

**DBL-Diffusion / TriLayer**: arXiv 2607.25802, July 2026.
- *Mechanism:* a dual-branch diffusion model trained on a large triplet dataset (composite, background, and RGBA foreground with effects) for both decomposition and insertion [abs].
- *Code:* GitHub KyujinHan/DBL-Diffusion [abs]; licence not checked.

**Can a per-layer atlas be painted once and propagated? Yes, with conditions.**
- *Where it works:* the layer is close to planar, the camera mostly rotates, or the camera translates only a little relative to depth variation inside the layer.
- *Where it breaks:*
  1. **Parallax inside a layer.** A 2D atlas cannot hold two depths along one ray.
  2. **Large camera translation.** The atlas gets stretched or distorted, which CoDeF names as a known flaw of prior atlases [paper].
  3. **Changes over time inside the layer**, such as water or lighting. Hashing-NVD handles lighting with a multiplicative residual; water needs a video model.
  4. **Several occluders interacting**, which NAG addresses.

For moebius the fix is straightforward. The app already stores **depth** for each plate, so the canvas can be a textured 3D surface (world-anchored mesh, point set or splats) instead of a 2D atlas. That is the OmnimatteRF / Omnimatte3D choice.

---

### 2. Using the camera motion: copy real pixels first, generate only the never-seen

#### 2a. Flow-guided video inpainting (2D correspondence)

**ProPainter**: arXiv 2309.03897, ICCV 2023.
- *Mechanism:* completes the optical flow inside the hole, propagates in both image and feature space, then a mask-guided sparse video transformer fills the rest.
- *Evidence* [paper]:

  | Dataset | PSNR | SSIM | VFID | E_warp (×10⁻²) |
  |---|---|---|---|---|
  | YouTube-VOS | 34.43 | 0.9735 | 0.042 | 0.974 |
  | DAVIS | 34.47 | 0.9776 | 0.098 | 1.187 |

  E2FGVI scores 1.013 and 1.289 for E_warp on the same two datasets.
- *Compute:* 0.083 s per frame at 432×240 [paper]. GPU memory in fp16 is 8 GB for 80 frames at 720×480 and 25 GB for 80 frames at 1280×720 [repo].
- *Licence:* **NTU S-Lab 1.0, non-commercial** [repo].

**E2FGVI**: arXiv 2204.02663, CVPR 2022. End-to-end flow completion, feature propagation and hallucination. Runs at 0.12 s per frame at 432×240 on a Titan XP. Licence **CC BY-NC 4.0** [repo].

**FGT**: arXiv 2208.06768, ECCV 2022. A flow-guided transformer. The ProPainter paper reports it needs >32 GB at 480p [paper].

*Why 2D flow is second-best for us:* flow inside a disocclusion is exactly where it is least reliable. Flow completion interpolates from the hole boundary, and that boundary includes the foreground object whose flow is wrong for the background. We have something better than flow: the plate's own depth plus camera poses give exact correspondences, with a z-test for visibility.

#### 2b. Consistent depth and camera poses (the geometry that makes 3D reprojection possible)

**Depth Anything 3 (DA3)**: arXiv 2511.10647, Nov 2025.
- *Mechanism:* a single transformer predicts depth plus a ray map from any number of views, with or without known poses. It beats VGGT by 44.3% on pose accuracy and 25.1% on geometry on the authors' benchmark [abs].
- *Assumes:* the paper lists "extend its reasoning to dynamic scenes" as future work [paper]. So **assume the scene is static in multi-view mode**, and mask people out before estimating poses.
- *Long clips:* DA3-Streaming handles "ultra-long" video in under 12 GB with a sliding window [repo].
- *Licences* [repo]:
  - DA3-Small, DA3-Base, DA3Metric-Large and DA3Mono-Large: **Apache-2.0**.
  - DA3-Large, DA3-Giant and DA3Nested: **CC BY-NC 4.0**.

  Check which checkpoint moebius uses today.

**Video Depth Anything (VDA)**: arXiv 2501.12375, CVPR 2025.
- *Mechanism:* a DA-V2 backbone with a spatio-temporal head and a temporal-gradient loss. Works on videos minutes long; the small model runs at 30 fps [abs]. It reports TAE, a reprojection error between consecutive depth maps [paper].
- *Licence:* Small is **Apache-2.0**; Base and Large are **CC BY-NC** [repo].
- *Use:* consistent depth for *dynamic* layers.

**DepthCrafter**: arXiv 2409.02095, CVPR 2025.
- *Mechanism:* video diffusion (SVD) repurposed for depth, up to 110 frames per pass, with stitching beyond that [abs].
- *Compute:* ~26 GB at 1024×576 (2.1 fps on A100), or ~9 GB at 512×256 [repo].
- *Licence:* a Tencent licence; contact them for business use [repo].

**MegaSaM**: arXiv 2412.04463, CVPR 2025.
- *Mechanism:* deep visual SLAM, modified to give robust poses and depth on casual *dynamic* videos, including videos with little parallax [abs].
- *Compute:* its optimisation runs at about 1.3 fps at 336×144 [paper].
- *Licence:* Apache-2.0 code [repo].

**MonST3R**: arXiv 2410.03825, ICLR 2025. A pointmap for each timestep, fine-tuned from DUSt3R for dynamic scenes. Needs ~23–33 GB for 65 frames at 16:9 [repo]. **CC BY-NC-SA** [repo].

**CUT3R**: arXiv 2501.12387, CVPR 2025. A recurrent model with persistent state that turns a stream of frames into pointmaps in one shared coordinate frame [abs]. **CC BY-NC-SA** [repo].

**VGGT**: arXiv 2503.11651, CVPR 2025. Feed-forward cameras, depth, points and tracks from hundreds of views in about a second [abs]. A **commercial-use checkpoint (VGGT-1B-Commercial) has existed since July 2025** [repo].

**π³**: arXiv 2507.13347. A permutation-equivariant model with no reference view [abs]. Code BSD-3; **weights CC BY-NC** [repo].

**MapAnything**: arXiv 2509.13414. Feed-forward metric reconstruction that accepts optional poses, intrinsics or depth as inputs [abs]. An **Apache-2.0 model variant** is available [repo].

*What to take from 2b:* the reprojection step is solved well enough, and has permissive options: DA3-Base/Small or VGGT-Commercial or MapAnything-Apache for static scenes, MegaSaM for dynamic scenes, VDA-Small for per-frame dynamic depth. Whatever gives poses must be run with the moving people masked out.

#### 2c. The combined recipe, already published in pieces

Three methods split the problem the same way:
- **GEN3C** (arXiv 2503.03751, CVPR 2025) keeps a "3D cache" of point clouds from predicted depth and renders it along the new camera path. Its video model then "can focus all its generative power on previously unobserved regions" [abs].
- **CogNVS / "Reconstruct, Inpaint, Finetune"** (arXiv 2507.12646) renders the pixels visible in both views from a 4D reconstruction and inpaints only the hidden ones with a video model. That model is self-supervised on 2D videos and fine-tuned at test time on the target clip [abs].
- **Geometric Reciprocity** (arXiv 2607.05354, July 2026) proves that, under nearest-neighbour depth warping, the disocclusion mask for a target view equals the set of pixels lost when warping back. This lets a stereo inpainter train on unlimited monocular video [abs]. They fine-tune **ProPainter** this way for video stereo inpainting [paper].

This is the same split we need: *exact geometric mask, real pixels where available, generation only for the rest.* It also agrees with the app's lesson so far that an exact geometric mask works best.

---

### 3. Video inpainting diffusion models (fill the whole clip at once)

**One benchmark caveat first.** The common "temporal consistency" metric is CLIP similarity between consecutive frames, and it is saturated. In MiniMax-Remover's table, ProPainter scores 0.9769 and MiniMax scores 0.9776 on DAVIS [paper]. The PROVE benchmark (arXiv 2605.14534, May 2026) shows that full-reference metrics reward copy-paste, that no-reference metrics favour blur, and that global temporal metrics miss local artifacts. It proposes RC-T, which measures temporal consistency *inside the restored region* [abs][paper]. For our own tests, measure inside the hole only (Section 9).

**Comparison table** from MiniMax-Remover (arXiv 2505.24873) [paper]. Latency is in seconds, on each method's own settings (from context, per frame); memory is in GB.

| Method | Params | Steps | Latency (s) | GPU mem (GB) | DAVIS PSNR | DAVIS TC | GPT-o3 "success" % (DAVIS) |
|---|---|---|---|---|---|---|---|
| ProPainter | 37.5M | – | 0.27 | 13.5 | 35.33 | 0.9769 | 56.7 |
| DiffuEraser | 2.04B | 70 | 0.35 | 10.4 | 34.42 | 0.9767 | 56.7 |
| VideoPainter | 5.45B | 50 | 8.14 | 44.7 | 34.60 | 0.9620 | 18.0 |
| VACE | 1.66B | 25 | 1.93 | 23.6 | 31.92 | 0.9747 | 8.9 |
| FloED | 1.30B | 25 | 1.32 | 47.6 | 32.02 | 0.9630 | 45.6 |
| COCOCO | 1.45B | 50 | 3.56 | 36.5 | 32.10 | 0.9511 | 12.2 |
| MiniMax-Remover (6 steps) | 1.05B | 6 | 0.18 | 8.2 | 36.56 | 0.9770 | 82.2 |

Read these numbers with care:
- The authors wrote this table themselves, and the "success" column is judged by an LLM.
- The key point for us: **ProPainter, which only propagates and does not generate, matches the diffusion models on temporal consistency.** The diffusion models' gain is in plausibility where nothing was seen.
- That matches the lesson moebius already learned with LaMa versus SD.

**DiffuEraser**: arXiv 2501.10018, Jan 2025.
- *Mechanism:* SD1.5 plus a BrushNet branch plus AnimateDiff-style motion modules. **ProPainter output is used as a prior** for initialisation and weak conditioning, "to suppress hallucinations" [abs].
- *How it gets consistency:* the known pixels are pre-propagated across the whole clip, and there is overlap between its 22-frame clips [paper].
- *Compute:* 20 GB and 175 s for 250 frames at 960×540, or 12 GB and 92 s at 640×360, on an L20 [repo].
- *Licence:* Apache-2.0, **but the ProPainter prior is non-commercial** unless replaced [repo].

**FloED**: arXiv 2412.00857.
- *Mechanism:* SD-inpainting plus AnimateDiff, with a flow-completion branch and a multi-scale flow adapter. Latents are warped by flow to skip half the denoising work.
- *Evidence* (background restoration) [paper]:

  | Method | PSNR | E_warp | TC |
  |---|---|---|---|
  | FloED | 29.17 | 2.83 | 0.994 |
  | DiffuEraser | 24.23 | 2.98 | 0.984 |
  | CoCoCo | 23.08 | 3.73 | 0.991 |

**AVID**: arXiv 2312.03816, CVPR 2024 [sec for venue]. Text-guided, any length through "Temporal MultiDiffusion" with middle-frame attention guidance [abs].

**CoCoCo**: arXiv 2403.12035, AAAI 2025 [sec for venue]. Text-guided, with a motion-capture module [abs].

**VACE**: arXiv 2503.07598, ICCV 2025 [sec for venue].
- *Mechanism:* an all-in-one Wan/LTX adapter; masked video-to-video is one of its modes.
- *Output size:* Wan2.1-VACE-1.3B gives ~81 frames at 480×832; the 14B model gives 81 frames at 720×1280.
- *Licence:* **Apache-2.0** for the Wan variants and RAIL-M for LTX [repo].
- *Removal quality:* weak in MiniMax's DAVIS test (above).

**VideoPainter**: arXiv 2503.05639, SIGGRAPH 2025 [sec for venue]. A context encoder that is only 6% of the backbone, on a CogVideoX-5B DiT, with "ID resampling" for any length [abs]. **CogVideoX licence** [repo]. Default is 49 frames at 8 fps [repo].

**MiniMax-Remover**: arXiv 2505.24873.
- *Mechanism:* Wan2.1-1.3B with the text/cross-attention removed. It is then distilled with "minimax" training on adversarial noise, so it runs in 6 steps without CFG [paper].
- *Compute:* 24 s per 81-frame 480p video on an RTX 4090, 14 GB peak [paper].
- *Code:* GitHub zibojia/MiniMax-Remover; **no licence file found**. The Wan base is Apache-2.0.

**ROSE**: arXiv 2508.18633. Removes objects *and their side effects* (shadows, reflections, light, translucency, mirrors), trained on Unreal Engine pairs with camera motion [abs]. **Apache-2.0** [repo]. Clip length must be 16n+1 frames [repo].

**EraserDiT**: arXiv 2506.12853. A DiT with a "Circular Position-Shift" for long-range consistency. 65 s for 97 frames at 2160×2100 on an H800 [abs].

**Newer 2026 work, abstracts only:**
- **SVOR** (arXiv 2603.09283, Xiaomi, code on GitHub): "flicker-free, mask-defect-tolerant", with window-union masks and side-effect-weighted losses [abs].
- **UnderEraser** (arXiv 2604.01693, code WeChatCV/UnderEraser): effect-aware removal plus framewise context cross-attention [abs].
- **D2DF** (arXiv 2607.14976): one-step removal, "about 1 second" per video [abs].
- **FFF-VDI** (arXiv 2408.11402): first-frame filling with an image-to-video model [abs].

**GenProp**: arXiv 2412.19761, CVPR 2025 [sec for venue]. Edit the *first frame*, then propagate with an image-to-video model plus a selective content encoder. It also removes shadows and reflections [abs]. This is the "paint a keyframe, let a video model carry it" pattern.

**Summary for moebius:**
- These models give *within-clip* coherence (81-frame windows for Wan-based models, 22-frame clips with overlap for DiffuEraser) and handle genuinely dynamic content.
- They are still 2D. Each fills the *original camera path*. The fill must still be stored as a layer texture and reprojected for head offsets.
- They still invent content. MiniMax's "success" judgement is 82–91% on DAVIS, and VideoPainter and VACE score much lower [paper].
- The Apache-licensed options that fit a 24 GB card: ROSE, VACE-Wan-1.3B, DiffuEraser only if ProPainter is swapped out, and the Gen-Omnimatte public models. MiniMax-Remover also fits on 24 GB, but it has no licence file.

---

### 4. 2D-to-3D and stereo video conversion (the closest published problem)

Most of these papers follow the same pipeline: warp by depth, take the exact disocclusion mask, then fill it with a *video* model.

**StereoCrafter**: arXiv 2409.07447, Tencent.
- *Mechanism:* depth-based video splatting produces the warped view and the occlusion mask; the splatting runs in real time on GPU. SVD is fine-tuned for stereo inpainting.
- *Consistency:* auto-regressive windows, since SVD only gives 25 frames, plus tiled processing [paper].
- The authors explicitly reject dynamic 3D reconstruction as impractical, and note it "cannot address the occlusion that does not appear in the neighboring frames" [paper].
- *Licence:* not stated in the README; no licence file found.

**SVG (Stereo Video Generation)**: arXiv 2407.00367, ICLR 2025 [sec for venue].
- *Mechanism:* training-free and pose-free. Warp to **several views spaced along the baseline**, forming a *frame matrix* of views × time. Denoise it alternately along the time and view directions, with "disocclusion boundary re-injection" [paper].
- *Why it matters:* this is the one method that makes a fill consistent across **both time and viewpoint**, which is what a head-tracked window needs.

**StereoCrafter-Zero**: arXiv 2411.14295. Zero-shot, with a "noisy restart" and iterative latent harmonisation to reduce flicker [abs].

**ImmersePro**: arXiv 2410.00262. Implicit disparity, the YouTube-SBS dataset; gains of 11.8% L1, 6.4% SSIM and 5.1% PSNR over stereo-from-mono [abs].

**SpatialMe**: arXiv 2412.11512, JD.com. Depth-warp plus multi-branch "blend-inpainting", with **disparity expansion against foreground bleeding**, and the StereoV1K dataset [sec, search summary].

**Mono2Stereo**: arXiv 2503.22262, CVPR 2025 [sec for venue]. A benchmark plus the Stereo-IoU metric. It finds that warp-then-inpaint pipelines distort the image and one-stage pipelines weaken the stereo effect [abs].

**M2SVid**: arXiv 2505.16565, 3DV 2026.
- *Mechanism:* SVD conditioned on the left view, the warped right view and the disocclusion mask, with full attention for the disoccluded pixels. It is trained end-to-end *without iterative diffusion steps*.
- *Evidence:* ranked best 2.6× more often than the runner-up, and 6× faster [sec, search summary].

**Eye2Eye**: arXiv 2505.00135, Google. Skips depth entirely: a text-to-video model is turned into a "shifted view" generator. The motivation is that single-layer depth fails on specular and transparent surfaces [abs].

**StereoWorld**: arXiv 2512.09363. An end-to-end video generator with geometry regularisation and an 11M-frame stereo dataset [abs].

**StereoPilot**: arXiv 2512.16915, Kling.
- *Mechanism:* "diffusion as feed-forward", predicting the target view in one step with no depth map [abs].
- *Limits:* 81 frames at 832×480, ~23 GB VRAM [repo].
- *Licence:* **MIT** [repo].

**αDepth**: arXiv 2606.00386, May 2026. Estimates **layered colour and depth at soft boundaries** such as hair and defocus, to stop background bleeding in stereo conversion [abs]. Relevant to how moebius builds the fringe of each silhouette.

**Geometric Reciprocity**: arXiv 2607.05354. Self-supervised stereo inpainting from monocular video (Section 2c).

**Elastic3D** (arXiv 2512.14236) and **DreamStereo** (arXiv 2604.12270): found by search, not read.

**How this family gets temporal consistency:**
1. A video diffusion backbone with overlapping or autoregressive windows.
2. Joint denoising across views and time (SVG).
3. One-step or feed-forward models, which remove sampling noise between frames (M2SVid, StereoPilot).

None of them paints a world-anchored canvas. They can skip it because the target is **one fixed extra view about 6 cm away**. Moebius needs a **continuous range of views** chosen at runtime, so it must store a texture rather than a video per view. That is why the canvas approach suits us better than the stereo-conversion approach.

---

### 5. Camera-controlled re-rendering and 4D reconstruction

**ReCamMaster**: arXiv 2503.11647, ICCV 2025 [sec for venue].
- *Mechanism:* Wan2.1 conditioned on the source video by frame concatenation, trained on an Unreal Engine multi-camera dataset; 384×672 [paper].
- *Code:* MIT [repo].

**TrajectoryCrafter**: arXiv 2503.05638. A dual-stream model on CogVideoX-Fun-5B that takes point-cloud renders plus the source video; 49 frames at 384×672 [paper]. Needs ≥28 GB [repo]. Limitation: "struggles to synthesize very large-range trajectories" [paper].

**GEN3C**: arXiv 2503.03751, CVPR 2025.
- *Mechanism:* a 3D cache as above; 14 frames take about 30 s on an A100 [paper]. With dynamic content it "relies on a pre-generated video to provide the motion" [paper].
- *Compute:* ~43 GB even with offloading [repo].
- *Licence:* code Apache-2.0; weights under the **NVIDIA Open Model License** [repo].

**EPiC** (arXiv 2505.21876): anchor-video ControlNet [abs]. **Uni3C** (arXiv 2504.14899): point-cloud control plus SMPL-X human control, 50.8 GB with offload [repo]. **ReCapture** (arXiv 2411.05003): masked video fine-tuning [abs]. **DepthDirector** (arXiv 2601.10214): argues that warp-and-inpaint falls into an "Inpainting Trap" and conditions on warped *depth* instead [abs].

**SEE4D**: arXiv 2510.26796, Eurographics 2026. Renders to **a bank of fixed virtual cameras** instead of one trajectory, with a view-conditional video inpainter and spatio-temporal auto-regression [abs]. This is structurally the closest to "precompute a grid of head poses".

**Shape of Motion**: arXiv 2407.13764. 3D Gaussians whose motion is a combination of SE(3) motion bases, fitted from monocular depth and 2D tracks [abs]. **MIT** [repo].

**MoSca**: arXiv 2405.17421, CVPR 2025 [sec for venue]. A 4D motion scaffold plus Gaussian fusion, with camera poses optimised during fitting [abs].

**Newer generative 4D work** that fills unseen regions with video diffusion, then distils the result into 4D Gaussians:
- **Vivid4D** (arXiv 2504.11092, ICCV 2025): warp to new views, then video-inpaint them [abs].
- **ViDAR** (arXiv 2506.18792) [abs].
- **World from Motion** (arXiv 2607.01202, July 2026) [abs].
- **C4G** (arXiv 2605.31595): feed-forward, pose-free [abs].

**Could the app render a 4D representation instead of layers?** In principle yes, since Gaussian splats render in WebGL. In practice not yet, for three reasons:
1. Per-clip fitting takes minutes to hours ("on the order of hours", per the CogNVS paper [paper]).
2. Monocular 4D is fragile on casual clips, and hidden regions still need a generator, as every 2025–26 paper above adds one.
3. The asset per frame is far larger than a few RGBD layers.

The camera-controlled video models are *offline samplers*, not representations. Their realistic use in moebius would be to bake a small set of offset views per clip (the SEE4D or SVG frame-matrix idea), then fuse the extra observations into the plates. That is costly (28–50 GB-class GPUs) and it does not guarantee consistency between the baked views.

---

### 6. Dynamic objects (people)

What changes each frame for a moving person, from the viewer's side:
1. **The background behind the person.** For a static camera, this is revealed over time as the person moves, so it is not a per-frame problem (Section 8b).
2. **The person's own middle surfaces**: the gap between the legs, an arm in front of the torso, a hand in front of the body. These change every frame and must be filled per frame, but *coherently*.
3. **The person's back and sides.** These are almost never needed at head-tracking offsets of a few centimetres.
4. **Effects**: shadows and reflections on the background plate.

Relevant methods:

**TACO**: arXiv 2503.12049, ICCV 2025 [sec for venue].
- *Mechanism:* SVD (14-frame version) fine-tuned for video amodal completion of a prompted object, with progressive curriculum training on synthetic occlusions [paper][repo].
- *Code:* GitHub; no licence file found. Training uses 8×80 GB [repo].

**Diffusion-VAS**: arXiv 2412.04623, CVPR 2025. Two-stage amodal *mask* then amodal *RGB*, from a video diffusion model conditioned on modal masks plus pseudo-depth; up to +13% amodal segmentation in occluded regions [sec, search summary]. Code at GitHub Kaihua-Chen/diffusion-vas [sec].

**Temporally consistent amodal completion for human-object interaction**: arXiv 2507.08137, ACM MM 2025 [sec].

**Omnimatte family and ROSE / UnderEraser / SVOR (above).** These are the tools for moving a person's *shadow* out of the background plate. Otherwise the shadow gets baked into the plate or leaks into the source layer.

**Per-object canonical space**: Deformable Sprites / CoDeF. A person-layer atlas can hold appearance that is consistent across frames, such as clothing texture. It cannot hold what is behind an arm that moves.

**What must stay per-frame:**
- The source layer: real pixels and consistent depth for each frame, using VDA or MegaSaM rather than monocular DA3.
- The person's matte (SAM 2 video, which moebius has already planned).
- The person's middle-surface fills.

Everything else can be static.

---

### 7. Consistency tricks if we keep an image model (SD or LaMa)

**Rerender-A-Video**: arXiv 2306.07954, SIGGRAPH Asia 2023 [sec for venue]. Translate keyframes with cross-frame constraints, then propagate with patch matching and blending (EbSynth-style) [abs].

**FRESCO**: arXiv 2403.12962, CVPR 2024 [sec for venue]. Adds intra-frame and inter-frame correspondence constraints plus an explicit feature update, with keyframes and propagation [abs]. **S-Lab non-commercial** [repo].

**TokenFlow**: arXiv 2307.10373, ICLR 2024 [sec for venue]. Edit keyframes jointly, then propagate *diffusion features* along nearest-neighbour correspondences [abs]. MIT [repo].

**Noise warping:**
- **How I Warped Your Noise** (ICLR 2024; arXiv 2504.03072 listing) [sec].
- **Go-with-the-Flow** (arXiv 2501.08331, CVPR 2025): real-time flow-warped noise used to fine-tune video models [abs].
- The **Warped Diffusion** paper (arXiv 2410.16152, NeurIPS 2024 [sec for venue]) quotes the ∫-noise authors: noise warping has "limited impact on temporal coherency" for *latent* models, and "all the noise schemes produce temporally inconsistent results" [paper].
- Warped Diffusion itself adds test-time equivariance guidance to SDXL and does video inpainting. It needs a fine-tuned SDXL and takes about 5 minutes per 2-second clip on an A100 [paper].

**What to take from Section 7:**
- Shared or warped noise is **not enough** for SD latent inpainting.
- Cross-frame attention and keyframe propagation help, but they are soft constraints.
- **Painting once in canonical space** (CoDeF / StableVideo / a world-anchored canvas) is the only trick that gives *exact* consistency. It is the right way to keep SD in the pipeline for static layers.

---

### 8. Synthesis: recommended pipelines

#### The principle

Sort every hidden pixel of every plate into one of three classes:
- **(i) Seen elsewhere.** Copy it in by reprojection.
- **(ii) Never seen, static.** Paint it once in a stationary frame.
- **(iii) Never seen, changing.** Fill it with a video model in the object's frame.

Stability follows from that order. Class (i) is real data. Class (ii) is exactly stable by construction. Class (iii) is only as stable as the video model.

#### (a) Static scene, moving camera

1. **Geometry.**
   - Run DA3 in multi-view/pose mode over the clip (DA3-Streaming for long clips). Use DA3-Base/Small if licensing matters; Large/Giant are non-commercial.
   - Alternatives: VGGT-Commercial or MapAnything-Apache.
   - This gives poses and depth maps that agree with each other. Per-frame monocular depth would make the plates' depth shimmer.
2. **World-anchored layers.**
   - Choose keyframes. For each, build the layered representation the app already makes: source, plates, smooth depth continuation.
   - Then lift the plates into **world space** as textured depth surfaces.
   - Plates must be defined against the world, because which silhouette hides what changes as the camera moves. The hidden set is the union, over the clip, of everything that becomes disoccluded within the head-offset range around each frame's camera.
3. **Copy seen pixels.** For each plate texel, project into all frames. Use a z-test against that frame's depth to confirm the texel was really visible there. Take a robust average (median) with per-frame gain and offset matching.
   - The z-test is where the exact-mask lesson still applies: never copy pixels that fail the depth test.
   - Where a later frame saw the real surface, **replace the smooth depth continuation with the observed depth**. This removes parallax error inside the layer.
4. **Paint the never-seen texels once**, in canvas (plate) space, far surface first, then middle, as today. LaMa for stability; SD plus depth ControlNet only where structure is needed.
5. **Render.** Each output frame renders the real source layer for that frame, plus the fixed world plates from that frame's camera and the head offset.
6. **Lighting and exposure.** Store the canvas as a base texture. Add a smooth multiplicative gain per frame, estimated from the visible ring around each hole: the Hashing-NVD residual idea. This absorbs auto-exposure and slow light changes without re-painting.

**Where the user's proposal is right:** in (a) it *is* this pipeline. SD runs per static layer, once, and everything is composited and rendered at every pose. No SD pass per frame.

**Where it breaks:**
- **(1) Parallax inside one layer during a large move.** A single 2D plate with a smooth depth guess will visibly slide against the true background once the camera translates more than a small fraction of the depth range. Fix: world-anchored 3D plates, plus observed depth taking over from the guessed depth (step 3).
- **(2) Stale painting.** If a region painted at time t is later *seen*, the painting is visibly wrong from that point on. Fix: copy seen pixels first, and paint only what is never seen in the whole clip.
- **(3) Lighting changes** such as clouds, a light switched on, or auto-exposure. Fix: the gain field. Strong changes need a video model.
- **(4) Layers that are not static**: water, foliage, screens, people. These move to (b) or (c).

#### (b) Moving people, static camera

1. Per-frame masks from SAM 2 video. Consistent per-frame depth from Video Depth Anything; its Small model is Apache-licensed.
2. **One background plate for the whole clip.**
   - Take a temporal median of background pixels over the frames where no person covers them. That is the classic clean-plate method.
   - Paint the pixels a person covered for the *whole* clip **once** (LaMa/SD) on that single image.
   - The user's proposal is exactly right here.
3. **Shadows and reflections**: run an effect-aware remover to get a clean plate and a shadow layer, rather than baking the shadow into the plate. Candidates:
   - ROSE (Apache-2.0).
   - The Gen-Omnimatte public CogVideoX/Wan models (Apache-2.0).
   - Alternatives: EasyOmnimatte, OmnimatteZero.

   For a static camera, a cheap alternative also works: accept that shadows stay in the source layer, and only the person's colour and depth sit in front.
4. **The person layer stays per-frame**: real pixels plus video depth.
   - Middle surfaces (legs gap, arm over torso) need a **video** fill in a person-stabilised crop. Candidates: MiniMax-Remover / DiffuEraser / ProPainter on the person layer's hole video, or TACO / Diffusion-VAS for true amodal completion.
   - At small head offsets these slivers are thin. ProPainter- or LaMa-class continuation may be enough, and it is more stable than generation.
   - Do **not** run image SD per frame here. That is the known flicker source.

#### (c) Moving camera and moving people

- Do (a) for the static world, with people masked out *before* pose estimation. DA3 assumes a static scene; MegaSaM tolerates motion.
- Do (b) steps 3–4 for each person, in person-tracked crops.
- Pixels behind a person are handled by the world canvas: most are seen from other camera positions or at other times.
- A video inpainter is the fallback for anything left: background regions that are dynamic *and* never seen.
- 4D Gaussian reconstruction plus generative fill (Shape of Motion/MoSca + CogNVS/Vivid4D/World-from-Motion) is the principled all-in-one alternative. Revisit it once feed-forward 4D (C4G-class) matures. It is not the first thing to build.

#### What should replace or augment per-layer SD

| Content | Paint once? | Tool |
|---|---|---|
| Static, seen elsewhere in the clip | no paint | 3D reprojection + z-test + median |
| Static, never seen | yes, once, world space | LaMa first; SD+depth ControlNet only where needed |
| Static but lit differently over time | once + gain field | multiplicative residual per frame |
| Dynamic background (water, foliage) | no | video inpainter on the plate video |
| Person's middle surface | no | video inpainter / amodal video model in a person crop |
| Shadows / reflections of people | no | ROSE / Omnimatte-family |

---

### 9. The experiments that decide it (run on our own clips)

**Experiment 1: coverage.** How much actually needs painting?
- Take 4–6 of our clips: handheld walk-past, slow pan, tripod with a person, handheld with a person.
- Run DA3 multi-view (people masked) to get poses and depth. For each frame, render the app's disocclusion mask at the maximum head offsets (left, right, up, down).
- For each disoccluded plate pixel, test whether any other frame saw that 3D point (z-test within a tolerance).
- Report the fraction seen, per clip and per offset.
- *How to read it:* if most disoccluded pixels are seen elsewhere (for example >70–80%) on handheld clips, the world canvas plus reprojection path clearly wins. Painting drops to the remainder, which is painted once. If coverage is low (tripod, tiny moves), the problem reduces to case (b): one clean plate plus a video fill for the dynamic parts.
- *Cost:* hours of scripting, no new models. It also checks whether DA3's poses and depth are good enough on our footage, because the reprojected seen pixels will visibly misalign if they are not.

**Experiment 2: stability shoot-out, with free ground truth.** Same clips, four arms:
- **A.** Per-frame LaMa (and SD) on the per-frame plate. This is today's tool run naively.
- **B.** World canvas: reprojected seen pixels, plus LaMa painted once for the never-seen.
- **C.** The plate hole video filled by one video inpainter (MiniMax-Remover or DiffuEraser; ROSE or VACE-Wan if the licence matters).
- **D.** B for static content plus C for dynamic.

Measure two things, both **inside the hole only**; CLIP temporal consistency is saturated and useless here:
1. **Warp error inside the hole.** Reproject frame t's filled plate into frame t+1 with the known geometry. Take the mean absolute difference, at a fixed head pose and across a sweep of head poses.
2. **Revealed-truth error.** Pixels hidden at t but *visible* at t+k give ground truth for free. Hold those frames out of the copy step, fill, then compare. This is the same self-supervision trick used by Geometric Reciprocity and CogNVS.

Add a blind A/B viewing on the head-tracked display, because the numbers will not capture "identity change" as well as eyes do. This experiment decides whether a video inpainter is needed beyond the dynamic layers, and which one.

---

### 10. Licence quick reference

Checked in repo LICENSE or README files unless marked otherwise.

- **Permissive:**
  - DA3-Small/Base/Metric/Mono (Apache-2.0).
  - VDA-Small (Apache-2.0).
  - MegaSaM code (Apache-2.0).
  - VGGT-1B-Commercial.
  - MapAnything Apache model.
  - VACE-Wan (Apache-2.0).
  - ROSE (Apache-2.0).
  - Gen-Omnimatte public (Apache-2.0).
  - ReCamMaster code (MIT).
  - StereoPilot (MIT).
  - LNA (MIT).
  - Shape of Motion (MIT).
  - TokenFlow (MIT).
  - GEN3C code (Apache-2.0); its models are under the NVIDIA Open Model License.
- **Non-commercial:**
  - ProPainter and FRESCO (S-Lab).
  - E2FGVI (CC BY-NC).
  - DA3-Large/Giant (CC BY-NC).
  - VDA-Base/Large (CC BY-NC).
  - MonST3R and CUT3R (CC BY-NC-SA).
  - π³ weights (CC BY-NC).
- **Conditional:**
  - DiffuEraser is Apache-2.0 but depends on the ProPainter prior.
  - VideoPainter is under the CogVideoX licence.
  - DepthCrafter is under a Tencent licence.
- **No licence file found:** MiniMax-Remover, StereoCrafter, TrajectoryCrafter, EPiC, TACO, CoDeF.

---

### Sources

Full texts were read through the Hugging Face arXiv mirror; abstracts through the Hugging Face papers API; READMEs and licences through raw.githubusercontent.com.

- Generative Omnimatte https://arxiv.org/abs/2411.16683 · public code https://github.com/gen-omnimatte/gen-omnimatte-public
- EasyOmnimatte https://arxiv.org/abs/2512.21865 · OmnimatteZero https://arxiv.org/abs/2503.18033 · OmnimatteRF https://arxiv.org/abs/2309.07749 · DBL-Diffusion https://arxiv.org/abs/2607.25802 · Neural Atlas Graphs https://arxiv.org/abs/2509.16336
- Omnimatte3D https://openaccess.thecvf.com/content/CVPR2023/html/Suhail_Omnimatte3D_Associating_Objects_and_Their_Effects_in_Unconstrained_Monocular_Video_CVPR_2023_paper.html · Deformable Sprites https://openaccess.thecvf.com/content/CVPR2022/html/Ye_Deformable_Sprites_for_Unsupervised_Video_Decomposition_CVPR_2022_paper.html
- LNA https://arxiv.org/abs/2109.11418 · CoDeF https://arxiv.org/abs/2308.07926 · INVE https://arxiv.org/abs/2307.07663 · Hashing-NVD https://arxiv.org/abs/2309.14022 · StableVideo https://arxiv.org/abs/2308.09592
- ProPainter https://arxiv.org/abs/2309.03897 · E2FGVI https://arxiv.org/abs/2204.02663 · FGT https://arxiv.org/abs/2208.06768
- DA3 https://arxiv.org/abs/2511.10647 · VDA https://arxiv.org/abs/2501.12375 · DepthCrafter https://arxiv.org/abs/2409.02095 · MegaSaM https://arxiv.org/abs/2412.04463 · MonST3R https://arxiv.org/abs/2410.03825 · CUT3R https://arxiv.org/abs/2501.12387 · VGGT https://arxiv.org/abs/2503.11651 · π³ https://arxiv.org/abs/2507.13347 · MapAnything https://arxiv.org/abs/2509.13414
- DiffuEraser https://arxiv.org/abs/2501.10018 · VACE https://arxiv.org/abs/2503.07598 · FloED https://arxiv.org/abs/2412.00857 · AVID https://arxiv.org/abs/2312.03816 · CoCoCo https://arxiv.org/abs/2403.12035 · MiniMax-Remover https://arxiv.org/abs/2505.24873 · VideoPainter https://arxiv.org/abs/2503.05639 · ROSE https://arxiv.org/abs/2508.18633 · EraserDiT https://arxiv.org/abs/2506.12853 · SVOR https://arxiv.org/abs/2603.09283 · UnderEraser https://arxiv.org/abs/2604.01693 · D2DF https://arxiv.org/abs/2607.14976 · FFF-VDI https://arxiv.org/abs/2408.11402 · GenProp https://arxiv.org/abs/2412.19761 · PROVE https://arxiv.org/abs/2605.14534
- StereoCrafter https://arxiv.org/abs/2409.07447 · SVG https://arxiv.org/abs/2407.00367 · StereoCrafter-Zero https://arxiv.org/abs/2411.14295 · ImmersePro https://arxiv.org/abs/2410.00262 · SpatialMe https://arxiv.org/abs/2412.11512 · Mono2Stereo https://arxiv.org/abs/2503.22262 · M2SVid https://arxiv.org/abs/2505.16565 · Eye2Eye https://arxiv.org/abs/2505.00135 · StereoWorld https://arxiv.org/abs/2512.09363 · StereoPilot https://arxiv.org/abs/2512.16915 · αDepth https://arxiv.org/abs/2606.00386 · Geometric Reciprocity https://arxiv.org/abs/2607.05354 · Elastic3D https://arxiv.org/abs/2512.14236 · DreamStereo https://arxiv.org/abs/2604.12270
- ReCamMaster https://arxiv.org/abs/2503.11647 · TrajectoryCrafter https://arxiv.org/abs/2503.05638 · GEN3C https://arxiv.org/abs/2503.03751 · EPiC https://arxiv.org/abs/2505.21876 · Uni3C https://arxiv.org/abs/2504.14899 · ReCapture https://arxiv.org/abs/2411.05003 · DepthDirector https://arxiv.org/abs/2601.10214 · SEE4D https://arxiv.org/abs/2510.26796
- Shape of Motion https://arxiv.org/abs/2407.13764 · MoSca https://arxiv.org/abs/2405.17421 · Vivid4D https://arxiv.org/abs/2504.11092 · CogNVS https://arxiv.org/abs/2507.12646 · ViDAR https://arxiv.org/abs/2506.18792 · World from Motion https://arxiv.org/abs/2607.01202 · C4G https://arxiv.org/abs/2605.31595
- TACO https://arxiv.org/abs/2503.12049 · Diffusion-VAS https://arxiv.org/abs/2412.04623 · HOI amodal https://arxiv.org/abs/2507.08137
- TokenFlow https://arxiv.org/abs/2307.10373 · Rerender-A-Video https://arxiv.org/abs/2306.07954 · FRESCO https://arxiv.org/abs/2403.12962 · Go-with-the-Flow https://arxiv.org/abs/2501.08331 · Warped Diffusion https://arxiv.org/abs/2410.16152 · How I Warped Your Noise https://arxiv.org/abs/2504.03072
