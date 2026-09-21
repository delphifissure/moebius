# S43 — Sprint 23, the measurement fix: and the do-nothing baseline overturns the reading of five notes (2026-09-21)

S41's first sprint. The score is now defined once, in `truthkit/tk.py` (`depth_scores`, `commit_scores`), used by the kit
scorer (`check_app_band.py`, a new `s23` block) and by the offline instruments (`bleed/rescore.py`). Four families are
reported: **d**, the app's own normalised depth, which is primary; **steps**, the same over the scene's visible quantisation;
**m**, metres behind the window, kept for continuity and no longer quoted; and **log₁₀ and δ** on camera distance, which are
the literature's metrics and make our numbers comparable with published work for the first time. Added alongside: the
interior/exterior/whole split, a do-nothing baseline, the accuracy/completeness split, and error binned by depth.

**The measurement fix was expected to be housekeeping. It is not.** The baseline it adds changes what five earlier notes
mean.

---

## 1. The do-nothing baseline, and the identity that makes it the right one

Doing nothing means keeping the occluder's own plate depth across the band — which is exactly §47's definition of a clone,
since an unowned band texel keeps that depth by construction. Its error is therefore **identically the median depth change
there is to recover**. The baseline column and the "how much is there to get right" column are the same column, which is why
it belongs in every table.

**Hidden-thing class, in d:**

| scene | our construction | the model | **do nothing** |
|---|---|---|---|
| L1 leaves | **0.0183** | — | 0.1044 |
| L5 clumps | 0.2633 | 0.0395 | **0.0314** |
| L6 forest | 0.0732 | 0.0686 | **0.0641** |
| L7 boulders | **0.0205** | 0.0239 | 0.0463 |
| L8 crowd | 0.0516 | **0.0351** | 0.0366 |
| L9 tufts | **0.0097** | 0.0334 | 0.0371 |

**Doing nothing beats both the construction and the learned model on L5 and L6.** The model beats it on exactly one scene,
L8, by four per cent. **So on the hidden-thing class the learned amodal prior never meaningfully beats the null**, and the
five notes that reported the model winning that class — S36, S39, S40, S42 — were all scored without one.

The reason is visible in the baseline itself. On these field scenes the thing-class depth change to recover is only 0.031 to
0.046 in d, because the hidden clumps, crowd figures and tufts sit at nearly the occluder's own depth. **There was very little
there to get right.** This is Counterfactual Depth's filter arriving late: they excluded test cases whose depth changed by
less than 0.25 m because *"slight changes in depth can hardly be examined the performance"*, and our thing class on field
scenes is exactly that case.

## 2. The background class is where the depth change actually is, and the construction owns it

**Background class, in d:**

| scene | our construction | the model | do nothing |
|---|---|---|---|
| L1 | **0.1312** | — | 0.2392 |
| L5 | **0.0256** | 0.0978 | 0.0902 |
| L6 | **0.0000** | 0.2114 | 0.3609 |
| L7 | **0.0372** | 0.0957 | 0.1109 |
| L8 | **0.0368** | 0.1691 | 0.2282 |
| L9 | **0.0000** | 0.1819 | 0.1836 |

The construction wins all six, is exact on two, and the depth change to recover here is three to eight times larger than on
the thing class. **The model barely beats the null on the background either** — on L9 by one per cent, on L5 it is worse.

Putting the two tables together: **on these five field scenes the learned model is close to indistinguishable from leaving
the occluder's depth in place.** That is a much stronger statement than S39's "the model is always mediocre", and it is the
correct one. On the whole band the model beats the null on two scenes of five, loses on two and ties one.

## 3. A methodological correction to S39 and S40

Those notes made the spread ratio the headline — the construction spanning 23× against the model's 2.5×. **Do not use that
statistic.** When the best case sits at the 16-bit quantisation floor the ratio is division by nothing: the construction's
background spread reads 8,600× in d and 37,000,000× in metres purely because it is exact on L6 and L9. Report the worst case
and the median instead. On the whole band:

| | worst | median | best |
|---|---|---|---|
| our construction | 0.2070 d | 0.0399 | 0.0003 |
| the model | 0.1500 | 0.0652 | 0.0496 |
| do nothing | 0.2079 | 0.0630 | 0.0321 |

The construction has the better median and the worse worst case. The model's worst case is lower. Doing nothing is
indistinguishable from the model on both.

## 4. Completeness caught something nobody was looking for

On L1 the construction's completeness over the whole band is **0.679**, and on the background class **0.576**. **A third of
L1's band is left at the occluder's own depth** — a clone by the §47 fall-back, against the project's own "everything filled,
wash never clone". Its accuracy where it does commit is 0.0186 d, essentially its overall figure, so the score was not being
flattered; but no instrument before today would have reported the omission at all. Every other scene commits on 99.5% or more.

## 5. The unit reversal, now confirmed twice

On the whole band, L1 reads **0.0198 d / 0.0112 m** and L6 reads **0.0106 d / 0.0154 m**. On the thing class the do-nothing
baseline reads **0.0314 d / 0.0545 m** on L5 and **0.0366 d / 0.0409 m** on L8. **Both pairs rank in opposite orders under the
two units.** S38 argued this from the depth law's gain; it is now observed twice in real data, which is why d is primary from
here.

## 6. What the literature metrics add

δ₁, the fraction of band texels within a 1.25 ratio of the true camera distance, discriminates well and is directly
comparable with published work: the construction reads 0.971 on L1's thing class and 0.190 on L5's, and 0.991 on L9's
background. The kit scorer's `s23` block also reports log₁₀, δ₂, δ₃, the exterior column against the scene's own rest depth,
and the error binned by the truth's own depth quintiles.

The exterior column passes its first sanity check: on L6 the visible plate matches the rest depth to 1.5 × 10⁻⁵ d, which is
the 16-bit floor. That column exists to catch a construction that improves the band while corrupting what the viewer already
sees, and nothing in the harness could previously have noticed.

---

## What this changes

1. **Every future comparison is scored in d, with the do-nothing baseline in the table.** A row that does not beat the null is
   not a result.
2. **The Phase D question is smaller than it looked.** The learned model's advantage on the thing class was, to within the
   precision of these five scenes, the advantage of not moving far from the occluder. That does not make the model useless,
   but it removes the motivation for a gate to switch to it, and it removes most of the motivation for training one — S41's
   Sprint 29 should be re-argued on the background class, where there is real depth change and where our construction is
   already exact on two scenes of six.
3. **S42's conclusion survives and strengthens.** The contest is class-level. The background class is where the work is, and
   the construction owns it outright.
4. **The kit needs scenes whose hidden things are not nearly coplanar with their occluders.** Every field scene we built has a
   thing-class depth change under 0.05 d. That is a gap in the kit, not a property of the world, and it should be fixed
   before any further thing-class claim.

**Recommendation unchanged in order: Sprint 24, the live pass, is next.** The only addition to S41 is item 4 above, which is
a cheap scene-building task that belongs with Sprint 29 rather than before Phase A.
