# Handoff — direction, stop-list, and how this arc terminates

**To:** whoever picks up moebius next.
**From:** a literature/architecture review run against `REVIEW.md` (Addenda 1–116)
and the field's published record, July 2026.
**Read time:** ~10 minutes. Everything here is grounded in numbers already in
`REVIEW.md`; nothing depends on trusting an outside claim.

Background, if and when you want it — not required to act on this doc:
- `RESEARCH-LDI-MPI-DISOCCLUSION.md` — 28 years of layered representations and
  disocclusion inpainting, licence-filtered
- `RESEARCH-DEPTH-DISOCCLUSION.md` — hidden depth specifically: background
  disocclusion vs self-occlusion vs contact

---

## 0. The situation, stated plainly

The measurement discipline in `REVIEW.md` is excellent and should not change.
The problem is not rigour. The problem is that **rigour is being applied
downstream of an unexamined decision**, so each fix is correct, lands, is
verified — and the image does not improve, because the thing generating the
defects is upstream of everything being fixed.

Addendum 116 says this in its own words: *"a101/a102 are worth nothing AS A
TEAR CRITERION… A large slice of this arc changed no rendered pixel."* That is
the pattern, not an isolated case.

**One parameter is generating the defect stream.** Fix the parameter and most of
the open threads stop existing. Keep the parameter and no amount of downstream
work converges — which is the observed history.

---

## 1. The parameter

`k` = screen displacement, in source texels, between the near and far ends of
the depth range, at the rim of the supported view cone. The app already computes
it: `max(|m0|,|m1|)` from `bgShiftLUTFor(pw,ph)` (`REVIEW.md`:6270). Addendum 110
measured it:

```
source            k        fold limit √2/k    in 8-bit levels
851 x 1023       775          0.00182              0.47
1920 x 1080      818          0.00173              0.44
2047 x 1200      909          0.00156              0.40
3000 x 1688     1279          0.00111              0.28
```

At 851 px wide, a surface spanning the depth range sweeps **775 px — 91% of the
image width — across the cone.**

### Everything below is the same inequality

| open thread | the inequality | source |
|---|---|---|
| 8-bit depth unusable | `q·k ≥ √2` | A110, `:5746` |
| fold test drops 40% of the mesh | `Δδ·k ≥ √2` | a117, A116 |
| "tears must pay for themselves" | `Δδ·k ≥ 2` | A47 item 2 |
| **v2 ghosting / banding** | MPI needs `N_planes ≳ k`. **20 planes vs k=775 → a 39 px parallax step per plane** | A116 |
| band always too narrow (D2, D3) | required extent `= Δδ·k`; a 0.5 step needs **388 px**, cap was 28 | D2, D3 |
| a113 margin blow-up (0.87 → 7.8 Mtexel) | same | A115 |
| backstop sweep, 60 s = 65% of the v1 bake | policing a plate whose extent is set by `k` | A116 |
| hidden-depth precision required | `1/k` px — at k=775, **one 8-bit level of hidden-depth error = 3 px of misplacement** | derived |

They are not five problems. They are one number.

### What changes at a sane `k`

| | k = 775 (now) | k = 30 |
|---|---|---|
| 8-bit quantum vs fold limit | 2.2–3.5× over (3.7–6.1× at 120°) | 0.12× — safe |
| troll triangles folding | 33.6% | ~0% |
| planes needed for artifact-free MPI | ~775 | ~30 — **v2's 20 is already close** |
| completion extent behind an occluder | up to 388 px | up to 15 px — **a band actually works** |
| plate margin | 851×1023 px | ~30 px skirt |
| backstop sweep | 60 s | unnecessary |
| hidden-depth precision needed | 0.33 of an 8-bit level (impossible) | 8.5 levels (easy) |

Note what this says about a109: the cone was widened 90° → 120° *after*
`REVIEW.md`:5793 had already identified the only three knobs — "more bits, a
lower source resolution, or **a narrower cone**". Widening it tightened the fold
limit from 2.2–3.5× to 3.7–6.1× of an 8-bit level (`:6173`).

---

## 2. The decision that must be made before more work

> **UPDATE — this has now been dug into. See `CONE-DECISION.md` for the full
> analysis and the recommendation.** Headline: the decision is much smaller than
> it looks, because `bgViewFadeEndDeg` is a *budget* parameter and does not
> appear in the per-frame shift — **narrowing the cone changes no pixel at any
> pose a viewer can reach.** a109's premise (front cameras reaching 120° FOV) is
> contradicted by the app's own A33 device LUT (mac 54×32, iphone 65×50,
> ipad 105×80), and the last envelope measured hole-free is 45° (A30/A32).
> **Immediate zero-risk action: revert `bgViewFadeStartDeg/EndDeg` to 35/45
> before taking any other baseline measurement.**

The framing below is retained because the product split it describes is still
the right one.

**This is the user's call, not yours and not mine.** Do not start §4 until it is
answered, and do not answer it by inference from the code.

> There are two products fused into one cone. Which one is being built?
>
> **(a) The geometric cone.** Parallax reconstructed from what the image
> actually contains plus bounded completion. Pixel-faithful at rest, testable,
> convergent. `k` in the tens. This is what every shipped single-image 3D-photo
> system does.
>
> **(b) The cinematic cone.** The wide dramatic move. At 0.85× the rim of a
> 120° cone, most of what is on screen was never in the source image — that is
> not rendering, it is generation. Legitimate, can look wonderful, baked
> offline, judged by eye.

If the answer is "both" — which is likely the right answer — then they are **two
paths with two sets of thresholds**, and the generative one must never set
constants for the geometric one. Fusing them is why every constant has been
tuned to satisfy a requirement no measurement can meet.

**Concrete question to put to the user:** *"At what viewing angle should the
image still be pixel-honest? Beyond that angle, is a beautiful invented image
acceptable?"* One sentence back from them unblocks everything.

---

## 3. Stop-list

Freeze behind a flag, measure the delta, then delete. Every item is justified by
a measurement already in `REVIEW.md`.

| stop | why | evidence |
|---|---|---|
| **v1 bake, entirely** | most expensive and worst-looking of the three modes | A116: v1 92.7 s vs v2 11.7 s; v2 is 0.00% black at all four user poses and the only render that still reads as the painting |
| **the backstop sweep** | 60.4 s = 65% of the v1 bake, policing an invariant that a clamp enforces for free | A116; §4.2 below |
| **the all-viewpoint / SD scan** | pruned **0 px in all six quick bakes**, at ~2.75 s of a ~10 s bake | A116 |
| **further precision on the tear criterion** | a101 exact vs a102 slope: 692469 vs 692246 triangles (**0.03%**), identical black, identical comb to 3 s.f. | A116 |
| **the fold-mode tear** | dropped 40% of the mesh and shipped the debris as a 1 px comb; cliff-only wins on every axis at once | a117 |
| **new screen-space heuristics of any kind** | the band/rind/cut family is the 2005–2016 DIBR literature's known dead end; `REVIEW.md` §4 already reached this verdict independently | §4 verdict; research doc §3 |
| **renderer-side repair of depth-estimator errors** | stroke repair, adopt-map, footing rule, wire rule, ink-follows-layer. Unbounded: every new asset brings new estimator errors | A44, A47, A55, A57 |
| **any new tuned constant** | see §5 rules | A96, A97, A101 |

Deleting these is not a loss of work. The measurements that produced them stay
in the record; the code they justify is what goes.

---

## 4. Do-list, in order

Each step is independently shippable, independently measurable with the existing
harness, and has a pass/fail condition. **Do not start step N+1 until step N's
number is recorded.**

### 4.1 Print `k`. (one line)
Log `bgShiftLUTFor(pw,ph)` per asset at the current cone, next to the fold limit
and the tear threshold. **Pass:** the number appears in the bake log.
Everything in §1 becomes checkable the same afternoon. Cheapest, highest-value
action available.

### 4.2 Add the ordering clamp. (small)
After the plug/plate depth is solved, clamp it:
```
d_hidden(x) ≥ d_occluder_silhouette(x) + ε
```
This is unconditional, one pass, and cannot regress correctness. Then turn off
behind a flag and measure: the backstop sweep, the protrusion hunts (A21, A41,
A43, A112), the cap cards, and the 0.004-unit offset — all of them exist to
find or paper over violations of an invariant that this clamp forbids at bake
time. **Pass:** rest-pose and off-axis black% unchanged, bake time down by the
sweep's 60 s, protrusion probes still clean with the sweep off.

*Searching rendered poses for violations of an invariant is strictly worse than
enforcing the invariant.*

### 4.3 Cone sweep. (existing harness, no code change)
With v2 unchanged, sweep `bgViewFadeEndDeg` and record black%, comb energy, and
plate exposure at each angle. **Pass:** a curve. That curve, plus §2's answer,
sets the honest cone empirically rather than by argument.

### 4.4 One law, one implementation. (refactor)
Route tear, fold, band width, completion extent, and plane placement through a
single function `revealPx(Δδ) = Δδ · k`. a104 retired three private copies of
the parallax law; a113 found a fourth. **Pass:** grep finds one implementation.

### 4.5 Fix the depth fill's operator. (contained)
Replace the first-order smoothing (pull–push / diffusion / reflect-smooth) in
the *depth* fill with a second-order solve:
```
∇²d = ∇·g   in Ω,   d = d_bg on the BACKGROUND boundary (Dirichlet),
                    ∂d/∂n free on the FOREGROUND boundary (Neumann)
```
`g` = background rim gradient extended into the hole. First-order priors are
biased to fronto-parallel plateaus — that is the plate that "moves at a
different rate than the floor it continues". This is A63b's intent with the
correct operator, multigrid on the pyramid that already exists. **Pass:** the
hold-out test in §6 improves; the ground ramp's fill no longer flattens.

### 4.6 Introduce ownership. (the self-occlusion fix)
Before filling any hole, answer *which visible surface do these hidden pixels
belong to?* Start classical and free: T-junction + convexity depth ordering over
the ink/edge maps you already compute. On painted and inked assets these are
**hand-authored occlusion annotations** — the illustrator drew the T-junction
deliberately. Use the answer to choose which rim seeds the hole's Dirichlet
condition.

This is the fix for the doppelgänger / hole-in-figure / "seated figures must
STAND" / troll-arm class. Those are *ownership* errors: the monotone constraint
is satisfied (the torso really is behind the arm), so no depth-domain test
catches them. **Pass:** the class-B hold-out test (§6) improves; the
doppelgänger shots stop reproducing.

### 4.7 Then, and only then, layering and detail.
Per-layer depth displacement to replace flat binning (kills v2's ghosting and
the ground-ramp banding together); soft/fractional alpha at layer boundaries
(kills thin-lift, ribbons, staff taffy, filaments, confetti — one defect, not
five); and finally the generative detail pass.

---

## 5. Process rules

These exist because the failure modes below are all in the record, several
times, and they cost more than any single bug.

1. **No change without a rendered-pixel delta.** If a change moves no pixel at
   the user's poses, it does not ship, however correct it is. a101/a102 is the
   worked example.
2. **Verify the instrument before believing a null.** Three confident nulls in
   Addenda 113–115 were instrument failures: a stale server, a probe pointed at
   a branch that returns before the code under test, and a watcher deleting the
   bake it was measuring. **Rule: every A/B must first demonstrate it can
   detect a deliberately broken arm.**
3. **Measure what the user sees.** A47's lesson (760 px probe vs the user's
   canvas) and a117's (black% is blind to an alternating light/dark comb).
   Pick the metric from the artifact, not from convenience, and state what the
   metric cannot see.
4. **No new constant without (a) a derivation with units, (b) a test that fails
   if it is wrong, and (c) a name that says what it means physically.** The
   constant count should be going *down*. A96/A97/A101 did this work; keep the
   ratchet.
5. **One law, one implementation.** Four private copies of the parallax law were
   found across A104 and A113. Any duplicated law will drift.
6. **Bound the scope of estimator repair.** A depth estimator's errors are
   unbounded across assets. Renderer-side repair of them cannot terminate. Fix
   at the depth stage or accept and document the ceiling (A44 does this
   correctly).
7. **When two modes both work, delete one.** Three bake modes were maintained
   for months; A116 priced them and one dominates on both cost and quality.

---

## 6. How this arc terminates

The arc has had no stopping condition. Here is one. It is falsifiable, and every
test runs on the existing harness.

**Gate 1 — Rest fidelity.** At zero offset, 0 pixels differ by >8/255 from the
bare-source reference render. Currently ~17.6k on Starwatcher (D1).

**Gate 2 — Cone honesty.** At the *declared* cone rim (from §4.3, not the
slider): black ≤ 0.1% of the visible image, and comb energy no worse than the
no-tear baseline. Currently v2 is already at 0.00% black at the user's four
poses — the comb is the open half.

**Gate 3 — Hidden depth, measured.** New test, and the important one, because
hidden depth currently has no number attached to it at all:

> **Hold-out occlusion test.** Take a region of an asset that is *not*
> occluded. Composite over it a mask shaped like a real occluder from the same
> asset. Run the full ownership + completion pipeline. Compare the completed
> depth to the depth that was actually there.
>
> Report **RMSE in pixels of misplacement at the cone rim** (`ε·k`), not in
> depth units — that makes it directly comparable to the fold limit and the
> tear threshold.
>
> Run it three times with three mask classes: background-adjacent (class A),
> self-occluding (class B), contact-adjacent (class C). For the first time this
> separates the three failure modes *numerically* instead of by eye.

**Pass: ≤ 1 px of misplacement at the rim, in all three classes.**

This is exactly how the ADIW dataset was built and how SLIDE trains its
inpainter — synthetic occlusion of known content is the standard way to get
ground truth here. It needs a harness script and no new data.

**Gate 4 — Cost.** Bake ≤ 10 s at 1920 px. v2 is at 11.7 s today with the
sweeps still in it, so this is nearly met already once §3's deletions land.

**Gate 5 — Complexity, monotone.** Constant count, config-flag count, and
lines-in-the-composite-shader all lower than the previous release. If a change
raises any of them, it needs an explicit justification in the addendum.

When Gates 1–5 pass simultaneously on all four assets, **stop**. Ship it, and
open a new arc for the cinematic path if the user wants one.

---

## 7. The shortest version

1. Revert the cone to 35/45 (`CONE-DECISION.md` §6). Zero risk, 1.73× off `k`,
   and it is the last envelope measured hole-free. Do this before taking any
   baseline.
2. Print `k`.
3. Build the simulated-viewer preview mode (`CONE-DECISION.md` §8) and re-triage
   the open defect list through it — a chunk of the current list is raw
   pre-distortion being read as breakage.
4. Delete v1, the backstop sweep, and the viewpoint scan; measure the delta.
5. Add the ordering clamp.
6. Log real head poses; set the cone per-device from the FOV LUT, budgeted at
   fade-start, per axis.
7. Second-order depth fill; ownership before filling.
8. Then layering and detail.
9. Gates 1–5, then stop.

Everything currently open that is not on that list is downstream of `k` and will
either disappear or become tractable once it is set.
