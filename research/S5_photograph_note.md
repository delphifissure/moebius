# The plane far side on a photograph (estimator depth, 8 bits, no truth)

Written 2026-09-09, the night after Sprints 3 and 4. First run of the plane far side
(`window._farRule='plane'`, rim law, first arrival, plate 2) on the app's default picture: the
troll, the woman and the cave, 851 × 1023, 8-bit depth from a monocular estimator, the app's
default volume (outer 0.02 m, inner 0.04 m, portal plane at 0.5). No truth exists for this image;
every finding below is from the buffers and the shots (a196), and nothing here changes a default.

## 1. Two ground rules found on the way (both on `main` already)

The kit's scenes have a ground run in every column; the photograph does not. The ground fit
(Theil–Sen plane over the lowest horizontal run per column) found a **12-column, 209-texel plane
at the water's edge** — the pool at the woman's feet — and, since the fitted plane bounds every
candidate below the horizon, it cut nine million candidates across the whole frame and emptied
every reveal (the woman's band went from 41 texels to nothing).

- **Rule (a): the ground bounds candidates only in columns that have a ground run of their own**
  (`groundCol[x]`). On the kit nothing changes (every column has one).
- **Rule (b): the fitted plane is the ground only if it explains a majority of the columns that
  offered a pick** (`nGroundIn·2 ≥ nGroundPicks`; on the photograph 10 of 435, so "no ground").
  Justification: the plane is a global hypothesis (one vanishing line for the whole frame, R3);
  a plane that a minority of columns support is a local surface — a puddle, a table — not the
  ground, and a local surface must not bound the world. Nothing is tuned: the majority is the
  natural threshold for "the frame's ground" against "a surface in the frame". The kit's scenes
  pass with every column.

After both rules the woman's central texels get the background behind her; her band is 41 texels,
the same as the rim arm's.

## 2. The holes right of the troll's head (poses 0.25 / 0.5) and above it (0 / 0.4)

Read from the buffers (`harness/shots/a257probe/photo_plane_v1`, the run before the fix) and the
per-layer shots (`sheet: scratch hide_crops.png` — all layers, plate 2 hidden, foreground hidden,
plates hidden, on magenta = nothing drawn):

- **They are holes, not black plates**: nothing is drawn there. The plates cover the right part of
  the reveal (the band texels near the silhouette) and miss the part next to the head — the texels
  deep inside the head that should carry the cave's depth are not in the band.
- **Cause 1 — a texel's own surface named as its far side.** The head's 8-bit depth is bumpy
  (row 340: 156 155 153 153 153 152 151 146 159 158 157 …/255); runs break on curvature, so one
  joined surface is several runs. A neighbouring run of the head that sits a hair behind
  (Δ just over the tolerance) counted as a candidate, and being adjacent (gap 1–4 texels) it
  arrived first (f0 = g/(kΔ) ≈ 0.07), so the far field was the head's own depth (kind 2, "same
  plane", value within one tolerance of own) — the reach walk, whose span is
  shift(edge) − shift(far field), stopped on it. Offline (`s3_dbg2.js`): texel (380, 340), own
  0.592, far side 0.579 = its own surface; the cave (0.06) is the second run to the right.
- **Cause 2 — a notch tears the head in two.** At x 381 the estimator's map dips 13 quanta for one
  texel (151 → 146 → 159). At this depth the rim law's t (1.0125) is ~9 quanta, so the pair
  146|159 is a rim, correctly: the map says the right half of the head is 6 mm nearer than the
  left half, which is a 75-texel relative slide at the envelope rim. The right half's texels then
  see the left half through the slit on one side and the cave on the other; the two lines do not
  meet inside the gap (kind 4), and the midpoint hedge put the nearer rim's line — the head's own
  depth — on them. Same effect: reach stops, cave not carried.
- **Not the cause**: plate depths one quantum below zero (7 558 texels with source depth < 1/255 sit
  at d − q = −0.0039 by the same-texel clamp behind the source; harmless, the shader clamps);
  plate 2 (no black colours; hiding it changes nothing); the fringe (see §4).

## 3. The two rule changes (commit `b81d4ce`, flag arm only)

- **A far-side candidate must lie beyond a rim.** In `cand`, runs are skipped until the walk along
  the line has crossed a not-joined pair (`rl.joinedIdx`, the same test the reach walk and the
  mesh tear use); only runs beyond it are candidates. This is the rim law's own definition of a
  surface applied to the plane law: inside one joined stretch the mesh is continuous and nothing
  is disoccluded, so nothing there can be a far side. No constant.
- **Kind 4 becomes two layers.** Two different surfaces on a texel's two sides whose lines do not
  meet inside the gap: the boundary between them is unknowable from one view. With one plate the
  texel went to the nearer rim's side (midpoint hedge, S3 report §1). With plate 2 it carries both
  — the farther as layer 1 (its depth gives the wider reach, so the band is the superset), the
  nearer as layer 2, which occludes the first wherever it really is there; the depth test sorts
  them and no depth is invented between the two. The side's own next arrival (S4's second layer)
  is dropped for kind 4 texels — a third layer would be needed; recorded, not built.

- **The plane arm's reach walk is removed** (third change, in two steps). With the two rules above
  the band grew from 87 628 to 111 162 texels, but rows 320–360 through the face still ended at
  the notch: `walkP` broke at every not-joined pair, so the internal tear at x 381 stopped it,
  although the cave's reveal at half the envelope is 154 texels wide and the head's right half
  only 28 — the head's left half must carry the cave too. A first repair (walk through rims, stop
  only where a texel has no far side or its span fails) gave 138 580 band texels and still ended
  the face rows at the notch texel itself (no far side of its own → stop), and exposed a second
  flaw: the walk measures the slide from the *edge texel's* depth, and at this silhouette the edge
  is the end of a 20-texel ramp (d 0.42) while the head's body is at 0.6 — 48 texels short. The
  walk was a pre-filter inherited from the membrane arm (it decided which texels got a field value
  at all). Under the plane law every texel has its own far side, and the sweep's rim-law demand
  (the far-field plate splatted forward per pose; a cell the foreground leaves uncovered names the
  texel that landed there; a texel whose far field is its own is a pinhole) is already the exact
  screen-space test of which offers are taken. So: every texel with a far side of its own is free,
  and the sweep decides. `walkP` is deleted (rule 7); the rim arm's `walk` is untouched.
- **The sweep demands every texel that lands on an uncovered cell** (fourth change). Without the
  walk the band was 269 307 texels, but still a comb through the face (row 340: 273–280, 284–286,
  …, 341–364, 371–410): the sweep's demand named, per cell, only the far-field texel that *won*
  the cell. Where the far field varies texel to texel (0, 13, 18 /255 along that row) neighbouring
  copies overtake one another by a few texels; the losers were never demanded, kept their own
  depth, and the plate — torn wherever a band texel meets a non-band one — was a set of patches.
  A `landed[]` mark per texel in the sweep's `splat`/`quad` (a landing on any cell the foreground
  does not cover) now joins the demand, still excluding pinholes (far field within a quantum of
  own). On the kit's exact planes neighbouring copies land side by side without overtaking, so no
  change is expected there; measured below.
- **The frame's margins are outpaint, and a loser counts only behind its own sheet** (fifth
  change, after the kit rerun of the fourth). The eight scenes said the third and fourth changes
  over-demand: S26 precision 0.858 → 0.346 (band 29 782 → 74 009), S16 0.360 → 0.148, S15
  0.830 → 0.414 with the band depth median 0.062 → 2.734 m; recall rose everywhere (S15 0.935 →
  0.999, S32 0.811 → 0.868). The S26 sheet shows where: a 60-row band across the ceiling at the
  top of the frame. Those are the frame's own margins — at a vertical pose the far content slides
  down and vacates the top strip; with a far side at every texel (no walk) the ceiling's copies
  land there and the sweep named them reveals, while the truth's hidden scope stops at the frame
  (the content there is beyond the picture: outpaint). The sweep's observe pass already walks
  from each uncovered cell against the parallax to find the foreground lip; a cell whose walk
  reaches the frame edge first has no occluder — it is the margin. That flag (`farLip`) now
  gates both the winner demand and the landed mark, and a landed loser is demanded only when the
  cell is empty or its winner is the same sheet (joined on the far field): a copy behind a nearer
  sheet's copy is hidden for real (S15: sky copies behind hill copies, the 2.7 m). Rerun of the
  photograph and the eight scenes below.
- **The margin gate withdrawn the same hour (rule 7), and what the S26 buffer actually said.** The
  flag never ran: the sweep's observe block sits under `if (revealTex && !rimFF)`, skipped on the
  rim-law arm, so the flag stayed 0 and the photograph's band fell to 5 535 texels — the check
  that caught it. Then the S26 probe (a196): column 400, rows 0–64 are the ceiling (d 0.48 → 0.27,
  near the portal plane), rows 72–88 fall 0.12 → 0.02 → 0.00 and the wall sits at d = 0, the
  volume's far end. The rim law tears there — a receding surface meeting the far-end clamp — and
  every ceiling texel's column candidate beyond that rim is the wall's plane (kind 1, far field
  0). At a downward pose the wall slides down 100+ texels while the ceiling, at the portal plane,
  stays; the gap that opens at the crease is filled by the ceiling texels' copies at wall depth,
  and all 40 000 of them are demanded because all of them land in it. The kit's truth has a
  crease with no gap, so it scores them as false positives — but the app's own mesh is torn
  there, and without the fill the gap is a hole. The over-demand is not a frame margin; it is the
  rim law tearing at the far-end clamp, an S2b question upstream of this arm. Recorded, not
  changed tonight. (The photograph's real margins — the left strip, the bottom-right wedge — get
  no copies at all, `own = −1`, and were never demanded.)
- **Kind 4: the nearer line first** (sixth change). S15's 2.7 m was the farther-first order: on the
  sign's texels below the horizon the ground's line passes in front of the sky, and the farther
  line (sky) was made layer 1 where the truth is the hill; the reach argument for farther-first
  fell with the walk. Of two surfaces that both continue behind a texel the nearer occludes the
  farther — the layered depth image's order — so layer 1 is the nearer line and layer 2 the
  farther. On the troll's right half this puts the head's left half first and the cave second;
  plate 2 renders the cave, but plate 2 does not take part in the demand sweep (S4 plan §2's
  union is not built), so those 28 texels are demanded only if their layer-1 copy is uncovered
  somewhere. Expected: a slit up to 28 texels wide at the notch, not the 154-texel hole.

Offline on the same buffers after the change: (380, 340) far 0.061 kind 2 (the cave, by the
column); (388, 340) far 0.051 kind 4 (the cave first, the head's left half second); (360, 340)
0.155; the synthetic unit test (`s3_unit.js`) unchanged, 0 bad texels. Whole-frame candidate
counts: texels with a far side 741 361 → 712 374; midpoint 14 203 (before: n/a in the same run —
the counts are from the offline evaluator on the v1 buffers).

## 4. What the photograph's depth looks like at a silhouette (for the record, no change made)

The head's right silhouette on row 340 is a 20-texel ramp (152 → 148 → 136 → … → 115 → 106) and
then a cliff (106 → 6). The ramp is a run of its own (15 texels, sloping away) and is treated as a
surface — the cheek curving away, which it may well be. At the cliff there is a two-texel sliver at
nearly the cave's depth (d ≈ 0.02): a mixed pixel of the estimator (R1 §2.3, "every ramp pixel is
a flying pixel"). As a thin run it continues at constant depth ≈ the cave's, so it is harmless here.
The kit's degradation ladder has blur rungs (σ 1, 2, 4 within 3σ of the exact rims) built for
exactly this; the plane arm has not been scored on them yet (rungs now built for S2 and S15;
`rung_chain.sh`). Shih et al. 2020's discontinuity-aware weighted median (five passes, windows
7, 7, 5, 5, 5 at a 960-px long side) is the published treatment; its window is in pixels, i.e. not
invariant to the image size, so it is not adopted without a measurement on the rungs.

## 5. Results on the photograph (shots `harness/shots/s2c_skyshot/sheet_photo_ab.png`, face crop sent)

Band (texels demanded of 870 573) and undrawn pixels inside the picture (alpha 0 in x 190–400 of
the 572 × 322 shot; the rim arm's fill is a translucent wash, counted as drawn):

| arm | band | 0.25, 0 | −0.25, 0 | 0.5, 0 | 0, 0.4 |
|---|---|---|---|---|---|
| S2b.4 rim arm | 127 830 (14.7 %) | 74 | 15 | 442 | 9 |
| plane, before (v1) | 87 628 (10.1 %) | 320 | 58 | 1 288 | 311 |
| + beyond-rim candidates, kind 4 = two layers (v2) | 111 162 | — | — | — | — |
| + walk through rims (v3) | 138 580 | — | — | — | — |
| + no walk, winner-only demand (v4) | 269 307 (30.9 %) | 117 | 17 | 619 | 136 |
| + every lander demanded (v5) | 502 270 (57.7 %) | 97 | 16 | 401 | 79 |
| + kind 4 nearer first, losers only behind their own sheet (v7, current) | 470 209 (54.0 %) | 95 | 15 | 412 | 73 |

v7 is the state on `main` (commit `68d4be7`). The same-sheet condition on losers took 6 % off the
band: the losers are the cave's own copies overtaking one another. At 0.5 the notch shows as a
comb of slits up to 28 texels wide right of the head (the right half's texels carry the head's
left half first; the cave is their second layer, and plate 2 is not in the demand sweep), and the
undrawn count is back at the rim arm's level, not below it.

### 5a. The kit under v7 (16-bit, rim law, shipped envelope; "before" = the S3 report's plane arm)

| scene | truth px | band before → after | P before → after | R before → after | depth median (m) | layer-2 texels |
|---|---|---|---|---|---|---|
| S2 | 16 454 | 18 190 → 18 644 | 0.901 → 0.882 | 0.996 → 0.999 | 0.000 → 0.000 | 1 108 |
| S26 | 25 631 | 29 782 → 73 325 | 0.858 → 0.349 | 0.998 → 1.000 | 0.000 → 0.000 | 56 234 |
| S16 | 4 513 | 12 164 → 29 320 | 0.360 → 0.150 | 0.972 → 0.973 | 0.000 → 0.000 | 260 |
| S15 | 34 867 | 39 260 → 58 326 | 0.830 → 0.593 | 0.935 → 0.993 | 0.062 → 0.183 | 22 429 |

(S27, S12, S31, S32 below when their rerun lands; under v5 they were 5 623 → 5 725, 18 011 →
19 714, 72 798 → 74 400 and 47 995 → 50 398 with recall up on S32, 0.811 → 0.868.)

Reading: recall rose on every scene and depth stayed exact where it was exact; precision fell
where the band grew, and the band grew for three different reasons, none of them the photograph's:

- **S26 (+43 500):** the ceiling. Column 400 of the probe: rows 0–64 are ceiling at d 0.48 → 0.27
  (the portal plane), rows 72–88 drop 0.12 → 0.02 → 0.00, then the wall at d = 0 (the far end).
  That step is a beam at the ceiling–wall junction, a real rim. Every ceiling texel's column
  candidate beyond it is the wall's plane, and at a downward pose the wall slides ~100 texels
  while the ceiling, at the portal plane, stays; every ceiling copy at wall depth lands in the gap
  under the beam, so all 40 000 of them are demanded. The truth's hidden scope there is the
  ceiling's far part behind the beam (16 rows), not the wall behind the ceiling, which nothing can
  ever see. The plane law's answer is right at the rim (the beam's own texels get the ceiling line
  then the wall, kind 3) and wrong 64 rows away, and the sweep's demand pulls its carriers from
  exactly that far because a carrier must sit one slide upstream of the cell it fills. This is the
  limit of "a texel's far side is what its own line neighbours say", made visible by demanding
  from the whole field instead of a reach from the rim.
- **S16 (+17 000):** the edge-on ledge and return face, whose texels have no rest surface behind
  them at all (S3 report §5, the user's taxonomy call); more of them now carry a far side.
- **S15 (+19 000, depth median 0.062 → 0.183):** the sky-as-first-layer texels are gone with the
  nearer-first order (the farther-first run read 2.7 m); what remains is the crown and the sign,
  where a first layer at the hill's depth and a second at the sky's are both offered and the kit's
  first hidden layer is one or the other. Best of the two layers against the truth's first:
  median 0.103 m over the band (layer 1 alone 0.183); recall of sky reveals 0.99.

- The holes right of the head are filled from v4 on; what remains at 0.5 are slits along the
  ramp of the head's right silhouette and a jagged left edge of the wash, and at (0, 0.4) a row of
  slits along the top of the shoulders (not yet read from the buffers).
- Whole frame at 0.5 (`sheet_photo_ab.png`): both plane arms leave the picture's own margins
  undrawn where the rim arm fills them — the left strip the far content vacates as it slides
  right, and a wedge at the bottom right the near water vacates as it slides left. These are
  frame-edge reveals (content beside the frame, the sweep's "outpaint" class), not occluder
  reveals; the rim arm's membrane covers them with its wash, the plane law has no rim to continue
  from there. Open item, not touched tonight.
- The fill is the plane colour (rim window means through the membrane): a flat grey-brown wash
  where the rim arm's membrane gave a translucent one — the plausible-wash stage, as intended.
- **The band is now 58 % of the plate**, against 15 % on the rim arm. The band is what the later
  texture stage would inpaint, so this is a real trade: v4 (winner-only demand) at 31 % left the
  plate a comb through the face (619 undrawn at 0.5); v5 closes the comb by demanding the copies
  that lose their cell to a neighbour's copy of the same sheet. The losers exist because the far
  field varies texel to texel (0, 13, 18 /255 for the one cave) — the plane law's output on an
  8-bit estimator map is not smooth at the texel level, and copies six texels apart in slide
  overtake one another. A demand that admits losers only when the winner is the *same sheet*
  (joined on the far field) would not reduce it here (the cave is one sheet). Two routes, not
  taken tonight: (i) the plate keeps far depths on every texel with a far side while the texture
  band stays the winner set — needs the plate's torn-footprint machinery (`islandF`) to draw
  fragments outside the band; (ii) a far field that is one value per sheet along a line (the
  candidate runs already are planes; the per-texel variation comes from axis and kind switching
  between neighbours). This is the user's trade to see on screen before either is built.
