# S28 — SAM 2.1 visible masks as the object map, and the live standpoint highlight (Sprint 20, 2026-09-14)

**Ask.** Wire SAM 2.1 in for the visible masks; per object, click it and see the object blue, its self-occlusion orange
(faint at rest, revealed as the head moves), and what another object hides of it red; from the background's standpoint the
troll and the woman red, the background's own steps orange, the rest blue. Everything is behind buttons and window functions;
no default changed.

## 1. What was built (app, CODEMAP §36)

**Offline segmenter** `harness/segment/sam2_objects.py` (SAM 2.1 hiera-small, Apache-2.0, CPU; weights from HF). Input: the
plate-grid picture and the app's object export (`objl_view.js` dumps `source_plate.png`, `objects.json`, `objIds.u8`; an
SD Bundle carries the same). Prompts, in order: **clicks** (`--points "x,y+x,y;x,y"`, several clicks on one object joined
with `+`), **boxes** of the depth-only objects (the SAMEO front end: any detector's box → a mask decoder — here SAM's own
decoder, which returns the *visible* mask), and the **automatic generator** (`--auto`, `--pps`). Boxes or masks covering more
than `--max-frac` (0.6) of the picture are background, not objects; automatic masks that lie more than half inside a kept
mask are parts of it (SAM's masks are hierarchical; the whole object wins). Overlaps: the nearer object wins (front depth
from the export; click/automatic masks have none and lose to prompted ones). Output: `plane_object_ids_sam.png` (0 = none,
ids as in `objects_sam.json`), `overlay_sam.png` (depth-only map beside the SAM map).

**Import** `📤 Import object masks (S28)` (both HTML files) → `window._setObjectIds(ids, objects, source)`: recomputes footprint,
band demand, front and background depth per id on the current bake, ranks as the export ranks, and stores `window._extObj`;
`_planeObjects()` returns it instead of the depth-only components for everything downstream (export, Object view, layer
import, highlight). `window._clearObjectIds()` goes back to the depth-only rule.

**Band continuation** `window._bandContinuation(ob)`: every band texel (plate texel with a far side under a foreground pixel)
has an *occluder* — `ids[p]`, the foreground pixel in front of it — and a *continuation* — the visible surface its far-side
depth joins on the plate. Labels are flooded from the visible texels into the band along the plate depth with the rim law's
join predicate (the same test `_planeObjects` uses for "one surface"). **Seeds are gated**: a visible texel may seed a band
texel only if it is not the occluding surface there (its source depth not joined to the band texel's own source depth).
Without the gate the first troll run labelled 61 749 of the troll's 77 074 band texels as "the troll hiding itself": where
the plate is stretched to meet the foreground (seams = stretched) the plate depth ramps up to the occluder at the band's
deep edge, the occluder's interior passes the join there, and a breadth-first race is decided by distance, not by depth.
Inside the band the flood follows the plate depth alone. Unreached band texels stay `-1` (grey in the Object view, untinted
in the highlight) rather than guessed.

**Highlight** `🎯 Highlight object` + id (`window._objectHighlight(sel)`; `-1` off) paints per-texel classes into `u_sdPaint`
on the plate and the foreground (classes 5 red, 6 orange, 7 blue, 8 faint red, 9 blue + faint orange; shader tint table
extended) and turns SD regions on; off restores the C classes and the checkbox.

| standpoint | foreground (at rest) | plate band (revealed as the head moves) |
|---|---|---|
| object k | its footprint **blue**; **blue + faint orange** where the band behind continues k itself (its own step: the arm over the torso); **faint red** on another object's pixels that hide part of k | band texels continuing k: **orange** under k itself, **red** under another surface |
| background (0) | objects **red**; background **blue**, **blue + faint orange** where the band behind continues the background under a background occluder (a wall's own step) | band texels continuing the background: **red** under an object, **orange** under the background |

**Object view** (S27) now uses the same continuation: red = band continuing a surface other than its occluder, orange = band
continuing its own occluder, grey = unjoined; legend counts.

## 2. Segmenting the troll (851 × 1023 plate grid, SAM 2.1 small on CPU: 10 s encode, < 1 s per prompt, 100–160 s automatic)

**Depth-only boxes on a painting are not object boxes.** The depth-only rule (A253 + continuity) on the troll gives one
480 442-px component (the troll, the woman, the floor streaks and half the walls; DA3's steps in a painting are not
silhouettes) whose box is the whole picture — filtered as background. The three remaining boxes are small far-field steps
(branch tips, the top-left tree); SAM's masks for them agree with the depth footprints at IoU 0.17–0.23 (SAM adds 1.7–4.4 k px
each: it segments the whole visible thing, the depth rule only the part in front of the far field). On kit scenes the
depth-only boxes are exact (S27) and SAM is not needed; on photographs the prompt has to come from somewhere else.

**Clicks.** One click on the troll's chest returns three nested candidates: 293 998 px (troll + tree + wall, SAM iou 0.16),
56 741 px (the torso, 0.20), 4 427 px (a muscle, 0.08). The whole troll is none of them — the figure is dark on dark, the
arms merge with the trees. Four clicks (chest, belly, thigh, foot) return one mask of 134 236 px (iou 0.50) that is the troll
with a speckled left arm and its shoulders; the woman needs two clicks (32 289 px, iou 0.92, vs 32 303 with one). The
automatic generator finds 8–11 more objects (branch shapes, a foot, a stone) and nothing background-sized. **A generic
"one click = one object" rule does not exist in SAM's output**: the candidate the user means is the one they would point at
again, so the live tool needs the click (or a box) and, for a figure like this, several clicks. That is what SAMEO's box prompt
is for; without an amodal decoder the visible mask is what we get.

## 3. Results

### 3a. S9 (kit: three cards behind each other, exact depth, depth-only objects) — the control for the continuation
The cards are band over their whole footprints (26 986 / 20 862 / 16 619 px; the envelope reveals everything behind
them). The plate's far side behind the red card is the green card's depth over 15 554 texels and the wall around the rim;
behind the green card the blue card's depth over 14 813 texels (probe dump `a257probe/S9_16plane_c`, levels 0.274 / 0.176).

| run | joined | other | self | unjoined |
|---|---|---|---|---|
| first rule (non-band seeds only, gated) | 33 350 | 33 350 | 0 | **31 010** — the far sides at card depth touch no non-band texel |
| final rule (every visible surface seeds, gated) | **63 717** | 63 717 | 0 | 643 (19 seed edges gated) |

Highlights (`hl_S9b/`, the three truth layers imported): background — red 121 201 (the cards), orange 0 (no wall step in the
picture), blue 272 149. Red card (id 1, nothing in front of it) — blue 26 986, red 0. Green card (id 2) — blue 20 862 visible;
**red 15 554** band texels continuing it behind the red card, plus its layer's 10 094 hidden px red on the layer; faint red
on 17 331 red-card pixels at rest. Self-occlusion 0 everywhere, as it should be for flat cards. Shots: at rest the green card
blue and the red card faintly red where it covers it; at 0.6 the revealed layer red, the visible card blue, the wall wash
untinted.

### 3b. The troll with the multi-click masks (`hl_troll3/`, gated seeds)
Continuation on the DA3 map (`[S28] band continuation`): 258 943 band texels; **194 739 joined** (68 523 hidden by another
surface, 126 216 a surface hiding itself), **64 204 unjoined** (25 %); 68 175 seed edges gated. Before the seed gate: 240 899
joined but 194 313 "self" — the troll's whole silhouette band was "the troll hiding itself" (61 749 of 77 074), which is the
stretched-seam leak described in §1. After it:

| standpoint | red | orange | blue | faint red (FG) | faint orange (FG) |
|---|---|---|---|---|---|
| troll (id 1, 134 236 px) | 1 128 (behind the woman) | 27 721 (its own steps) | 106 515 | 1 128 | 27 721 |
| woman (id 2, 32 289 px) | 256 | 5 367 | 26 922 | 256 | 5 367 |
| background | 266 455 (the objects' footprints + their band) | 93 128 | 578 129 | – | 93 128 |

What the pictures show (`hl_troll3/object_view.png`, `hl1_*`, `hl0_*`): the troll's silhouette band is red where it continues
the background (head, shoulders, the right arm's underside) — the envelope's reveal of the wall behind him; the woman's band
is red throughout (she hides the background and, over 1 128 texels, the troll's leg). The **orange inside the troll is DA3's
internal steps** — horizontal runs across the arms and torso where the depth map steps inside the figure (muscle folds read
as ledges, and the line-wise far field's row structure) — not the knee behind the thigh: on this map the thigh/knee region is
mostly *grey* (unjoined: SAM's speckled mask there and DA3 ramps leave far sides that join nothing). The background's orange is
the floor-streak region at the bottom left (DA3 steps in the painting's floor, the same texels the depth-only object rule
took for a 480 k-px object). So on the photograph the semantics are right but the inputs are not clean: **the labelling is
only as good as the depth steps and the mask edges** — the kit control (§3a) shows the mechanism itself is exact when they are.
Nothing was tuned per picture; the two rules (join under the rim law, seed only from a surface that is not the occluder) have
no constants of their own.

### 3c. What orange means, and what it cannot mean
Orange is a surface hiding itself at a depth step **inside the picture** — the far side of that step continues the same
surface (the wall behind its own ledge, the torso behind the arm). It is read from the depth map and the mask identity, not
guessed. What is **not** in the picture is an object's own sides and back faces beyond its silhouette (the troll's flank as
one walks round him); no texel layer and no continuation can hold them (S27 §4, S26 §3b: the far side is at the front, zero
thickness). The user's "knee area revealed as we rotate" is the first kind when the knee is hidden by the troll's own thigh
in the picture (a step inside the mask) and the second kind when it is the knee's own side. A 3D prior per object
(Amodal3R, R5 §1e) is the only route to the second kind; the highlight leaves it undrawn rather than paint something the
picture does not contain.

## 4. What the user sees live (LIVE_PASS §6)
Build → `Export SD Bundle` (or `objl_view.js` headless) → `python3 harness/segment/sam2_objects.py <dir> --auto --points "…"` →
`Import object masks (S28)` (the PNG + JSON) → `Highlight object` with an id from the console's `[S28] object map set` line
(the Object view PNG shows the outlines with ids in `objects_sam.json`). The clicks are plate-grid pixel coordinates today;
a click in the app is the next step (below).

## 5. Next steps, with trades

1. **Clicks in the app, SAM in the browser** (ONNX Runtime Web, SAM 2.1 small image encoder ≈ 40 MB, decoder ≈ 5 MB; the
   encoder runs once per picture, seconds on WebGPU, tens of seconds on WASM; each click is a decoder pass, milliseconds).
   + The tool becomes what was asked for: click the troll, see him. + No round trip through files. − A second model in the
   page, a first-load cost, WebGPU availability; − the same nested-candidate ambiguity: the UI has to show the three masks or
   accept several clicks (SAM's own demo does the latter).
2. **Keep it offline** (as built) and add a box tool in the app that writes `objects.json` prompts. + Nothing new in the page.
   − Two-step workflow; the user segments in one place and looks in another.
3. **Amodal masks** (the blue "whole troll" behind the woman): reproduce SAMEO's recipe (EfficientSAM/SAM decoder fine-tuned
   on Amodal-LVIS-style pairs; no release found) or run pix2gestalt (weights public, a diffusion model per object, GPU).
   + The blue outline becomes the full object and the red section becomes the object's true hidden extent, not the envelope's
   reveal. − GPU (pix2gestalt) or a training run (SAMEO); the plane arm still needs the object *layer* (S27) to show it.
4. **Self-occlusion beyond the silhouette**: Amodal3R or another per-object 3D prior. + The only source for sides and
   back faces. − GPU, a mesh per object, and the render path for a mesh layer does not exist yet (the object layer is texel).
Recommended order: 1 (the tool as asked, on the visible masks), then 3 for the amodal outline when a GPU is available.
