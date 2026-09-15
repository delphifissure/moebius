# S34 — sheets, step A: the axis seam under the layered order (2026-09-15)

The user's instruction after S33: "keep going as you suggest A, C, B"; the goal restated — no diffusion test until the
atlas, masks and layers are clean and seamless, "clearly defined blobs to inpaint". This note is step A: the row/column
arbitration replaced by the layered order, measured on the kit and the six pictures with the S33 instrument. The S32 plate
arm is removed in the same commit (rule 7; S32 §4–§6).

## 1. What was built (`window._axisOrder = 1`)

In the far-side law's pass 3, where a texel has both a row and a column candidate, the per-texel priority (a same-plane
pair wins; otherwise the nearer rim by distance; sky loses to any finite value) is replaced by the rule `combine()` already
applies to two surfaces on one axis (kind 4) and the layered depth image's order (Shade et al. 1998): **the nearer value
shows, the farther is behind it.** Sky (disparity 0) is the farthest by construction, so the sky clause is subsumed; the
same-plane priority is dropped. The argument was continuity: the nearer of two continuous fields is continuous, so the
seam between axes cannot exist under the rule. That argument has a hole, found by the measurement (§4).

Sprint 7b's D1 (re-read as promised) was a different thing — an inverse-variance *blend* gated on the two axes agreeing
within their uncertainties — and was not built because the gate fired on 12 % of the axis-flip seam edges. A is not gated
and touches every arbitration.

## 2. Kit (nine scenes, `_ao` against the per-line law under the same chain)

| scene | precision | recall | band px | band depth err median (m) | p90 (m) | axis changed (band texels) | far field changed |
|---|---|---|---|---|---|---|---|
| S2 boxes | 0.887 → 0.887 | 0.999 | 18 531 → 18 531 | 0.0000 → 0.0000 | 0.0427 → 0.0427 | 18.9 % | 18.9 %, median 0 |
| S16 steps | 0.190 → 0.185 | 0.972 | 23 078 → 23 747 | 0.0000 | 0.0000 | 5.4 % | 0 |
| S26 quads | 0.457 → 0.455 | 0.937 | 52 608 → 52 751 | 0.0000 | 0.0560 → 0.0552 | 14.1 % | 1.6 % |
| S15 sky | 0.723 → 0.723 | 0.996 → 0.997 | 48 020 → 48 099 | **0.184 → 0.234** | 8.566 | 34.3 % | 21.5 % |
| S9 cards | 0.958 → 0.962 | 1.000 | 65 417 → 65 182 | 0.0000 | 0.0640 | 20.3 % | 16.6 % |
| S10 | 0.937 | 0.999 | 56 140 → 56 139 | 0.0000 | 0.0498 → 0.0482 | 30.5 % | 2.3 % |
| S11 | 0.947 | 1.000 | 38 540 | 0.0000 | 0.0542 → 0.0532 | 33.7 % | 27.6 % |
| S31 hedge room | 0.946 | 1.000 | 74 398 | 0.0000 | 0.0000 | 0 | 0 |
| S32 hedge open | 0.729 | 0.811 | 47 202 | 0.0002 | 0.0004 | 0 | 0 |

The arbitration changes on 5–34 % of band texels; the truth barely notices: precision and recall within 0.005, medians 0
on eight scenes, p90 lower on four. S15's median rises 5 cm: on 3 454 texels of the hill (truth 6.76 m) the rule takes the
ground's column continuation (6.68 m) over the hill seen on both row rims (6.74 m) — 8 cm at 7 m — and on 2 245 texels
it is better by the same order (`s34/S15_ao_vs_pl.png`: red worse, green better). The kit cannot rank the two rules.

## 3. The six pictures — vertical bends, at the visible step (S33 instrument)

| picture | visible bends | total wall length | class 1 wall | class 2 wall | class 3 count / wall |
|---|---|---|---|---|---|
| troll | 99 205 → 88 939 | 1 712 k → 1 561 k (−9 %) | 664 → 542 k | 447 → 358 k | 12 245 → 15 122 / 600 → 662 k |
| vermeer | 110 225 → 118 373 | 4 152 k → 4 065 k (−2 %) | 851 → 870 k | 1 452 → 998 k | 16 683 → 30 848 / 1 850 → 2 197 k |
| room | 44 834 → 48 616 | 655 k → 659 k (+1 %) | 236 → 223 k | 175 → 186 k | 9 311 → 11 279 / 244 → 249 k |
| silverwarrior | 23 888 → 21 540 | 1 341 k → 819 k (−39 %) | 129 → 149 k | 785 → 538 k | 4 055 → 3 319 / 427 → 132 k |
| octopus | 20 445 → 20 730 | 340 k → 336 k (−1 %) | 100 → 113 k | 122 → 133 k | 4 887 → 3 963 / 117 → 90 k |
| bristlecone | 17 604 → 24 732 | 519 k → 623 k (+20 %) | 63 → 91 k | 303 → 400 k | 2 146 → 3 059 / 154 → 132 k |

(wall length in step-texels: the summed jump over the visible bends = the total length of the walls at the cone rim.)

## 4. Reading

1. **The rule is not a fix.** Total wall length: troll −9 %, vermeer −2 %, room +1 %, silverwarrior −39 %, octopus −1 %,
   bristlecone +20 %. The class-3 count rose on four pictures (vermeer 16 683 → 30 848) while its median jump fell (98 → 33
   steps): the seam moved and multiplied rather than vanished. The crops (`s34/vermeer_p45_line_vs_axisorder.png`) show the
   band behind the woman turning from row streaks into vertical blocks where the column axis now wins.
2. **Why the continuity argument failed.** Class 3 split by whether both texels had both candidates (`*_sub` runs):

   | picture, rule | flips (both axes present at both texels) | domain boundaries (one axis missing at one texel) |
   |---|---|---|
   | troll, per-texel priority | 9 907 (wall 291 k) | 2 338 (309 k) |
   | troll, layered order | 12 493 (301 k) | 2 629 (361 k) |
   | vermeer, per-texel priority | 15 759 (1 803 k) | 924 (46 k) |
   | vermeer, layered order | 29 641 (2 143 k) | 1 207 (54 k) |

   On vermeer 97 % of the seam length is flips with both candidates present on both sides. Under the nearer-value rule a
   flip with a jump of 33 steps is only possible if one of the two candidate fields itself jumps by that much between the two
   rows — and it does: the row candidate is a kind-3/4 answer whose crossing point between two rims' lines moves from row to
   row, and the column candidate switches which column run it takes from texel to texel (the first-arrival pick is per texel).
   The nearer of two jumping fields jumps. Continuity of the max holds for continuous inputs; the inputs are not continuous.
3. **So the seam is not in the arbitration.** It is in the candidates: per-line fields that jump along their own line (run
   switches, crossing points) and across lines (fit noise, S33 class 1). Any per-texel rule that chooses between them —
   the current priority, the layered order, D1's blend — inherits their jumps. A and B were framed as two fixes for two
   classes; the sub-classes say they are one problem with one cause, and C as planned (tear the plate at unjoined internal
   cliffs and put the second layer behind) would tear along every one of these artifact walls — 42–74 % of the wall
   length — and shatter the plate into strips before it reached the real steps.

## 5. Decision

- `window._axisOrder` is **removed** (rule 7); the per-texel priority stands until replaced. The measurement is the deliverable.
- **C and B in their S33 form are withdrawn** for the reason in §4.3: they operate on the plate the per-line candidates
  produce, and that plate's walls are mostly the candidates' own jumps. The order A → C → B assumed the three classes
  were separable; the sub-classes show class 3 is class 1's mechanism seen through the arbitration.
- **What the measurements point at — one sheet per visible surface (the user's own model, S33 thread):**
  1. *Surfaces*: cluster the rim texels of the band along the rim contour by the join law (rims joined to their neighbours
     along the silhouette are one surface); a surface's extent across lines is the extent of its rim run cluster — the
     evidence of where it exists.
  2. *Sheets*: per surface one continuation over the band it can reach: its plane (the S7 pooled fit, which S7 measured as
     not matching the visible rim within tol on curved or noisy surfaces) **plus** the harmonic extension of the rim
     residuals (Laplace with the rim's misfit as Dirichlet data, zero flux elsewhere), so the sheet meets the visible surface
     exactly at every rim texel and relaxes to the plane away from it. No constants: the decay is set by the band's geometry.
  3. *Order*: per texel the nearest sheet behind the texel's own depth shows (the layered order); because each sheet is
     continuous, the nearest-sheet field is continuous, with creases along the sheets' intersections — the obstacle problem's
     answer (R4) — and no flips, because there are no per-line candidates to flip between.
  4. *Ends*: a sheet ends where its rim cluster ends across lines; beyond it the next sheet shows — a real step, a tear with
     a sheet behind it (this is C, in the only place C is right).
  5. *Second layer*: the second-nearest sheet at each texel — plate 2 with a regular domain.
  This removes class 1 (one sheet per surface, smooth by construction), class 3 (no candidates to arbitrate) and gives class
  2 its tear-and-fill, in one construction. It is B, A and C as one design, and it is what S22's closure asked for ("a rule
  that does not choose per line at all — a far field solved on the reveal region with the rims as boundary and the layering
  as a constraint").
- **Risks, stated before building:** (a) the plane per surface loses real curvature away from the rim (the residual extension
  decays) — the kit's curved scenes (S26 quads, the hedge scenes) will show how much; (b) the rim-contour clustering is the
  S2b join law along the silhouette, which on DA3's ramps at silhouettes can chain a wall into a floor — the crease then
  comes from the order step rather than the cluster, which is acceptable; (c) surfaces visible on both sides of an occluder
  (kind 2 today) become one cluster only if the rim contour connects them (above or below the occluder) — otherwise two
  sheets of the same plane, which the order merges harmlessly; (d) S7's pooled-plane misfit becomes the residual field's
  amplitude, not a tear — this is the point of step 2, and it is untested.
- **Proposed next step (measure before the app):** an offline prototype on the existing dumps (rims, dQ, band, runs) for
  the troll, vermeer and three kit scenes with truth (S15, S26, S9): build the sheets, the order and the ends in Python,
  score the far field with the S33 instrument (wall length by class) and against the kit truth (band depth median / p90),
  next to the per-line law. One to two days. If it clears the S22 bar and cuts the wall length by the artifact share, it goes
  into the app behind the far-side select.

## 6. Files

`moebius.js` (the `_axisOrder` branch built and removed in pass 3, its record in a comment there; the S32 plate block removed), `harness/streak_class.js` (flip / domain
sub-classes of class 3), kit `check_app16plane*_ao.json` / `_pl2.json`, `harness/shots/streakclass/*_ao`, `*_sub`, `*_sub_ao`,
`harness/shots/liverepro/{troll_ao,vermeer_ao}`, `research/s34/`.
