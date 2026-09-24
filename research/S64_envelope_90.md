# S64 — the design envelope is ±90° × ±90°, not the webcam's ±45° × ±30°

Date: 2026-09-24. Recorded from the user's direction: the band must eventually cover **180° horizontal by 180°
vertical**, for a "wall-embedded fishtank in a gallery" portal. The ±45°/±30° used so far (`bgViewFadeEndDeg = 45`,
`bgViewFadeEndDegV = 30`, the truth kit's env45 grids, `reveal.py --fade 45`) is only the test webcam's range. Results
at ±90° are not expected to be good yet; the apparent size of the scene can be scaled later if the geometry is wonky.
The user's second point: **the viewing region gets thinner the further off-axis you are.**

## What the geometry says

For an eye at lateral offset e and distance D from the glass (the app's law: shift of a texel at depth z behind the
glass = e·z/(D + z)), the disocclusion band between two depths z₁ < z₂ is, on the glass plane,

    w(θ) = D·tan θ · Δ,    Δ = z₂/(D + z₂) − z₁/(D + z₁),    e = D·tan θ,

and the size the viewer actually **sees** (its angle at the eye, the glass foreshortened by cos θ, the eye at D/cos θ)
is

    seen(θ) = w·cos²θ / D = ½·sin 2θ · Δ   (radians).

So on the glass the band grows without bound (tan θ), but the band **as seen** is largest at 45° and falls to zero at
90°: the user's "thinner and thinner". Example (D = 0.20, the app's rest distance; window 0.16 wide):

| θ | band on the glass, z 0.02→0.30 | seen size | glass seen at |
|---|---|---|---|
| 30° | 5.9 cm (0.37 × window) | 12.6° | 87 % width |
| 45° | 10.2 cm (0.64 ×) | **14.6° (max)** | 71 % |
| 60° | 17.6 cm (1.10 ×) | 12.6° | 50 % |
| 75° | 38 cm (2.4 ×) | 7.3° | 26 % |
| 85° | 116 cm (7.3 ×) | 2.5° | 9 % |
| 89° | 583 cm (36 ×) | 0.5° | 2 % |

## Consequences (to carry into every later step)

1. **The app cannot simply be set to 90°.** The bake's envelope `ex = D·tan(fadeEnd)` is infinite at 90°. It needs a
   cut-off, and the cut-off should be derived, not chosen: e.g. the angle where the band's seen size drops below one
   display pixel (or one arc-minute of acuity) for the actual viewing distance.
2. **Atlas resolution can fall with the reveal angle.** A band texel first revealed at angle θ is only ever seen
   squeezed by ~cos²θ, so the far-out band can be painted progressively coarser — a derived resolution rule, not a
   quality knob. `reveal.py` already carries a cos³ retinal weight (`w_ret`); it should be checked against cos²θ for the
   walk-along-the-wall case.
3. **Angle alone does not fix the band.** It depends on the lateral offset and the distance to the glass separately
   (walking along a gallery wall at fixed D reaches 80°+ only at large offsets; leaning in close reaches it at small
   ones). The envelope should be stated as a region of eye positions (offset, distance), with the angle derived.
4. Every measurement so far that used ±45°/±30° (env45 truth, band scores, SD bundles) is a subset of the real target;
   they remain valid for what they measured, and the extreme-angle band is new territory.

## Rules evaluated "at the rim" break at ±90°, and the seen-size form fixes them (item 3 of the render-time list)

The app's tear/continuity rule — neighbours stay one surface while their shift step is ≤ 1 px — is Scharstein's
**disparity gradient limit of one pixel** (quoted in Sun et al. 2010, read first-hand in R1's second batch): a step
under one pixel can only leave a sampling gap, a step over it opens a real hole. An independent derivation of the same
constant.

But every rule that evaluates the reveal **at the envelope rim**, e_max = D·tan(fadeEnd), becomes unbounded at ±90°: the
S50 cliff tolerance in screen pixels (`_plateNearOnlyPx`), the rim law's joins (`bgRimLawFor`), the reach walk
(|shift(d_far) − shift(d_near)| at e_max), and the sky's Z (`bgSkyZ`). At fadeEnd → 90° every depth step exceeds any
pixel tolerance and every rim tears. Measured as **seen** size instead, a step whose shift difference is Δσ at 45°
(f = 1) opens a gap seen as

    Δσ · tan θ · cos²θ = Δσ · sin θ cos θ,   largest at θ = 45°, value Δσ/2,

whatever the envelope beyond 45°. So for any envelope ≥ 45° the rim rules should be evaluated at 45° with half weight —
derived, no new constant — and the envelope's extent then only matters for the outpaint strip (which does not thin:
the strip added per degree is seen at a constant size, see `reveal90.py`) and for the band texels first revealed
beyond 45°, weighted by cos²θ.

Measured on a video frame (truck_trunks frame 0, app law, 3° steps): the in-plate band is 93 % first revealed by 30°
and 98.5 % by 45° (65 776 / 3 954 / 258 / 177 / 658 px in the rings 0–30 / 30–45 / 45–60 / 60–75 / 75–90°); beyond 45° the new need is almost all outpaint beyond the frame (0.76 × window at 48°, 2.5 × at 75°,
6.5 × at 84° on the glass; seen, the visible strip peaks near 45–50° and falls to 5 px at 84°).
