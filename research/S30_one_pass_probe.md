# S30 — Towards one decomposition pass: what proposes the objects? (probe, 2026-09-14)

**Why.** The user's direction: ideally a single automatic decomposition pass, not clicking every object; SAM 2.1 is a part in
the stack, and the stack must work for video in time. S28/S29 give the *mask* half (SAM 2.1 from a prompt, offline and in
the browser). This probe asks what can supply the *prompts* without a person — on the troll (851 × 1023, DA3 depth), the
reference being the S28 click masks (troll 134 236 px, woman 32 289 px).

## 1. SAM 2.1's own automatic generator does not find the figures
`harness/segment/sam2_auto_probe.py` (grid prompts, the generator's defaults: predicted iou ≥ 0.8, stability ≥ 0.9, min
area 0.1 %):

| grid | masks | time (CPU) | picture covered | best IoU with the troll | with the woman |
|---|---|---|---|---|---|
| 16 × 16 | 10 | 81 s | 5 % | 0.06 | 0.00 |
| 32 × 32 | 17 | 240 s | 7 % | 0.06 | 0.04 |

It returns muscle-sized parts (3–10 k px, 94–100 % inside the depth-object footprint) and branch pieces. The whole-figure
candidates SAM produces from a click carry predicted iou 0.2–0.5 (S28 §2) and the generator's thresholds drop them; a single
grid point never proposes the whole troll anyway (the chest point's three candidates are a muscle, the torso, troll + tree).
**Automatic SAM alone is not a decomposition on this picture.**

## 2. The depth alone does not either
The depth-only object rule (A253 + continuity) on the troll gives one 480 k-px component — the troll, the woman, the floor
streaks, half the walls (S28 §2): DA3's steps in a painting are not silhouettes, and the contact regions join the figures
to the ground. On kit scenes it is exact (S27); on photographs it needs a second cue.

## 3. Class-free object proposals + SAM box prompts + depth: the figures come out first
`harness/segment/owlv2_sam_probe.py`: OWLv2 (`google/owlv2-base-patch16-ensemble`, CPU) run once; its **objectness head**
(class-free — no text prompt is used for the ranking) gives boxes; non-maximum suppression at box IoU 0.5, boxes over 60 %
of the picture dropped; the top 20 go to SAM 2.1 as box prompts (the SAMEO front end: detector box → mask decoder); the
best-scored candidate per box is kept.

| rank | box (plate px) | objectness | SAM mask px / iou | IoU troll | IoU woman | inside the depth-object footprint |
|---|---|---|---|---|---|---|
| 1 | [428,430,547,929] | 0.367 | 30 744 / 0.93 | 0.00 | **0.93** | 0.99 |
| 2 | [106,163,595,821] | 0.263 | 104 953 / 0.70 | **0.75** | 0.00 | 0.95 |
| 3 | [376,852,567,944] | 0.244 | 5 058 / 0.83 | 0 | 0.07 | 0.92 (a stone / the pool) |
| 8 | [430,429,525,680] | 0.115 | 12 005 / 0.89 | 0 | 0.37 | 0.99 (the woman's upper half — a part) |
| 9 | [15,212,293,934] | 0.115 | 94 941 / 0.77 | 0 | 0 | 0.83 (the left tree) |
| 10 | [616,327,819,896] | 0.106 | 27 813 / 0.46 | 0 | 0 | 0.65 (the right tree) |
| 19 | [206,558,451,873] | 0.070 | 44 762 / 0.87 | 0.28 | 0 | 0.75 (the troll's legs — a part) |
| 20 | [508,36,829,878] | 0.069 | 97 311 / 0.56 | 0 | 0 | 0.34 (background) |

The two strongest class-free proposals are the woman and the troll, with no click and no per-image setting; the troll's
mask from its box matches the dragged-box result (S29 §3b: 0.787) — the dark arms are what a box does not give. The rest
of the list is parts (nested inside a kept mask → dropped by the S28 hierarchy rule), scenery (the trees: far-field
surfaces the depth does not put in front of anything → no band demand → not exported), and small things.

## 4. Proposed one-pass decomposition (S30, not built)
1. **Propose**: OWLv2 objectness boxes (class-free), NMS. 2. **Mask**: SAM 2.1 box prompt per proposal (same encoder
features as the click mode; ~300 ms each on WASM). 3. **Keep by the depth**: a mask is an object if it has band demand
(it hides something inside the envelope — the S27 ranking) and is not nested in a kept mask; overlaps to the nearer
surface. 4. **Refine by hand where wanted**: the S29 click mode on top (add the troll's arms with a click). 5. **Video**: SAM 2's
memory half propagates each kept mask through the clip from the frame it was proposed on (one proposal pass per clip, not
per frame); OWLv2 re-proposes only where a new object enters.

Trades. *For*: no clicks, no thresholds of ours beyond the standard NMS, class-free, everything already runs in the browser
in principle (onnx-community publishes OWLv2 ONNX; base fp32 ≈ 600 MB, q8 ≈ 155 MB — a second download of that size).
*Against*: OWLv2 on paintings is untested beyond this one picture; objectness ranks the trees above the small real objects,
so the depth step (band demand) is doing real work and must be kept; a box never gives thin dark limbs (the arms), so the
result is an object map with the same 0.75–0.79 troll as the box drag — the amodal / limb completion is still the S27 layer
question. Offline first (`owlv2_sam_probe.py` extended into a bundle-writing script like `sam2_objects.py`), the browser
port after the S29 pattern once the six pictures confirm the proposals.

## 5. The user's question: can the depth pass (cliffs) drive SAM? — measured
`harness/segment/depth_prompts_probe.py` and `_probe2.py`, on the troll's DA3 bake (`a257probe/photo_da3_16n`, 256 928
band texels = the cliff set: plate texels under an occluder's silhouette with a far side). Reference: the S28 click masks.

**5a. One multi-point prompt per connected piece of the cliff set.** 359 pieces; the largest is 216 162 texels and runs
through the troll, the woman and the floor streaks in one piece (DA3's steps connect them, as with the depth-only objects).
Its prompt (six interior points spread along it) returns one 205 k-px mask: IoU troll 0.60, woman 0.11 — the figures and
the floor as one thing. The other pieces are floor streaks and branch tips. Merged objects ranked by band demand: none is
the woman, none the troll alone. (Outline-on-cliff, a constant-free objectness score — the fraction of a mask's outline
lying on the cliff set — reads 1.00 for the woman's click mask, 0.53 for the troll's, 0.56 for the merged blob: it separates
the woman from the floor but not the troll from the blob, because the troll's arms are not cliffs in DA3.)

**5b. One single-point prompt per point spread over the cliff set, then the hierarchy rule, then depth gluing** (adjacent
masks merged where their shared edge is not a cliff — the principled glue: parts of one surface meet without a step).
128 prompts (one per ~2 000 band texels, farthest-point spread on the deepest band pixels), 6 s of SAM. Result: the
**woman at IoU 0.80** (one mask, outline-on-cliff 0.78), the **troll at 0.22**: a single point anywhere on the troll makes
SAM rate the "whole scene" candidate best (590 708 px, a dark figure on dark trees), and that candidate swallows the troll's
parts under the hierarchy rule; without the rule the best troll part is 0.24. Gluing helped the woman (0.55 → 0.80) and
nothing else.

**So:** the cliff set is a fine *prompt source* where it separates objects — kit scenes (S27: exact), the woman here — and
it is what makes SAM's masks *objects* (band demand, outline-on-cliff) rather than regions. It cannot by itself propose the
troll on this painting, for the same reason the depth-only rule could not: DA3's cliffs join him to the floor and the trees,
and SAM's single-point answer there is the scene. The troll needs a box or several points: a person's (S29), or a class-free
proposal's (OWLv2, §3: 0.75). The design that follows is the union, not a choice: **proposals from both the cliff set and
OWLv2, SAM masks for each, the depth to keep and glue** — the cliff set contributes what it separates, OWLv2 what the
depth merges, and the depth (band demand, outline-on-cliff, gluing across non-cliff edges) is the arbiter throughout.

## 6. Amodal masks and self-occlusion: status (asked 2026-09-14)
- **Amodal (the whole troll behind the woman, the red section from a model).** Not started. What exists: pix2gestalt's
  weights are public but the checkpoint is 15.5 GB (`cvlab/pix2gestalt-weights`, `epoch=000005.ckpt`) and this sandbox has
  6.3 GB free and no GPU — a CPU probe would need a machine with the disk and hours per object; SAMEO has no release
  (R5 §1e). What is ready for it: the S27 layer import takes exactly what an amodal model returns (`obj_<k>_color.png` +
  `_visible.png`) and puts the hidden part at the object's own depth; the S28 highlight then shows the layer's hidden part
  red and the S30 pipeline would hand the model its visible mask and box. The first amodal run needs a GPU box (or a hosted
  pix2gestalt endpoint); nothing in the app blocks it.
- **Self-occlusion (an object's sides and back).** Not started; needs a 3D prior per object. Amodal3R is on the Hub
  (`Sm0kyWu/Amodal3R`, TRELLIS-based, CUDA extensions) — GPU only. The app side that would consume it (a mesh layer per
  object rather than a texel layer) does not exist yet; S28's orange is the readable part (steps inside the picture).
- Both are the same dependency: a GPU. Until then the plane arm carries the background behind every object (S26: nothing
  beats it there), the box/click masks carry the visible objects, and the layer import is the landing place.
