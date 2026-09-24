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

Measured on a video frame (truck_trunks frame 0, the app's default volume outer 0.02 / inner 0.04 / pn 0.5 / D 0.2,
moebius.js L2959–2960; 3° steps): the in-plate band, weighted by seen size, is 77 % first revealed by 30°, 86 % by 45°,
94 % by 60° and 99.9 % by 75° (raw texels 38 356 / 6 678 / 10 501 / 26 605 / 1 202 in the rings 0–30 / 30–45 / 45–60 /
60–75 / 75–90°: the far rings hold many texels but each is seen small). *(A first version of this paragraph, and of the
two examples below, used outer = 0.24, a truth-kit scene's depth, about six times deeper than the app's default; the
derivations do not depend on it, the example numbers do, and they are now the default's.)*

## The outpaint strip at ±90° is finite if it is stored by angle (item 3)

Beyond 45° almost all new need lies beyond the photograph's frame. Let σ be the farthest content's shift on the glass
at 45° (px). At angle θ the strip beyond the frame edge is σ·tan θ on the glass — 57σ at 89°, unbounded at 90°. But a
glass texel seen from θ is seen at cos²θ of its rest size, so the strip **added per degree** is seen at

    d(σ tan θ)/dθ · cos²θ = σ   (px per radian, constant).

Every degree adds the same visible amount, so the thinning does not bound the outpaint the way it bounds the band.
What bounds it is the parametrisation: **store the strip by angle** (texel u ∝ θ, like a cylindrical sky map) instead
of by position on the glass. One texel per dθ = 1/σ is then seen at a constant size at every angle, the resolution the
glass needs falls exactly as cos²θ without a rule for it, and the whole strip from 0 to 90° is

    σ · π/2 texels per side   (finite; 89° and 90° cost the same).

Example: truck_trunks frame 0 under the app's default volume, σ ≈ 150 px at 45° on a 480-px plate (the pop-out near
content; the far background moves 55 px) → ≈ 236 texels per side, about half a window width, for the full ±90°. On the
glass the same strip would be 8 600 px at 89°.

**When the view becomes all invention.** The window shows only content beyond the photograph's frame (for the far
background) once σ·tan θ exceeds the window width W_px: tan θ* = W_px / σ. truck_trunks at the default volume: θ* ≈ 73°
for the pop-out content (σ = 150 px) and ≈ 83° for the far background (σ = 55 px). Past θ*, what the
viewer sees through the window at the far depth is entirely outpaint. This is where "scale the apparent size of the scene
later" enters with a formula: compressing the depth range scales σ, and θ* = atan(W_px/σ) is the angle up to which the
photograph itself still fills the far view. A target θ* sets the depth scale; nothing else needs choosing.

**No acuity cut-off inside the envelope.** The window itself subtends (W/D)·cos²θ; with the app's W/D = 0.8 it falls
under one arc-minute only past 88.9°. So everything to ~89° is visible, and the finite, angle-parametrised strip is the
way to cover it, not a cut-off.

## App audit: every use of D·tan(fadeEnd), and what it does at ±90°

| where (moebius.js, worker branch) | kind | at fadeEnd → 90° |
|---|---|---|
| `bgPoseFrac` / `bgFadeFrac` (L150–160) | display fade | works up to 89° (the fade is angle-based through tan); exactly 90° divides by ∞ |
| `bgShiftLUTFor` default `ex` (L341) | **coverage**: band, reach walk, sweep | shifts ×57 at 89°: band reach and sweep extent explode |
| sweep pose grid (L9512: `ex = z0·tan(fadeDeg)`, poses uniform in e) | **coverage sampling** | poses uniform in e put ~all of a 17-pose grid beyond 80° and ~1 pose below 45° — must be uniform in angle (or in seen size) |
| `bgSkyZ` (L1698) | coverage | sky Z ∝ tan: unbounded |
| `bgConeSlopeAtDepth` (L266), L2293 (D hard-coded 0.2) | coverage (cone fill) | unbounded |
| exRim (L9706) | probe extent | unbounded |
| band tiers (L10677) | tier by pose fraction relative to tan(end) | angle-based, fine |
| `_revealLaw` exH/exV (L11920) | **visibility tolerance** (S48/S50) | should cap at 45° (seen gap max) |
| `bgRimLawFor` (L1609) | join test | does **not** use the envelope (fov/pw and a grazing angle) — unaffected |

So ±90° is not a settings change. It needs (1) pose sampling by angle, (2) coverage extents from the angle-parametrised
strip and the cos²-weighted band instead of D·tan(fadeEnd), (3) the visibility tolerance capped at 45°. (3) is one line
and changes nothing at today's 45°; (1)–(2) are a sprint.
