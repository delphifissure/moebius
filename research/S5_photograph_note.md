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

Screen (`self_sheet.png`, sent): the reveal behind the troll's head fills with the cave's texture
reflected across the rim, one row at a time, so it reads as a horizontally streaked cave rather
than the flat grey wash; no foreground colour appears in it. Whether streaked cave beats flat wash
as the placeholder is the screen call; both stay available (`_selfSample` off = the wash).
A cheaper cure for the streaks, not built: mirror along the winning axis but average the two
axes' samples where both exist, or mirror a small window rather than one texel.

### Item 3 — second pass with the corrected mask (rim law's full join): decision

| scene | input | P | R | depth median (m) |
|---|---|---|---|---|
| S2 | exact / + Shih | 0.887 / 0.882 | 0.999 / 0.997 | 0.000 / 0.000 |
| S2 | σ 1 / σ 2 / σ 4 + Shih | 0.885 / 0.873 / 0.852 | 0.995 / 0.990 / 0.935 | 0.000 / 0.000 / 0.004 |
| S31 | exact / + Shih | 0.946 / 0.926 | 1.000 / 1.000 | 0.000 / 0.000 |
| S31 | σ 1 / σ 2 / σ 4 + Shih | 0.926 / 0.917 / 0.936 | 1.000 / 1.000 / 1.000 | 0.000 / 0.000 / 0.004 |
| S15 | exact / + Shih | 0.723 / 0.637 | 0.996 / 0.982 | 0.184 / 0.696 |
| S15 | σ 1 / σ 2 / σ 4 + Shih | 0.564 / 0.456 / 0.468 | 0.982 / 0.971 / 0.941 | 1.953 / 3.123 / 0.668 |

The rooms are as in the first pass (the corrected mask changed almost nothing there); the open
scene is still damaged, less than before (exact map 0.754 → 0.696 m) but far from its untreated
0.184 m. The 13 509 discontinuity pixels left on S15's exact map are the far hills' curvature
against a two-quantum window — the affine rescue joins planes, not curved surfaces — and the median
across them smears real geometry. **Decision: the Shih pre-filter is not adopted** as a pass on the
plane arm. Where it helps (soft edges in rooms: S2 σ 1 precision 0.824 → 0.885 with depth exact,
S31 recall back to 1.000) it is a real gain, and `prefilter_shih.py` stays in the kit for a
per-picture choice; the thing that would make it safe everywhere is a join that also spares
smoothly curved surfaces (a second-difference rescue over a longer window), which is a rim-law
change, not a filter change. The photograph keeps its fringes for now.

### Item 5 — step faces: result (second shots, flag truthy)

Built: S16 217 quads, S2 248, the photograph 977 (23–43 ms). Screen (`steps_sheet.png`, sent):
on S2 the boxes' right sides appear as slabs where the plane arm left the wall showing through
(0.25 and 0.5); on S16 the pilaster's return face closes the slit along the jump row. The slabs
are striped: each quad takes the mean of *its* two rim texels, and a checkerboard's rows differ,
so the face reads as horizontal stripes of box-and-wall means rather than one flat wash — a
window mean along the rim (the plane law's own rim window) would smooth it; not done. The
undrawn-pixel counts did not move (S16 −0.25: 5 498, S2: 3 616, interior x 150–520) because at
those poses the count is the vacated frame margin, which the faces have nothing to do with — the
measure for the faces is the sheet, or a count with the plug margin on so only geometry holes
remain. On the photograph the faces change little (91 → 80 at 0.25, 65 → 31 at 0, 0.4): its
steps are estimator notches, not architecture. Kept behind `_stepFaces`; with `_plugMargin` it is
part of the recipe to see on screen.

Item 6, second reading — `_plugMargin=2` (strips clipped to the picture's rest footprint) against
`=1` (whole window), photograph, undrawn pixels (interior | left strip | bottom-right corner |
outside the picture):

| | 0.5, 0 | −0.25, 0 | 0, 0.4 |
|---|---|---|---|
| plane v11 | 395 \| 1 \| 1 244 \| 38 488 | 15 \| 1 643 \| 505 \| 44 931 | 65 \| 39 \| 720 \| 45 080 |
| + margin = 1 | 28 \| 1 \| 31 \| 0 | 0 \| 368 \| 0 \| 5 | 65 \| 0 \| 0 \| 0 |
| + margin = 2 (+ step faces) | 17 \| 1 \| 632 \| 38 488 | 0 \| 368 \| 468 \| 45 080 | 31 \| 0 \| 720 \| 45 080 |

`=1` paints the whole window with the border's replicated colour (the streaked bands beside a
portrait picture in a landscape window); `=2` stays inside the picture's own rectangle, fills the
left strip and the interior holes it can reach, and leaves the part of the bottom-right wedge that
lies outside the rectangle empty (632 of 1 244). Recommendation for the recipe: `_plugMargin=2`
(nothing drawn where the picture never was); `=1` if you would rather see wash than window.

## 7. Where Sprint 5 leaves things (all on `main`, all behind the plane arm's flags)

- Live-pass recipe: `_tearLaw='rim'; _skyInf=1` (open scenes); `_farRule='plane'; _plugMargin=2;
  _stepFaces=1;` optionally `_selfSample=1` (mirrored far side instead of the wash); then
  `_plugGeoBand({flush:true, observed:true, gateAPriori:true})`.
- Photograph: undrawn 91 / 15 / 395 / 65 → with the margin 17 at 0.5; texture band 47 % of the
  picture (the honest demand at ±45° on a 0.06 m volume), carriers 55 %, no clones on the final
  plate.
- Kit (v11): rooms within 1–2 points of Sprint 3's precision with recall up and depth exact; S15
  recall 0.996; S26 and S16 the two open geometries (the beam's gap: the plane law's reach;
  the edge-on faces: now synthesised, measured only on screen).
- Not adopted: the Shih pre-filter (hurts curved far surfaces; kept in the kit); interpolated
  depth on every quad (withdrawn); the far-lip margin gate (withdrawn).
- Yours to call: wash vs mirrored far side as the placeholder; `_plugMargin` 1 vs 2; whether the
  envelope or the volume should shrink for a smaller texture band; the 16-bit re-export of the
  photograph's depth (`harness/depth16.py`).

## 8. Sprint 6 — your decisions built as bake-time options (commits `99a9b5e` … `fabe9c6`)

Decisions (from the brief in `S5_plan.md`): build both fills and choose at bake time; build
both margins and choose at bake time; tier the band by first-uncover pose with "paint all" as an
option; 16-bit deferred but standing.

- **Bake panel** (`moebius.html`, Debug View row, group "plate"; wired in
  `_wireDebugSheetControls`): far side (membrane | plane), fill (wash | mirrored far side),
  margin (off | picture | window), step faces (off | on), texture band (paint all | tier ≤ 35° /
  25° / 15°), sky (off | on). Remembered in `localStorage` (`bgPlateOptions`); the Build button
  runs the plane recipe when the far side is plane; stamped on the HUD (`plate=…`). Defaults are
  today's behaviour (membrane, wash, no margin, no faces, paint all, no sky) until you choose.
- **Band tier**: the sweep records per texel the smallest pose fraction at which it is demanded
  (`bandPose`); `_plugGeoBand` logs the band by first-uncover angle (15/25/35/45°) and builds the
  tier mask for the chosen angle (`tan(tier)/tan(envelope)`, no new constant); the SD bundle
  adds `dir_band_first_uncover.png` (the pose map) and `dir_mask_inpaint_tier.png` (the tier).
- **Smoothing**: the mirrored fill reflects the texel across the *local rim line* (tangent from
  the rim texels of the neighbouring lines) instead of along its own row; a step face takes one
  colour per rim segment (the run of pairs sharing the rim), the mean of its rim texels.
- **Measurement**: the photograph baked at ±30° horizontal (`ENV_DEG=30` in the harness), band
  against ±45°.


### 8a. What ran (all on `main`; commits `a297339`, `ea7248e`, `50a735d`, `fabe9c6`)

One serial chain per stage, watchdog on: the photograph three ways (full recipe with the mirrored
fill; the same with the wash; the plane arm at ±30°), then the kit eight with the recipe defaults,
then the follow-ups the results demanded (below). Every option is off in the kit chain, so the kit
is a regression check of the Sprint 6 code: **all eight scenes are bit-identical to v11** (band,
precision, recall, depth, carriers, clones: the v11 table in §6 stands unchanged).

### 8b. The band by first-uncover angle (decision C: the tier)

`bandPose` is the smallest pose fraction at which the sweep demanded a texel; the buckets are head
angles (fraction = tan θ / tan 45°). The sweep grid is 17 × 5, so its first horizontal pose is
7.1° and its first vertical pose 16.1°: a scene whose reveal is only vertical (S31's full-width
occluder, S32) shows nothing inside 15° for that reason, not because nothing opens.

| bake | band | ≤ 15° | ≤ 25° | ≤ 35° | ≤ 45° |
|---|---|---|---|---|---|
| photograph ±45° | 412 329 (47.4 % of the picture) | 24 % | 54 % | 85 % | 100 % |
| photograph ±30° | 359 220 (41.3 %) | 27 % | 71 % | 100 % | 100 % |
| S2 | 18 531 | 70 % | 89 % | 98 % | 100 % |
| S26 | 52 608 | 29 % | 64 % | 99 % | 100 % |
| S15 | 48 020 | 91 % | 97 % | 99 % | 100 % |
| S16 | 23 078 | 29 % | 45 % | 82 % | 100 % |
| S27 | 5 695 | 88 % | 93 % | 97 % | 100 % |
| S12 | 18 209 | 68 % | 97 % | 99 % | 100 % |
| S31 | 74 398 | 0 % | 58 % | 100 % | 100 % |
| S32 | 47 202 | 2 % | 76 % | 100 % | 100 % |

Reading: on the photograph a quarter of the band opens inside 15° and half inside 25°; the tier
at 35° (the bake panel's default) is 85 % of it. **The inner tiers are more precise than the whole
band** (`check_app_band.py`, tiers scored against the same truth: S2 precision 0.944 at ≤ 15°,
0.937 at ≤ 25°, 0.905 at ≤ 35°, 0.887 whole; S15 0.765 / 0.734 / 0.724 / 0.723): what is
demanded early is hidden content, what is demanded only at the rim carries the over-demand. So
tiering the texture stage costs nothing in precision and saves 15–46 % of the paint at 35° / 25°
on the photograph. The SD bundle now carries the pose map (`dir_band_first_uncover.png`) and the
tier mask (`dir_mask_inpaint_tier.png`, `meta.band_tier_deg`).

**Envelope (the C2 number):** ±30° horizontal shrinks the band from 47.4 % to 41.3 % of the
picture, not the ×0.58 the slide ratio suggests. The band is bounded by the far runs, not by the
slide: most of the photograph's reveals are already fully open well inside 30° (71 % of the ±30°
band opens by 25°), so the outer 15° of head angle adds only the last 13 % of texels. The envelope
is not the lever for the atlas; the tier is.

### 8c. Fill: wash vs mirrored far side (decision A)

Holes are unchanged by the fill (both 8 / 0 / 17 / 31 with the picture margin and faces; v11 was
91 / 15 / 395 / 65 without them), so this is a colour question. Kit colour error against the
truth's first hidden layer (mean |Δ| /255 on true-positive band texels):

| scene | wash | 1-D mirror (S5) | 2-D reflection (S6, tried) |
|---|---|---|---|
| S15 (open, textured far side) | 65.4 (median 56.7) | 32.4 (17.7) | 33.2 (18.3) |
| S2 (room, brick) | 32.8 (28.7) | — | 32.9 (29.0) |

- The **2-D reflection across the local rim line** (S6's streak fix) is falsified: the kit says
  equal, and on the photograph's plate texture (`plate_wash_1d_2d.png`) it is a patchwork of box
  streaks where the 1-D mirror is a coherent, if warped, continuation of the cave wall. The rim's
  tangent from three rim texels is too noisy on an 8-bit rim to define a reflection. Removed
  (rule 7), the 1-D mirror restored as the "mirrored far side" option (commit `fabe9c6`).
- The mirror halves the error where the far side is textured and the reveal wide (S15); on a
  room with a regular texture the wash is as good (S2). On the photograph the mirror reads as a
  warped copy of the wall behind the arm (`s6_face_sheet.png`, right column): more "something is
  there" than the wash, and more that the SD stage will have to overrule. Both remain bake
  options as you decided; **the plane recipe keeps the wash** until you have seen both live.

### 8d. Margins (decision B)

Nothing new to measure beyond §6 Item 6: picture margin 8 / 0 / 17 / 31, window margin closes the
outside corners too. Both are in the panel; the recipe's default is the picture margin.

### 8e. Step faces: the criterion was wrong, twice, and is now derived (decision E)

The Sprint 5 test ("parallel lines": the two runs' slopes along the rim's line equal within the
fit uncertainty) drew 977 faces on the photograph, and the Sprint 6 sheets showed what they were:
**bars across the reveal behind the arm and a picket fence along the arm's top** — faces between
the arm's silhouette and the cave wall, a true occlusion, not a step (`s6_isolate.png`). The
first correction (`ea7248e`, both axes' slopes equal) removed 672 of them but also **every one of
S16's 217 return-face pairs**: the diagnostic showed S16's two walls with identical column slopes
(0 = 0) and row slopes of −0.00138 vs −0.00134, sixty times the uncertainty. That is not noise:
a plane n·X = ρ is the disparity plane A x + B y + C with (A, B, C) = (n_x, n_y, n_z f)/(f ρ), so
**parallel planes at different distances have proportional gradients, not equal ones** — the
equal-slope test was only ever passing planes whose slope along the line was zero. The derived
test (`50a735d`): the normal is ∝ (A, B, C/f) with f the focal length in texels
((pw/2)/tan(hfov/2), from the portal), C from the fitted disparity at the rim texel and the two
slopes; two rims are a step when the two normals are parallel (cross product zero) within the
uncertainties propagated from the fits (slope tol/(2(len−1)) as before; value tol/2). No new
constant.

| bake | Sprint 5 (parallel lines) | equal slopes, both axes | parallel normals |
|---|---|---|---|
| S16 (grazing wall, jump row) | 217 | 0 | 209 (422 rims not parallel) |
| S2 (contact) | 248 | 105 | 105 (569 not parallel) |
| photograph | 977 | 305 | 361 (2 258 not parallel, 446 without a gradient across the line) |

On S16 the return face closes the slit along the jump row again (`steps_v3_zoom.png`). On the
photograph the count is back near a third of Sprint 5's and the faces that remain are between
terraces: **on 8-bit depth a jump between two flat terraces is, geometrically, a step between two
parallel fronto-parallel planes**, and no depth-only criterion can tell it from an occlusion —
the arm's curvature that would fail the test is below the quantum. Undrawn with faces v3: 18 / 0 / 28 / 44 (the Sprint 5 faces were covering a few holes: 8 / 0 / 17 / 31 with them).
Decision as recorded: faces are a bake option, on in the kit's recipe (exact depth), **off by
default for 8-bit photographs** until the 16-bit re-export (decision D) makes the test honest
there too. The segment colouring (one mean per rim segment) holds: S2's box side is one colour
instead of the checkerboard's stripes.

### 8f. Standing items

- **16-bit re-export of the photograph's depth** (`harness/depth16.py`, decision D): still the
  gate for step faces on photographs and for the far field (§4a); waiting on the estimator's
  output format.
- Open geometries unchanged: S26 beam gap (plane law far from the rim), rim-law join sparing
  curvature (would make the Shih pre-filter safe).

## 9. The live pass (2026-09-10): what your screen showed, what was wrong, what the holes are

You baked from the panel, dragged to 0.30 m / 0.07 m (56° / 19°, past the ±45° envelope, with the
Angle fade off) and saw holes with both fills, the mirror worse. Three separate things were true.

### 9a. The recipe's fill never reached the screen (bug, fixed; commit `2c0f269`)

Every rim-law bake since Sprint 2b threw at the last line of the band-fill block: the A215 log
line read `NREL` outside the block that declared it, the `catch` dropped the recipe's colour
texture (`plateColorTex = null`), and the plate rendered from the quick bake's one-sided colour
target instead. Wash and mirror alike. The harness never saw it because its console filters
passed only tagged lines; the raw browser log from yesterday's crash run has it. Consequences,
stated: the kit colour numbers (§6 Item 7, §8c) were computed on the pre-throw plate colour and
stand; **no screenshot or shot sheet before today showed the recipe's fill**, and the "mirror"
column of the Sprint 6 face sheet was the same fallback as the wash column plus faces. With the
fix in, wash and mirror render differently (`colourfix_check.png`). `NREL` is hoisted; the failure
now logs as an error and sets `window._qbBandFillFailed`; both harness filters pass any
`FAILED`/error line.

### 9b. The Build button and the blank select (fixed; commit `2c0f269`)

The Build button applied a *cached* copy of the plate options, so selects set without a change
event (the console command I gave you) built the membrane path with the plane flags. Your second
screenshot is that: the far-side select blank, the quick bake's a126 chamfer in the log (the plane
recipe skips it), the mirror flag applied to the wrong pipeline. The button applies the selects
first now; every plate bake logs `[S6] plate bake: far=… fill=…`; a select with no value resets to
its default with a warning. A re-bake by changing a select reproduces the first bake's holes
within ten pixels at every offset (measured, `ui_plane` first vs after change).

### 9c. Holes by angle, on your path (real Build button, eye offsets in metres as a drag sets them)

`harness/ui_path.js`; undrawn pixels inside the picture's rectangle; the membrane row is the
shipped quick bake for reference.

| eye offset (m) | head angle | membrane (shipped) | plane arm, 45° bake | plane arm, 60° bake |
|---|---|---|---|---|
| 0.05, 0 | 14° | 0 | 19 | 17 |
| 0.10, 0 | 27° | 0 | 28 | 27 |
| 0.14, 0 | 35° | 0 | 55 | 48 |
| 0.20, 0 | 45° (the rim) | 0 | 283 | 254 |
| 0.24, 0 | 50° | 0 | 459 | 420 |
| 0.26, 0.088 | 52° / 24° (your drag) | 0 | 307 | 265 |
| 0.301, 0.068 | 56° / 19° (your drag) | 0 | 441 | 371 |

Reading:
- The membrane has no holes at any angle because it never tears: it stretches the plate across
  every jump (the smear the plane arm was built to remove). That is the trade, not a bug.
- The plane arm's holes grow with the angle from ~50 px at 35° to ~300 at the rim and ~450 past
  it. My Sprint 5/6 shots were all at ≤ 27° (pose fractions 0.25 and 0.5), which is why they
  read 18–28 px: I never shot the rim. That was a gap in the measurement, now closed.
- **Baking the geometry to 60° instead of 45° barely helps** (283 → 254 at the rim, 441 → 371 at
  56°) although it costs almost nothing (band 47.4 % → 50.4 %). So the holes are *not* the
  carrier band running out, which was my first explanation. The buffer says what they are:
  slits in the *middle* of the reveal (`holes50_zoom.png`) — the plate torn at its own far-field
  discontinuities (S2b.4: a plate quad across an unjoined plate edge is not drawn). Those cliffs
  are sub-pixel at small angles and open in proportion to the pose. Plate 2 bridges the ones
  that carry a second layer; the rest open.

### 9d. What the slits are (probe `photo_torn`, `plate_torn_overlay.png`; corrected by the Sprint 7 audit)

The plate-tear pass drops 136 191 of 1 737 400 plate triangles (7.8 %) on the photograph, touching
113 997 plate texels, 84 234 of them inside the carriers and 73 010 inside the band. The overlay
(yellow = torn inside the carriers) is a lattice of long straight horizontal and vertical seams
across the whole band: the far field is computed one line at a time and neighbouring lines
disagree, so the plate behind an occluder is a patchwork of ribbons torn along every boundary.
Each seam is sub-pixel at rest and opens in proportion to the pose. That is the whole residual:
not the band's extent (§9c), not the fill.

**Correction (2026-09-10, Sprint 7 step 1).** The first version of this section quoted "91 094
carrier-next-to-carrier pairs of the same kind, median jump six quanta, p90 a third of the
volume". Those jump statistics were computed with the plate-depth dump unflipped (plate rows are
stored bottom-up) against source-row masks, i.e. at the wrong texels; the torn-texel counts above
were right, the pair statistics were not. The audit below (§10a) replaces them.

### 9e. Where this leaves the "comprehensive" question

Your intuition is right for the part of the plate that exists: a carrier moves with the far
surface and covers its reveal at every pose, including past the envelope (60° bake: the band grows
3 %, nothing new opens at its edge). What opens are the seams between the plate's own ribbons, and
the choice is the same one the plane arm made at the foreground: tear (a hole, honest) or stretch
(a skin, covered). Options, with the numbers above:

- **A. Stretch the plate's internal seams, tear only its rim** (`window._plateStretchInner`,
  built today: an unjoined plate edge between two *carriers* is drawn; an edge touching an
  own-depth texel, the foreground rim or the occluder's interior, stays torn). Both sides of an
  internal seam are far surfaces, so the skin is between two backgrounds, never a foreground
  clone, and the reveal's outline stays the rim law's tear. Advantages: no new constant, the
  membrane's coverage with the plane arm's silhouettes, hours not days. Disadvantages: where the
  far field really is two surfaces (p90 jump 0.35) the skin is a visible smear at large angles;
  it hides the seams rather than removing them. Measured below (§9f).
- **B. One sheet per reveal**: reconcile the per-line far candidates in 2-D, one least-squares
  plane (or one smooth surface) per connected reveal region with the same fit uncertainty, split
  only where the samples disagree beyond it (the crossing rule in 2-D). Advantages: the honest
  fix, the seams vanish instead of being skinned, and it would make the Shih pre-filter safe (the
  same join-across-lines question). Disadvantages: a rim-law change with the kit re-scored on all
  eight scenes; days; and 8-bit terraces will still produce ribbons where the source has them.
- **C. Enforce the design boundary**: the Angle fade (35° → black at 45°) is the contract the
  bake was built to; with it on, the worst you see is the 35° row. Advantages: nothing to build.
  Disadvantages: 50 px at 35° and ~280 at the rim remain, and you turned the fade off to look,
  which is a legitimate use.

Recommendation: A now as the plane recipe's default (once you have seen it), B as the next rim-law
item; A does not preclude B, and when the far field is one sheet the skins vanish on their own.

### 9f. Option A measured

`window._plateStretchInner`, now the panel's seventh option (**seams: torn | stretched**); the
bake keeps 96 701 of the 136 191 triangles it used to drop (the 39 490 still dropped touch an
own-depth texel: the rim, the occluder's interior).

| eye offset (m) | head angle | membrane (shipped) | plane, seams torn | plane, 60° bake | plane, seams stretched |
|---|---|---|---|---|---|
| 0.05, 0 | 14° | 0 | 19 | 17 | 3 |
| 0.10, 0 | 27° | 0 | 28 | 27 | 4 |
| 0.14, 0 | 35° | 0 | 55 | 48 | 3 |
| 0.20, 0 | 45° (the rim) | 0 | 283 | 254 | 7 |
| 0.24, 0 | 50° | 0 | 459 | 420 | 3 |
| 0.26, 0.088 | 52° / 24° (your drag) | 0 | 307 | 265 | 0 |
| 0.301, 0.068 | 56° / 19° (your drag) | 0 | 441 | 371 | 0 |

The stretched plate reads as one continuous far surface behind the arm at every angle
(`stretch_sheet.png`); the skins are wash-coloured and mostly a few quanta deep, with faint
striping where the ribbons differ more. Kit precision/recall are untouched by construction (the
band and carriers are the same; only the plate's index changes). The recipe for the live pass is
therefore: far side plane, fill wash (or mirror to compare), margin picture, faces off, band
tier 35°, sky off, **seams stretched**; the Angle fade is your choice. B (one sheet per reveal)
remains the honest next item; with it the skins disappear on their own.

## 10. Sprint 7 — one far-field sheet per reveal (plan approved 2026-09-10; `quiet-snacking-brook` plan)

### 10a. Step 1 — the seam audit (probe `photo_audit`; `scratchpad/seam_audit.py`)

Every 4-neighbour edge between two carriers whose plate depths the app's own join
(`joinedIdx`: eye-distance ratio ≤ t = 1.0125, or the affine rescue along the line) rejects, with
the plate rows flipped correctly, classified by the two texels' far axis, far kind, rim texel and
the rim texels' source sheet (4-connected component of the source under the same join):

| class | edges | share |
|---|---|---|
| same axis, same kind, **across lines** (adjacent lines chose different rim texels / runs on one surface) | 23 785 | 41.2 % |
| **axis flip**, same kind (row candidate next to column candidate) | 13 454 | 23.3 % |
| axis flip + kind flip, same sheet | 7 283 | 12.6 % |
| axis flip + kind flip, other sheet | 5 320 | 9.2 % |
| same axis, kind flip, across lines | 5 245 | 9.1 % |
| along the line (any class) | 1 492 | 2.6 % |
| the rest (other sheet, same axis) | 1 198 | 2.1 % |
| **total unjoined carrier–carrier edges** | **57 777** | (row 26 k / column 31 k) |

Jump across a torn edge: median 19 × tol (eye-distance ratio 1.046 against t 1.0125), p25 10,
p90 82 × tol. Along a line the plane law is continuous (2.6 % of the seams, as the design says
it must be); **the seams are cross-line disagreements (41 %) and row-versus-column arbitration
(45 %)**, with jumps far above fit noise: different runs or different axes chosen on neighbouring
texels, not least-squares scatter. Two consequences for the plan:

- **Step 5 (one continuous rule replacing the row/column arbitration) is not optional**: 45 % of
  the seams are axis flips, which pooling within an axis cannot touch.
- **The source "sheet" is useless as a grouping key on 8-bit data**: the join with its affine
  rescue leaves 24 sheets on the whole photograph, so "same sheet" holds for 89 % of the seams.
  Groups must be formed by local structure (adjacent lines' far runs overlapping in position and
  agreeing within tol at the shared position), not by the global component. The plan's risk
  note said as much; the audit makes it a design change for step 3.

Also recorded: the observed-depth merge is not a seam source (along-line jumps > tol: a-priori
1.4 % of same-rim pairs, after the merge 0.6 %), and the rendered plate depth equals the far
field within a quantum on 475 964 of 476 941 carriers (the 977 others are the A252 push-back).

### 10b. Step 3 — pooled planes, tried and falsified; the join law across lines instead

**Pooled planes (built, measured, removed).** As planned: nodes = (axis, side, run) used by a
texel; links between adjacent lines whose runs overlap and are joined at the overlap; groups by
union-find; pieces by greedy growth while one plane fits every member line's window with RMS
≤ tol; one plane per (piece, rim distance). On S2 (exact planes) it reproduces v11 exactly
(97 pieces, 90 ms; band 18 531, P .887, R .999). On the photograph it does nothing: 8 609 nodes,
7 827 links, 782 groups but **5 977 pieces** — the piece test rejects 5 195 of 7 827 merge
attempts, and the diagnostic says why: the worst RMS/tol on an attempt is 1.53 at the median,
3.4 at the 75th percentile, 9.1 at the 90th. Adjacent lines' far runs on this cave do **not** lie
on one plane within the tolerance; only a quarter of the attempts fit under 0.8. Plate tears
139 206 against 136 191. The premise ("piecewise planar across lines within tol") is falsified on
8-bit curved data; the code is removed (rule 7), the pass 1 / pass 3 structure stays.

**The join law across lines (built; `window._farJoin`, on).** The runs are defined by the rim
law along a line (second differences within tol, the ratio test for a first pair), and the plate
is torn by the same law. So the far field is made to satisfy that law across lines as well: for
every triple of free texels along either axis the second difference is clipped to tol at the
middle texel (the minimum-norm correction, (1, −2, 1)/6 of the excess); for an isolated pair the
ratio bound linearised at the pair. Projections are applied from a worklist of violated
constraints until none remains; the total is bounded by the line length times the domain. A plane
has zero second differences and is untouched. A jump of J·tol between lines becomes a ramp of
curvature tol over roughly √(2J) texels: 19 tol → 6 texels, 82 tol → 13. Every edge inside the
free set then passes the plate's tear test by construction; the rim (free against not free) and
the sky stay as they are. Falsified premises removed with it: none yet; `_plateStretchInner`
and the seams select are candidates once the kit and the holes table are in.

First measurement (sweep form, before the worklist): 713 765 free texels, 315 531 violations at
the start, 441 425 texels moved (mean 0.046 of the normalised depth = 2.8 mm on the 0.06 m
volume, max 0.51); carrier–carrier unjoined edges **57 777 → 4 124**; torn plate texels inside
the carriers **84 234 → 19 576**, outside 29 763 → 9 599; plate triangles dropped
**136 191 → 32 224**. Cost 24 s and not converged at the sweep bound (the isolated-pair rule was
in log space); the worklist form (all constraints in disparity, work proportional to violations) still ran to its
budget: 730 M projections, excess 0.0135, 36 s, tears 32 375.

**Gated by the extrapolation uncertainty (tried, removed).** Only seams within the two texels'
extrapolation uncertainties (tol/2 plus the slope uncertainty tol/(2(w−1)) times the distance;
a one-sample window: half a quantum per texel) were projected, the correction weighted toward
the less certain texel. Offline, only 33–41 % of the seams pass that gate; in the app the tears
stayed at 112 734 / 114 099 and the loop again ran to its budget (19–37 s). Two lessons: the
formal uncertainty of a flat 8-bit terrace extrapolation is far too small (a six-sample flat
window is "confident" and 10 tol wrong at g = 60), so the gate keeps the ribbons; and iterative
projection onto curvature constraints is diffusion, hopeless at this scale.

**The closed form (kept; `window._farJoin`).** The plate's tear test is the rim law's join: an
edge holds when the eye-distance ratio across it is within t. So the far field is made
t-Lipschitz across the free set in log disparity — no step larger than log t per texel along
either axis — with the smallest sup-norm change to the per-line estimates: the midpoint of the
upper and lower Lipschitz envelopes (McShane–Whitney), each an L1 distance transform in two
raster passes. O(N), deterministic, no iteration, no constant beyond t. A plane's slope is far
below the bound and is untouched; a ribbon seam of ratio r becomes a ramp of log r / log t texels
(r = 1.046 → 4 texels); a genuine step between two far surfaces becomes a longer ramp, a skin
between backgrounds where plate 2 carries the second surface when it is known. Three details mattered on the way: the transform must be the chessboard metric, not L1, because
the plate's tear test checks a triangle's diagonal too (L1 allowed t² across a diagonal and left
87 849 torn triangles at the ramps' kinks); the bound is taken a hair inside (1e-4) because the
tear test runs on float32 depths (56 200 → 34 726 triangles); and the midpoint is capped at the
texel's own disparity (the reach) with one more upper-envelope pass, which only lowers and stays
Lipschitz (226 texels).

Measured (photograph, `photo_v19`): 713 765 free texels, 56 731 axis edges beyond the ratio t
before, **0 after**, 189 047 texels moved (mean 0.097 of the normalised depth, 5.8 mm on the
0.06 m volume; max 0.39), **0.3 s**. Carrier–carrier unjoined edges 57 777 → 4 551, of which
3 867 are the band's own rim ring (own-depth texels against the far plate, which must tear) and
**684 are interior** (the sweep's 816 push-back texels): −98.8 %. Torn plate texels inside the
carriers 84 234 → 20 858; plate triangles dropped 136 191 → 34 726, the remainder the rim, the
band's outer boundary (carriers against free texels the sweep never demanded, at their own
depth, hidden behind the foreground inside the envelope) and the push-back. S2: 4 edges beyond t,
14 texels moved, band 18 529 (18 531), P .887, R .999 — unchanged.

**Kit under the unconditional join** (every scene, the same truth; v11 → joined):

| scene | band v11 → v12 | P v11 → v12 | R v11 → v12 | depth median (m) | depth p90 (m) | layer-2 px |
|---|---|---|---|---|---|---|
| S2 | 18531 → 18529 | 0.887 | 0.999 | 0.000 | 0.043 | 1108 |
| S27 | 5695 | 0.859 | 1.000 | 0.000 | 0.000 | 60 |
| S12 | 18209 → 18255 | 0.927 → 0.924 | 0.994 | 0.000 | 0.076 | 30 |
| S26 | 52608 → 62619 | 0.457 → 0.396 | 0.937 → 0.968 | 0.000 → 0.002 | 0.056 → 0.055 | 35396 → 45405 |
| S16 | 23078 → 23120 | 0.190 → 0.189 | 0.972 → 0.969 | 0.000 | 0.000 → 0.004 | 565 → 505 |
| S31 | 74398 | 0.946 | 1.000 | 0.000 | 0.000 | 0 |
| S15 | 48020 → 57181 | 0.723 → 0.594 | 0.996 → 0.975 | 0.184 → 1.475 | 8.566 | 18781 → 25083 |
| S32 | 47202 → 55995 | 0.729 → 0.314 | 0.811 → 0.415 | 0.000 → 1.604 | 0.000 → 1.985 | 0 |

Rooms hold (S2, S27, S12, S16, S31 within noise); S26's beam gap widens the band (+19 %, P .457 →
.396, R .937 → .968); **S15 and S32 break** (S15 depth median 0.18 → 1.48 m, P .723 → .594;
S32 P .729 → .314, R .811 → .415, depth 0 → 1.6 m): an open scene's far side is genuinely layered
— crown, hill, sign, sky — with eye-distance ratios of 2 to 10 between the layers, and ramping
those at t per texel drags whole surfaces toward their neighbours. On the photograph no seam has a
ratio above 2; on S15 the 2 247 that do are the layers.

Holes on the user's path with the unconditional join and the seams torn (no skin): 1 / 1 / 0 / 0 /
1 / 3 / 8 px at 14 / 27 / 35 / 45 / 50 / 52 / 56°, the same coverage the stretched skin gave
(3 / 4 / 3 / 7 / 3 / 0 / 0) with the plate genuinely continuous. The band shrank to 36.9 % of
the picture (47.4 %): ramps put plate nearer than the far runs did and some reveals close earlier.

### 10c. The gate: a seam is one surface only if its ramp fits inside the reveal

A disagreement between two neighbouring far estimates can be reconciled as one surface only within
the reveal that produced them: if the ramp closing it, log r / log t texels, is longer than the
larger of the two texels' distances to their rims, the two estimates cannot both be continuations
of what is visible on either side of that rim, and the seam is a layering (plate 2 carries the
second surface where the law found one). Texels against texels, no constant. Offline it keeps
100 % of the photograph's, S26's and S2's seams and excludes 91 % of S15's seams of ratio > 2
(2 247 → 192). Implemented as cut edges the distance transform does not cross (the raster passes
then repeat until nothing changes; a path of L steps needs at most L passes). Measured: the photograph keeps 61 of 56 731 seams as layerings and is otherwise as above; S15
improves from 1.48 to 0.89 m median depth but stays far from 0.18 (the envelope leaks around gaps
in a layering boundary); S32 has no seam the gate excludes (its reveal is 180 rows deep) and stays
broken.

### 10d. Two more forms, and the honest state

- **Second-layer texels left out.** Where the law found two far surfaces at a texel, layer 1 is
  one of two sheets and its neighbour may hold the other; such texels are excluded from the join
  (plate 2 carries the other sheet there). S26 returns exactly to v11 (52 608 / .457 / .937; its
  beam gap has a second layer throughout). S15: 33 494 of 56 354 free texels excluded, still
  P .583, depth median 0.74 m. S32 has no second layer and is unchanged.
- **The plane law's own slope as the step bound.** S32's ground recedes to 43 m; near the horizon a
  legitimate plane changes eye distance by more than t per texel, which the source joins by the
  affine rescue, not the ratio — so the allowed step across an edge became the larger of log t and
  the slope the winning candidate extrapolates along that axis. S32's seam count did not move
  (28 800) and this paragraph first blamed neighbouring columns the plane law treats differently.
  **Corrected by Sprint 7b (§10f):** the slope bound had simply never taken effect on S32 — the
  ground cut records the candidate's slope as 0 while its value follows the ground plane, so the
  bound fell back to log t on every one of S32's 144 800 free texels (all ground-cut). With the
  slope the value actually has (`mv`, D4), S32 under the join is identical to v11 (47 202 / .729 /
  .811 / 0.0 m). S15's regression under the join stands (§10f).

Kit under the final form (second-layer texels out, ramp gate, slope bound):

| scene | band v11 → v12 | P v11 → v12 | R v11 → v12 | depth median (m) | depth p90 (m) | layer-2 px |
|---|---|---|---|---|---|---|
| S2 | 18531 → 18529 | 0.887 | 0.999 | 0.000 | 0.043 | 1108 |
| S27 | 5695 | 0.859 | 1.000 | 0.000 | 0.000 | 60 |
| S12 | 18209 → 18255 | 0.927 → 0.924 | 0.994 | 0.000 | 0.076 | 30 |
| S26 | 52608 | 0.457 | 0.937 | 0.000 | 0.056 → 0.055 | 35396 |
| S16 | 23078 → 23120 | 0.190 → 0.189 | 0.972 → 0.969 | 0.000 | 0.000 → 0.004 | 565 → 505 |
| S31 | 74398 | 0.946 | 1.000 | 0.000 | 0.000 | 0 |
| S15 | 48020 → 58450 | 0.723 → 0.583 | 0.996 → 0.977 | 0.184 → 0.735 | 8.566 | 18781 → 24318 |
| S32 | 47202 → 55995 | 0.729 → 0.314 | 0.811 → 0.415 | 0.000 → 1.604 | 0.000 → 1.985 | 0 |

Photograph under the final form: 58 786 texels with a second layer left out; carrier–carrier
seams 57 777 → 21 060, plate triangles 136 191 → 65 908 (the unconditional form: 4 551 and
34 726). Half the photograph's gain goes with the exclusion.

**State on `main`.** The join is a bake option (plate → *far field: per line | joined*), **off by
default**: right on closed scenes (rooms unchanged, the photograph's seams gone or halved), wrong
on open layered scenes with grazing ground, and no constant-free rule found today separates the
two from the depth alone. The recipe for holes stays *seams stretched* (§9f: 3 / 4 / 3 / 7 / 3 / 0
/ 0 px), which touches no depth and no kit number; the joined field with the seams torn gives
1 / 1 / 0 / 0 / 1 / 3 / 8 on the photograph if you prefer a plate with no skins.

### 10e. What the sprint established, and what remains

1. The seams are choice flips of the per-line plane law (which run, which axis), not fit noise;
   along a line the law is continuous (§10a).
2. Pooling across lines cannot fix them on 8-bit curved data (no plane within tol); a
   Lipschitz join can, in closed form, at 0.3–0.6 s (§10b).
3. The join is wrong where the far side is genuinely layered or grazing (S15, S32): the plane
   law's per-column treatment flips (ground continuation vs flat) and its layer-1/layer-2
   patchwork are the real defects, and they sit upstream, in the candidate choice (§10d).
4. The plan's steps 4–5 (kind-2 pair planes; one continuous layered rule replacing the axis
   arbitration) were designed for the pooling that was removed; their aim — a candidate choice that
   is consistent across lines and columns — is exactly what item 3 asks for and is the next honest
   step. Step 6 (removals): `_plateStretchInner` stays as the hole fix; the join stays as an option;
   the pooling and the iterative projections are already out.

## 10f. Sprint 7b — a consistent per-texel choice (plan approved 2026-09-10; four designs, measured one by one)

The four designs from the §10e item 3, each built behind the measurement and kept only if the
seams, the tears and the kit eight agree. Baselines: photograph carrier–carrier seams 57 777
(45 % axis flips, 41 % same axis across lines, 2.6 % along a line), plate tears 136 191; kit as in
the §10d table's v11 column.

### 10f.1 Step 0 — the exports, and what the pre-measurements said (probe `photo_s7b0`, `S32/S15_…_s7b0`)

New audit exports from the plane law: `farM` (the winning slope along its axis), `farCut` (the
value came from the ground cut), `farAxV`/`farAxS` (each axis's candidate value and its
uncertainty σ = tol_i/2 + g·tol_j/(2·max(1, w−1))), the second layer's arrays.
`scratchpad/s7b_checks.py` reads them.

- **D4's premise held.** S32: all 144 800 free texels are ground-cut; 29 600 column edges step
  beyond log t and every one of them is also beyond the recorded slope bound, because the
  recorded slope was 0. S15: 2 936 column edges beyond the bound, 1 970 of them with `farM` = 0 at
  both ends (thin runs continued flat — D3's target), 709 kind flips.
- **D1's gate is immaterial.** Photograph: 22 068 axis-flip seam edges; only 2 676 have both
  endpoints whose row and column candidates agree within σ_r + σ_c (median |row − col| is 2.2 σ).
  An inverse-variance blend would touch 12 % of the axis flips and none of the rest. D1 was not
  built.

### 10f.2 D4 — `farM` is the slope the value has (kept; commit `69ef0fb`)

The candidate carries `mv`: the ground's slope where the value was cut to the ground plane, the
interpolation's slope for a same-plane pair, the fitted slope otherwise; the far field itself is
untouched (`m`/`v0` unchanged). Under the join (option on):

| scene | v11 | join on, before D4 | join on, after D4 |
|---|---|---|---|
| S32 | 47 202 / .729 / .811 / 0.000 m | 55 995 / .314 / .415 / 1.604 m | **47 202 / .729 / .811 / 0.000 m** |
| S15 | 48 020 / .723 / .996 / 0.184 m | 58 450 / .583 / .977 / 0.735 m | 58 041 / .587 / .977 / 0.716 m |

S32's regression under the join was the missing bound, not the columns' treatment (§10d
corrected). S15's is not: its seams are thin runs continued flat next to sloped runs and layer
flips, which no bound repairs.

### 10f.3 D2 — first arrival resolved toward the better-fitted run (built, falsified, removed)

As planned: candidates whose arrival poses cannot be told apart within their uncertainties
(|f0_a − f0_b| ≤ df0_a + df0_b, df0 = f0·σ/dlt) count as one arrival, and the run fitted over the
larger window wins, then the longer run. Kit-safe as predicted (S12's far field byte-identical;
S2 moved 4 of 360 000 texels, 11 ties, P .887 unchanged). On the photograph it made the choice
**less** consistent:

| photograph | before (D4) | D2 |
|---|---|---|
| ties resolved | — | 227 585 of 1 183 755 arrivals |
| carrier–carrier seams | 57 777 | 65 448 |
| same axis, same kind, across lines | 23 785 | 29 406 |
| plate triangles torn | 136 191 | 148 151 |
| free texels whose slope is 0 (flat thin runs) | 437 861 | 397 251 |

The window is min(len, g+1) and a run's *length* is the quantity that 8-bit curvature fragments
from one line to the next (median run 6–8 texels on the photograph): preferring the wider window
prefers the attribute that changes most between neighbouring lines. Removed (the strict first
arrival stands); the reason is recorded at the pick.

### 10f.4 D3 — a thin run borrows the slope of the joined, longer run on the neighbouring line (built, falsified, removed)

First the refactor: the candidate arithmetic of the walk and of the rebuild became one helper
(`evalRun`), byte-identical on S2 and the photograph. Then the borrow, as planned: a thin run
(shorter than the gap it must cross) that is neither sky nor a ground run takes the fitted slope of
the run on line l±1 that overlaps it, is joined to it by the rim law at both ends of the overlap,
and is longer beyond the rim; own rim value and own colour window kept; ground branch first.

| | v11 | D3 |
|---|---|---|
| S2 | 18 531 / .887 / .999 | unchanged (5 far-field texels moved) |
| S32 | 47 202 / .729 / .811 / 0.000 m | unchanged (0 borrows: every column is ground-cut) |
| S15 | 48 020 / .723 / .996 / 0.184 m | 47 831 / .726 / .996 / 0.159 m (12 698 borrows) |
| S26 | 52 608 / .457 / .937 | 53 705 / .448 / .938 (984 borrows) |
| S16 | 23 078 / .190 / .972 | 23 068 / .190 / .972 (861 borrows) |
| photograph seams | 57 777 | **136 040** (304 847 borrows) |
| photograph plate tears | 136 191 | **298 038** |
| photograph "same axis, same kind, across lines" | 23 785 | 80 038 |

S26 shows the mechanism at kit scale: 84 far-field texels changed, all on the beams' edges, and
the flat rule had every one of them exactly right (error 0.000 m against the truth); the borrowed
slope put them 0.037 m off, and the sweep then grew the band by 1 397 texels of which 40 are
truly hidden. The two lines *are* joined by the rim law, at a **fold**: the beam's side face meets
the background continuously, so "joined at both ends of the overlap" does not mean "one plane" —
and a fold across lines is exactly where the neighbour's slope is not the thin run's. On the
photograph the neighbouring line's run is no steadier than the thin run's own (8-bit curvature
fragments both), and the borrowed slope doubled the seams. Removed; the helper stays; the reason
is recorded above it.

### 10f.5 What Sprint 7b established

1. **The join's S32 failure was a missing bound, not a per-column inconsistency** (D4). With the
   slope the value has, S32 under the join is v11 exactly. D4 is kept; it changes nothing unless
   the *far field: joined* option is on.
2. **Both attempts to make the per-line choice steadier by leaning on run attributes made it
   less steady** — D2 on the run's length, D3 on the neighbouring run's slope. On 8-bit curved
   data the run structure itself is what varies from line to line (median run 6–8 texels on the
   photograph); any rule that reads more of it inherits more of that variation. The strict first
   arrival with flat thin continuation — the v11 law — is the steadiest of the forms measured.
3. **D1 is immaterial** (12 % of the axis flips pass its gate; not built).
4. **State on `main`.** Defaults unchanged from §10d: the join is an option (now right on S32,
   still wrong on S15 by 0.5 m of depth median), *seams stretched* is the hole fix, the strict
   per-line law stands. What the seams need is not a steadier per-line choice but a rule that
   does not choose per line at all — a far field solved on the reveal region with the rims as
   boundary and the layering (plate 2) as a constraint. That is the join's problem statement with
   S15's layered reveals handled inside it, and it is the next design, not this sprint's.

Standing item unchanged: the photograph's 16-bit depth re-export (the app's float path is ready;
the source model run is not in this environment).

## 11. The 16-bit test — what the first export was, and what the next one needs (2026-09-10 late; `tmph88azwsl.png`, `moebiusv2` commit `eb37cd9`)

The file is a 16-bit PNG container (I;16, 851×1023, the photograph's size) holding about eight
bits of content:

| property | `tmph88azwsl.png` | a 16-bit export |
|---|---|---|
| value range | 27 … 329 | 0 … ~65535 |
| distinct values | 303, every gap exactly 1 | tens of thousands |
| relation to the 8-bit map | 1.18·d8 + 27, residual σ ≈ 1.8 eight-bit quanta, corr .9995, same near/far sign | sub-quantum detail |
| as the app loads it (`bgDecodeDepth16`: value/65535, no normalisation) | depth 0.0004 … 0.0050 — the scene in 0.46 % of the range | the full range |

The model's output was rounded to integer units (303 levels) and cast to uint16, rather than
scaled to 0…65535 from the float tensor. It is not the 8-bit map rescaled (residual 1.8 quanta),
so it is a second quantisation of the same estimate, not more precision.

**Run 1, the file as pushed (probe `photo_16raw`).** The 16-bit ingest path ran (max depth in the
dump = 329/65535 exactly). The bake is flat: 26 972 row runs, texels with a far side 0, reach
0 %, plate torn 0. The whole photograph sits at one depth as far as the parallax law is
concerned. Valid as the ingest test; nothing else.

**Run 2, the same 303 levels stretched to 0…65535 (probe `photo_16str`; a scratchpad copy, never
the photograph's depth).** Worse than the 8-bit map, not equal to it:

| | 8-bit map (`photo_s7b0`) | 303 levels stretched to 16 bits |
|---|---|---|
| runs per row / column (median length) | 9.3 (6) / 7.9 (8) | 9.6 (2) / 7.5 (3) |
| texels with a far side | 713 765 (82.0 % of the plate) | 676 889 (77.8 %) |
| carrier–carrier seams | 57 777 | 81 133 |
| plate triangles torn | 136 191 | 189 130 |

The reason is the app's own rule, and it matters for the real export too: the source quantum is
*detected* as the smallest grid the samples land on (a89/`bgSourceQuantum`: 255, 4095, 65535),
and the bake overwrites `_qbSrcQuantum` with it. The stretched samples land on the 65535 grid,
so every tolerance was set to 1/65535 while the map's real step is 217/65535 — each level change
read as a jump, the runs fragmented to 2–3 texels, and the seams rose 40 %. There is no honest
control on this file: 303 levels cannot be put on the 255 grid, and a 16-bit PNG cannot land on
the 4095 grid exactly.

**What the next export needs.** From the model's float output `d`, before any 8-bit step:
`uint16(round((d − d.min()) / (d.max() − d.min()) · 65535))`, same near/far sign as today's map
(this file already has the right sign), saved as 16-bit greyscale PNG; `len(np.unique(img))`
should be in the tens of thousands. And one thing to decide *before* reading its numbers: with
a genuinely continuous map the detected quantum will be 1/65535, and the rim law's tolerance
(the quantisation step) will then be far below the estimator's own noise. The 8-bit runs never
met this because the quantum was above the noise. The first 16-bit bake should therefore be read
with the tolerance question open, and if the runs fragment as they did here, the tolerance needs
a noise term measured from the data (the residual of the affine fit along runs is one candidate),
not a constant.

### 11b. The real 16-bit map (`depth16.png`, `moebiusv2` commit `0c00443`; probes `photo_16bit`, `photo_16q8`)

The second export is a true 16-bit map: 0…65535, 58 177 distinct levels, Depth Anything V2
**Large** through `transformers`, scaled from the float output. It is a different estimate from the
old map (correlation 0.92; new − old mean +38, σ 22 of 255 levels; the Space that made the 8-bit
map ran a smaller model — see `s16_maps_sheet.png`). So the comparison is three-way: the old map,
the new map requantised to 8 bits (`round(v/257)`, 248 levels), and the new map at 16 bits. The
middle column isolates the model; the right column isolates precision.

| | old 8-bit (Space model) | new model, 8-bit | new model, 16-bit |
|---|---|---|---|
| source sheets under the join law | 24 | 128 | **1 346** |
| runs per row (median length) | 9.3 (6) | 8.6 (4) | 10.3 (**2**) |
| runs per column (median length) | 7.9 (8) | 7.3 (5) | 7.5 (**2**) |
| texels with a far side | 713 765 | 732 118 | 697 270 |
|   same-plane pairs | 56 100 | 65 187 | 55 602 |
|   crossings | 15 172 | 7 343 | 9 241 |
| thin candidates / all | 738 939 / 1 183 755 | 786 782 / 1 149 532 | 643 970 / 1 046 574 |
| second-layer texels | 58 786 | 85 601 | 78 564 |
| reach, % of plate | 82.0 | 84.1 | 80.1 |
| band at 15° / 25° / 35° / 45° | 100 130 / 223 167 / 349 546 / 412 329 | 142 726 / 307 773 / 487 015 / 598 571 | 137 290 / 296 687 / 479 051 / 581 727 |
| carrier–carrier seams | 57 777 | 64 354 | **89 355** |
|   same axis, same kind, across lines | 23 785 | 26 907 | 29 583 |
|   jump median, in tol | 19.0 | 14.4 | 3 290 |
| plate triangles torn | 136 191 | 155 874 | **199 962** |
| holes on the user's path, seams stretched (px at 14/27/35/45/50/52/56°) | 3 / 4 / 3 / 7 / 3 / 0 / 0 (old map) | 7 / 14 / 3 / 0 / 0 / 0 / 0 | 30 / 33 / 29 / 19 / 9 / 11 / 2 |

**The model changed more than the precision did.** At 8 bits the new estimate has 45 % more band
at 45° (598 571 vs 412 329 texels), more second-layer texels and fewer crossings: it separates the
figure from the cave more strongly and carries the corner vignette as depth. Seams and tears rise
with it (+11 %, +14 %), at the same jump size in tol. That is the estimate, not the pipeline.

**Sixteen bits made the per-line law worse, and the reason is measured.** The extra eight bits of
this map are mostly noise: the part of each value below one 8-bit step has σ 0.29 of a step and a
lag-1 autocorrelation along rows of 0.16 (smooth ramps would give ≈ 1, white noise 0). The rim law's
tolerance is the quantisation step, so at 16 bits it is 257× smaller while the estimator's jitter
is unchanged: along rows the second difference exceeds tol on **79 %** of texel triples (8-bit:
1.4 %), the runs fragment to two texels, the source falls into 1 346 sheets, and every candidate is
thin. A 5-texel affine fit along rows leaves a residual of median 1.8 tol at 16 bits (p90 6.8),
against 0.01 tol at 8 bits — the same physical residual (7e-5 vs 1e-4 in disparity), read against
two different tolerances. This is the §11 question answered: **the tolerance has to carry a noise
term measured from the data, not only the quantum.** The natural form is the one this measurement
used — the residual of the along-line affine fit, which is exactly the quantity the rim law's
affine rescue already computes — with the quantum as its floor. Until it exists the 16-bit map
is not a better input to this pipeline than its own 8-bit requantisation; with it, the 16-bit map
removes the 8-bit quantisation as a cause without adding one. Not built here; it is the next design
step and it precedes any further seam work on the photograph, because it changes the run structure
every measurement in §10 was made on.

Holes (`ui_path.js`, now taking the seams/join selects as OPTS 7–8): single digits on the 8-bit
requantisation, tens on the 16-bit map — the fragmented runs reach the plate as more torn
triangles (149 873 stretched vs 119 215) and a few land as holes. `s16_angles_sheet.png` shows
the two side by side at 27°, 45°, 52°/24° and 56°/19°.

**State.** `harness/defaultImgDepth.png` is unchanged (the old map); `depth16.png` sits at the
root of `moebiusv2` where the user put it. Nothing in the app changed. The standing 16-bit item is
closed as delivered and measured; the noise-term tolerance is the new open item, ahead of the
reveal-region far field of §10f.5.

## 12. The depth bake-off (2026-09-11; plan `S8_depth_bakeoff_plan.md`; outputs and scripts in `research/bakeoff/`)

Run in this session on CPU after the environment's network access was set to Custom (the user's
change took effect on the running session). Four models on the photograph, each once, at their
own resolution handling; each output kept as the raw float and as a 16-bit inverse-depth PNG
(bright = near); every app number from the 8-bit requantisation of that PNG, as the plan fixed.
Baselines: the old Space map and the DA2-Large map at 8 bits (§11b).

| model | how it ran | seconds (4 CPU cores) | what came out |
|---|---|---|---|
| Depth Pro (Apple) | `apple/ml-depth-pro`, `depth_pro.pt`, `model.infer` | 50 | metres 4.4 … 6.0: **a flat picture** with a top-to-bottom gradient; no figure, no cave (`check_depthpro.png`) |
| MoGe-2 ViT-L | `Ruicheng/moge-2-vitl`, `model.infer`, resolution level 9 | 11 | metres 4.85 … 5.13: **a picture with 28 cm of relief**; right sign, faint figure |
| Depth Anything 3 Mono-Large | `depth-anything/DA3MONO-LARGE`, `process_res=1008` (default 504) | 14 | scale-invariant depth 0.32 … 1.41, full scene |
| Pixel-Perfect Depth | `gangweix/pixel-perfect-depth`, 4 steps, DA2 semantics, float32 | 838 | affine-invariant depth in 0 … 1 with a **19-row floor band at the bottom** (value 0.02, a border artifact) |

**Two metric models read the painting as a painting.** The photograph is a reproduction of a
painting, and both metric models answered the metric question honestly: a flat object about five
metres away. For a portal that wants the scene *inside* the picture, a metric model is the wrong
tool for illustrations, and this will hold for any drawn, painted or rendered input. Both fall out
on criterion 2 (Depth Pro reaches 0.7 % of the plate, MoGe-2 35 %).

**Pixel-Perfect Depth needed two corrections, both recorded in `log.json`.** Its output is
affine-invariant depth, which cannot be inverted to disparity without a shift; it was anchored to
DA3's depth by a least-squares scale and shift fitted on the data (1.0298, 0.2346; residual 0.125,
correlation 0.86). Its bottom 19 rows had collapsed to a floor and were marked invalid. Even so,
at 8 bits its runs fragment to 2–3 texels (its texel-scale roughness is the highest of the five,
below) and the plane law finds a far side on 1.9 % of the plate: its published edge quality does
not survive this pipeline's requantisation and per-line law.

### Criterion 1 — noise at the texel scale (from the float outputs, inverse depth, own full range)

| model | kind | s (CPU) | corr with DA2 map | sub-8-bit sigma (steps) | lag-1 autocorr | affine residual median / p90 (8-bit steps) | triples > 1 step |
|---|---|---|---|---|---|---|---|
| da2large | inverse | ? | 1.000 | 0.290 | 0.156 | 0.014 / 0.037 | 0.0186 |
| depthpro | depth | 50.3 | -0.364 | 0.289 | 0.425 | 0.048 / 0.097 | 0.0028 |
| moge2 | depth | 10.8 | 0.684 | 0.289 | 0.102 | 0.065 / 0.143 | 0.0013 |
| da3mono | depth | 14.2 | 0.884 | 0.289 | 0.272 | 0.005 / 0.028 | 0.0145 |
| ppd | depth | 838.1 | 0.666 | 0.290 | 0.316 | 0.059 / 0.185 | 0.0314 |

Reading: the "affine residual" is the 5-texel along-row fit residual in units of the map's own
8-bit step; the "lag-1 autocorrelation" says whether the sub-8-bit part is structure (≈ 1) or noise
(≈ 0). DA3-Mono has a quarter of DA2's residual and twice its autocorrelation: its extra bits carry
more signal and less jitter. (Depth Pro and MoGe-2 are flat maps; their rows are not comparable.)

### Criteria 2 and 3 — the app at 8 bits (probes `photo_bo_*`, shots `ui_bo_*`)

| | old map (Space model), 8-bit | DA2-Large, 8-bit | depthpro, 8-bit | moge2, 8-bit | da3mono, 8-bit | ppd, 8-bit |
|---|---|---|---|---|---|---|
| source sheets under the join law | 24 | 128 | 6 | 26 | 42 | 287 |
| runs per row (median length) | 9.3 (6) | 8.6 (4) | 1.5 (851) | 4.2 (7) | 7.8 (23) | 5.9 (3) |
| runs per column (median length) | 7.9 (8) | 7.3 (5) | 1.3 (1023) | 4.7 (6) | 7.2 (13) | 9.3 (2) |
| texels with a far side | 713765 | 732118 | 5981 | 306793 | 665153 | 16380 |
|   same-plane pairs | 56100 | 65187 | 307 | 7764 | 67679 | 8150 |
|   crossings | 15172 | 7343 | 0 | 4915 | 26800 | 51 |
| thin candidates / all | 738939 / 1183755 | 786782 / 1149532 | 6286 / 6308 | 238523 / 364308 | 696453 / 1138676 | 37763 / 42320 |
| second-layer texels | 58786 | 85601 | 11 | 18335 | 58301 | 6538 |
| reach % of plate | 81.99 | 84.10 | 0.69 | 35.24 | 76.40 | 1.88 |
| band at 15° / 25° / 35° / 45° | 100130 / 223167 / 349546 / 412329 | 142726 / 307773 / 487015 / 598571 | 266 / 5729 / 6384 / 6484 | 20523 / 66208 / 100650 / 113625 | 56054 / 127637 / 225981 / 278355 | 11630 / 13512 / 14201 / 14270 |
| carrier–carrier seams | 57777 | 64354 | 2140 | 20453 | 22433 | 18473 |
|   same axis, same kind, across lines | 23785 | 26907 | 1 | 5787 | 10549 | 1829 |
|   jump median (tol) | 19.0 | 14.4 | 9.9 | 17.4 | 11.0 | 14.9 |
| plate triangles torn | 136191 | 155874 | 5968 | 83570 | 77006 | 9867 |
| holes on the path (px, seams stretched) | ? | 7 / 3 / 14 / 0 / 0 / 0 / 0 | 135 / 1568 / 865 / 3432 / 622 / 2675 / 1195 | 5 / 6 / 6 / 17 / 17 / 7 / 42 | 0 / 15 / 6 / 5 / 60 / 7 / 55 | 0 / 0 / 1 / 1 / 0 / 0 / 1 |

### Decision

By the rule fixed in the plan — rank by criterion 1 among models not worse than DA2 on seams and
tears, with single-digit holes — **no model passes cleanly**, and the reading is:

1. **Depth Anything 3 Mono-Large is the input to take forward.** Lowest texel-scale noise of any
   structured map (residual 0.005 steps against DA2's 0.014); seams 22 433 against DA2's 64 354
   and the old map's 57 777; plate tears 77 006 against 155 874 and 136 191; the same 60 %-range
   of thin candidates as the others. It misses the single-digit-hole bar at two poses past the
   45° envelope (60 px at 50°, 55 px at 56°) and one inside it (15 px at 27°); DA2-Large misses it
   at 27° too (14 px). The angle sheet is the decisive evidence: DA2-Large smears the cave into
   horizontal streaks at every pose; DA3 renders cave, figure and troll intact with specks.
2. Its band is smaller than DA2-Large's (278 355 vs 598 571 texels at 45°) — it separates the
   troll from the cave wall less strongly and does not turn the corner vignette into depth. Whether
   that is truer is the user's eye's call; it is not a criterion.
3. The metric models are out for illustrated input; PPD is out for this pipeline as it stands
   (affine ambiguity plus roughness at 8 bits).
4. Not built, not tuned: no ensembles, no second runs, no app change. The default depth is
   unchanged pending the user's live pass; `depth_da3mono16.png` is committed to `moebiusv2` next
   to `depth16.png` for that pass, and DA3's float output is the input to the noise-term tolerance.

Sheets: `bakeoff/bo_maps_sheet.png` (five maps at 8 bits and differences to DA2),
`bakeoff/bo_angles_sheet.png` (each map at 27°, 45°, 52°/24°, 56°/19°, seams stretched).
