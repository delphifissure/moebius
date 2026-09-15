# S35 — the sheet construction, offline (2026-09-16)

The user's model, built as a measurement before any app change: one continuation sheet per visible surface behind each
hole, the nearest sheet behind the texel shows, the next one is the second layer. `research/s35/sheets.py` on the app's own
dumps (source depth, band, per-line far field, depth law, join law, ground plane), scored against the kit's truth and with
the seam instrument, next to the per-line law. Envelope note: everything here is measured at the 45°/30° instrument pose;
the target is the fishtank (±90° with a sliver in view at grazing angles), which the kit truth does not yet cover.

## 1. What the prototype does (every rule the app's own, ported)

1. **Far rims.** For a band texel and each of its four line directions, the runs beyond its own run (runs = maximal chains of
   texels joined pairwise by the join law) that lie behind it by more than the join tolerance, or are sky, are its far sides
   — the app's `cand()` list. A rim may itself be a band texel (the reveal set holds one texel of the background at a
   silhouette; its far side is itself).
2. **Surfaces.** A visible surface is a connected component of the depth map under the join law through the interior (not
   only along the hole's contour: contour clustering gave the troll 643 pieces, 338 single texels, and the boundaries between
   pieces were the seams; components give 308, one of them the whole cave).
3. **Strip and sheet.** Per surface, the component texels within its reach (the longest march its rims' texels make into the
   band, +1 — the app's window rule in 2-D); a least-squares plane in disparity (affine: the plane's homography), trimmed at
   3 MAD; per axis, a slope the strip cannot support (extent shorter than the reach along that axis) is not extrapolated (the
   app's thin rule per axis); a surface whose rims are ground texels follows the fitted ground plane (the app's thin-ground
   rule); a strip under three texels supports no model and makes no sheet. Optionally the plane is pinned to the rim by a
   harmonic extension of the rim residuals (Dirichlet at the entry texels of each march, zero flux elsewhere).
4. **Domain ('stop').** The band texels a surface's rims march into along their lines. ('extend' = the whole hole: dead —
   0.5–9 % of texels reached on S15 and the wrong surface elsewhere; not reported further.)
5. **Order.** Per texel, among the sheets whose domain holds it and whose value lies behind its own depth by more than the
   tolerance (the app's candidate test), the nearest shows; the second-nearest is the second layer; none → the texel keeps
   its own depth and is counted as **unreached**.
6. **Instruments.** Truth: band depth error against the kit's first hidden layer (metres, as the kit scorer). Seams:
   *jumps* = adjacent band texels whose depths differ by more than the visible step (count and summed length in steps = the
   total length of the walls the renderer would draw at the cone rim); *kinks* = second differences beyond the step (a slant
   has none). The per-line law's own far field is scored the same way in the same run.

## 2. Kit (truth)

| scene | arm | reached | truth median (m) | p90 (m) | jumps v (len) | jumps h (len) | kinks v (len) | kinks h (len) |
|---|---|---|---|---|---|---|---|---|
| S2 boxes | per-line | — | 0.0000 | 0.0427 | 8 189 (24 426) | 35 (507) | 859 (13 000) | 55 (836) |
| | sheets, plane + pinned residual | 100 % | 0.0007 | 0.0404 | 8 190 (35 273) | 485 (22 709) | 1 126 (28 610) | 503 (23 391) |
| | sheets, local planes | 100 % | 0.0000 | 0.0533 | 6 326 (32 550) | 473 (24 521) | 1 742 (31 104) | 384 (26 435) |
| S9 cards | per-line | — | 0.0000 | 0.0640 | 1 013 (80 742) | 880 (70 762) | 2 017 (161 475) | 1 740 (141 474) |
| | plane + pinned | 100 % | 0.0006 | 0.0640 | 841 (38 459) | 915 (42 384) | 1 118 (50 809) | 1 366 (62 163) |
| | local planes | 100 % | 0.0000 | 0.0640 | 0 | 0 | 0 | 0 |
| S26 quads | per-line | — | 0.0000 | 0.0560 | 11 129 (148 302) | 465 (26 710) | 3 555 (201 600) | 840 (52 663) |
| | plane + pinned | 100 % | 0.0153 | 0.0551 | 2 908 (117 930) | 1 839 (64 423) | 3 323 (180 425) | 1 554 (71 757) |
| | plane, no residual | 100 % | 0.0161 | 0.0552 | 2 365 (36 782) | 232 (15 649) | 1 538 (53 698) | 253 (17 352) |
| | local planes | 100 % | 0.0000 | 0.0564 | 16 556 (203 966) | 3 578 (102 091) | 4 342 (312 308) | 3 131 (155 746) |
| S15 sky | per-line | — | **0.1838** | 8.566 | 8 115 (800 260) | 6 041 (978 458) | 8 743 (1 456 088) | 9 780 (1 858 057) |
| | plane + pinned | 99.7 % | **0.0133** | 6.838 | 8 413 (910 087) | 6 043 (933 650) | 10 770 (1 437 862) | 9 503 (1 526 983) |
| | plane, no residual | 98 % | 0.1871 | 5.442 | 10 650 (1 032 449) | 6 276 (1 279 221) | 9 595 (1 778 045) | 10 149 (2 222 225) |
| | local planes | 99.7 % | 0.0207 | 6.817 | 9 835 (1 006 920) | 8 006 (1 125 557) | 13 429 (1 589 989) | 11 775 (1 800 031) |

Earlier configurations along the way (contour clustering, first rim only, ground surfaces dropped) are in the run logs;
the one that mattered: with the first version of the rim rule (the texel immediately beyond the band) the trunk's hole on
S15 had no ground sheet from the sides and took the sky — median 4.9 m — because the band's own edge texel is a ground
texel; the app's rule (march past the own run) fixed it.

Reading: on exact data the sheets keep the per-line law's truth on S2 and S9, are within 1.5 cm on S26, and take S15 from
18 cm to 1.3 cm (the per-line law's median error there was the hill behind the sign; one ground sheet through the side rims
answers it as the row-axis kind-2 does, and the pinned residual follows the dome). Seams: S9 halves or vanishes, S26 falls by
half to three quarters with the bare plane, S2 is unchanged to slightly worse (its floor's slant is already the whole
signal). The kit cannot separate the three interior models; the pictures do.

## 3. Pictures (DA3-16, no truth)

| picture | arm | reached | jumps v (len) | jumps h (len) | kinks v (len) | kinks h (len) |
|---|---|---|---|---|---|---|
| troll | per-line | — | 99 203 (1 711 260) | 65 535 (1 452 445) | 91 287 (2 727 132) | 65 610 (2 488 140) |
| | plane + pinned residual | 91.5 % | 107 134 (1 910 079) | 74 266 (2 067 177) | 104 488 (3 303 182) | 79 739 (3 573 663) |
| | plane, no residual | 78.9 % | 17 444 (311 365) | 16 772 (421 282) | 18 325 (501 328) | 20 648 (682 536) |
| | local planes | 62.2 % | 120 970 (2 387 551) | 106 621 (2 948 346) | 107 671 (4 046 349) | 107 324 (5 110 597) |
| vermeer | per-line | — | 110 222 (4 151 799) | 78 795 (2 188 851) | 132 525 (7 705 370) | 66 697 (3 780 473) |
| | plane + pinned | 95.8 % | 61 528 (1 162 405) | 42 675 (1 356 066) | 76 273 (2 160 650) | 35 170 (2 513 265) |
| | plane, no residual | 68.6 % | 22 945 (311 306) | 41 184 (485 788) | 14 511 (463 194) | 18 531 (729 414) |
| room | per-line | — | 44 834 (655 195) | 44 071 (628 026) | 54 298 (1 129 550) | 53 276 (1 089 251) |
| | plane + pinned | 92.4 % | 45 482 (845 880) | 65 493 (1 382 845) | 52 534 (1 442 596) | 72 372 (2 392 241) |
| | plane, no residual | 83.6 % | 14 265 (326 013) | 13 027 (232 864) | 17 753 (575 432) | 16 025 (390 071) |

Where the seams of the sheet arms sit (kinks by owner, vertical): with the bare plane there are **no same-sheet kinks at
all** on any picture (0 on the troll, 18 on vermeer); what remains is sheet boundaries (real steps and the specks below)
and the unreached texels. With the pinned residual the same-sheet class returns at 1.6 M (troll) — the rim's own noise,
carried into the first texels of the sheet by the Dirichlet data.

Surfaces on the pictures: troll 308 components, of which 1 is the cave (5 019 rim texels), 305 are specks thin along both
axes (constant-depth sheets) and 267 of those have strips under three texels and make no sheet; vermeer 2 full, 263 thin;
room 4 full, 463 thin. DA3's silhouettes are ramps and specks; the join law makes each its own component.

## 4. What the numbers say

1. **The construction does what it was built to do.** One sheet per surface removes the within-surface hatching by
   construction (same-sheet kinks 0) and, with it, most of the wall length: bare plane −82 % (troll), −92 % (vermeer),
   −50 % (room) on vertical jumps, −71 / −78 / −63 % horizontal. On the kit the truth holds and S15 improves fourteen-fold.
2. **The cost is coverage.** A single plane per surface lands in front of 8–32 % of the band's texels (the cave is not a
   plane; extrapolated 300 texels its tilt crosses the troll's own depth) and those texels get nothing — they would keep the
   occluder's depth, a clone, which the user's rules forbid. The per-line law reaches every texel (its window is local).
3. **Following the rim brings the noise back.** Pinning the plane to each rim texel's residual (or fitting a local plane
   per rim texel) restores coverage to 92–96 % but re-imports DA3's silhouette noise as same-sheet kinks: troll +12 %/+42 %
   jumps over the per-line law, room +29 %/+120 %; vermeer still −72 %/−38 %, whose wall is flatter and cleaner.
4. **The two are one question:** what is the sheet's interior on a surface that is curved *and* whose rim is noisy. A
   rigid plane is smooth and wrong in shape; an exactly pinned surface is right at the rim and noisy. Neither choice was
   ever available to the per-line law, whose window of g + 1 samples is a local smoother along the line — which is why it
   reaches everywhere and hatches everywhere.

## 5. The next arm (proposed, not built)

**A smoothing thin-plate sheet with the noise level from the data.** Per surface, the field over strip ∪ domain that
minimises Σ_strip (u − disp)² / σ² + λ · bending, with λ set by the discrepancy principle (Morozov 1966): the strip's RMS
residual equals the strip's own noise σ, measured as S21 measured it (third differences on the source, MAD → σ). On the kit
σ = 0 and the sheet interpolates (the S25 plate, equal to the line law on truth); on DA3 σ > 0 and the sheet follows the
surface's shape at the scale the noise allows and no finer. No free constant: λ is solved for. Advantages: one model for
both regimes; coverage of the pinned version, seams of the plane version, if the theory holds. Disadvantages: a sparse solve
per surface per λ (bisection, ~10 solves; the cave's domain is 200 k unknowns — minutes offline, needs care in the app);
S21's σ estimate read 0 on three of the six pictures' maps (the σ gate), so the noise measure itself must be re-checked on
the strips rather than the whole map; the specks (305 constant sheets on the troll) remain a separate question — they are
DA3's silhouette fragments, and whether a speck is a surface is the porous class (S15's canopy wants them, the troll's
silhouette does not).

**Alternatives.** (a) Hybrid: sheets where they reach, the per-line law where they do not — keeps 100 % coverage and most of
the seam reduction, but reintroduces the per-line hatching exactly in the hardest places (the unreached texels are where the
per-line law's own answer is ~100 steps behind the texel). (b) Sheets per surface with a quadratic instead of a plane: adds
curvature with 6 coefficients and no λ, but a quadratic extrapolated 300 texels is the ill-posed case S22 named.

## 6. Files and figures

`research/s35/sheets.py` (flags `--no-residual`, `--local`, `--drop-thin2`, `--no-extend`, `--step`, `--q`, `--truth`, `--out`);
outputs under each dump's `s35/` (or `s35_base/`, `s35_nores/`): `farField_stop.f32`, `farField2_stop.f32`, `who_stop.i32`,
`summary_<tag>.json`, `surfaces_stop.png`, `far_{perline,stop}.png`, `kinks_{v,h}_stop.png`. Picture dumps from
`harness/streak_class.js` (now writes `meta.json`, `disocc.u8`, `farField.f32`, `groundCol.u8`, `groundTex.u8`). Figures in
`research/s35/`: `troll_unreached_local.png`, and the far-field pairs added below.
