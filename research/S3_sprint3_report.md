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

## 3. Offline test (scratch `s3_unit.js`, exact synthetic scenes through the app's law, 16 bits)

| scene | occluder texels | median |err| (norm. d) | texels > 4 q | horizon |
|---|---|---|---|---|
| box on a floor, wall behind | 6 433 | 3e-8 | 3 (0.05 %) | 224.4 / 225 |
| hedge across a room | 103 200 | 3e-8 | 0 | 224.5 |
| hedge on open ground, sky | 203 200 | 2e-6 | 1 600 (0.79 %: the two rows at the kit's finite ground edge) | 224.5 |

## 4. A/B on the truth kit (16-bit, rim law, shipped envelope)

(filled in below from `check_app_band`; arms: S2b.4 as shipped vs + `_farRule = 'plane'`)

## 5. Decisions

## 6. Next
