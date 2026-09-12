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

**Step 3 — option A/B on the same shots** (`s20/s13b_table.py`; interior holes, px, base → option; offsets 0.1 / 0.2 /
(0.26, 0.088) / (0.301, 0.068) m = 27° / 45° / 52°·24° / 56°·19°):

| picture | step faces on | margin = window | plate drawn with NO tear (`_plateKeepAll`) |
|---|---|---|---|
| silverwarrior | 217 / 488 / 1 796 / 1 635 → identical (2 step quads exist) | → 0 / 474 / 1 334 / 1 685 | → 217 / **14** / 482 / **2** |
| vermeer | 12 / 6 / 1 336 / 334 → identical | → 12 / 6 / **229** / **140** | → 0 / 0 / 1 107 / 194 |
| room | 710 / 194 / 756 / 326 → identical | → 382 / 186 / 598 / 253 | → identical |

Margin = window also zeroes the edge-connected alpha-0 on all three, as it is meant to.

**Three pictures, three classes.**

- **Silverwarrior: plate rim tears.** With the plate drawn untorn the 45° and 56° holes vanish (488 → 14, 1 635 → 2); the
  diagonal pose keeps 482. These are the edges the stretched-seams option leaves torn on purpose — between a carrier at
  far depth and its own-depth neighbour inside the occluder ("that is the disocclusion"). At these poses the foreground has
  moved further than the band's carriers reach, and the tear opens onto nothing; the sweep did not predict it because it
  draws plate quads stretched. Sheet `s20/s13_silverwarrior_tear_ablation.png`.
- **Vermeer: the picture-clipped margin.** Margin = window closes most of it (1 336 → 229, 334 → 140): the milkmaid stands
  against the right edge and the content behind her lies beyond the frame. The untorn plate helps less here (→ 1 107 / 194).
- **Room: neither.** Its holes (710 at 27°, the largest at the nearest pose) move only with the margin (→ 382) and are
  otherwise untouched — a different class again, not diagnosed in this sprint; the sunflower field has 539 source sheets
  and 149 k layer-2 texels, and the place to look is the class map at 27°.

**What was built.** `window._plateKeepAll` (the plate without its rim tear) is now the panel's third seams value,
**"seams + rim stretched"** (`bgPlateSeamSel = all`, which also sets `_plateStretchInner`). Default unchanged. For the
live pass, the trade as measured: it closes rim-tear holes at the far poses; its price is a skin between every silhouette
and its background wherever the band's carriers stop short — coloured with the wash on the carrier side and the source on
the other, never a foreground clone as background, but a stretch the eye may read. The picture margin option already
exists for the vermeer class. An offline reproduction of the sweep for per-hole attribution (`s20/s13_attrib.py`) did not
match the app's cell counts (890 vs 9 277 interior cells at 45°) and was superseded by the ablation; kept as a record.

## 3. Summary

1. The line-aware despeckle recovers one-texel structures (S5 recall 0.51 → 0.98) and is inert on the troll, S9, S11 and the
   six pictures; recommended as the default at the live pass.
2. The far-pose holes are not a band or far-field failure. They are plate rim tears (silverwarrior), the picture-clipped
   margin (vermeer), and one unclassified case (room). Two panel options now cover the first two; both are the user's call
   on screen.
