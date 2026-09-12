# S20 — Sprint 13: thin lines through the despeckle; the far-pose holes by class (2026-09-12)

## 1. The line-aware despeckle (13a)

**The rule.** The quick bake's despeckle snaps a texel to its 5×5 median when its 3×3 range exceeds 0.06 and fewer than 8
of its 25 neighbours lie within 0.02 of it (two passes). Its own comment says what that does: "filaments (1px wide, any
length) are minority" — an 8-of-25 majority is a two-texel width threshold, and S18 §2 measured the cost on S5 (one-column
poles erased over 71 % of their length). The new arm, `window._despeckleLines`, keeps a minority texel if **a one-texel
line passes through it**: along any of the four directions of the same 5×5 window (row, column, both diagonals) all four
neighbours, two each side, lie within the same 0.02 of it. That attests a line at least 5 texels long — the window's own
extent — so no constant is added; flecks of 1–4 texels in every direction still take the median. Tolerances unchanged.

**Measured** (plane recipe, 16-bit exact depth on the kit, DA3 on the pictures; `_s13` tags):

| case | current rule | line rule |
|---|---|---|
| S5 thin poles: precision / recall | 0.489 / **0.514** | 0.398 / **0.979** (band 1 691 → 3 955 px against 1 608 truth; depth p90 0.056 m both) |
| S9 stacked cards | 0.958 / 1.000 | identical (band 65 417 both) |
| S11 rounded bodies | 0.947 / 1.000 | 0.947 / 1.000 (band 38 540 → 38 538) |
| troll (8-bit, the combs the rule was built for) | 1 180 texels snapped | 1 180 snapped, 201 + 346 kept over the two passes; **14 pixels of 184 184 differ at 0.2 m**; interior holes on the path 3/4/101/71/55 → 3/4/103/71/60 |
| six pictures, DA3 | — | kept 270–1 070 texels each; band % identical to 0.1, seams within −0.2…+2.2 %, torn within −0.3…+2.1 %, clones 0 / 0 everywhere |

So the rule recovers the thin structures it was aimed at (S5 recall 0.51 → 0.98) and is inert everywhere else that was
measured: the troll's striation combs are not lines, and nothing on the six pictures moves beyond the seam noise. S5's
precision falls because a one-texel pole's reveal band is a few texels wide against a truth of one or two — 2.3 k extra
texels in absolute terms. **Recommendation for the live pass: make it the default**; until then it is an option arm.
Sheet: `s20/s13_S5_lines.png` (the poles found), `s20/s13_troll_sheet.png` (no visible change).

## 2. The far-pose holes (13b)

The B batch (S19 §3.1) left interior holes on the user's path on **silverwarrior** (1 307–1 633 px at 52–56°),
**vermeer** (1 336 px at 56°) and **room** (610 px). Diagnosis by class before any fix.

**Step 1 — the sweep's own model.** The CPU sweep at the shot poses (fractions 1, 1.3/0.44, 1.505/0.589 of the 45° rim;
class maps `s20/s13_*_classmap_*.png`, red = no owner) already shows holes inside the frame where the shots show them:
silverwarrior 9 277 / 8 252 / 9 972 interior red cells at 45° / 52° / 56°; vermeer 14 547 / 6 778 / 5 239. So they are not
render tears of the mesh.

**Step 2 — the reveal texels at those poses against the band and the far field** (`pose_*_reveal.u8` vs `disocc`,
`farField`):

| picture | pose | reveal texels | in the band | of which without a far side | not in the band |
|---|---|---:|---:|---:|---:|
| silverwarrior | 45° | 45 280 | 45 035 | 151 | 245 |
| silverwarrior | 52°/24° | 35 677 | 34 288 | 128 | 1 389 |
| silverwarrior | 56°/19° | 35 610 | 32 901 | 123 | 2 709 |
| vermeer | 45° | 118 247 | 118 231 | 0 | 16 |
| vermeer | 52°/24° | 112 964 | 111 445 | 0 | 1 519 |
| vermeer | 56°/19° | 92 613 | 91 156 | 0 | 1 457 |

Inside the envelope (45°) practically every reveal texel is in the band with a far side; the few hundred outside the band
at 52–56° are reveals beyond the envelope the band was built for (the sweep grid stops at 45°), a known price. That means
the in-frame holes are **not** "never demanded" and **not** "demanded without a far side". What is left: the far content
those cells need lies **beyond the picture frame** (the bear at silverwarrior's bottom-right edge, the milkmaid against the
right edge — content behind a near thing at the frame's edge comes from outside the picture), or the plate's coverage
breaks along the per-line far field (the vermeer's alternating red/green rows behind the silhouette in the class map).
Step 3 tests the first with the plate options that address it — step faces (rim step gaps) and margin = window (the A245
strips over the whole window instead of the picture's rest footprint) — on the same shots.

*(step 3 results follow when the chain finishes)*
