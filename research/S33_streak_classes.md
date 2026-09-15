# S33 — what the plate's visible bends are (2026-09-15)

The user's question after S32: why are there streaks at all, if per pixel only the nearest fragment is drawn and the
sheets are meant to be continuous rubber that interlocks? Answer given in the thread: the streak is the sheet itself
where it bends steeply between two rows of unequal depth — a wall one texel tall and as long as the parallax difference,
drawn because the plate's bends are kept as rubber (the fold law was measured on the plate in S25 and opened holes: nothing
sits behind the plate). The question that decides what to do is *why the plate bends*: is each bend a real step between two
background surfaces (then it should be a tear with a sheet behind it), or the construction disagreeing with itself (then
the rows belong to one sheet and should have one depth). This note measures that on six pictures. Nothing is built.

## 1. Instrument

`harness/streak_class.js` (per-line plane bake with the start-up defaults) + `harness/streak_class_render.py`. For every
pair of adjacent band texels (vertical pairs = the bends the eye reads as horizontal streaks; horizontal pairs too) whose far
field differs by more than the visible step (S10's 1/k: one pixel of parallax at the 45° cone rim — the smallest bend that can
show), the pair is classified by the RIMS the two texels continue from (the far-side law's own bookkeeping, `farRimJ`, the
side that gave the value: kind 2 either rim, otherwise the heavier side of the mix):

1. **same surface, law disagrees** — both texels extrapolated along the same axis, their rims joined by the join law
   (`rl.joinedIdx`, S2b/S10) or the same texel: one visible surface, two answers;
2. **real step** — same axis, rims not joined: two visible surfaces, and the step between them carried into the band;
3. **axis change** — one texel extrapolated along its row, the other along its column: the arbitration flipped between
   neighbours (a seam of the construction);
4. no rim (sky, own depth) — did not occur.

Per class: count, share of visible bends, median and p90 jump in visible steps (= the wall's length in pixels at the cone
rim), and the summed jump = the total wall length, which is what the eye integrates. Three of the six maps (room,
silverwarrior, bristlecone) read the grid as their effective quantum (σ gate 0, S19 §3.4); they are re-thresholded offline at
their visible step (`--step`), so all six are counted at the same criterion.

## 2. Result — vertical bends (the horizontal streaks), at the visible step

| picture | band texels | visible bends (share of vertical band edges) | 1 same surface: count / wall length | 2 real step: count / wall | 3 axis change: count / wall | jump median, steps (1 / 2 / 3) |
|---|---|---|---|---|---|---|
| troll | 258 943 | 99 205 (40.5 %) | 77.2 % / 38.8 % | 10.4 % / 26.1 % | 12.3 % / 35.1 % | 3.3 / 31 / 25 |
| vermeer | 370 698 | 110 225 (30.1 %) | 73.3 % / 20.5 % | 11.6 % / 35.0 % | 15.1 % / 44.5 % | 3.2 / 97 / 98 |
| room | 142 841 | 44 834 (33.1 %) | 73.2 % / 36.1 % | 6.0 % / 26.7 % | 20.8 % / 37.3 % | 4.1 / 52 / 18 |
| silverwarrior | 147 555 | 23 888 (16.6 %) | 56.9 % / 9.6 % | 26.2 % / 58.5 % | 17.0 % / 31.9 % | 2.9 / 121 / 98 |
| octopus | 46 855 | 20 445 (50.5 %) | 59.7 % / 29.5 % | 16.4 % / 36.0 % | 23.9 % / 34.5 % | 3.6 / 29 / 16 |
| bristlecone | 96 114 | 17 604 (19.2 %) | 62.5 % / 12.1 % | 25.3 % / 58.2 % | 12.2 % / 29.6 % | 2.2 / 64 / 59 |

Horizontal bends (the vertical streaks, from column-axis regions) split the same way: class 1 is 52–78 % by count and
9–41 % by length; class 3 is 29–53 % by length. Full tables in `harness/shots/streakclass/<picture>/counts.json`; maps in
`s33/<picture>_class_v.png` (red 1, blue 2, yellow 3, grey band without a visible bend).

## 3. Reading

1. **By count the construction disagreeing with itself dominates everywhere**: 57–77 % of all visible bends are two rows
   that continue one visible surface and got two depths. Those walls are short — median 2–4 pixels at the cone rim, p90
   12–30 — the fine hatching over the whole band in the maps.
2. **By wall length the two artifact classes together (1 + 3) are 42–74 %** (troll 74, room 73, vermeer 65, octopus 64,
   silverwarrior 42, bristlecone 42) and **real steps 26–58 %**. The long walls (median 16–120 pixels) come from the real
   steps and from the axis flips in almost equal measure; on vermeer, room and octopus the axis flip is the largest single
   source of wall length.
3. **Class 3 is a seam of the arbitration, not of the scene.** Two adjacent texels, one continued along its row and one
   along its column, land a hundred pixels of parallax apart. The per-texel choice between axes (kind 2 wins, then the
   nearer rim) is made independently per texel, so it can flip between neighbours wherever the two axes' answers are close
   in rank but far in value.
4. **Class 2 is real and is drawn wrongly.** A step between two background surfaces (the table's edge against the wall,
   the rock against the sky) is carried into the band as a rubber ramp. Under the user's model it is a tear with the
   farther surface behind it. The app already knows these cells ("plate internal cliffs stretched: 32 663 unjoined
   triangles between carriers kept" on the troll) and keeps them as rubber by the seams choice, because tearing them
   opened holes (S25): the second layer (plate 2 from the arrival order) exists only where the sweep demanded it, not
   behind every internal cliff.
5. **Class 1 is not "one plane per piece".** S7 tried pooling each candidate's fit across neighbouring lines (one plane per
   piece within tol) and was falsified on the troll: adjacent lines' far runs do not lie on one plane within the tolerance
   (code comment at the far-side law, `bgFarSidePlane`). S22 tried cross-line medians of slope and value; S32 the bending
   plate per run cluster. None couples rows the way the visible surface itself does at the rim: the line law carries the
   surface's slope *along* the line and lets each row float *across* lines. What has not been tried is the first-order
   carry in both directions — the local tangent plane at the rim (value, along-line slope, across-line slope from the
   neighbouring rows' fit windows), one per texel, no pooling, no global plane: on a plane it is exact (kit identity), on a
   curved surface it disagrees between rows by the surface's second derivative rather than by the fit's noise.

## 4. What this decides

The streaks are mostly ours: on the six pictures 42–74 % of the visible wall length (and 57–77 % of the bends) come from the
far-side construction, not from the scene. The remaining quarter to half are real steps drawn as rubber where they should
be tears with a sheet behind. Both halves have a specific cause with a specific fix; neither is a rendering setting.

## 5. Options, with trades (nothing built)

- **A. The axis seam (class 3): decide the axis per connected far-side piece, not per texel.** One axis per piece (the
  piece's majority under the same kind-2 / nearer-rim rule), or the per-texel choice kept but the losing axis's value
  blended in over the join tolerance. For: removes the largest long-wall source on three pictures with no new constant (the
  piece is a connected component of the far side, the rule is the existing one). Against: a piece can genuinely need both
  axes (a corner); S7b's D1 axis blend was measured per step — its note must be re-read before this is built. Kit: identity
  expected on planes. Cost: a day.
- **B. The self-disagreement (class 1): the tangent-plane carry.** Per texel, the far side from the rim's local plane
  (value, slope along, slope across from the adjacent rows' fit windows), same trimming as the line fit. For: the first-order
  law completed in 2-D, the same family as what is shipped, exact on planes; attacks the class that is 57–77 % of the bends.
  Against: the across-line slope is estimated from as few rows as the fit window is long, so it is noisier than the along-line
  slope; curved surfaces still disagree between rows (by their curvature, which is honest); it is the fourth attempt at
  cross-row consistency and must clear S22's bar (S15 band depth 0.18 m; the photographs' same-sheet seams must fall, by
  this instrument). Cost: two days with the kit and the six pictures.
- **C. The real steps (class 2): tear + a sheet behind.** Tear the plate at unjoined internal cliffs (the seams select's
  torn value already exists) and extend the second layer to cover every internal cliff's reveal (plate 2 today covers only
  the sweep's demand). For: the user's model taken literally where it is right; no skins over real steps. Against: layers
  multiply; plate 2's colour and depth are the arrival-order continuation and are themselves a per-line law (classes 1 and 3
  recur inside it); holes where plate 2 has no rim to continue from. Cost: two days.
- **Order.** A first (cheapest, largest long-wall share, cited rule), then C (the model's requirement), then B (the hatching;
  the hardest, the fourth attempt). Each measured by this instrument on the six pictures and by the kit for identity.
  The diffusion loop (PLAN_REVIEW W1) waits behind these only if the user ranks the streaks above it; the two are independent.

## 6. Files

`harness/streak_class.js`, `harness/streak_class_render.py`; `harness/shots/streakclass/{troll,vermeer,room,silverwarrior,octopus,bristlecone}/`
(class maps, jumps, band, far field, source depth, counts.json); `research/s33/*_class_v.png`.
