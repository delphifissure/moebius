# S71 — The plan of record: a magic button, a perfect offline pass, a streamable layered format

Date: 2026-09-25. The user:
- "I really want a 'magic button' UX. If we end up needing to tune a model, so be it. Let's push everything as far as we
  can, and then determine what models we need to build."
- For the offline SD workflow: "comprehensive and PERFECT, as good as gaussian splatting with way less compute and
  storage budget, it's got to be streamable." Picture portal / 6-DoF Netflix without glasses: streaming to a light-field
  display, or a front-facing camera, or a small no-CV head tracker worn over the ear.
- "or integrates a mix of layers and splats".

The method is the one used so far: every stage gets a known-answer test before it gets a default. Off-the-shelf models
are pushed until the tests say where they stop. The failures that remain name the models to build.

## 1. The magic button: every object layer, no clicks

**What exists.**
- Depth-cliff objects (A253). These are exact on the kit and automatic, but on paintings DA3's steps are not silhouettes:
  the troll came out as one component with the floor and half the walls (S28 §2).
- SAM 2.1, offline and in the browser, from boxes or clicks (S28, S29). One click rarely gives the whole object: the
  troll needed four clicks.

So the missing piece is a **prompt source** that finds objects without a person, and a **clean edge**.

**Candidates, all open and reachable here** (checked 2026-09-25):

| stage | candidate | licence |
|---|---|---|
| find the objects | Grounding DINO (tiny), from generic class words; Florence-2 caption → phrase grounding (already used for the labelled prompts) | Apache-2.0 / MIT |
| visible mask | SAM 2.1 from those boxes (the app already runs it in the browser) | Apache-2.0 |
| edges | BiRefNet (high-resolution dichotomous segmentation); ViTMatte (matting from a trimap made of the mask and the depth-cliff band) | MIT / Apache-2.0 |
| split and order | depth: one layer is one rim-law-connected surface inside a mask; the layer order comes from depth | ours |
| hidden extent (amodal) | none open: SAMEO has no release, pix2gestalt needs a GPU per object | — |

SAM 3 (text prompts that return every instance) is gated on Hugging Face and needs the user's account to accept Meta's
licence.

**The test** (next, `harness/seg_bench.py`):
- Objects with exact masks pasted into real pictures: the fixture method of S70 §6, generalised to many cut-outs, thin
  parts (staffs, hair, branches) included.
- The kit scenes, which have exact object ids.
- Scores: IoU, boundary F-score, recall of thin parts, objects missed, false objects, and time.
- Every arm runs with no clicks.

**Where a model probably has to be built:** a **layered decomposition model**. It would take image + depth and return K
layers, each with alpha, its hidden colour and its depth, including the amodal extent. The training data is the asset
we already have: the truth kit and pasted composites give unlimited exact supervision (visible mask, amodal mask,
per-layer depth, the colour behind). No public dataset has all four for single pictures.

## 2. The offline pass: perfect means passing a test battery

"Perfect" is made measurable as a battery every candidate must pass:
- **No invention:** zero invented objects in the hole (S70 §6's new-structure metric), on object-shaped holes with the
  occluder in context.
- **Fidelity:** against truth where it exists (pasted and kit cases).
- **Consistency across views:** the plate is painted once and viewed from every pose, so it is view-consistent by
  construction. That is this format's advantage over per-view generation.
- **Stability over time for video:** the B3 world-space store (S68 §4), frame-to-frame warp error.
- **Depth order:** backgrounds depth-first, an object's own back colour-first (S70 §5).

**Status:**
- Hiding the occluder from the painter removes the invention (S70 §6, LaMa).
- The SD arms and the stronger negative prompt are running.

**Where a model probably has to be built:** a **removal inpainter fine-tuned on reveal holes**: object-shaped masks next
to the object, trained never to regrow it, from the same synthetic data.

## 3. As good as splats, at a fraction of the budget, streamable: layers first, splats where layers fail

**What splats buy over layers:**
- appearance that changes with the viewing angle (shine);
- soft and semi-transparent structure (hair, foliage, smoke, glass);
- parallax inside a self-occluding object.

**What they cost:**
- 236 bytes per Gaussian, derived (S68 §3): about 236 MB for a million, per static scene, before compression;
- training per scene;
- no natural temporal compression.

**The layered format measured so far (S68 §3):**
- 139–492 MB per minute at 1080p24;
- depth lossless (12-bit), colour through a video codec;
- static layers stored once per shot.

**The hybrid.**
- Each layer is a texel layer (colour + depth + alpha) unless a test says it cannot be.
- A layer is flagged when its porosity, its translucency, or its parallax error against truth within the viewing
  envelope exceeds what one depth per texel can show. The porous-silhouette scenes P1–P6 are the starting test.
- A flagged layer is carried as splats.
- The stream is a per-shot manifest: layers in video tracks, splat layers as compressed assets, and the viewing envelope.

**To claim "as good as splats":**
- Render views inside the envelope from truth (kit: exact; real: multi-view captures).
- Fit splats to the same views.
- Compare per view (LPIPS / PSNR), plus storage, decode cost and time to produce.
- The claim holds when the layered and hybrid formats match splats inside the envelope at a fraction of the bytes.

## 4. Playback

- **Webcam head tracking:** built (x, y, z; S67).
- **Light-field displays:** the renderer already draws any eye position. A display that wants N views per frame (a quilt)
  is N renders from the envelope's positions, a small addition and a direct test of the format.
- **An ear-worn tracker, no camera:** an inertial sensor gives head rotation well, but position drifts within seconds,
  and the portal's parallax comes from position. It needs an absolute reference: ranging to the display (ultra-wideband
  or ultrasound), or the webcam as an occasional correction. This is a hardware question; the format does not change
  for it.

## 5. Order of work

1. The segmentation test (§1) on the open models; a "Find objects" button once an arm passes it.
2. The painter battery finished (§2); Paint holes' default set by it.
3. The hybrid test (§3): layers vs splats on kit views and P1–P6, with bytes counted.
4. The light-field quilt output (§4).
5. Then the models the tests call for: the layered decomposition model first, the removal inpainter second, with the
   synthetic kit as the training source.

Meanwhile every picture runs through the workflow as it stands. The gallery page is updated as they finish.
