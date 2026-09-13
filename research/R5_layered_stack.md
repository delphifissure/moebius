# R5 — The layered-decomposition stack: what the 2025–2026 papers give us, the stack they suggest, and how to test it on our truth (2026-09-13)

Prompted by the user's list (RevealLayer, Referring Layer Decomposition, Amodal SAM, SAMEO, Lift3Dreamer, DepthLab,
MoGe-3, the video NVS models, the 3–4-layer representations) and the proposal: *run the generated layers through a depth
model and normalise against the full-scene depth map*. **What could be read from here:** GitHub and Hugging Face pages
(RevealLayer, MoGe, DepthLab, Lift3Dreamer) and search abstracts. **What could not:** arXiv, OpenReview, alphaXiv and the
github.io project pages are blocked by this environment's egress policy, and the three PDFs named as attached (Amodal SAM,
SAMEO, Lift3Dreamer) did not arrive in the container — no file landed under the repos, `/mnt/user-data` or `/tmp`. If you
push them into `research/papers/` I will read them in full; the paragraphs marked *(abstract only)* are the ones that need it.

## 1. The papers, one paragraph each, with what matters for us

**RevealLayer (May 2026; code Apache-2.0).** Decomposes one RGB image into *multiple RGBA layers*, recovering occluded content
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

**MoGe-3 (released 18 Aug 2026; code MIT, DINOv2 Apache).** Metric point map + depth + normals + intrinsics (FOV) + validity
mask from one image; Self-Guided Sparse 3D Refinement moves refinement from the image plane to a sparse voxel space, so thin
and elongated structures and boundaries come out clean at linear cost in occupied voxels; reported to beat Depth Pro,
Depth Anything 3 and InfiniDepth on fine-detail metrics at strict thresholds. *(abstract only for the numbers.)* Flexible
aspect ratios 2:1–1:2; FOV can be given or estimated.

**GEN3C, Stable Virtual Camera, ViewCrafter.** Camera-controlled video/NVS diffusion that completes views along a path; SEVA
under the Stability Community licence; GEN3C under NVIDIA's licence (check); ViewCrafter code Apache (its DynamiCrafter base
Apache). Heavy; the fill for the envelope's rim, not the representation.

**Layered representations.** Multi-Layer Gaussian Splatting (ACM MM 2025): base layers for the visible, occlusion layers
for the hidden, from one image; WonderWorld: foreground / background / sky layers in < 10 s; Broxton et al. 2020: a small
fixed number of RGBA + depth layers in texture atlases, browser-rendered. The field converged on 3–4 layers, which is what
plate 1 + plate 2 + sky already is.

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
| 3. layers | **RevealLayer** for the whole picture; **RLD** per object when its code lands; amodal masks (Amodal SAM / SAMEO) to decide self-occlusion and to prompt RLD | complete hidden appearance, discrete objects — your "world of objects" | FLUX-dev licence for RevealLayer; layer count and ordering unknown until run; failure on porous / thin objects likely (the canopy set is the test) |
| 4. depth of each layer | **DepthLab** on (layer RGB, visible depth, hidden mask); alternative: depth model on peeled composites + affine alignment; the plane law as verifier/fallback | scale preserved; the truth kit scores it directly | two more models at bake; DepthLab is SD2-era at 640–768 px, so upsample against the layer's own edges |
| 5. ordering and cleanup | a135 ordering clamp between layers; fold test on every layer; despeckle line rule | already built | — |
| 6. colour where no layer model reached | Lift3Dreamer-class inpainter on the atlas with our mask, depth-conditioned; coherence-transport wash as the placeholder before it | masks shaped like ours; placeholder with structure | SD-inpaint resolution; prompt discipline ("continue the surface") |
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
