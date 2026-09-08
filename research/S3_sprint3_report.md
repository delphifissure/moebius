# Sprint 3 report — the far side by the plane law (2026-09-08)

Plan: `S3_sprint3_plan.md`. Code: CODEMAP §21. Everything on the rim-law arm behind
`window._farRule = 'plane'`; no default changed.

## 1. What was built

1. **Runs.** Every row and column of the source depth is cut into maximal segments on which the
   disparity (1/ze on the app's own depth law) is affine: interior second differences within the
   S2b.3 quantisation bound; a two-sample segment must pass the ratio test; sky never joins a
   finite run. A run ends at a jump *and* at a crease.
2. **Candidates.** For a texel, on each of its four sides, the first run outward whose least-squares
   line (over the g + 1 samples nearest the texel, g the rim distance; fewer only if the run is
   shorter, which is counted) extrapolates to a disparity behind the texel by more than the bound.
   A crease neighbour extrapolating nearer (a box's top face from its front) is passed over; one
   extrapolating behind (the floor under a foot, up the column) is the far side. Among several runs
   behind the texel on one side, the first-arriving one is taken: the shift law is affine in
   disparity, so a run g texels away and Δ behind starts to show at head fraction ∝ g/Δ. (The
   first run behind was tried first: on S15 it named the leaf 2 cm behind a leaf, which covers three
   texels of a 54-texel reveal, for the whole reveal; recall 0.80.)
3. **The ground.** Rising column runs (disparity increasing downward) whose zero-disparity rows agree
   are horizontal surfaces — parallel planes share a vanishing line (Hartley & Zisserman ch. 8).
   The shared row is found by interval stabbing of each run's zero row with its 3σ least-squares
   bar (σ from the run's own residual, floored at the quantisation bound); the ground is the
   horizontal run of smallest slope per column (the lowest surface); one plane a + b·x + c·y is
   fitted to those runs, first by medians (slope, Theil–Sen tilt, intercept), then by least squares
   over the runs within their own bound. The ground bounds the world from below: a candidate that
   extrapolates under it is cut at it (a wall or a box front continued below its foot meets the
   ground there). Its zero line is the horizon.
4. **Two candidates on one axis.** Same plane (either line predicts the other rim within
   tolAt·(½ + G/(2(w−1)))) → the line through both rims; two planes crossing inside the gap →
   switch at the crossing (floor meets the wall's foot; ground meets the sky at the horizon); no
   crossing → switch at the midpoint. Never a blend.
5. **Two axes.** A finite far side beats the plane at infinity from the other axis (the sky is what
   remains when nothing finite intervenes; S15's sign board: the column crossed sky with ground at
   the horizon, the row saw hills on both sides). Then two rims on one plane beat an axis whose two
   rims differ (a positive detection of a continuing surface against a boundary guess). Then the
   nearer rim. Texels with no candidate are their own far side.
6. **The reach** walks from each unjoined edge with a per-texel span, shift(d_edge) − shift(far side
   of that texel), positive only when the texel's own far side lies behind the occluding edge, and
   stops at the first failure. Sky class = far side at infinity. No membrane, no Neumann solve, no
   clamp (candidates are behind by construction).
7. Probe dumps `farKind` (1 single, 2 same plane, 3 crossing, 4 midpoint) and `farAxis`; truth-kit
   scenes S31 (hedge in a room) and S32 (hedge on open ground with sky, taller than eye level).

Constants: q, tolAt, g_min as before. New: the 3σ width of the zero-row bars (a confidence level in
units of each run's own standard error; invariant to resolution, depth range and quantisation).

## 2. Defects found and fixed before any number was read (a196)

- The per-line prefix sums had L slots per line, so the last entry of every line was overwritten by
  the next line's zero: every fit touching a frame edge was garbage (the floor's zero row came out
  at 408 instead of 224.5). Fixed (L + 1 slots).
- Without a ground bound a wall's line continued below the floor and became "the far side" of the
  floor in front of a box's foot (the offline test showed it at the foot rows). The ground bound
  fixed it.
- The ground plane by least squares over all lowest rising runs was tilted 0.1 % in slope by two
  two-texel runs on box edges (four texels of 60 k, with a 100-row lever arm); the far side behind
  every box then read four quanta off and the same-plane test failed everywhere (midpoint kind on
  the whole lower half of each box). Fixed by the median fit and the bound-based inlier pass.
- "The lowest surface is the rising run of smallest slope" picked S15's hills (their cap lines rise
  100× more slowly than the ground). Fixed by the shared vanishing line.
- The most-covered row of the stabbing was taken at a bar's own edge, so the very runs that defined
  it failed the containment test by rounding (S31: all floor runs excluded, the hedge's two-texel
  top face left as the ground). Fixed (midpoint of the most-covered stretch).

- (After the first shots.) The horizontal streaks in S15's crown were not the far side: the plate-only
  shot showed 200-px streaks from every leaf-depth plate patch toward the hill, and they survived a
  change that removed every extrapolated ramp (a thin run — shorter than the gap it crosses — now
  continues at constant depth, or along the fitted ground plane if it is a ground run). They were
  the plate's displacement texture, still linearly filtered: the plate's vertices sit at k/(pw−1),
  the texel centres at (k+0.5)/pw, so a vertex beside a torn plate edge took a blend of both sides
  and its triangle stretched across the tear. The foreground had been given nearest filtering in
  S2b.4 for exactly this reason; the plate had not. Fixed for the whole rim-law arm (both A/B arms
  benefit; the S2b.4 arm's vertical hill streaks beside the crown were the same defect).

## 3. Offline test (scratch `s3_unit.js`, exact synthetic scenes through the app's law, 16 bits)

| scene | occluder texels | median |err| (norm. d) | texels > 4 q | horizon |
|---|---|---|---|---|
| box on a floor, wall behind | 6 433 | 3e-8 | 0 (max 1e-7) | 224.5 / 225 |
| hedge across a room | 103 200 | 3e-8 | 0 | 224.5 |
| hedge on open ground, sky | 203 200 | 2e-6 | 1 600 (0.79 %: the two rows at the kit's finite ground edge) | 224.5 |

## 4. A/B on the truth kit (16-bit, rim law, shipped envelope)

Arms: S2b.4 as shipped (`_tearLaw='rim'`, `_skyInf` on the open scenes) against the same plus
`_farRule='plane'`. Both arms baked in this session on the same truths (S31/S32 new; the others
regridded in Sprint 2). Depth error is on true-positive band texels against the truth's first
hidden layer, in metres. Sheet: `out/sheet_s3_plane.png` (sent).

| scene | truth px | arm | band px | P | R | sky R | depth median (m) | depth p90 (m) | scene depth (m) |
|---|---|---|---|---|---|---|---|---|---|
| S2 | 16454 | S2b.4 | 20811 | 0.788 | 0.997 | — | 0.003 | 0.044 | 0.128 |
| S2 | 16454 | plane | 18190 | 0.901 | 0.996 | — | 0.000 | 0.043 | 0.128 |
| S27 | 4894 | S2b.4 | 6002 | 0.815 | 1.000 | — | 0.005 | 0.030 | 0.240 |
| S27 | 4894 | plane | 5623 | 0.870 | 1.000 | — | 0.000 | 0.000 | 0.240 |
| S12 | 16975 | S2b.4 | 19792 | 0.855 | 0.997 | — | 0.000 | 0.076 | 0.128 |
| S12 | 16975 | plane | 18011 | 0.935 | 0.992 | — | 0.000 | 0.076 | 0.128 |
| S26 | 25631 | S2b.4 | 33057 | 0.773 | 0.998 | — | 0.002 | 0.055 | 0.112 |
| S26 | 25631 | plane | 29782 | 0.858 | 0.998 | — | 0.000 | 0.055 | 0.112 |
| S16 | 4513 | S2b.4 | 8606 | 0.484 | 0.924 | — | 0.001 | 0.006 | 0.160 |
| S16 | 4513 | plane | 12164 | 0.360 | 0.972 | — | 0.000 | 0.000 | 0.160 |
| S31 | 70400 | S2b.4 | 79988 | 0.880 | 1.000 | — | 0.000 | 0.000 | 0.128 |
| S31 | 70400 | plane | 72798 | 0.967 | 1.000 | — | 0.000 | 0.000 | 0.128 |
| S15 | 34867 | S2b.4 | 40286 | 0.832 | 0.961 | 0.95 | 0.142 | 8.554 | 8.640 |
| S15 | 34867 | plane | 39260 | 0.830 | 0.935 | 0.91 | 0.062 | 8.567 | 8.640 |
| S32 | 42400 | S2b.4 | 79997 | 0.080 | 0.151 | — | 42.961 | 42.973 | 43.200 |
| S32 | 42400 | plane | 47995 | 0.717 | 0.811 | — | 0.000 | 0.000 | 43.200 |

(Final code state: plate depth texture nearest-filtered, thin-run rule, first-arrival pick. The
earlier run of the same table, before those, differed only in S15 recall 0.944 and S16 band 12 203.)

**Depth by what is actually behind the texel** (rooms; the first hidden layer's class in the kit):

| scene | arm | background texels: median / p90 (m) | side-face texels: median (m) |
|---|---|---|---|
| S2 | S2b.4 | 0.0014 / 0.0136 | 0.047 |
| S2 | plane | **0.0000 / 0.0000** | 0.047 |
| S27 | S2b.4 | 0.0036 / 0.0229 | 0.113 |
| S27 | plane | **0.0000 / 0.0000** | 0.114 |
| S12 | S2b.4 | 0.0000 / 0.0092 | 0.076 |
| S12 | plane | **0.0000 / 0.0000** | 0.076 |
| S26 | S2b.4 | 0.0007 / 0.0043 | 0.057 |
| S26 | plane | **0.0000 / 0.0000** | 0.057 |

On every room the plane far side is exact to the quantum wherever the truth behind the texel is a
background surface (floor or wall); the residual p90 in the main table is entirely the side-face
texels, where the truth's first layer is the object's own side (never in the rest image) and the
app carries the layer behind it — the S2 check showed the app's value equals the truth's *second*
layer to 0.000 m on all 2 793 of them. That layer is A257's, not this sprint's.

S15 by class (plane arm): the ground behind the trunk and the post is exact (median 0.000 m, p90
0.009 m on 6 399 texels; the S2b.4 membrane had 0.031 / 1.1 m); the hills behind the sign are
0.011 m median (S2b.4: 0.076 m); the crown's leaves-behind-leaves (side/interior classes, 12 800
texels) read sky or hill where the kit's first layer is the next leaf 2 cm back — the layered case a
single depth per texel cannot hold (see §5). Sky-reveal recall 0.91 against 0.95: the same crown.

**What the scenes say, one by one (a196, from the buffers):**

- **S2, S27, S12, S26.** Precision up 0.05–0.11 with recall held; the foot strips are gone. What is
  left of the false band is a strip a few rows deep just above each box's back foot: the plane law
  puts the floor behind the box there, correctly, but the box's own depth shadows that floor from
  every side eye, and the rest depth map does not carry a box's thickness. A modelling limit
  (occluder thickness), recorded, not a bug.
- **S31 (hedge across a room).** 0.97 / 1.00, depth exact: the floor's line from below crosses the
  wall's line from above at the wall's foot, hidden behind the hedge. The S2b.4 membrane also got
  the depth right here (Dirichlet at the wall, Neumann at the floor gave the wall everywhere, and
  the wall is most of the truth) with a fatter band (0.88).
- **S32 (hedge on open ground, sky).** The decisive case for the horizon: S2b.4 called everything
  behind the hedge sky (nearest far rim; 43 m error, 0.08 / 0.15); the plane law puts the ground up
  to the horizon row 224.5 (eye level is 225) and sky above, exact in depth (0.000 m), 0.72 / 0.81.
  The remaining misses are ground rows near the horizon that move over a window height at the
  envelope rim and fall between the sweep's five vertical poses; the false band is the sky and far
  ground strips the kit's display-weighted truth excludes because the top eyes compress them below
  one display pixel per rest texel. Both are measurement limits; the far side is right.
- **S16.** Recall 0.97 (was 0.92), precision 0.36 (was 0.48). The extra false band is the wedge
  above the jump wall's top and the strip beside the return face, both wider than under S2b.4:
  the plane law names the back wall (row axis) or the jump wall (column) as the far side and the
  reach opens for their full slide, but what a low or side eye actually sees in those gaps is the
  ledge's underside and the pilaster's return face, surfaces that are edge-on at rest and occupy
  one row or four texels of the rest grid. The same collapsed-surface limit as the S2 report's §3;
  a rest-texel representation cannot hold them, and the kit scores them as one row.
- **S15.** Band and recall essentially unchanged (0.83 / 0.94 vs 0.83 / 0.96), depth median 0.055 m
  from 0.142 m, the ground behind the trunk exact, the hill behind the sign right instead of sky.

## 4b. Colour (added after the first S15 shots)

The S15 shots of both arms were identical to the eye although the depth differed everywhere: the
wedge each vertical occluder uncovers was filled brown behind the trunk and grey behind the post on
both. Cause (from the code, not the numbers): the A242 membrane seeds a band texel's colour from
non-band texels whose *source* depth is within `fgTearStep = 0.06` normalised units of the band
texel's plate depth. That gate's units are the depth volume's; on the 8.64 m scene 0.06 spans half a
metre at the trunk, so the trunk itself seeded the ground behind it. Under the plane far side every
band texel already knows which rims it continues from, so on that arm its colour is the mean over
each rim's window mixed by the same weight as its depth, the band's outline holds those as
Dirichlet values and the interior is the harmonic membrane between them (no gate, no constant).
Scored against the kit's first-hidden-layer colour on true-positive band texels (mean |Δ| per
channel, 0–255; "clone" = what copying the source colour would score):

| scene | texels behind which the truth is | S2b.4 membrane | plane colour | clone |
|---|---|---|---|---|
| S2 | background (floor, wall) | 26.7 | 27.1 | 50.1 |
| S2 | the box's own side | 60.8 | 59.2 | 59.9 |
| S15 | background (ground, hills) | 13.6 | 11.3 | 60.3 |
| S15 | leaves behind leaves (side, interior) | 58.7 / 56.9 | 79.7 / 82.9 | 19.9 / 16.5 |

Equal on the rooms (both are washes on a checkered floor), better on S15's ground and hills, worse
in the crown, where the truth's first layer is the next leaf and the plane arm fills with the hill
or sky behind. On the screen (`sheet_S15_s3c.png`, sent): the brown wedge behind the trunk and the
grey band behind the post are gone on the plane arm. The crown's streaks on both arms were the
plate's linearly filtered depth texture (§2, last item); with nearest filtering the plate in the
crown is small leaf-depth patches and the rest of the reveal is the sky layer, whose vertical
bands are the stand-in sky texture's per-column continuation (known since Sprint 2). Fixed on the
way: a band texel whose plate depth is its own (the band's margin, pinholes) keeps its own colour
and is outside the colour domain; the domain's ring is its own outline (with "touching a non-band
texel" the box outlines were interior and the whole box went floor-grey); a component with no ring
value keeps its per-texel rim colours (the aggregation multigrid diverged on S15's crown, error
1.4e5/255, the same null space as S16's Neumann components in Sprint 2).

## 5. Decisions

- The far side of an occluder on the rim-law arm is the plane law's (`_farRule='plane'`), not the
  membrane: exact on every planar far side in the kit, and the only arm that puts ground behind a
  full-width occluder up to the horizon. The nearest-rim class rule is superseded and stays only on
  the S2b.4 arm for comparison.
- The horizon is the fitted ground plane's zero-disparity line. No estimator is trained or run:
  with a trusted depth map the vanishing line is exact (224.5 of 450 on every scene; eye level 225).
- Three rule choices were made from the buffers and are recorded with their evidence: first-arriving
  run over first-run-behind (S15 crown, recall 0.80 → 0.94), finite over sky across axes and same
  plane over boundary guess (S15 sign, 1 137 texels of sky where the truth is a hill), ground by the
  shared vanishing line over smallest slope (S15 hills).
- Removed under rule 7: least-squares ground plane over all lowest rising runs (four texels tilted
  it 0.1 %); the first-run-behind candidate; the bar edge as the stabbing row.
- Nothing ships as a default. Live-pass recipe: `window._tearLaw='rim'; window._skyInf=1;
  window._farRule='plane'; window._plugGeoBand({flush:true, observed:true, gateAPriori:true})`.

## 6. Next

- The second layer (`S4_second_layer_plan.md`): the sign's far side is the hill when the reveal
  opens and the sky for 85 % of the envelope; the crown's is the next leaf in its dense parts and
  the sky or hill in its sparse parts. Both choices are implemented (`window._farPick`: first
  arrival by default, pose coverage as the alternative) and neither is complete; the arrival
  order the plane law already computes is the layered depth image, and plate 2 is where its
  second entry goes.
- One texel, one depth: the crown (leaf, leaf, hill, sky behind one texel) and S16's edge-on
  ledge and return face need a second layer where the reach finds more than one arriving surface
  (A257's object-back machinery, or an LDI-style second plate). The plane law already lists the
  candidates per texel in arrival order; the second layer is the second arrival.
- Occluder thickness for the reveal test (the strip above each box's back foot): the top face's
  back edge, where visible, gives it for boxes; symmetric inflation otherwise.
- The sweep's vertical pose grid (5) under-samples far surfaces on open scenes (S32's misses).
- The rule's behaviour on an estimator's depth (texture noise breaks runs; the thin-evidence count
  and the horizon bars will show it) before any of this is tried on a photograph.
