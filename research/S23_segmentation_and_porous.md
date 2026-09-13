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

Env45 truth for all four (the dense and fine canopies needed a memory fix in the truth kit's disc intersector — a running
top-k per disc chunk instead of a rays × discs table; P1's render is byte-identical before and after; renders 2.8 and 3.9
hours). Current law → with the ceiling cut; sheet `s23/p_canopies_sheet.png`, buffers `s23/checks/`, table `s23/p_table.txt`,
ring split `s23/p_ring.txt`:

| scene | band → | truth | P → | R | depth median / p90 m | over-claim above the crown → | between the leaves (distance ≥ 2 from any leaf) → | ring (distance 1) | ring ÷ area | layer 2 app → (kit) |
|---|---|---:|---|---:|---|---|---|---:|---:|---|
| P1 sparse (300 discs) | 45 207 → 29 017 | 22 383 | 0.491 → **0.765** | 0.992 | 0.000 / 0.135 | 10 541 → 1 063 | 7 209 → **717** | 5 027 | 0.32 | 19 956 → 3 451 (6 349) |
| P2 dense (1 800) | 59 944 → 46 241 | 42 210 | 0.704 → **0.912** | 0.999 | 0.012 / 0.141 | 10 758 → 1 608 | 5 032 → **565** | 1 851 | 0.06 | 30 835 → 21 778 (33 971) |
| P3 fine (3 600, r/2) | 57 835 → 47 455 | 36 878 | 0.636 → **0.775** | 0.997 | 0.010 / 0.138 | 10 023 → 3 363 | 5 507 → **1 896** | 5 426 | 0.17 | 31 174 → 20 294 (23 475) |
| P4 two crowns | 66 838 → 53 958 | 47 380 | 0.708 → **0.877** | 0.999 | 0.010 / 0.133 | 8 807 → 1 239 | 6 722 → **1 593** | 3 776 | 0.10 | 37 061 → 26 600 (33 280) |
| S7 (reference) | 56 367 → 42 457 | 36 559 | 0.648 → **0.860** | 0.998 | 0.010 / 0.139 | 10 231 → 1 116 | 5 862 → **1 222** | 3 608 | 0.12 | 28 191 → 15 158 (23 199) |

Read across the variables:

1. **The ceiling over-claim does not depend on porosity.** Under the current law it is 8.8–10.8 k texels on every canopy,
   from 300 to 3 600 discs and for two crowns, because it is the crown's footprint against the ceiling, not its gaps. The
   ceiling cut finds the same plane on all four (a 4.989, c −0.0222, from 728–774 of 800 columns) and removes 84–90 % of
   it (P3 66 %: the fine leaves make 6 316 falling runs against P1's 2 487 and leave 72 columns without a ceiling).
2. **The between-leaf demand was mostly the same wash.** Under the current law 5–7 k texels lie two or more texels from any
   leaf inside the crown's box on every canopy — again independent of density. With the cut they fall to 0.6–1.9 k
   (1–4 % of the band): the merged ceiling-and-crown run had been extrapolating the wall into the gaps as well as above the
   crown. There is no separate between-leaf rule to write.
3. **What is left orders by perimeter.** After the cut the precision runs 0.912 (dense, ring ÷ area 0.06), 0.877, 0.860,
   0.775, 0.765 (sparse, 0.32) — the one-texel ring of §2.4, 70–87 % of every silhouette's perimeter. The sparse canopy,
   with the most silhouette per leaf, pays the most; nothing in it is a wash.
4. **Recall and depth are not the variable.** R 0.992–0.999 everywhere (37–189 texels missed, all inside the box); depth
   median ≤ 0.012 m; p90 0.13–0.14 m on every canopy including S7 — the far side of a leaf is often another leaf, which the
   first plate's plane cannot be, and the kit's layer-2 demand says so (6–34 k). The cut also removes the spurious second
   layer (the wall "behind" the ceiling): P1 19 956 → 3 451 against a kit demand of 6 349.

### 2.4 What the over-claim inside the occluder's box is: the one-texel ring

After the ceiling cut, what remains of the porous scenes' over-claim lies inside the occluder's bounding box (P6 94 %, P5
98 %, S7 78 %). Its distance to the nearest occluder texel (chessboard) says what it is:

| scene | over-claim inside the box | at distance 1 (the ring around every silhouette) | at distance ≥ 2 (between the leaves) | occluder perimeter ring, texels | band's share of the ring | ring ÷ occluder area |
|---|---:|---:|---:|---:|---:|---:|
| P6 grille (ceiling cut) | 11 238 | 11 038 | 200 | 11 844 | 99 % | 0.45 |
| P5 fence | 6 126 | 6 061 | 65 | 6 416 | 96 % | 0.26 |
| S7 canopy (ceiling cut) | 4 648 | 3 601 | 1 047 (842 at ≥ 3) | 4 524 | 80 % | 0.12 |
| S2 contact | 2 092 total | 681 | 45 | 964 | 71 % | — |
| S9 cards | 2 736 total | 795 | 8 | 1 056 | 75 % | — |
| S11 bodies | 2 028 total | 1 398 | 630 | 1 650 | 85 % | — |

The truth's hidden texels lie on the occluder's own texels (every scene: 100 %); the band adds the **one-texel ring** around
each silhouette on 71–99 % of its perimeter, the same on the compact scenes as on the porous ones. On a compact silhouette
the ring is a few per cent of the area and the precision reads 0.94–0.96; the porous scenes have perimeter of a quarter to
half of their area (the grille's 0.45), and the same ring costs P 0.31 on the grille and 0.20 on the fence. So the porous
set's residual is **not a between-leaf demand**: S7's 842 texels at distance ≥ 3 are the only between-leaf over-claim
measured, 2 % of its band (the four canopies after the cut: 565–1 896, §2.3). Which rule puts the ring texel in the band was not traced in this sprint (the sweep's cell size
at the rim and the far lip's carrier texel are the two candidates); it is one texel wide at the silhouette, where an
inpainter paints anyway, and its price scales with perimeter ÷ area, which is what "porous" means. Recorded, nothing changed.

## 3. Summary

1. Persistent departure along the line: 1–4 % of the breaks on any source; skipping them adds seams. Falsified offline,
   nothing built. Both readings of "persistent departure" are now closed by measurement.
2. Six porous scenes with env45 truth. The grille reproduced S7's above-occluder wash exactly and explained it (the ceiling
   merged into the occluder's column run, the wall extrapolated up); the fence had none. The **ceiling cut** — the ground
   cut's mirror, no new constant — removes it on S7, P1–P4, P6 and S26 (P +0.17 to +0.36), is inert or byte-identical on
   every scene and picture without a ceiling plane. Recommended default at the live pass.
3. The between-leaf demand is not a class of its own: it was the same wash entering the gaps, and it is 1–4 % of the band
   after the cut, on sparse, dense, fine and layered crowns alike.
4. What remains on porous scenes is the one-texel ring around every silhouette, 70–99 % of the perimeter, the same as on the
   compact scenes; the precision after the cut orders by perimeter ÷ area (0.91 dense → 0.77 sparse). One texel at the rim,
   recorded, not chased.
5. Harness: the truth kit's canopy intersector keeps a running top-k (the old rays × discs table reached 11 GB and the
   kernel killed the dense renders); P1's render is byte-identical.
