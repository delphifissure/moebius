# Plan: fill everything on the plane arm, then the remaining items

## Context — what the "band" is, and why "filled vs band size" only looked like a trade

The plane arm (`window._farRule='plane'`) gives every rest texel a **far side**: the depth of the
surface that continues behind it, read off the neighbouring runs along its row and column. The
**plate** is a second full-frame mesh drawn behind the picture; a texel of the plate sits at its far
depth, so when the head moves and the foreground slides off, the plate texel slides with the far
layer and lands in the hole. The plate is a full-frame sheet already (the island mask that could
discard fragments is off: `matQ.uniforms.u_useBgIslands = false`, moebius.js:15372); its triangles
are dropped only where neighbouring plate depths are not joined (moebius.js:15797).

The **band** (`disocc`) is the set of rest texels that actually get a far depth and a synthesised
colour on the plate. Every other texel's plate depth is its own source depth (moebius.js:14166,
14289), i.e. a copy of the foreground that never separates from it. Tonight the band went from
10 % to 54 % of the picture because two things are tied to one mask:

1. **Coverage.** Between two band texels, a non-band texel keeps its own depth, so the plate's
   triangles around it are torn; the plate becomes a comb of patches and holes appear. To close
   the comb every "loser" copy (one that lands where a neighbour's copy already landed) had to be
   put in the band too. That is what took the photograph from 31 % to 54 %.
2. **Synthesis.** The band is also what the later texture stage would have to paint (today a wash
   from the rim colours through a membrane; later, if wanted, inpainting). Its cost and its
   plausibility both scale with area. The kit's precision metric scores exactly this set against
   the truth's hidden scope.

These are different needs and need not share a mask. **Carriers** (texels whose plate vertex sits
at far depth so the sheet is continuous) can be the large set; the **texture band** (texels whose
colour is synthesised) can stay the small winner set. Carriers outside the texture band are hidden
behind winners on the pose grid by construction (they lost their cell), so their colour is almost
never seen and the wash suffices. With that split the picture is filled *and* the band for
synthesis is the small one. There is no trade to make; there was a bookkeeping conflation.

Nothing below changes a default; all of it stays behind `window._farRule='plane'` on the rim-law arm.

## Item 1 — Decouple carriers from the texture band

**Where.** `_plugCpuSweep` (moebius.js ~8098–8420), `_plugGeoBand` (~8840–8880), quick bake
(`plateF` at 14152/14166/14289; S3 PLANE COLOUR domain at 14879; S4 PLATE 2 membership at 16166;
`_qbDisocc` at 14164).

**Change.**
- The sweep returns two masks: `revealTex` = winners only (the per-cell nearest lander, as before
  tonight's fourth change) and `landedTex` = every lander behind its own sheet (tonight's `landed`,
  with the same-sheet join test). Drop the merge of `landed` into `revealTex`.
- `_plugGeoBand` builds `band` (texture: winners ∪ pinholes ∪ 4-neighbour dilation, as now) and
  `carrier` = `band ∪ landedTex`, exported as `window._bandReplace` and a new
  `window._carrierReplace` / `_qbCarrier`.
- Quick bake: `plateF` takes the far field on **carriers** (14152, 14289 loop over `carrier` instead
  of `disocc`); `_qbDisocc` stays the texture band; the S3 plane colour domain becomes the carriers
  (the ring/membrane machinery is unchanged, the domain array changes); plate 2 membership uses
  carriers. The A253 lip floor and the plate-tear test already run on the whole plate.
- Probe (`harness/a257_probe.js`) dumps `carrier.u8`; `check_app_band.py` keeps scoring `disocc`.

**Verify.** Photograph: texture band back near 31 % (v4's number), undrawn pixels at 0.5 ≤ 412 (v7)
and ideally ≤ v5's 401; face and full-frame sheets; per-layer shots. Kit: rerun the eight scenes;
expect precision back toward the S3 report's values (S2 0.90, S31 0.97) with recall kept, and S26's
73 k re-read: if its ceiling texels are landed losers they leave the texture band by themselves.

## Item 2 — Plate 2 takes part in the demand

**Where.** `_plugCpuSweep` plate pass (8383–8387, `sPL`/`pFs` from `opts.farField` at 8154), the
rim-law demand block (~8388), `_plugGeoBand` call sites (8748/8842/8877), S4 PLATE 2 block (16156).

**Change.** `opts.farField2` (the S4 second layer, −1 where none). After the plate-1 pass, a
plate-2 pass splats texels with a second layer at that depth (same quad fill). A cell won by a
layer-2 copy demands its texel into a `revealTex2`; `band2 = revealTex2 ∪ landed2`. Plate 2 is
built on `carrier2` (drop the `disocc &&` in the `has2` test at 16166), coloured as now. The
texture band for synthesis becomes `band ∪ band2`.

**Verify.** The notch's comb right of the troll's head at pose 0.5 closes (the right half's cave is
its second layer). S15 sign shots at 0.1/0.25/0.5 read hill then sky. Kit `layer2` block: `app_px`
grows, `best_of_two_vs_first_median` on S15 ≤ 0.103 m.

## Item 3 — The estimator's fringe (soft depth edges)

**Evidence so far** (note §4a): soft edges σ 1–2 px cost S2 9–11 points of precision with depth
intact and cost S15 0.6 m of depth; on the photograph the head's silhouette is a 20-texel ramp.

**Change.** An optional pre-pass on the source depth, `window._depthPre='shih'`, applied in
`_plugGeoBand` before the rim law reads `dQ`: Shih et al. CVPR 2020's discontinuity-aware weighted
median (five passes, windows 7,7,5,5,5, range kernel zeroed across the discontinuity mask; R1 §2.3
and §4). Two window conventions are tested, not chosen: the paper's pixels at its 960-px long side,
and the same scaled by `longSide/960` (the invariance question). The discontinuity mask is the rim
law's own not-joined pairs, so no new threshold enters.

**Verify.** `rung_chain.sh` on S2, S15, S31 at σ 1, 2, 4 (`degrade.py` builds the rungs; S31 still
to build) for: untreated, fixed window, scaled window. Read precision, recall, depth median. Adopt
only if the rungs say so at all three σ; then the photograph's shots. If neither convention holds
across σ, record and leave the fringe as a surface (the current behaviour).

## Item 4 — Carriers far from the rim (S26's ceiling), conditional on Item 1

If S26's 40 k ceiling texels remain in the texture band after Item 1, they are winners: the
beam's own stretched quads (its 16 carriers at the ceiling line) lose the gap cells to the wall-depth
copies because a quad "takes its farthest corner" (moebius.js:8380) and ties go to the first
lander. Then: give a plate quad the depth of the corner nearest the cell (or interpolate), so a
stretched near-line quad beats a far copy where both land. Measure on S26 only, then the eight.

## Item 5 — S16's edge-on faces (your call: a step face when both rims are one object)

Ledge and return faces have no rest texels; the plane law offers nothing there (S16 precision
0.15). Rule chosen (R1 §2.3's prior): where the two rims of a jump belong to one object (the A257
object ids, `_geoObjId`), the jump is a step and its face is synthesised as a quad spanning the
step at the nearer rim's plane continued; a jump between different objects stays an open jump to
the far side. Built as a third small mesh (or plate-2 texels where the texel has no second layer),
coloured from the nearer rim's window. Kit: S16 and S2 (boxes have sides) before/after; the
photograph's boxes-like edges (the sword, the arm) on screen.

Decisions taken with you before this plan: both a small texture band and full coverage are wanted
(Item 1 as written), and S16's jumps inside one object are step faces.

## Item 6 — The picture's own margins

At off-axis poses the picture vacates a strip on one side (the far content slides in from the other
and nothing follows). The rim arm covers it with its membrane wash; the plane arm leaves it empty
(note §5). Fill: continue the border row/column at its own depth beyond the frame (clamp-to-edge,
as Kopf 2020 pads), as an outpaint ring of the plate with the wash colour. Small; after Items 1–2.

## Standing rule for every item: wash, never a foreground clone as background

The atlases the SD stage will inpaint must be accurate about *where* new content is needed (the
texture band) and must never present foreground pixels as background. Concretely, enforced and
measured, not assumed:

- A plate texel whose depth is behind its own source depth never carries its own source colour; it
  carries the rim wash (Item 1 extends the wash to all carriers). A probe check is added:
  `count(plateColor == sourceColor && plateF < dQ − q)` must be 0 on every bake, printed in the
  `[S3] plane colour` log line and asserted by `check_app_band.py`.
- Plate 2 and the step faces of Item 5 follow the same rule (rim window means, never the texel's
  own colour).
- The texture band exported for SD is the small winner set of Item 1 (plus pinholes and the
  1-texel dilation), so the inpainter is asked only where a reveal is real.

**Self-occlusion (Item 7, after 1–3).** Where the far side behind a texel is the *same object*
(the A257 object ids: the notch through the troll's head, the back of a limb), a wash of the rim
colours is a placeholder and the object's own texture is a better one. Experiment: for kind-4/
notch texels whose two rims share an object id, colour the carrier by sampling the object's own
texels mirrored across the rim (the other side of the face), falling back to the wash where the
mirrored sample leaves the object. Judged on screen (the troll's head at 0.25/0.5) and on the
kit's S15 crown colour error; adopted only if it beats the wash on both.

## 16-bit depth: prep (Item 0, first, small)

The app already decodes 16-bit greyscale PNG depth directly (`bgDecodeDepth16`, moebius.js:775;
quantum 1/65535; 8-bit and interlaced files fall back to the 8-bit path). The kit's 8-bit rung
shows why it matters (S15 far depth median 3.4 m at 8 bits, 0.18 m at 16). Prep:

- `harness/depth16.py`: converts an estimator's float output (`.npy`, `.pfm`, `.exr`, 16-bit
  `.tiff`, or an 8-bit PNG to be re-exported at source precision) to the app's convention — one
  channel, 16-bit, non-interlaced, bright = near, normalised to [0, 1] with the normalisation the
  app assumes for its depth law (documented in the script header from the loader's code path).
  Prints the source's effective quantum and warns when the input is already 8-bit (nothing to
  gain).
- A check in the app's load path that logs which decoder served the depth (`[A99] … 16-bit` vs the
  8-bit path) so a silently-8-bit file is visible; `_qbSrcQuantum` already follows it.
- The default troll image has no float source in the repo; it stays 8-bit until you re-export it
  from your estimator with the script. The kit scenes are already 16-bit.

## Order and checkpoints

0 → 1 → 2 (small, same code paths; one kit rerun after each) → 3 (a measurement with a decision
rule) → 4 and 6 (conditional/small) → 5 (step faces) → 7 (self-sampling experiment). After each
item: photograph sheets sent, the wash-not-clone count printed, kit table appended to
`research/S5_photograph_note.md`, commits on both repos.
