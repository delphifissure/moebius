# S21 — Sprint 14: the noise estimate made regional (2026-09-12)

**Why.** The S10 floor (the visible step 1/k as the effective quantum on a 16-bit source) is gated by "the source is noisier
than its grid", measured as one median absolute second difference over the whole map (S9). S19 §3.4 found that median to
be exactly 0 on four of the six DA3 maps — the ones with a sky or a large flat far region — although their figures are as
noisy as the troll's. The user's queue put a per-region estimate first.

## 1. Offline first: what the tiles say (`s21/s14_tiles.py`, table `s21/s14_tiles_table.txt`, sheet `s21/s14_tiles_sheet.png`)

Per 32×32 tile of the raw depth PNG, in units of the map's grid q: the MAD-σ of the second differences (σ₂, the S9
estimator), their lag-1 autocorrelation ρ (white texel noise: ρ = −2/3, since adjacent second differences of white noise
have covariance −4 var against variance 6 var; a smooth surface: ρ → +1), and the MAD-σ of the **third** differences (σ₃:
Δ³ annihilates any quadratic surface, so curvature does not read as noise; white noise has var(Δ³) = 20 σ², and uniform
quantisation error alone, var q²/12, gives σ₃ = √(20/12) q = 1.29 q — a level, not a tuned constant).

| map | tiles with median|Δ²| = 0 | σ₂ > 0 | σ₃ > 1.29 q ("noisy") | note |
|---|---:|---:|---:|---|
| kit S32, S31 | 100 % | 0 % | 0 % | planes |
| kit S2, S26, S16 | 94–97 % | 3–6 % | 0 % | |
| kit S15, S11, S7, S5 | 71–84 % | 16–29 % | 0–0.6 % (S7 canopy 3.7 %) | curved / textured / thin content |
| troll, old 8-bit map | 100 % | 0 % | 0 % | quantisation only |
| troll DA3 16-bit | 0 % | 100 % | 39 % | |
| troll DA2 16-bit | 3 % | 97 % | 96 % | |
| bristlecone DA3 | 78 % | 22 % | 18 % | the tree noisy, the sky exact |
| room DA3 | 50 % | 50 % | 49 % | sunflowers noisy, sky exact |
| silverwarrior, starwatcher DA3 | 58 % | 42 % | 17–22 % | the figure / ground noisy |
| octopus, vermeer DA3 | 0–7 % | 93–100 % | 55–59 % | (σ₂ > 0 globally already) |
| repo 8-bit maps | 100 % | 0 % | 0 % | |

The sheet shows the noisy tiles exactly where a viewer would put them (the trunk and branches, the sunflowers, the figure)
and the sky exact. Two candidate per-tile rules follow from this table: **(1)** σ₃ above the quantisation level — noise
measured independently of curvature; **(2)** the S10 gate itself per tile — median |Δ²| > 0. On the troll's DA3 map they
differ a lot (39 % vs 100 % of tiles noisy).

## 2. In the app (`window._noiseTiles`; defaults unchanged)

In the a89 block, on the raw source before the dequantiser and the despeckle: per 32×32 tile the chosen test; a per-texel
effective quantum `window._qbQuantumMap` (source rows) = max(grid, 1/k) in noisy tiles, the grid elsewhere. Consumers:
the rim law's `joinedIdx` (the pair's own quanta) and `tolAtI`, and the plane law's `tol[]` — the join tolerances that
decide run segmentation, candidate admission and the plate's tears. The global scalars (band margins, sky threshold,
tear floors) keep the S10 global gate, so the arm changes exactly one thing: *where* the join tolerance is the floor.
`_noiseTiles = 1` is rule (1), `= 2` is rule (2). The probe dumps `quantumMap.f32`.

## 3. Rule (1), σ₃ against the quantisation level

- **Kit** (`_s14`): S32, S31, S2, S11 byte-identical to their references (0 noisy tiles). S15 (1 tile): band 48 020 → 47 973,
  P 0.723 → 0.724, depth median 0.184 → 0.188 m. S7 (12 canopy tiles): band 56 367 → 56 264, P 0.648 → 0.649.
- **Troll DA3 16-bit** against the S10 baseline (global floor): 41 % of tiles noisy; the other 59 % drop to the grid tolerance
  and **the runs fragment there**: 10.3 → 135.7 runs per row, far-side texels 661 632 → 612 981, band 265 899 → 250 636,
  layer 2 79 045 → 108 301, seams 27 267 → 27 553; holes on the path 0 both, clones 0. So "below the quantisation level in
  Δ³" is not "segmentable at the grid": DA3's smooth regions still carry second differences beyond the grid's tolerance
  often enough to break every run (the heavy tail S9 §13 measured).
- **Sky pictures**: bristlecone under rule (1) equals the forced-floor arm of S19 in every number (layer 2 19 962 vs 19 959,
  seams 10 361 vs 10 329, holes 21/25/16/50/74 vs 21/25/16/48/76) — the tree's tiles take the floor and the sky, being flat,
  never mattered to the plane law. Octopus (noisy globally already) equals its baseline.

## 4. Rule (2), the S10 gate per tile

- **Kit** (`_s14b`): S32, S2 identical to their references (0 and 4 % noisy tiles — S2's 15 tiles changed nothing).
  **S15 (31.5 % of tiles noisy: the hill and the tree) loses**: P 0.723 → 0.717, band depth median 0.184 → 0.213 m. S11
  (21 %), S5 (16 %), S7 (42 %): ±0.002 in precision, depth unchanged.
- **Troll DA3 16-bit**: 100 % of tiles noisy → **byte-identical** to the S10 baseline (the consistency check the rule owes).
- **Six pictures** (`s21/s14_pictures_table.md`): wherever the global gate read 0, rule (2) equals the forced-floor arm of
  S19 within a fraction of a percent — bristlecone layer 2 27 690 → 19 963 (forced 19 959), seams 9 434 → 10 380 (10 329);
  room layer 2 149 393 → 72 124 (71 442), holes 610 → 304 (304) at the far pose; silverwarrior torn 28 788 → 35 639
  (35 611), holes 1 307 → 1 400 (1 398); starwatcher layer 2 102 135 → 20 427 (19 805), holes 84 → 160 (160). Octopus and
  vermeer (noisy everywhere already) are identical to their baselines.

## 5. Closing: built, measured, removed

Both rules find the noise where a viewer would put it — that part of the premise held. What did not hold is that anything
downstream cared where the floor stops: on the sky pictures the plane law's result under a regional floor equals the
result under the floor everywhere, because the flat sky never needed a tolerance in the first place; and S19 §3.4 had
already measured the floor everywhere on these maps as not clearly better (layer 2 falls 30–80 %, seams and torn triangles
rise 10–25 %, holes move both ways). Rule (1) additionally fragments the troll's DA3 runs ten-fold where its "exact" tiles are
below the quantisation level in Δ³ but not segmentable at the grid; rule (2) is exact on the troll but costs S15's hill.

So the arm is **removed from the code** (rule 7; a comment at the a89 block records it), the global S10 gate stays as it
was, and the question is filed where the numbers put it: **not the region of the floor but its value** — whether 1/k is
the right join tolerance on a noisy 16-bit source at all is the open item, and S10's own numbers (DA3-16 under the floor
against DA3 at 8 bits: holes 5/10/11/5/13/10/12 vs 0/15/6/5/60/7/55, seams 27 267 vs 22 433) already said the 8-bit
quantisation was the better denoiser. The offline tile instrument (`s21/s14_tiles.py`) stays: it is the right tool the next
time a map's noise has to be characterised, and the σ₃-against-quantisation level is a cited, tuning-free test.

Verification of the removal: S2 re-probed after it is byte-identical to its S12 dump (far field, plate, band, carriers,
plate 2).
