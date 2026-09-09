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

### 4a. The kit's degradation rungs on the plane arm (v7; exact truth, degraded input)

| scene | input depth | band px | P | R | depth median (m) | depth p90 (m) |
|---|---|---|---|---|---|---|
| S2 | exact 16-bit | 18 644 | 0.882 | 0.999 | 0.000 | 0.043 |
| S2 | soft edges σ 1 px | 20 763 | 0.792 | 0.999 | 0.002 | 0.037 |
| S2 | soft edges σ 2 px | 21 066 | 0.774 | 0.991 | 0.003 | 0.040 |
| S2 | 8-bit quantised | 23 387 | 0.703 | 1.000 | 0.000 | 0.044 |
| S15 | exact 16-bit | 58 326 | 0.593 | 0.993 | 0.183 | 8.566 |
| S15 | soft edges σ 2 px | 82 965 | 0.416 | 0.990 | 0.789 | 5.355 |
| S15 | 8-bit quantised | 57 837 | 0.598 | 0.991 | 3.411 | 8.567 |

- **Soft edges (the estimator's fringe, M1):** on the room the plane law keeps recall and depth
  (3 mm) and pays 9–11 points of precision — the ramp texels are runs of their own and offer far
  sides, so the band widens by the ramp; nothing tears, nothing is lost. On the open scene the
  ramp costs more (0.183 → 0.789 m median): a ramp between a hill and the sky is a "surface" at
  intermediate depth that arrives first. The fringe is worth a treatment, and Shih 2020's
  discontinuity-aware median is the published one; its window is in pixels at a fixed image size,
  so it needs the rung measurement across σ before it is adopted. Not done tonight.
- **8-bit quantisation (M3):** harmless on the room (depth exact, precision −18 points from
  terraces offering far sides), and it wrecks S15's depth (median 3.4 m): on an 8.64 m scene a
  quantum of normalised depth at the hills is metres, and the terraces break the hills into runs
  whose lines say whatever the step says. The photograph is 8-bit. This is the S1 finding ("the
  app reads terraces as rims") at the plane law's level, and it says the plane law's numbers on a
  photograph are only as good as the source's resolution in the far field — a 16-bit (or float)
  estimator output is the cheap fix upstream of everything here.

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
| S27 | 4 894 | 5 623 → 5 725 | 0.870 → 0.855 | 1.000 → 1.000 | 0.000 → 0.000 | 60 |
| S12 | 16 975 | 18 011 → 19 540 | 0.935 → 0.865 | 0.992 → 0.996 | 0.000 → 0.000 | 30 |
| S31 | 70 400 | 72 798 → 74 400 | 0.967 → 0.946 | 1.000 → 1.000 | 0.000 → 0.000 | 0 |
| S32 | 42 400 | 47 995 → 50 398 | 0.717 → 0.730 | 0.811 → 0.868 | 0.000 → 0.000 | 0 |

Depth p90 unchanged on every scene (S2 0.043, S12 0.076, S26 0.055, S15 8.57 m — the crown; the
rest 0.000). S32, the open hedge, is the one scene that gained on both counts.

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

## 6. Sprint 5 log (plan: `S5_plan.md`)

### Item 0 — 16-bit prep (done)

The app already ingests 16-bit greyscale PNG depth at 1/65535 (`bgDecodeDepth16`, moebius.js
~L775; 8-bit or interlaced files fall through to the 8-bit path and the bake logs which quantum it
found: `a89: source depth quantum = 1/255 (8-bit)` vs `a99: depth read at 16-bit precision`).
`harness/depth16.py` writes an estimator's float output (`.npy/.npz/.pfm/.exr`, 16-bit tiff/png) as
that PNG: one channel, 16-bit, non-interlaced, bright = near, linear min–max of the (inverse) depth
with optional percentile clipping; it warns when the source is already 8-bit. Self-test: a float
ramp round-trips with 60 000 distinct levels. The troll's depth has no float source in the repo; it
stays 8-bit until re-exported from the estimator.

### Item 1 — carriers split from the texture band (done; commit `166a20d`)

Two masks now: the **band** (`_qbDisocc`: the sweep's winners, pinholes, one texel of rounding) is
what the texture stage synthesises; the **carriers** (`_qbCarrier`: the band plus every lander that
lost its cell to a copy of the same sheet) get their far depth on the plate and the rim wash through
the same membrane. Photograph (v8):

| | band | carriers | undrawn 0.25 / −0.25 / 0.5 / 0,0.4 |
|---|---|---|---|
| v7 (one mask) | 470 209 (54.0 %) | — | 95 / 15 / 412 / 73 |
| v8 (split) | 266 691 (30.6 %) | 445 904 (51.2 %) | 95 / 15 / 413 / 73 |

Same coverage, the band for synthesis halved. The wash check (plate texels behind their own depth
with no synthesised colour) read 701 on v8 with a one-quantum criterion: 688 non-carrier texels
that later depth passes (the a126 slope limit, the A253 floor) pushed 1–2 quanta behind their own
depth, and 58 carriers whose far side is within two quanta of their own. Both sets are joined to
their own foreground texel by the rim law (they cannot separate from it), so the criterion is now
the rim law's join, and a second count runs on the final plate after every depth pass.

### Item 2 — plate 2 in the demand sweep (built; commit `c0828f3`)

The sweep now splats the second layer's copies after plate 1's (ids `N + i`; the depth test keeps
the nearer copy per cell); a cell won by a layer-2 copy demands that texel's second layer, and its
losers behind their own sheet are plate 2's carriers. Plate 2 is built on its own carriers, no
longer only where plate 1 is behind the source. Photograph (v9): 22 355 texels demanded for their
second layer, 51 419 carriers of it; the notch's right half (x 381–410 on rows 330–350) now carries
the cave as its second layer across the whole half. Band 264 382 (30.4 %), carriers 445 990
(51.2 %). Wash check: 2 texels at colour time (two quanta behind, their rims empty), 0 on the final
plate. The same-sheet test between a lander and a cell's winner is now the rim law's ratio test on
cached eye distances; calling `joined()` per cell had tripled the sweep's time (the photograph's
probe took 10 min at v7; 7 min now, the plate-2 pass included). Shots and the kit below.

Shots (v9): undrawn 95 / 15 / 407 / 73 (v8: 95 / 15 / 413 / 73). The comb of slits right of the
head at 0.5 is still there although plate 2 now carries the cave on the notch's right half: the
slits are the seams between layer assignments. A texel whose *first* layer is already the cave
(kind 1 or 2, x 389, 391, 409 on row 340) has no second layer, so plate 2 has no vertex there and
plate 1's vertex there is torn from its neighbours (their first layer is the head's left half).
Two meshes, each torn at the other's seam, leave a one-texel slit. Fix to apply after the kit run:
plate 2's vertices where no second layer exists take plate 1's depth and colour, and a plate-2
triangle is kept when any corner has a second layer and all three are joined — plate 2 then bridges
plate 1's seams with coincident, same-coloured triangles (no clone: plate 2's colour canvas starts
from plate 1's wash, not from the source).

### Kit under Items 1 + 2 (band = winners + layer-2 demand; carriers separate)

| scene | truth px | band S3 → v7 → now | P S3 → v7 → now | R S3 → v7 → now | depth median (m) | carriers | plate-2 carriers | clones (final) |
|---|---|---|---|---|---|---|---|---|
| S2 | 16 454 | 18 190 → 18 644 → 18 529 | 0.901 → 0.882 → 0.887 | 0.996 → 0.999 → 0.999 | 0.000 | 18 548 | 1 108 | 0 |
| S27 | 4 894 | 5 623 → 5 725 → 5 703 | 0.870 → 0.855 → 0.858 | 1.000 | 0.000 | — | 60 | — |
| S12 | 16 975 | 18 011 → 19 540 → 18 642 | 0.935 → 0.865 → 0.905 | 0.992 → 0.996 → 0.994 | 0.000 | — | 30 | — |
| S26 | 25 631 | 29 782 → 73 325 → 50 833 | 0.858 → 0.349 → 0.496 | 0.998 → 1.000 → 0.983 | 0.000 | 73 033 | 21 218 | 0 |
| S16 | 4 513 | 12 164 → 29 320 → 22 216 | 0.360 → 0.150 → 0.198 | 0.972 → 0.973 → 0.973 | 0.000 | 28 351 | 593 | 1 |
| S31 | 70 400 | 72 798 → 74 400 → 74 398 | 0.967 → 0.946 → 0.946 | 1.000 | 0.000 | 74 398 | 0 | 0 |
| S15 | 34 867 | 39 260 → 58 326 → 43 466 | 0.830 → 0.593 → 0.749 | 0.935 → 0.934 → 0.934 | 0.062 → 0.183 → 0.131 | 51 134 | 5 163 | **223** |
| S32 | 42 400 | 47 995 → 50 398 → 47 995 | 0.717 → 0.730 → 0.717 | 0.811 → 0.868 → 0.811 | 0.000 | — | 0 | — |

Reading: the split gives back most of the precision the losers had cost (S12 0.865 → 0.905, S15
0.593 → 0.749), and S15's recall returns to the S3 level (0.934) — the v7 recall 0.993 had come
from losers, i.e. from carriers that are still there but no longer counted as demand; S32's gain
went the same way. Layer 2's best-of-two against the truth's first layer: S15 0.078 m median.

- **S15's 223 clones (final plate).** Non-carrier texels on rows 131–278 (the hills), pushed from
  d 0.274 to 0.262 by a whole-plate depth pass — 39 % of them have no far side at all. That is the
  a126 slope limiter (a chamfer for the continuous-plate arm), which lowers a texel toward a
  neighbour that dropped; under the rim law the plate is torn instead, so the pass is redundant
  there and now makes clones. To guard: skip a126 when the rim law is on, as a162 already is.
- **S26 still +21 000 over S3, all in the top 64 rows (29 037 band texels).** With losers out these
  are winners: the beam's own stretched quads (their corners run from the ceiling line to the
  wall, kind 3) take their FARTHEST corner as the quad's depth in the sweep, i.e. the wall's, and
  tie with the ceiling copies at wall depth; ties go to the first lander, and rows 0–64 splat
  before rows 72–88. Item 4 as planned: a quad's cells take the depth interpolated from its
  corners, so a stretched near-line quad beats a far copy where both land.

**Caveat on the table above (a run-hygiene failure, recorded).** A queue script waited for an
"ALL DONE" marker in a log that still held the previous night's marker, so it started at once: it
applied the plate-2 seam patch to `moebius.js` while the kit chain was on S26, shot the photograph
on the shared port, and later two rung queues overlapped. The harnesses copy each run's images to
one shared pair of files, so runs that overlap can bake another run's picture. S26 (started before
the overlap) is clean; S15 through S32 in that table ran alongside another harness and are marked
for rerun; the rung results of that hour are discarded (`rung_chain_overlapped_15h.log`). From
here one sequential driver runs everything (`s5_driver.sh`), and the v10 table below replaces this
one.

### Item 4 + a126 (commit `de65cba`), v10 running

Plate 2 bridges plate 1's layer seams; a plate quad's cells take the depth interpolated across
the quad in the sweep (the farthest corner stays for the foreground's quads); a126's chamfer is
skipped under the rim law. Photograph v10 and the eight scenes below, then the rungs
(untreated, 8-bit, Shih-filtered at σ 1/2/4 and on the exact map; S2, S15, S31).

### Item 6 — the picture's margins: the A245 plug margin already exists (to run, not to build)

`window._plugMargin` (A245, quick bake ~L16124) extends the plate by four strips of M texels
beyond the frame, M the largest rim shift of a foreground or plate texel on the border (from the
shift LUT, not chosen); the strips sample the same textures with UVs past [0, 1], so ClampToEdge
replicates the edge depth and the edge colour outward — a Neumann continuation, drawn only inside
the frame's rest footprint. The plane arm's recipe never set it. Item 6 is therefore a run:
the photograph's shots with `_plugMargin=1` added to the flags, read the left strip and the
bottom-right wedge at 0.5, and add the flag to the recipe if the strips fill them without artefacts
(the edge colour replicated outward is a wash of the border, not a clone of the foreground — the
strips carry the plate's edge, which on a carrier is its far side).

Photograph v10 (seam bridge + interpolated quad depth + a126 off): undrawn 91 / 15 / 395 / 71
(v8: 95 / 15 / 413 / 73; rim arm 74 / 15 / 442 / 9). Band 260 803 (30.0 %); carriers 504 795
(58.0 %) — up from 51 %, the interpolated quad depth re-sorts who wins and who loses a cell, and
losers of the same sheet are carriers; plate 2: 16 938 texels demanded, 57 111 carriers, 120 621
triangles (twice v9's — the bridges). Wash check 2 at colour time, 0 on the final plate (a126 was
the source of the final-plate clones). The notch's comb at 0.5 is down to a few one-texel lines
along the notch column and the ramp. Sheet `photo_ab_face_v10.png` sent.

### Item 5 — step faces (built, behind `window._stepFaces`; runs queued after the rungs)

Rule: a rim between two runs whose fitted lines are parallel within their fit uncertainty (equal
slopes; `|m1 − m2| ≤ tol/(2(n1−1)) + tol/(2(n2−1))`, no constant) is a step inside one surface;
its face has no rest texels and cannot be a carrier, so it is synthesised as a quad between the two
rim texels (one texel wide at rest, displaced by the source depth at each end, so it opens with the
parallax exactly as the return face would), coloured with the mean of the two rim texels' colours —
a wash of the two edges. Rims whose lines are not parallel stay open jumps. Offline counts on the
existing probes: S16 217 pairs, all on the jump row (224|225) across the pilaster's columns
454–670; S2 248 (the boxes' sides: a box top's row run, slope 0, against the wall, slope 0);
S26 1 172 (table and shelf edges against the wall); the photograph 883. Two scan bugs were caught
offline before any bake (the run's first texel tested at the rim instead of its last; every other
run pair skipped). Measured next by undrawn pixels in the shots of S16, S2 and the photograph with
and without the faces.

### Kit under v10 — Item 4 as first built is falsified (rule 7), corrected in v11

| scene | P v9 → v10 | R v9 → v10 | band v9 → v10 | clones (final) |
|---|---|---|---|---|
| S2 | 0.887 → 0.853 | 0.999 → 0.999 | 18 529 → 19 282 | 0 |
| S27 | 0.858 → 0.808 | 1.000 | 5 703 → 6 054 | 23 |
| S12 | 0.905 → 0.867 | 0.994 → 0.994 | 18 642 → 19 470 | 0 |
| S26 | 0.496 → 0.515 | 0.983 → 0.968 | 50 833 → 48 225 | 0 |
| S16 | 0.198 → 0.225 | 0.973 → 0.970 | 22 216 → 19 491 | 1 |
| S31 | 0.946 → 0.946 | 1.000 | 74 398 → 74 398 | 0 |
| S15 | 0.749 → 0.586 | 0.934 → 0.878 | 43 466 → 52 220 | 183 |
| S32 | 0.717 → 0.729 | 0.811 | 47 995 → 47 201 | 0 |

(v9 rows are the overlapped run, S26 apart; the direction is unambiguous.) Interpolating the depth
of *every* quad turned the torn quads — a carrier beside a non-carrier, one corner at the far
depth and one at the source — into skirt quads that won cells between the two surfaces: texels
demanded that are not reveals (precision down on every scene) and cells covered that should have
been holes (S15 recall 0.934 → 0.878). The rendered plate is torn there, so the sweep must not
splat those quads: v11 splats a quad only where its four corners are one sheet by the rim law's
ratio test on the far field, and a torn quad's texel as a point at its own far depth
(commit `c49b95e`). The clones: S27's 23 texels had no far side and sat 0.016 below their own
depth, left there by pass 1; A244f now returns every non-carrier to its own source depth. S15's
183 (rows 149–276, 42 % with no far side) are expected to fall with that too; measured in v11.

Photograph v11 (joined quads only, non-carriers at own depth): undrawn 91 / 15 / 395 / 65 —
the same picture at the four poses — but the texture band is 412 329 (47.4 %; v10 260 803),
carriers 476 941 (54.8 %), plate 2 demanded 30 678. Read from the buffer: the 168 282 new band
texels are not isolated on the plate (11 of them are; 321 762 of the band's texels are joined to
all four neighbours) and they sit in the lower half of the picture, where the water and the
woman's reveals are widest. They are cells that a torn quad used to "cover" in the sweep — a
stretched quad between a carrier and a non-carrier, which the render never draws — and that now
need a copy of their own. So v10's 30 % was an undercount against the full ±45° envelope, and
the holes the torn quads hid were at poses the four shots do not sample (the sweep grid reaches
the rim). The honest texture band for this picture at this envelope and this depth volume is
about half of it. The lever that remains is not in the demand but in what is asked of it: the
envelope (±45° horizontal) and the volume (0.06 m for a cave), which set how wide every reveal
is — your call, not the geometry's.

### Kit under v11 (joined quads only; non-carriers at own depth; a126 off; plate 2 bridging) — the current state of `main`

| scene | truth px | band S3 → v11 | P S3 → v11 | R S3 → v11 | depth median (m) | carriers | plate-2 carriers | clones (final) |
|---|---|---|---|---|---|---|---|---|
| S2 | 16 454 | 18 190 → 18 531 | 0.901 → 0.887 | 0.996 → 0.999 | 0.000 | 18 560 | 1 108 | 0 |
| S27 | 4 894 | 5 623 → 5 695 | 0.870 → 0.859 | 1.000 | 0.000 | 5 696 | 60 | 0 |
| S12 | 16 975 | 18 011 → 18 209 | 0.935 → 0.927 | 0.992 → 0.994 | 0.000 | 18 883 | 30 | 0 |
| S26 | 25 631 | 29 782 → 52 608 | 0.858 → 0.457 | 0.998 → 0.937 | 0.000 | 73 425 | 24 145 | 0 |
| S16 | 4 513 | 12 164 → 23 078 | 0.360 → 0.190 | 0.972 → 0.972 | 0.000 | 28 301 | 593 | 0 |
| S31 | 70 400 | 72 798 → 74 398 | 0.967 → 0.946 | 1.000 | 0.000 | 74 398 | 0 | 0 |
| S15 | 34 867 | 39 260 → 48 020 | 0.830 → 0.723 | 0.935 → 0.996 | 0.062 → 0.184 (best of two 0.104) | 50 354 | 11 378 | 0 |
| S32 | 42 400 | 47 995 → 47 202 | 0.717 → 0.729 | 0.811 | 0.000 | 48 002 | 0 | 0 |

Reading, against the S3 report's plane arm:
- **The rooms hold** (S2, S27, S12, S31): precision within 1–2 points of S3, recall up, depth
  exact, no clones on the final plate anywhere (the colour-time count still shows S15 151 and
  S27 23 — texels within two quanta of their own depth, joined; the final-plate count is the one
  that matters and it is 0 on all eight).
- **S15**: recall 0.935 → 0.996 with precision 0.830 → 0.723; the depth median 0.062 → 0.184 is
  layer 1 alone, best-of-two 0.104 — the crown and the sign now carry a second layer.
- **S26 and S16 are the two open geometries**, unchanged in kind: the beam's gap (the plane law
  right at the rim, wrong 64 rows away, §5a) and the edge-on faces (Item 5's step faces, measured
  next by shots — the band metric cannot see a face with no rest texels). S26's recall fell to
  0.937 because the beam's stretched quad is no longer splatted (it is torn), so the beam's own
  texels are no longer demanded by it; the fill of that gap is the plane law's limit, not the
  sweep's.
- **Band on the photograph 47 %**: the honest demand for a ±45° envelope on a 0.06 m volume
  (§6, v11).

### Item 3 — the fringe on the rungs, first pass (v11 code; Shih pre-filter with the ratio-test mask)

| scene | input | band | P | R | depth median (m) |
|---|---|---|---|---|---|
| S2 | exact 16-bit | 18 531 | 0.887 | 0.999 | 0.000 |
| S2 | σ 1 / σ 1 + Shih | 19 913 / 18 489 | 0.824 / 0.885 | 0.997 / 0.995 | 0.002 / 0.000 |
| S2 | σ 2 / σ 2 + Shih | 18 903 / 18 653 | 0.854 / 0.873 | 0.981 / 0.990 | 0.003 / 0.000 |
| S2 | σ 4 / σ 4 + Shih | 17 084 / 18 062 | 0.869 / 0.851 | 0.902 / 0.935 | 0.004 / 0.004 |
| S2 | exact + Shih | 18 597 | 0.882 | 0.997 | 0.000 |
| S2 | 8-bit | 22 828 | 0.720 | 0.999 | 0.000 |
| S31 | exact 16-bit | 74 398 | 0.946 | 1.000 | 0.000 |
| S31 | σ 1 / σ 1 + Shih | 73 592 / 75 998 | 0.891 / 0.926 | 0.932 / 1.000 | 0.000 / 0.000 |
| S31 | σ 2 / σ 2 + Shih | 75 946 / 76 798 | 0.897 / 0.917 | 0.968 / 1.000 | 0.002 / 0.000 |
| S31 | σ 4 / σ 4 + Shih | 69 662 / 75 198 | 0.960 / 0.936 | 0.950 / 1.000 | 0.004 / 0.004 |
| S31 | exact + Shih | 75 998 | 0.926 | 1.000 | 0.000 |
| S15 | exact 16-bit | 48 020 | 0.723 | 0.996 | 0.184 |
| S15 | σ 1 / σ 1 + Shih | 63 384 / 70 925 | 0.547 / 0.483 | 0.995 / 0.982 | 1.237 / 1.994 |
| S15 | σ 2 / σ 2 + Shih | 75 065 / 77 384 | 0.458 / 0.437 | 0.986 / 0.971 | 0.787 / 3.126 |
| S15 | σ 4 / σ 4 + Shih | 81 862 / 67 788 | 0.412 / 0.483 | 0.968 / 0.939 | 0.807 / 0.815 |
| S15 | exact + Shih | 60 323 | 0.568 | 0.982 | 0.754 |
| S15 | 8-bit | 50 740 | 0.678 | 0.987 | 3.392 |

Reading: on the rooms the pre-filter does what the paper says — soft edges snap back to plateaus
(S2 σ 1: precision 0.824 → 0.885 and depth exact; S31: recall back to 1.000 at every σ) at a
small cost on an exact map (S2 0.887 → 0.882, S31 0.946 → 0.926). On the open scene it is harmful
at every σ and on the exact map (0.184 → 0.754 m): the mask it filtered around was the rim law's
*ratio test alone*, which marks the smoothly receding hills as discontinuities (35 652 px on the
exact map), and the median then smears real geometry. By the decision rule (all σ, all three
scenes) it is **not adopted**. The mask was the fault, not the median: `prefilter_shih.py` now
uses the rim law's full join (ratio test and affine rescue; S15 exact: 35 652 → 13 509
discontinuity px, the remainder the hills' curvature against a two-quantum window), and the
Shih rows are rerun with it (queued after Items 5–7).

Item 5, first shots: identical undrawn counts with and without the flag, and no `[S5] step faces`
line in the bake log — the mesh was never built. The harness passes flags as numbers
(`_stepFaces=1`) and the block tested `=== true`. Fixed (truthy), same for the self-sample flag
before its run; the step shots are queued again after the Shih rerun. The untouched numbers are
worth keeping: S2 has 23 875 undrawn pixels at pose 0.5 and S16 7 868 at −0.25 — the sides and the
return face are where the plane arm still leaves holes on the kit, and where the faces must show.

### Item 6 — result: the A245 plug margin fills the picture's margins (`_plugMargin=1` joins the recipe)

Undrawn pixels, photograph (interior x 190–400 | left strip x 152–200 | bottom-right corner):

| arm | 0.5, 0 | −0.25, 0 | 0, 0.4 |
|---|---|---|---|
| rim arm | 442 \| 33 \| 1 531 | 15 \| 4 763 \| 505 | 9 \| 39 \| 720 |
| plane v11 | 395 \| 1 \| 1 244 | 15 \| 1 643 \| 505 | 65 \| 39 \| 720 |
| plane v11 + plug margin | 28 \| 1 \| 31 | 0 \| 368 \| 0 | 65 \| 0 \| 0 |

M = 570 texels (the largest border rim shift, from the LUT), four strips, 7 496 vertices. The
corner and the strips fill; what remains of the left strip at −0.25 (368) is the strip's own
displacement at that pose. One effect to know: the strips also stand behind the picture's
*interior*, so interior holes fall too (395 → 28 at 0.5) — filled with the border's replicated
colour, a backdrop, not the far side. That is a fill in the sense you asked for (never a clone of
the foreground; the border texel's own colour continued), but it also hides holes from the
undrawn-pixel measure, so hole counts stay on the arm without the margin. The recipe for the live
pass is now `window._tearLaw='rim'; window._skyInf=1 (open scenes); window._farRule='plane';
window._plugMargin=1; window._plugGeoBand({flush:true, observed:true, gateAPriori:true})`.

### Item 7 — self-sampling (experiment, `window._selfSample`): what it turned out to be, and the numbers

As built: objects = 4-connected components of texels that have a far side; a texel whose first
layer's rim texel is in its own component takes the source colour of the texel mirrored across
that rim — the same distance *into the far run* — as a Dirichlet value for the membrane. Read
honestly, that is not "the other side of the face": the mirror point lies in the far run, so the
fill is the **far surface's own texture reflected into the reveal** (mirror padding of the visible
far side), and with this object definition nearly every texel qualifies (photograph: 292 451 of
the carriers; S15: 22 945). It is not a foreground clone — it samples the far side — but it is a
different placeholder from the wash, and the kit prefers it strongly on S15, colour error against
the truth's first hidden layer (mean |Δ| /255 on 26 087 true-positive band texels):

| class | rim wash | mirrored far side | clone (source as fill) |
|---|---|---|---|
| all | 65.4 (median 56.7) | 32.4 (median 17.7) | 38.3 |
| background (ground, hills) | 33.5 | 13.2 | 60.3 |
| side of a leaf | 93.0 | 51.0 | 19.8 |
| interior (leaf behind leaf) | 96.7 | 49.0 | 16.5 |

The background halves its error (repeating textures: grass, hills — reflection is a fair guess);
the sides and interiors of the crown are still far from the truth (the truth there is a leaf, the
fill a mirrored hill or sky) and there the clone would have been nearer — which is exactly the
self-occlusion case the item was meant for, and which this construction does not reach (a leaf's
far side is the hill, not the leaf's other side). Two conclusions: (1) "mirror the far run into
the reveal" is a better placeholder than the wash on the kit and costs nothing; it is left behind
the flag for your screen (the photograph's sheet below); (2) true self-occlusion needs the object
in the A253 sense (texels in front of the far field, `_plugObjectRule`), where the mirror should
stay inside the *near* object across the notch — not built.
