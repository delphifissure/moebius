# S22 — Sprint 15: the far field made consistent across lines, reopened (2026-09-12)

**The bar** (META_PLAN item 5, from §16's closure): the kit's band depth must not get worse (S15's 0.184 m median by more
than 0.01 m, p90 by more than 10 %), and the photograph's same-sheet seams must fall by at least half. §16 closed the
per-sheet thin-plate and local plane fits against that bar (S15 0.18 → 1.23 m; photograph seams +75 %). §10b had closed
pooling adjacent lines into planes (curved surfaces do not lie on one plane within tol) and the Lipschitz join (right on
rooms, wrong on layered scenes). What had not been tried is regularising the **per-line law's own parameters** across
lines instead of replacing the field by a surface: the law's linear extrapolation along the reveal axis is what the truth
liked (§16), so keep it and take the noise out of what it extrapolates from.

## 1. Three constructions, offline (`s22/sheetfield3.py`, from Sprint 12's reproduction of the law)

For a texel's candidate from rim j on its line, the neighbouring lines' candidates on the same side from the **same source
sheet** (the join-law component of the rim texel), not thin and not ground-cut, within **w lines each side** — w is the
candidate's own along-line window, so the evidence patch is w × (2w+1) of one sheet instead of the w × 1 strip, no new
constant:

- **slope** — the median of their along-axis slopes replaces the line's slope; the intercept stays the line's own rim value
  (continuity at the rim exact; a curved sheet keeps its per-line intercepts).
- **cmed** — the median of their extrapolated values replaces the value.
- **both** — median slope and median intercept (each neighbour's line evaluated at this rim's position; a symmetric median
  is unbiased for a linear cross-line trend).

Scored as §16 scored: band depth error against env45 truth on the kit (S15, S32, S2, S26, S16), free–free unjoined edges
under the join law (total / same sheet) on the kit and on the photograph's DA3 maps (8-bit `photo_bo_da3mono`, 16-bit
`photo_da3_s10d` at the visible-step quantum). "own" is the reproduction of the app's law in the same code (98.6 % of S15's
values within tol of the app's; on the photograph 59–62 %, so photograph rows compare against the reproduction's own seams).

## 2. Results

| scene | measure | app | own | slope | cmed | both |
|---|---|---|---|---|---|---|
| S15 hill + tree (truth) | band depth median m | 0.184 | 0.237 | 0.242 | 0.287 | 0.287 |
| S15 | seams total (same sheet) | 11 478 (2 413) | 11 474 (2 465) | 11 732 (3 527) | 12 242 (3 880) | 12 199 (3 850) |
| S32 open hedge | (all candidates ground-cut: nothing to regularise) | 800 | 800 | 800 | 800 | — |
| S2 contact | seams | 4 | 5 | **0** | 116 | 116 |
| S2 | depth median / p90 m | 0 / 0.043 | same | same | same | same |
| S26 | seams | 3 461 | 3 466 | 3 460 | 3 450 | — |
| S16 two walls | seams | 1 847 | 1 755 | 1 900 | 1 791 | 1 790 |
| S16 | depth p90 m | 0.000 | 0.000 | 0.000 | 0.001 | 0.001 |
| photograph DA3 8-bit | seams total (same sheet) | 33 239 (30 542) | 43 960 (38 114) | 43 455 (31 139) | 42 336 (32 233) | 42 664 (32 083) |
| photograph DA3 16-bit | seams total (same sheet) | 38 078 (24 766) | 41 079 (27 782) | 41 019 (26 572) | 42 645 (27 368) | 42 702 (27 435) |

Against the reproduction's own: the photograph's same-sheet seams fall by **18 %** (slope, 8-bit), 4 % (16-bit), 15–16 %
(cmed / both) — the bar was half. On S15 every variant **adds** same-sheet seams (+46 % to +60 %) and none improves the
truth (slope +0.005 m, the medians +0.05 m against own). S2 is the one place a cross-line slope helps: its four seams go
to zero, at no cost in depth — and cmed/both create 116 there. S26 and S16 do not move.

## 3. What this says

1. The same-sheet seams are **not per-line slope noise**. If they were, the slope median would have removed most of them;
   it removes a fifth on the photograph and adds them on S15. What remains are the *choice* disagreements §10a counted
   (axis flips, kind flips, different rims on adjacent lines) and rim-value differences that a slope median does not touch.
2. Medians of the values or intercepts across lines behave as §10a predicted for blends: they move seams, they do not
   remove them (S2 4 → 116, S15 2 413 → 3 850), because adjacent texels' windows differ and each median is its own field.
3. The kit's truth prefers the per-line law as it is: S15's median is best under the app's own choice (0.184 m), and the
   reproduction's own value (0.237 m) already shows how much the 1.4 % of texels where the reproduction differs matter.

**Closed again, on the reopened terms.** Three cross-line regularisations of the law's parameters fail the bar the user set;
nothing was built in the app. A consistent choice across lines (a labelling over candidates with a join cost) would be the
next different construction, and it needs a weight between arrival order and cross-line agreement that nothing in the
scene supplies — that is the reason it is not attempted here.

Scripts and log: `s22/sheetfield3.py`, `s22/s15_chain.sh`, `s22/s15b_chain.sh`, `s22/s15.log`.
