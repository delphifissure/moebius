# R5 — The layered-decomposition stack: what the 2025–2026 papers give us, the stack they suggest, and how to test it on our truth (2026-09-13)

Prompted by the user's list (RevealLayer, Referring Layer Decomposition, Amodal SAM, SAMEO, Lift3Dreamer, DepthLab,
MoGe-3, the video NVS models, the 3–4-layer representations) and the proposal: *run the generated layers through a depth
model and normalise against the full-scene depth map*. **What could be read from here:** GitHub and Hugging Face pages
(RevealLayer, MoGe, DepthLab, Lift3Dreamer) and search abstracts; **the four PDFs the user attached (Amodal SAM, SAMEO,
Lift3Dreamer, Referring Layer Decomposition) were read in full** (kept in `research/papers/`; §1b, §1c), and **the RevealLayer
paper arrived afterwards as text through the user's Google Drive link and was read in full** (§1d; text kept as
`research/papers/RevealLayer_2026_text.txt`; the figures did not come through, so the visual results are known only from the
captions). **What could not be read:** arXiv, OpenReview, alphaXiv and the github.io project pages are blocked by this
environment's egress policy, so MoGe-3's paper remains *(abstract only)*.

## 1. The papers, one paragraph each, with what matters for us

**RevealLayer (May 2026; code Apache-2.0).** *(README paragraph; the paper itself is in §1d.)* Decomposes one RGB image into
*multiple RGBA layers*, recovering occluded content
and the background behind it; built as LoRA + a layer positional embedding + a refiner on **FLUX.1-dev**, with a transparent
VAE decoder; trained on RevealLayer-100K, evaluated on RevealLayerBench (200 curated images). The README gives no layer
count, no resolution, no depth and no ordering statement. **Licence caveat that answers your question:** the RevealLayer
code is Apache-2.0, but it runs on FLUX.1-dev, whose weights are under the *FLUX.1 [dev] Non-Commercial License*; commercial
use needs a licence from Black Forest Labs (they sell one) or a swap of the base model. The dataset is "for research use".
So: open to try today, not open to ship as is.

**Referring Layer Decomposition, RLD (ICLR 2026, ByteDance).** Predicts a *complete* RGBA layer of a referred object (points,
boxes, masks, text, or combinations) from one image, hidden parts reconstructed; RefLade dataset of 1.11 M image–layer–prompt
triplets plus 100 K curated layers; baseline model RefLayer. Code and weights **"coming soon"** on the project page. *(abstract
only.)* For us it is the per-object variant of RevealLayer: ask for "the bear" and get the bear whole.

**Amodal SAM (Apr 2026).** SAM extended with a Spatial Completion Adapter to predict the *amodal mask* (the full silhouette,
occluded parts included) for images and video, trained with synthesised occlusions (TAOS), with regional-consistency and
topological losses; state of the art with generalisation to unseen categories. Masks, not appearance. *(abstract only;
code status unknown.)*

**SAMEO — Segment Anything, Even Occluded (CVPR 2025).** SAM as a mask decoder behind any detector, predicting amodal masks;
Amodal-LVIS (300 K synthetic images) for training; zero-shot state of the art on COCOA-cls and D2SA. *(abstract only; code
status unknown from here.)*

**Lift3Dreamer (Mar 2026; weights on Hugging Face, 0.9 B, a Stable-Diffusion-inpainting pipeline).** A 2D inpainter fine-tuned
with pseudo-3D supervision: depth is estimated for single images, lifted to 3D, novel views simulated by random camera
motions, and the resulting *visibility masks* supervise the inpainter; a data-free pipeline (LLM + text-to-image) scales the
training set. Usage is the standard `StableDiffusionInpaintPipeline` (image, mask, prompt; 512 px default). Licence not
stated on the card (the base is SD inpainting: OpenRAIL-M). For us: an inpainter trained on masks shaped like ours.

**DepthLab (Dec 2024; Apache-2.0; weights on Hugging Face).** RGB + partial depth + mask → completed depth, built on Marigold
(SD2 latent diffusion) with a reference U-Net for RGB features feeding an estimation U-Net; keeps the known depth's scale
(the README's normalisation note: when the known depth's range does not cover the scene's, reduce the normalisation
scale); recommended 640–768 px inference; applications include 3D scene inpainting and sparse-view reconstruction. "How
did we miss it": R1 predates it by weeks in our reading order, and we were building the depth of the hidden layer from the
depth map alone by design. Its **input is exactly what we have** (colour, the visible depth, the band mask).

**MoGe-3 (released 18 Aug 2026; code MIT, weights `Ruicheng/moge-3-vitl` on Hugging Face under MIT, DINOv2 Apache).**
Metric point map + depth + normals + intrinsics (FOV) + validity mask from one image; Self-Guided Sparse 3D Refinement moves
refinement from the image plane to a sparse voxel space, so thin and elongated structures and boundaries come out clean at
linear cost in occupied voxels; reported to beat Depth Pro, Depth Anything 3 and InfiniDepth on fine-detail metrics at strict
thresholds. *(abstract only for the numbers.)* Flexible aspect ratios 2:1–1:2; FOV can be given or estimated. **Correction to
S24:** MoGe-2 *was* in the S8 bake-off (S5 §11c): on the troll — a photograph of a painting — both metric models (Depth Pro,
MoGe-2) answered the metric question honestly and returned a flat object five metres away (MoGe-2: 28 cm of relief), which is
why the relative DA3-Mono won for a portal that wants the scene *inside* the picture. MoGe-3 must be run in its
affine-invariant mode (the relative point map, not the metric one) for illustrations, or the same failure returns; the
weights are fetchable from here, so the bake-off can be repeated on the six pictures and the kit.

**GEN3C, Stable Virtual Camera, ViewCrafter.** Camera-controlled video/NVS diffusion that completes views along a path; SEVA
under the Stability Community licence; GEN3C under NVIDIA's licence (check); ViewCrafter code Apache (its DynamiCrafter base
Apache). Heavy; the fill for the envelope's rim, not the representation.

**Layered representations.** Multi-Layer Gaussian Splatting (ACM MM 2025): base layers for the visible, occlusion layers
for the hidden, from one image; WonderWorld: foreground / background / sky layers in < 10 s; Broxton et al. 2020: a small
fixed number of RGBA + depth layers in texture atlases, browser-rendered. The field converged on 3–4 layers, which is what
plate 1 + plate 2 + sky already is.

## 1b. The three attached papers, read in full

**Amodal SAM (Zhang, Tian, Tao, Tang, Yu, Pei; arXiv 2604.20748, 22 Apr 2026; IEEE TIP submission).** Input: the image and a
*box* on the target (two points inside the visible part work as well: KINS 84.74/58.52 vs 85.43/59.27 with boxes). Output: a
binary **amodal mask** — the object's full silhouette, occluded part included — nothing else (no appearance, no depth). Method:
SAM's ViT encoder with a gated *Spatial Completion Adapter* (concatenate the ROI prior mask with the features, gated
convolution, three iterations) at shallow, middle and deep layers; prompt encoder and mask decoder frozen; trained on
occlusions synthesised on SA-1B (TAOS: paste a random object over the target, blur the seam, a VLM rejects bad composites);
losses: Dice + 10·BCE, a regional-consistency term (cosine similarity between the visible and occluded regions' pooled
features) and an adversarial "topological" regulariser (a discriminator on mask + image). Numbers: closed-domain KINS
mIoU_full 88.79 / mIoU_occluded 63.12, COCOA 84.27 / 59.94, COCOA-cls 87.65 / 54.34 (PLUG: 88.10 / 61.42 on KINS); zero-shot
COCOA-cls 83.18 and D2SA 91.62 against SAMBA 81.82 / 90.87 and pix2gestalt 79.08 / 81.82; video through SAM-2 (FISHBOWL
92.74 / 83.36). The occluded-region IoU is the honest number and it is 54–63: half to two thirds of the hidden silhouette is
recovered on average. No code statement in the text. *For us:* the per-object amodal silhouette on a box prompt — exactly the
input the elastica completion of R4 §1 would compute by hand, learned instead; the decision "is what is behind this rim the
same object?" (self-sampling) and the shape of a plate-2 object both come from it.

**SAMEO (Tai, Shih, Sun, Wang, Chen; CVPR 2025).** *EfficientSAM* with only the mask decoder fine-tuned (encoder and prompt
encoder frozen); prompt = a box from any detector, modal or amodal (training draws both at random — the "random" variant
scores best, AP 54.2); output = amodal mask + a predicted IoU used to re-rank detections. Data: Amodal-LVIS, 300 K synthetic
images from LVIS/LVVIS with *paired* occluded and unoccluded versions of each instance (training on occluded-only data
made the model segment the background object behind the prompted one — their Fig. 6); a cleaned collection of 1 M images /
2 M instances across ten datasets. Zero-shot: COCOA-cls AP 54.4 (RTMDet front end), D2SA 75.0 (CO-DETR), against AISFormer
40.6 / 66.3 trained in-domain. Stated failures: incomplete amodal masks, rough edges, a modal mask returned when objects
overlap heavily (points beside the box help). *For us:* the lighter of the two amodal-mask models, needs a detector for
the boxes; same role as Amodal SAM, lower ceiling, faster.

**Lift3Dreamer (Liang, Fu, Liu, Zhang; *Fundamental Research* 2026, CC BY-NC-ND; weights on Hugging Face).** The
architecture is *Stable Diffusion 2.0 inpainting*, 512 × 512, InstructPix2Pix-style extra input channels for the mask and
the masked latent. The training trick is the one that matters to us: **warp-back masks**. Estimate depth (ZoeDepth, metric),
lift, forward-warp to a random camera, then backward-warp the visible pixels to the source view; the pixels that do not
survive the round trip are the structured holes H₀, and the model is trained to reconstruct the source image from
(I₀ with holes, H₀, prompt). Data-free: 2 000 GPT-4 prompts → 200 000 SDXL images at 1024² → ZoeDepth; 8 × V100 for 100 k
steps. For continuous trajectories they add a **depth completion network** Ω(D′, H, I) for the inpainted pixels and build a
mesh that *discards long edges by thresholding depth discontinuities "following AdaMPI"* — the same gap rule as MoGe's
`depth_map_edge` (§2). Numbers on RealEstate10K (same depth and cameras for all): LPIPS 0.129 / PSNR 24.41 / SSIM 0.840
against PowerPaint 0.131 / 24.19 / 0.826, RePaint 0.132 / 24.02 / 0.820, SD-2 inpainting 0.160 / 22.01 / 0.775, AdaMPI
0.145 / 23.76 / 0.802; dropped into RealmDreamer: CLIP 32.02, depth-Pearson 0.93 vs 31.69 / 0.89. *For us:* (1) its holes
are ours — forward-warp reveals — so it is the first inpainter to try on the atlas; (2) its Ω is DepthLab's job; (3) the
gains over generic inpainters are real but modest (LPIPS 0.131 → 0.129), so the *mask shape* is worth a few per cent, not a
transformation; (4) 512² on SD-2 is a resolution ceiling for a 1 008-px atlas (tile, or reproduce the recipe on a larger base);
(5) **the recipe is reproducible on our own statistics**: our sweep produces the exact hole masks of *our* envelope (wide,
one-sided, up to 90°), so a FLUX-Fill- or SD-XL-inpainting LoRA fine-tuned with warp-back masks from our band generator would
be "Lift3Dreamer trained on the portal's occlusions" — a day of data generation from the six pictures plus any photo set,
and a few GPU-hours. That is the one place in this stack where a small amount of our own training buys something nobody
else's checkpoint has.

## 1c. Referring Layer Decomposition, read in full (Chen, Shen, Xu, Yuan, Zhang, Niu, Wen; ByteDance; ICLR 2026)

**What the task is, precisely.** *One* complete RGBA layer per prompt — a point, box, mask, text, or combinations — not a full
decomposition of the picture; their own suggested route to a full decomposition is "an MLLM describes the image and boxes
each object, RefLayer is applied per box" (Appendix C.1). "Background" is itself a prompt (a blue canvas), and the
background layer is the picture with the referred foreground removed.

**The model (RefLayer).** Stable Diffusion 3 initialised from **UltraEdit** (an editing model; SD3 or InstructPix2Pix
initialisations score lower, Table 5); the image and a *colour-coded prompt canvas* (blue = background, green box, red visible
mask, Gaussian heat-map for a point) are VAE-encoded and channel-concatenated with the noisy latent; a separate **alpha
decoder** (a VAE-decoder clone with one output channel, trained with L1 on latents of layers blended over a jittered
checkerboard — a plain black backdrop made it overfit) gives the transparency. Training: 64 × A100, batch 1 024, 7 k steps on
the 1 M set, then the 100 K curated set.

**The data engine (how the ground-truth hidden appearance is made).** Six stages: pre-filter (RT-DETR, OWL-v2, in-house
classifiers); scene understanding (detector ensemble + GPT-4o tagging grounded by Grounding-DINO, SAM-2 masks, OpenSeeD
panoptic, **Depth Anything V2 depth**); layer completion — Gemini-2.0 judges whether the object is occluded (90.3 %
precision, 56.1 % recall), then an inpainting mask is built **from the depth map: regions nearer than the instance's mean depth
are the likely occluders and are masked, background stuff excluded by the panoptic map**, and Bria's ControlNet inpainter
fills them with the class label as prompt; post-completion (SAM-2 refine, ViTMatte alpha); GPT-4o prompts; post-filter
(visible-region preservation, Gemini quality 1–5, CLIP semantic match). Success rate 70 % (MuLAn: 36 %); ~2 minutes per
image; audit: 74.7 % of foreground and 70.2 % of background layers "neutral or better"; **65 % of the engine's errors are
inpainting errors** (masks that include what should not change, identities not preserved — their Fig. 7), 20 % segmentation.
RefLade: 430 K images, average 1 831 × 1 437, 12 K categories, 872 K instances, occlusion rate 60.8 %, 95 % photographs
and 5 % stylised (paintings, cartoons included).

**Numbers.** Human-preference-aligned score (min-max-normalised mean of visible-region LPIPS, CLIP-directional completion
similarity, and FID of the layer blended on the clean background; Pearson 0.96 with human Elo): foreground 0.4813,
background 0.6682 for the best model; prompts: text alone 0.2403, point 0.4394, box 0.4719, mask 0.4842, **text + mask 0.4833
with the best occluded-region score 0.4403**. **Pass rate** (a human accepts at least one of K draws): background 28 % at K=1,
65 % at K=5, 74 % at K=10; foreground 45 / 74 / 79 %. Zero-shot amodal segmentation on COCOA from the alpha channel:
mIoU_occluded **38.83** (best prior zero-shot, pix2gestalt, 26.79; the in-domain PLUG / Amodal SAM reach 59–63 — different
regimes, same metric). Amodal completion on their own test set: HPA 0.4833 vs pix2gestalt 0.3397, MuLAn 0.3852. Nano Banana Pro
(Gemini 3) fails the task (does not preserve the visible pixels, no real alpha).

**Stated limits.** Shadows, reflections and other effects ignored; "mutual occlusion could be a problem when composing a
scene from multiple decomposed layers — a visibility mask for each layer should be given" (that is, they decompose, they do not
compose — the ordering is ours); part-level granularity absent; failures under severe occlusion, point-only prompts and
small objects. **Licence:** the paper's title page says "This work is for academic research purposes only"; code "will be
released" on the project page (not yet). Same class of hurdle as RevealLayer's FLUX-dev base.

**What it means for our stack.** (1) Our occluder masks are exact and pose-aware (the depth map, the band), so the
best-scoring prompt — text + mask — is available to us for free, and our sweep is a sharper version of the engine's own
"nearer than the instance's mean depth" mask. (2) The honest expectation for an automatic background completion is their
pass rate: about one in four first draws acceptable, three in four with ten draws — so the stage needs *several draws and a
selector*, and our scorecard (clone count, depth consistency against the plate, the magenta area at the far poses) is the
selector we already have instruments for. (3) The composition problem they leave open — visibility masks and ordering
between layers — is exactly what the plate, the ordering clamp and the arrival order do; the two halves fit. (4) Their
evaluation triad (preserve the visible, complete plausibly, blend faithfully) is a ready protocol for scoring any filler on
our atlas without truth.

## 1d. RevealLayer, read in full (360 AI Research; ICML 2026, PMLR 306; arXiv 2605.11818)

**Task as they define it.** Input: one image plus **user-specified bounding boxes**, one per instance to lift (B.3: one to
three boxes in the examples; the dataset caps at eight instances). Output: a *background layer* with every boxed instance
removed and its footprint, shadow and reflection completed, plus **one RGBA layer per box** with the instance's hidden parts
completed. Everything not boxed stays in the background. The text prompt is fixed ("Decompose the image into foreground and
background"); the boxes are the whole interface. There is no depth, no ordering and no composition step in the paper: the
layers come back as a set, and B.3 notes the model must be told which regions are foreground.

**Model.** FLUX.1 [dev] MM-DiT with a rank-64 LoRA, Prodigy optimiser (lr 1.0), 50 k iterations, batch 8, long side 1024.
The background and the N layers are one **variable-length token sequence** (image tokens ‖ background tokens ‖ layer-1 tokens
‖ … ) with a 3D-RoPE layer index, so N is free at inference. Two additions carry the paper: a **Region-Aware Attention** mask
(each layer's tokens attend to the whole input image but only to their own box's region of the other layers, so layer k cannot
copy layer j) and an **Occlusion-Guided Adapter** that injects the box geometry so the model knows *where* to complete. Losses:
flow matching plus a hard-constraint **alpha loss** (threshold τ 0.95, weight γ 1.5, pushes alpha to 0/1 away from the matte
edge) and an **orthogonality loss** between layer features (Eq. 15; B.5.1 shows it falling over the denoising steps toward the
ground truth's value). The transparent VAE is ART's TransVAE with its decoder fine-tuned on natural images ("XVAE"; B.4:
background PSNR 46.68 → 48.74, the foreground unchanged). B.5.2: giving all foreground layers the *same* initial noise helps
slightly (fg PSNR +0.18, FID −0.23) — they read it as a low-frequency-background / high-frequency-foreground prior.

**Data (Appendix A).** LAION-2B, GRIT-20M and internal images; Qwen3-VL for captions and instance lists, Florence-2 for boxes,
InstaOrder for the occlusion order, SAM-H masks refined by Qwen-Image-Edit, ViTMatte for the alpha; three pipelines
(real backgrounds with generated removals; Z-Image synthetic backgrounds with pasted instances; occlusion augmentation), an
LPIPS ≤ 0.1 filter against the source, ≤ 8 instances per image. 100 K training tuples; the benchmark is 200 curated images.
Figure 6: 54 % of the training images are *two-layer* (background + one instance), 20 % three, 15 % four, 5 % five, 5 % more;
categories human 32 %, indoor items 35 %, animals & plants 21 %, traffic 8 %, other 5 %.

**Numbers.** Object removal on OBER-Test, competitors given *effect masks* (shadow and reflection included) while RevealLayer
gets only the box: PSNR 30.16 / SSIM 0.9153 / LPIPS 0.0694 / FID 25.62, against ObjectClear 28.27 / 0.8657 / 0.0875 / 32.85
(Table 7). Layer decomposition on RevealLayerBench (Table 10): background PSNR 25.53 / LPIPS 0.1483 / FID 53.81, foreground
PSNR 32.13 / LPIPS 0.0217 / FID 18.42, SoftIoU 0.9432; the competitors on the same bench (main-text Table 2): CLD background
PSNR 19.75 / LPIPS 0.2293 / FID 127.77, foreground 26.42 / 0.0433 / 43.64, SoftIoU 0.8304, 97 s and 62 GB; Qwen-Image-Layered
background 16.85 / 0.3293 / 142.01, 418 s and 76 GB (no per-layer numbers, its layer count is not controllable). Q-Insight
scores (B.6, 1–5 by a vision-language judge): consistency 4.09 / fidelity 3.91 / editability 4.14 against CLD's 4.00 / 3.76 /
4.06. Stylised posters after a 4 k-step fine-tune on
PrismLayers (Table 8): PSNR 28.36 vs CLD 27.65, but CLD wins FID / IoU / F1. Matting on AIM500: MSE 0.0107. Human study
(B.7): three professional-evaluator scores, *layer count as requested* 99 %, *background quality* 85, *foreground quality* 90,
where background quality is scored 2 / 1 / 0 for "fully satisfactory / minor defects / unsatisfactory" on the completion of the
overlapped region and the fidelity of the visible region. Box robustness: 5–10 % box offsets degrade the result. **Cost: 122 s
and 60 GB of GPU memory per image** (main text, Table 4's setting) — a single-H100-class figure, not a consumer card.

**Stated limits.** Inaccurate boxes; heavy occlusion; transparent regions; dense repetitive textures. Nothing about thin or
porous objects, nothing about the completed content's *geometry*.

**How it compares with RLD for our purpose.** RLD returns one layer per prompt and reports pass rates (28 % first draw, 74 %
at ten); RevealLayer returns the whole set in one 122-s draw and reports 85 / 100 on background quality by a coarser
three-level human score. The two numbers are not the same scale, but they agree on the picture: the background completion is
the weak layer in both — RevealLayer's background FID 53.8 against its foreground 18.4, RLD's "background" prompt failing
most often. **Our band is exactly the background's hidden region**, so the layer stage's weakest output is the one we consume
most. That is the argument for several draws plus our selector regardless of which model, and for keeping the depth model
and the plate as the *verifier* of whatever comes back.

**What it means for our stack, concretely.** (1) Boxes from our depth sweep: an occluder's box is the bounding box of the
texels that own a far-side demand, which we already have per object from the arrival order — no manual input. (2) The
≤ 8-instance cap and the 54 % two-layer training prior mean pictures like the room scene (many small occluders) should be
lifted in *groups* of the largest demands, the rest left to the band inpainter. (3) The alpha loss makes hard alphas: fine for
our layers (we need a silhouette, not a matte) but it means porous canopies come back as solid or as noise — the P1–P6
scenes rendered as pictures are the test, as §4 already says. (4) Because the output is one texture per layer with no depth,
stage 4 (DepthLab or the peeled-composite depth + affine alignment) is unavoidable; RevealLayer's own results give no
opinion on it. (5) Licence: the paper adds nothing beyond the README — code Apache-2.0, base FLUX.1 [dev] non-commercial,
dataset research-only; the training recipe is public enough that a re-train on a permissive base (Qwen-Image, or SD3.5 under
its community licence) is a defined job, not a research question. (6) The 60 GB footprint rules out a laptop bake; it is a
server step or an API.

## 2. How the MoGe pages get such clean "displacement gaps"

From `moge/scripts/infer.py`: the mesh for visualisation and export is built with
`mask_cleaned = mask & ~utils3d.np.depth_map_edge(depth, rtol=threshold)` and `build_mesh_from_map(..., mask=mask_cleaned)`,
threshold 0.04 in the script (0.01 in the app). That is: **any face whose vertices differ in depth by more than 4 % is
removed**, and the sky/invalid mask is removed too. So at a depth discontinuity they draw *nothing* — no stretched triangle,
no skin — and the gap shows the viewer's background colour. The look is clean for four reasons: (1) no spaghetti ever
(a relative-depth edge test at mesh-build time); (2) small camera offsets in the demos (a few degrees, so the gaps are thin
slivers); (3) gaps rendered against a plain backdrop rather than against a wash; (4) sharp boundaries in the point map,
so the ambiguous ramp cells — which are where our fold decisions have to be made — are few.

Relation to ours: their test is our fold criterion made pose-independent with a relative constant (4 % of depth), which is
units-invariant (a ratio) but not parallax-aware (a 4 % step at the far plane opens no visible gap at any pose; a 4 % step
on a near face opens a wide one). Our A212/a102 fold test is the parallax-aware version and has no constant; the fold-alpha
of S25 is the same idea evaluated per fragment at the current pose. What they do that we do not: they *accept the gap* and
never fill it — they are showing geometry, not a portal. Our whole problem is what to put in the gap; theirs is to
render around it.

## 3. The proposal, examined: layers → per-layer depth → normalise against the scene depth

The idea: decompose the picture into complete RGBA layers (RevealLayer / RLD), run a depth model on each layer, align each
layer's depth to the full-scene depth map, and hand our pipeline a true layered depth image. It is the right shape, and
three things decide whether it works.

**(a) A depth model on an isolated RGBA layer does not see a scene.** Run on a cut-out object over transparency or black, a
monocular model returns object-relative geometry with arbitrary scale and, at the soft alpha edge and around inpainted
parts, halos. The fix is to run it on the **peeled composites** rather than on the layers: image₀ = the completed background
alone (a photograph with the foreground removed — exactly what the model was trained on), image₁ = background + the next
layer, and so on. Each composite is a plausible photograph, so the depth is well-behaved everywhere, including on the
hidden parts of the layer just added.

**(b) Normalisation against the scene depth is an affine alignment in disparity, per layer, over the visible pixels.** For
layer k, the pixels where it is visible in the original carry both the scene's depth (from the full-image map) and the
composite's depth; a robust least-squares fit of scale and shift in disparity space over those pixels (the standard
alignment used by every affine-invariant depth method) transfers the scene's scale to the layer, and the hidden pixels
inherit it. Edge cases: a layer with few visible pixels (a mostly hidden object) gets a poor fit — fall back to the
occluder's order and our plane law; a background layer that is *all* visible except the band is the easy case (its fit is
exact and its hidden depth is the model's continuation of the wall — which is precisely the question DepthLab was built
to answer directly, see (c)); layers must respect **occlusion order** after alignment (a hidden pixel of layer k lies
behind layer k+1's pixel on the same ray by at least one quantum) — our a135 ordering clamp, applied between layers rather
than within one, enforces it and repairs the small violations that two independent fits will produce.

**(c) DepthLab is the shortcut for the background layer, and possibly for every layer.** Its inputs are the completed
layer's RGB, the known depth on the visible pixels, and the mask of the hidden ones; its output is the completed depth at
the known depth's scale by construction — no alignment step, no composite trick. The plane law is then the *verifier and
fallback*: where DepthLab's completion disagrees with the plane continuation by more than the law's tolerance on a planar
run, one of them is wrong, and on the kit we know which.

**What stays ours.** The band and envelope mathematics (what must be complete, to which angle, the tier), the ordering clamp,
the fold test and fold-alpha, the sky and margin handling, the bundle and the renderer. The layers replace the *placeholder
wash and the arrival-order plate 2*; they do not replace the plate's geometry contract.

## 4. The stack, as I would build it (advantages / disadvantages per stage)

| stage | tool | for | against |
|---|---|---|---|
| 1. depth of the photograph | DA3-Mono (today) → bake-off with **MoGe-3** (metric, FOV, thin structures) | MoGe-3 gives the metric frame R1 asked for and cleaner edges at the source | new bake-off (a day); MoGe-3 numbers are abstract-only from here |
| 2. what must be complete | our band / envelope contract, 90° plate-1 demand = the far-side set (S24) | closed-form, measured on truth | object sides and box walls not yet in the demand |
| 3. layers | **RevealLayer** for the whole picture, driven by boxes from our own sweep (≤ 8 instances per call; group the largest demands); **RLD** per object (text + mask prompts from our own masks) when its code lands; several draws + our selector; amodal masks (Amodal SAM / SAMEO) to decide self-occlusion and to prompt | complete hidden appearance, discrete objects — your "world of objects"; RevealLayer's background completion 85 / 100 by human score with boxes only, and it removes shadows and reflections with the object; RLD's pass rate 74–79 % at ten draws | FLUX-dev licence (RevealLayer) and "academic research purposes only" (RLD); **122 s and 60 GB per image** (server or API, not a laptop); the background layer is the weakest output of both models and it is the one we consume; hard alphas (τ 0.95) so porous canopies come back solid or as noise; ordering between layers is ours to do; boxes off by 5–10 % already degrade it |
| 4. depth of each layer — **measured in S26, the row is now split by class** | *background layers*: the **plane law** (exact on every continued surface; beats DA3, MoGe-3 and DepthLab on 19 of 19 kit scenes); *the object's own far side*: **the object's own front depth continued, under the ordering clamp** (S26 §3b: the zero-thickness rule ties or beats DA3/MoGe-3 + clamp on 15 of 17 scenes; the models' own contribution there was nil to negative — the earlier "models win 17/17" was the clamp); a depth model on the completed layer is optional, for the layer's amodal part only, untested; DepthLab only as a learned continuation of known depth where the surface is not planar (S15 hills 0.031 m vs the pure models' 1.2 m) | both halves exist and need no model; the kit scored them directly | the "normalise against the scene depth" step is exact only when the hidden range lies inside the visible range, and cannot be repaired when it does not (S32 hedge wall 0.72 m for every model, oracle 0.037); thin objects defeat the models (S5, S9, S11, P5/P6 own faces); MoGe-3 was run without its refiner (CUDA-only) |
| 5. ordering and cleanup | a135 ordering clamp between layers; fold test on every layer; despeckle line rule | already built | — |
| 6. colour where no layer model reached | Lift3Dreamer on the atlas with our mask (first), then the same warp-back recipe fine-tuned on *our* envelope's masks on a larger base; coherence-transport wash as the placeholder before it | masks shaped like ours; placeholder with structure; the recipe is reproducible | SD-2 at 512² is a ceiling; prompt discipline ("continue the surface"); a few GPU-hours for the fine-tune |
| 7. the frame | outpainting of the margin strips / box walls at the far depth | the beyond-frame holes (vermeer, room) | a second inpaint job |
| 8. delivery | Broxton-shaped RGBA + depth layers = our bundle with plate 2 promoted to real layers; reimport | industry-standard shape; browser-rendered | reimport not built |

## 5. The test that decides it, on truth we already have

The kit's env45 truth contains, per texel, the hidden layers' colour *and* depth (classes 2–5). So the depth stage can be
scored without waiting for RevealLayer: feed the truth's own completed layer colour (exact appearance) with the visible
depth and the hidden mask to **DepthLab**, and to **DA3 / MoGe-3 on the peeled composite + affine alignment**, and score the
hidden-layer depth against truth on S2, S15, S26, S16, S11, S7, P1–P4 — against the plane law's 0.000 / 0.184 / 0.000 /
0.000 medians and its layer-2 numbers. That separates "the depth stage works" from "the layer model works". Then
RevealLayer on the six pictures (FLUX-dev on the GPU we have for DA3; egress permitting for the weights), with three
readouts: clone count 0, the magenta spaghetti area at the far poses, and the SD-regions view showing every layer's
placeholder set. Two days for the depth test, one for the RevealLayer run if the weights can be fetched.

## 6. Order

1. DepthLab / MoGe-3 / DA3 hidden-depth test on the kit's truth layers (needs the weights; DA3 came through the cache before).
2. RevealLayer on the six pictures; the canopy scenes rendered as pictures for it.
3. The stack of §4 wired through the bundle (layers in, Broxton-shaped layers out), reimport, the first end-to-end picture.
4. Licences settled before anything ships: FLUX-dev (RevealLayer), OpenRAIL-M (SD-based inpainters, Marigold/DepthLab),
   MoGe MIT, SAM Apache.
