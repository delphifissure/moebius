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
