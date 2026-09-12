# S23 — Sprint 16: the persistent-departure segmentation reopened; the porous-silhouette scene set (2026-09-12)

## 1. Persistent departure, along the line (a different criterion from §15's)

§15 closed the *cross-line* version at step 0: 99.6 % of DA3-16's run breaks are already supported by a break on an
adjacent line within one position — the surplus over 8 bits is coherent creases, not isolated triples. The reopened
criterion is **along** the line and needs no neighbour: a departure of one sample that the next sample does not continue
is an outlier, not a break, because one sample cannot establish a new line (two define one). The run's last two samples
predict the sample after the departure as 3·D[a] − 2·D[c]; three samples each within q/2 of the truth put that two-step
prediction within 1.5 tol (tol bounds one step, 2q of slope; two steps, 3q). If the prediction holds, the departing sample
is skipped — masked out of the run's fits — and the run continues through it. No constant beyond the law's own tolerance.

Offline in the reproduction of the law (`s23/sheetfield3.py`, `SEG=persist`), against the app's own segmentation:

| source | breaks skipped | runs per row / column | same-sheet seams (reproduction's own → persist) | truth |
|---|---:|---|---|---|
| photograph DA3 16-bit (visible-step quantum) | 394 | 10.3 / 9.6 → 10.2 / 9.4 | 27 782 → **29 983 (+8 %)** | — |
| photograph DA3 8-bit | 1 275 | 7.7 / 7.2 → 7.5 / 6.8 | 38 114 → 38 397 (+1 %) | — |
| S15 hill + tree | 218 | 20.8 / 16.2 → 20.7 / 16.1 | 2 465 → 2 468 | median 0.237 → 0.238 m |
| S2, S26 | 0 | unchanged | unchanged | unchanged |

Single-sample departures are rare on every source (3.7 % of the 16-bit troll's breaks, 1.6 % of the 8-bit's, 1 % on
S15, none on the planar scenes), which is §15's finding seen from the other side: the breaks are creases that persist.
Skipping the few that do not persist shortens no runs worth speaking of and adds seams, since a run that now spans a
skipped sample fits a slightly different line than its neighbours' runs do. **Falsified; nothing built in the app.** With
this, both readings of "persistent departure" — supported across lines (§15) and persisting along the line (here) — are
closed by measurement: the run structure on a DA3 map is what the map's creases dictate, not what a segmentation rule
leaves in.

## 2. The porous-silhouette scene set

Six scenes in S7's room and framing, one variable each (`truthkit/scenes.py`): **P1** sparse canopy (300 discs), **P2**
dense (1 800), **P3** fine leaves (3 600 discs at half radius), **P4** two crowns layered, **P5** picket fence (13 slats
against the flat back wall), **P6** grille (thin bars both axes, the vertical bars reaching up in front of the ceiling).
Env45 truth as for every other scene (the per-layer visibility product cannot be skipped: it is what the score reads).
Errors split by region (`s23/p_classes.py`): above the occluder's top row, inside its bounding box, below, elsewhere.

### 2.1 The first three settle S7's ceiling blob

| scene | band | truth | P | R | over-claim above the occluder | inside its box |
|---|---:|---:|---:|---:|---:|---:|
| S7 canopy | 56 367 | 36 559 | 0.648 | 0.998 | 10 231 (51 %) | 9 436 (47 %) |
| P6 grille | 53 607 | 26 544 | 0.495 | 1.000 | 13 342 (49 %) | 13 098 (48 %) |
| P5 fence | 31 113 | 24 961 | 0.799 | 0.996 | 111 (2 %) | 6 126 (98 %, the one-texel rims) |

The grille reproduces S7's over-claim above the occluder almost exactly; the fence has none. And it is a real wash, not a
statistic: of P6's 13 342 texels above the bars, 13 331 carry a synthesised colour (S7: 10 225 of 10 231). The dumps say
why: every one of them is a **column** candidate of kind 1 whose rim lies a median **306 rows below** — the wall (depth 0)
beyond the bar's lower end — with its own depth 0.323 = the bar's 0.322. The ceiling directly above a bar's top is at the
bar's depth within tolerance, so the column run merges ceiling and bar into one, and the wall found beyond the bar's far
end is extrapolated up the merged run onto the ceiling. The fence's slats end against the flat wall (no surface nearer
than the wall above them), so the same extrapolation lands on the wall's own depth and nothing is demanded.

The law's premise — a surface continues as a plane behind an occluder — is what the **ground cut** already bounds from
below (a wall continued below its foot meets the ground). The ceiling is the ground's mirror and needed the mirror rule.

### 2.2 The ceiling cut (`window._ceilCut`)

Falling column runs (disparity decreasing downward: a horizontal surface above the eye, slope −1/(h·D)) whose
zero-disparity row is the ground's horizon (parallel horizontal planes share the vanishing line; the falling runs' own
consensus row when there is no ground); per column the smallest |slope|; the same robust plane, inlier and majority
acceptance as the ground; a candidate that passes above the ceiling on a texel's rest ray is cut to it. No new constant.

| scene | before → with the ceiling cut | ceiling found |
|---|---|---|
| S7 canopy | P **0.648 → 0.860**, R 0.998, depth 0.010 / 0.139 m unchanged; above 10 231 → 1 116; layer 2 28 191 → 15 158 | 779 of 800 columns |
| P6 grille | P **0.495 → 0.690**, R 1.000; above 13 342 → 80; layer 2 5 328 → 424 | 800 of 800 |
| S26 beams | P **0.457 → 0.817**, R **0.937 → 0.999**; layer 2 35 396 → 1 834 | 800 of 800 |
| P5 fence | 0.799 / 0.996 → same (band 31 113 → 31 105) | 800 of 800 (nothing to cut) |
| S11 | P 0.947 → 0.956 | 791 of 791 |
| S2, S16 | P +0.001 / +0.002, R same, depth same | found |
| S31 | identical scores | 680 of 800 |
| S15, S32 (open, no ceiling) | **byte-identical** dumps | none (S15: 800 falling runs, 0 horizontal) |
| troll 8-bit; vermeer, room, silverwarrior (DA3) | **byte-identical** (band, far field, plate, plate 2); troll path holes 3/4/101/71/55 unchanged | none (majority test: 0–3 of 170–1 001 columns on one plane) |

S26 was the scene whose beams-against-the-ceiling over-claim §5 of Sprint 3 could only describe; it was the same
mechanism. The spurious second layers (the wall "behind" the ceiling) go with it. Recommendation for the live pass: make
the ceiling cut the default beside the ground cut; it is inert wherever no ceiling plane explains the falling runs.

### 2.3 The canopy variables (P1–P4)

*(truth rendering; results follow)*
