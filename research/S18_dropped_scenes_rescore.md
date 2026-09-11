# S18 — the Sprint 1 scenes that were dropped, rescored under the current law (2026-09-11)

Sprint 1 scored nine synthetic scenes against exact hidden-scope truth (`S1_sprint1_report.md` §5, env45 truth, the
app's membrane bake); Sprints 2–7 then developed the plane arm on eight of them (S2, S27, S12, S26, S16, S31, S15, S32)
and S5 (thin poles), S7 (canopy), S9 (stacked cards), S10 (crossing limbs) and S11 (rounded bodies) were not carried
along. This note rescores those five with the plane recipe exactly as the kit chain runs it (`_tearLaw=rim,
_farRule=plane`, 16-bit exact depth, `kit_s7b3_chain.sh`, tag `_c`) against the same env45 truth (S5 and S7's env45
truth built now with `scope.py --nx 800`, the grid the other scenes use). Buffers: `out/<S>/check_app16plane_c.png`.

## 1. Table — Sprint 1 (membrane bake, 8-bit) → now (plane recipe, 16-bit)

| scene | element | truth hidden px | app band px, S1 → now | precision S1 → now | recall S1 → now | band depth error now, median / p90 (m) |
|---|---|---:|---|---|---|---|
| S9 stacked cards | E5 stacked occluders | 62 682 | 175 346 → 65 417 | 0.36 → **0.958** | 1.00 → 1.000 | 0.000 / 0.064 |
| S10 crossing limbs | E2 interior self-occlusion, E4 sides | 52 680 | 200 027 → 56 140 | 0.26 → **0.937** | 1.00 → 0.999 | 0.000 / 0.050 |
| S11 rounded bodies | E4 object sides, E1 | 36 512 | 173 436 → 38 540 | 0.21 → **0.947** | 1.00 → 1.000 | 0.000 / 0.054 |
| S5 thin poles | E7 thin features | 1 608 | (§1 table: 200 552 plate; band n/a) → 1 691 | — → **0.489** | — → **0.514** | 0.000 / 0.056 |
| S7 canopy | E6 porous | *pending (truth build running)* | | | | |

Sprint 1's depth p90 on these three was 0.043–0.055 m with the band 3–5× too wide; the band is now the size of the truth
(1.04–1.07×) at the same recall, with the depth error where the two agree unchanged in kind (median 0, p90 ≈ 0.05 m — the
plate's far field is the wall behind, the p90 is the sides of the things). Layer 2 exists on S9 (32 715 texels: the card
behind the card) and S10 (3 141); the env45 truth of these scenes carries no second-layer channel, so it is not scored.
Sheet: `s18_S9_S10_S11.png` (green = both, orange = app only, blue = truth only — thin orange/blue lines are one-texel
rim disagreements).

## 2. S5 — what the thin-feature scene actually measures

The scene has four poles of 0.5, 1, 2 and 3 canvas pixels (canvas 1 600 px; the plate grid is 800 px, so 0.25, 0.5,
1 and 1.5 plate texels). In the 16-bit rest depth the poles occupy **0, 1, 1 and 2 columns** (mid-height columns 328,
471, 613–614; the 0.5-px pole is not in the depth map at all). In the app's source depth `dQ` after conditioning
(`S5_16plane_c/dQ.f32`) the two one-column poles survive in **130 of 450 rows**; the two-column pole survives in all
450. The step that removes them is the quick bake's **despeckle** (moebius.js ~L14050–14082, always on): a texel whose
3×3 range exceeds 0.06 and that has fewer than 8 of its 25 5×5 neighbours within 0.02 of itself takes the 5×5 median, two
passes — and the code says so in its own words: "filaments (1px wide, any length) are minority; ≥3px-wide structures keep
a majority on their own side and survive". A one-column line has 5 agreeing neighbours of 25; it is removed by design.

So S5's precision 0.49 / recall 0.51 decomposes as: the 0.25-texel pole is invisible to any depth-map method (truth counts
its reveal, 1/4 of the truth); the two 0.5-texel poles are erased by the despeckle over 71 % of their length (the blue
"truth only" columns in `s18_S5_poles.png`); the 1-texel pole is found (green) with the usual one-texel rim disagreement
(orange). The plane law itself is not the limiting step here; the despeckle's 8-of-25 majority is a **width threshold of
two texels**, chosen for the troll's striation combs (its comment), and it prices thin structures at the source. Not
changed here: it is a default-path constant on every bake, and whether a 1-texel line is a fleck or a pole cannot be
decided from the 5×5 alone — an along-line coherence test (a 1-wide run of ≥ N agreeing texels along one axis is a line,
not a fleck) would keep the poles and still remove isolated flecks; that is a candidate for the live pass, with the
troll's combs as the regression to watch.

## 3. Method notes

- Truth for S5/S7 built with the env45 grid (`--thx 0,5.6,…,45 --thy 0,15.7,29.4`, nx 800), as for the other scenes;
  scoring by `check_app_band.py` (band precision/recall against the envelope's hidden scope, band depth error in m via
  `app_z_of_d`).
- The rescore is read-only for the app: the probe (`a257_probe.js`) bakes with the panel's plane recipe and dumps; no
  defaults were touched. The five scenes' JSON: `out/<S>/check_app16plane_c.json`.
