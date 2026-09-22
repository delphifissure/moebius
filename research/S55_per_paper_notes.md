# S55 — per-paper notes, the stereo/DIBR corpus read first-hand (2026-09-22)

Companion to `S54_s33_directed_search.md`, which was search-level. These notes are from reading each supplied file
beginning to end. Quotations are transcribed from the text; equation numbers are the papers' own. Where the
PDF→markdown conversion mangled equations into one-symbol-per-line, I have reassembled them and say so.

**Corpus supplied: 17 files.** Still missing from the request: Daribo (depth-aided inpainting), Sun et al.
(structure propagation), the SGM penalty-function review. **Bornemann & März is truncated** — abstract plus about
one page of twenty, ending mid-sentence in §1; its method is not readable from what is here. Hirschmüller &
Scharstein arrived as the **CVPR 2007** "Evaluation of Cost Functions for Stereo Matching" rather than the PAMI
2009 version, which is a fine substitute.

---

## 1. Hirschmüller, "Stereo Processing by Semi-Global Matching and Mutual Information", PAMI 2008 [2126 lines] DONE

The single most useful paper in the set, and **it contains a better answer to class 1 than the one I proposed in
S54.**

### 1. The streaking diagnosis, in his own words, twice

§I, on prior work: *"Dynamic programming (DP) approaches [2], [15] perform the optimization in 1D for each
scanline individually, **which commonly leads to streaking effects**."*

§II-B, with the mechanism: *"Dynamic Programming solutions easily suffer from streaking [1], **due to the
difficulty of relating the 1D optimizations of individual image rows to each other in a 2D image. The problem is,
that very strong constraints in one direction, i.e., along image rows, are combined with none or much weaker
constraints in the other direction, i.e., along image columns**."*

**That is S33 class 1 exactly.** Our far-side law applies a strong constraint along the line it extrapolates and
none at all across lines. S54's mapping of class 1 onto streaking is confirmed first-hand, and the *reason* is the
same reason.

### 2. The penalty structure — S54's central claim, confirmed, plus one thing I did not have

Equation (11), reassembled:

```
E(D) = Σ_p ( C(p, D_p)
            + Σ_{q∈N_p} P1 · T[ |D_p − D_q| = 1 ]
            + Σ_{q∈N_p} P2 · T[ |D_p − D_q| > 1 ] )
```

> *"The second term adds a constant penalty P1 for all pixels q in the neighborhood N_p of p, for which the
> disparity changes a little bit (i.e. 1 pixel). The third term adds a larger constant penalty P2, for all larger
> disparity changes. **Using a lower penalty for small changes permits an adaptation to slanted or curved
> surfaces. The constant penalty for all larger changes (i.e. independent of their size) preserves
> discontinuities** [23]."*

So S54's claim holds: the penalty for a large jump is **flat**, not proportional. Our S51 join cost is
`revealPx`, monotone and unbounded, which penalises a class-2 real step (median jump 31) far harder than a class-1
self-disagreement (median 3.3) — the wrong way round. **Capping is right.**

**What I did not have:** P2 is *modulated by image contrast.*

> *"Discontinuities are often visible as intensity changes. This is exploited by adapting P2 to the intensity
> gradient, i.e. **P2 = P2′ / |I_bp − I_bq|** for neighboring pixels p and q in the base image. However, it has
> always to be ensured that P2 ≥ P1."*

A bigger colour difference between two neighbours makes the depth discontinuity between them **cheaper**. We have
colour on the plate everywhere, including the band, and our join cost ignores it completely. This is a second,
independent change to the same energy, and it is the one that would let a real step land in the right place
rather than a texel or two off.

§II-E.2 spells out why that matters: *"The energy function E(D) … does not include a preference on the location
of a disparity step. Thus, E(D) does not differentiate between placing a disparity step correctly just next to a
foreground object or a bit further away within an untextured background."*

### 3. THE FINDING: §II-E.3, "Discontinuity Preserving Interpolation" — this is our band, not their matching

Everything above is about the *matching* stage, which we do not have (no data term in the band). **§II-E.3 is
about filling holes where there is no data at all, which is exactly our problem**, and I had not seen it.

> *"Invalid disparities are classified into occlusions and mismatches. The interpolation of both cases must be
> performed differently. **Occlusions must not be interpolated from the occluder, but only from the occludee to
> avoid incorrect smoothing of discontinuities. Thus, an extrapolation of the background into occluded regions is
> necessary.**"*

and the method, equation (18):

> *"Interpolation is performed by propagating valid disparities through neighboring invalid disparity areas. This
> is done **similarly to SGM along paths from 8 directions**. For each invalid pixel, all 8 values v_pi are
> stored."*
>
> ```
> D′_p =  seclow_i v_pi    if p is occluded
>         med_i    v_pi    if p is mismatched
>         D_p              otherwise
> ```
>
> *"The first case ensures that **occlusions are interpolated from the lower background by selecting the second
> lowest value**, while the second case emphasizes the use of all information without a preference to foreground
> or background. The median is used instead of the mean for maintaining discontinuities."*

**This is a drop-in replacement for our far-side rule and it needs no cost volume.** Our law computes candidates
along 2 directions (row, column) and arbitrates by a hand-built rule (kind 2 wins, then the nearer rim). His
propagates along **8** and takes the **second-lowest** — lowest disparity being farthest, so "second lowest" is
"the second-farthest arrival", a one-step robustification against a single bad path.

It answers the objection I raised in the reading request — that our band has no data term, so stereo's
optimisation framing may not transfer. **This part of SGM has no data term either.** It is pure propagation plus
an order statistic over the arrivals.

And it independently confirms S45's far-side rim filter (worth 5.1×, 0.1776 → 0.0349): "must not be interpolated
from the occluder, but only from the occludee" is the same rule, arrived at for the same stated reason.

§II-G adds the same principle for fused orthographic data, by segment rather than by texel: fill a hole between
segments *"by only considering valid pixels of the segment whose pixel have the **lowest mean** … This strategy
performs smooth interpolation, but **maintains height discontinuities by extrapolating the background**."*

### 4. Aggregation details, for Sprint 31 if we still want them

- 8 directions minimum, **16 recommended**: *"The number of paths must be at least 8 and should be 16 for
  providing a good coverage of the 2D image."* Non-axis, non-diagonal paths are done as one step horizontal or
  vertical followed by one diagonal.
- Per-direction recursion (12), reassembled:
  `L′_r(p,d) = C(p,d) + min( L′_r(p−r,d), L′_r(p−r,d−1)+P1, L′_r(p−r,d+1)+P1, min_i L′_r(p−r,i)+P2 )`
- (13) subtracts `min_k L_r(p−r,k)` each step to bound the values; it does not change the argmin. Upper bound
  `L ≤ C_max + P2`.
- Costs summed over directions: `S(p,d) = Σ_r L_r(p,d)`. Complexity O(W·H·D), runtime 1–2 s on Middlebury.
- He is explicit that this is **not** classic DP: *"the approach is more similar to Scanline Optimization [1] than
  traditional Dynamic Programming solutions"* — it does not enforce the visibility or ordering constraints,
  because those cannot be defined for paths that are not epipolar lines. **Ours cannot either**, so we are in the
  same position.

### 5. §II-E.2, intensity-consistent selection — S22's idea, done with a data term

Mean-shift segment the *intensity* image; within each segment, segment the disparity; fit a **plane** to each
disparity sub-segment to make hypotheses F_ik; then *evaluate each hypothesis by substituting it and computing
E_ik from (11)*, and keep the argmin. Assumptions stated plainly: discontinuities do not occur inside untextured
areas; some texture exists on the same surface; the untextured surface is approximately planar.

S22 fitted per-line parameters and **median-filtered** them across lines, and it failed. This is the same idea
with the step S22 lacked: **generate hypotheses, then score them against the energy and choose.** It is the
"re-evaluate, don't average" principle that S54 attributed to PatchMatch, present here too and for the same
reason.

Note also his caution, which is our thin-evidence rule almost verbatim: *"only untextured areas above a certain
size are modified. Thus, only critical areas are tackled without the danger of corrupting probably well matched
areas."*

### 6. Numbers, for the record

Middlebury Oct 2006: at the 1-pixel threshold C-SGM ranks 6.2 and SGM 9.3; **at 0.5 pixel C-SGM ranks 3.6 and SGM
5.0, the top two**, which he attributes to sub-pixel performance. Runtime 1.8 s (SGM) / 2.7 s (C-SGM) on Teddy,
2.2 GHz Opteron. HMI costs 18% over Birchfield–Tomasi; iterative MI costs 164%.

### 7. What this changes for us

1. **Sprint 30 (cap the join cost) is confirmed and gains a second half**: also make the cap contrast-dependent,
   `P2 = P2′/|ΔI|`, using the plate colour we already have.
2. **Sprint 31 should be re-scoped.** I proposed multi-direction *cost aggregation*, which needs a cost volume we
   do not have. §II-E.3 is the version for a region with no data: 8-direction propagation of the valid rim values,
   then the second-lowest arrival. That is much closer to what the far-side law already does and is a smaller
   change than what S54 proposed.
3. The far-side-only rim filter (S45) has independent published support, with the same justification.

---

## 2. Scharstein & Szeliski, "A Taxonomy and Evaluation of Dense Two-Frame Stereo Correspondence Algorithms", IJCV 2002 [1014 lines] DONE

The field's framing document. Read in full. Three things matter to us; the rest is a taxonomy of a matching
problem we do not have.

### 1. Streaking again, and the same remedy, from a different lineage

§6.2, on their own implementations: *"All three global algorithms perform quite well, but **both DP and SO show
the 'streaking' characteristic for scanline-based algorithms**. The graph-cut algorithm performs best, both
quantitatively and qualitatively."*

And the mechanism, §5: *"Both DP and SO algorithms suffer from the well-known difficulty of enforcing
inter-scanline consistency, resulting in horizontal 'streaks' in the computed disparity map."*

Three papers now, three lineages, same word. This is not a coincidence of vocabulary — it is that **any method
that solves each line independently produces our class 1**, and everyone who has built one has seen it.

### 2. The sentence that sizes Sprint 31 exactly

> *"The SO algorithm solves the same optimization problem as the graph-cut algorithm described below, **except
> that vertical smoothness terms are ignored**."*

That is the whole difference between the streaking method and the best method in their table: **one term**. Not
a different model, not a data term, not a segmentation — the cross-line coupling. Table 1, bad-pixel percentages
on their test set: SAD 12.43, SAD/MF 12.43 (their local baselines), **DP 9.52, SO 9.76, GC 6.46**. Adding the
vertical term is worth a third of the error, and it is the only structural change.

For us: our far-side law is SO without the vertical term. Nothing else about it needs to change for the class-1
fraction to be attackable.

### 3. Intensity-modulated smoothness, in its original multiplicative form

Equation (5):

```
E_smooth(d) = Σ_{x,y} ρ_d(d(x,y) − d(x+1,y)) · ρ_I(I(x,y) − I(x+1,y))
            + (same for the y neighbour)
```

with equation (6):

```
ρ_I(ΔI) = 1 / (1 + γ|ΔI|)
```

> *"This idea encourages disparity discontinuities to coincide with intensity/color edges, and **appears to
> account for some of the good performance of global optimization approaches**."*

This is Hirschmüller's `P2 = P2′/|ΔI|` written as a *multiplier on an arbitrary ρ_d* rather than a division of a
constant, and with the `1 +` that keeps it finite at ΔI = 0. **The `1 + γ|ΔI|` form is the one to implement** —
Hirschmüller's bare division blows up on a flat patch and he has to bolt on `P2 ≥ P1` to stop it. Two free
parameters: λ (overall scale) and γ (how much colour matters). We have exactly the same two knobs available.

They are also explicit that this is a *tuning-sensitive* term: *"the algorithms are currently fairly sensitive
to the tuning of the smoothness cost, in particular to parameters λ and γ."* Sprint 30 should sweep γ, not pick
one.

### 4. What does not transfer, said plainly

Their DP charges a fixed `opt_occst` for occluded states and enforces the ordering constraint. SO drops both:
*"unlike in traditional (symmetric) DP algorithms, the ordering constraint does not need to be enforced, and no
occlusion cost parameter is necessary."* Hirschmüller drops them for the same reason (non-epipolar paths). **We
must drop them too** — our band has no second view to be occluded in. The three-state M/L/R machinery is dead
weight for us; the smoothness term is not.

### 5. Their own conclusion about local methods, which is our situation

*"As all local methods, however, shiftable windows fail in textureless areas, and they can even 'amplify' bad
matches."* Our band is, by construction, the region with no evidence at all — the limit of a textureless area.
Every paper in this corpus agrees that is where local/1-D methods break and where a 2-D prior is the only thing
that helps.

---

## 3. Bleyer, Rhemann & Rother, "PatchMatch Stereo — Stereo Matching with Slanted Support Windows", BMVC 2011 [686 lines] DONE

Read in full. §2.3 is the paper's gift to us and it is not the part it is famous for.

### 1. §2.3: they fill invalidated pixels the way we do, they hit our exact artefact, and they name the fix

> *"We now fill in the disparity for invalidated pixels. For an invalidated pixel p, we search its closest valid
> pixel **to the left and to the right**. The planes f_l and f_r of both points are recorded. We now compute the
> disparities when assigning p to f_l and f_r (equation (1)) and **select the lower of the two** as p's filled-in
> disparity. Selecting the lower disparity is motivated by the fact that **occlusion occurs at the background**.
> Note that this filling scheme **extrapolates planes, instead of replicating constant disparities** as is
> commonly done. Hence we can also correctly treat slanted surfaces at this stage."*

Point for point, that is our far-side law: nearest valid rim on each side of the gap, each contributing a fitted
plane rather than a constant, arbitrate toward the background. Written in 2011. Our S45 far-side-only rim filter
and our plane far rule are both here, and independently arrived at.

Then, immediately:

> *"However, the obvious problem is that **this strategy generates horizontal streaks in the disparity map**. To
> weaken this problem, we apply a **weighted median filter** on the filled-in disparities. The weight mask for
> the median filter is computed by equation (4). We use the same setting for γ and the window size that we have
> used in the matching process. **Note that all pixels that have survived left/right checking are not affected by
> this operation.**"*

**This is the single most directly applicable paragraph in the corpus.** Same construction as ours → same
artefact as ours (class 1) → and the remedy is a *post-hoc, colour-weighted, band-only median*, not a change to
the construction. Three properties make it cheap for us:

- **Band-only.** Valid pixels are untouched. That is our thin-evidence rule and our "never corrupt the plate"
  constraint, already satisfied by construction.
- **Colour-weighted**, with eq (4)'s bilateral weight `w(p,q) = exp(−‖I_p − I_q‖/γ)`. Same γ as the matching
  window — one parameter, already in the system.
- **Median, not mean** — for exactly Hirschmüller's stated reason (maintains discontinuities), so a class-2 real
  step inside the neighbourhood is not smeared into a ramp.

Note what it is *not*: it is not S22. S22 median-filtered the **plane parameters** across lines and failed.
This medians the **filled disparities** themselves, in a 2-D colour-weighted neighbourhood, after the fill. The
difference is the same one Hirschmüller's §II-E.2 draws — operate on the output with a data-aware weight, not on
the parameters blind.

### 2. The refinement schedule, if we ever do Sprint 32

Per-pixel plane as point + normal; propose Δz0 ∈ [−Δ^max_z0, Δ^max_z0] and Δn ∈ [−Δ^max_n, Δ^max_n]^3, accept only
if `m(p, f′_p) < m(p, f_p)`; then **halve both radii and repeat**, starting at `Δ^max_z0 = maxdisp/2`,
`Δ^max_n = 1`, stopping at `Δ^max_z0 < 0.1`. *"The idea is to allow large changes in the first iterations, which
makes sense if the current plane is completely wrong. In later iterations, we sample planes that are very close
to our current one, which allows capturing disparity details, e.g., at rounded surfaces."*

Accept-if-better on a **scored** proposal is again the "re-evaluate, don't average" principle. But note the gate
is `m(p, f)` — a photoconsistency cost. **We have no such cost in the band.** Sprint 32 would need a surrogate
(reveal-field smoothness? colour-alignment?), and without one, PatchMatch's machinery does not transfer. §2.3
does, because §2.3's remedy needs only colour and the filled values.

### 3. The fronto-parallel bias, and why it is our problem too

*"one also inherits a disadvantage of window-based matching, i.e., the **bias towards fronto-parallel surfaces**
… competitor (1) reconstructs a single slanted surface via various fronto-parallel disparity segments so that
the 3D reconstruction of the slanted plane from the Venus set looks like a **staircase**."* Table 1, error > 0.5 px,
Venus: fronto-parallel integer **7.57**, sub-pixel 1.73, slanted **1.00**.

Our plane far rule is the slanted-window answer, already. Worth recording that the measured gain from
"constant → plane" in their setting is 7.6× on a slanted surface at the sub-pixel threshold — which is the same
order as S45's 5.1× — and that it is *orthogonal* to the streaking fix. They needed both. So do we.

### 4. What they concede about untextured regions

*"Local adaptive support weight methods are starting to outperform global methods on Middlebury … However, we
believe that this is only because the Middlebury images are ideal for local methods, i.e., **almost no
untextured regions**. Global methods still make sense, because they allow occlusion handling directly in the
matching process and can **treat large untextured regions**."* Figure 6d/6e: their local method **fails** on the
Plastic set; the global one succeeds.

Our band is a large region with no data. On their own analysis we are in the regime where the local method is
the wrong tool — which is a third independent statement that the cross-line coupling, not a better per-line
estimator, is where the class-1 74% lives.

---

## 4. Schönberger, Sinha & Pollefeys, "Learning to Fuse Proposals from Multiple Scanline Optimizations in Semi-Global Matching", ECCV 2018 [405 lines] DONE

Read in full. **This is the paper that decides Sprint 31, and it decides it against the version I proposed —
but it hands over the replacement, and the replacement is cheap.**

### 1. The warning I asked for, confirmed in the first paragraph

> *"Summation of the aggregated costs from multiple directions and the final WTA strategy are both **ad-hoc steps
> in SGM that lack proper theoretical justification**. The summation was originally proposed to reduce 1D
> streaking artifacts [15] but is **ineffective for weakly textured slanted surfaces** and also generally
> **inadequate when multiple scanline optimization solutions are inconsistent**."*

And §4.1, "Slanted Surface", with the mechanism:

> *"the 1D scanline solutions are typically biased and jump at random pixel locations, leading to inconsistent
> solutions in different scanlines … In this case, **there is no clear outlier in the solution but final cost
> summation leads to a biased estimate** … On weakly textured slanted surfaces, adjacent scanlines solutions are
> mostly inconsistent leading to noisy disparity maps and well-known streaking artifacts."*

**Our band is the limiting case of "weakly textured slanted surface".** There is no texture at all (no data), and
the far field is by construction slanted (that is the whole point of the plane rule over the constant rule). So
we are squarely in the stated failure regime of multi-direction aggregation. S54's Sprint 31 as I scoped it —
"aggregate over more directions and combine" — is aimed at the part of SGM that these authors say does not work
in exactly our case.

### 2. And the numbers kill the obvious robust fixes too

Table 1, Middlebury 2014 training, non-occluded, bad@1px — this is the row set I most wanted to see:

| combination across directions | bad 0.5px | **bad 1px** | bad 2px | bad 4px |
|---|---|---|---|---|
| SGM (plain **sum**, WTA) | 50.85 | **23.04** | 8.89 | 5.16 |
| `min_d L_r(p,d)` — take the single best direction | 52.18 | **25.45** | 11.81 | 7.79 |
| `min_d median_r L_r(p,d)` — **median across directions** | 63.25 | **31.81** | 9.90 | 8.24 |
| SGM-Forest (learned per-pixel selection) | 46.08 | **19.99** | 7.78 | 4.41 |

> *"Both methods perform worse than baseline SGM, **underlining the need for a more sophisticated fusion
> approach**."*

The median across directions is **38% worse** than plain summation. That is a direct, published, measured
refutation of the naïve order-statistic combination — and I should flag that **Hirschmüller's §II-E.3 uses
exactly such an order statistic** (`seclow_i v_pi` / `med_i v_pi`). The two are not in contradiction — his is
over *arrivals of already-valid disparities into a hole*, theirs is over *aggregated cost volumes* — but it
means I cannot treat "take the second-lowest of 8 directions" as robust by assumption. **It has to be measured
against our own 2-direction baseline, and the null hypothesis is that it is worse.** That is a real correction
to my §7.2 note on Hirschmüller above.

### 3. The finding that makes it worth doing anyway

Figure 1 and §4.2:

> *"While SGM is more accurate than each SO on the whole image, **each SO solution is better in some specific
> areas** … the joint accuracy of all scanlines is much higher than SGM."*
>
> *"The disparities of the different scanline solutions are often inconsistent, especially in areas of weak data
> cost. Yet, **in almost all cases there is at least one scanline that is either correct or is very close to the
> correct solution.** The main challenge … is to identify the scanlines which agree on the correct estimate."*

So: the information **is** in the multiple directions. What fails is combining them by a fixed rule. The oracle
that picks the right one per pixel is far better than any of them; the whole paper is machinery for
approximating that oracle.

**This reframes Sprint 31 correctly.** Not "aggregate more directions" — *"produce several candidates and
select per texel."* We already have that shape: the far-side law computes four candidates and arbitrates. The
question S54 should have asked is not "should we add directions" but **"is our arbitration rule the weak part?"**
Their answer for stereo is yes, emphatically, and the fix is a per-pixel selector with a confidence output.

### 4. Their contrast-modulated P2 — the third form, and the best one

§5.1: `P1 = 100`, and

```
P2 = P1 · (1 + α · exp(−|ΔI| / β)),   α = 8, β = 10,  intensities in [0,255]
```

Compare the three forms now in hand:

| source | form | at ΔI=0 | as ΔI→∞ | bounded? |
|---|---|---|---|---|
| Hirschmüller 2008 | `P2 = P2′/|ΔI|` | **∞** | 0 | no, needs the `P2 ≥ P1` bolt-on |
| Scharstein & Szeliski 2002 | `ρ_I = 1/(1+γ|ΔI|)` | 1 | 0 | above, not below |
| **Schönberger 2018** | `P2 = P1(1 + α e^{−|ΔI|/β})` | `P1(1+α)` = 900 | **P1** = 100 | **both ends** |

The exponential form is the one to implement for Sprint 30. It is bounded **at both ends** — a strong colour edge
never makes a depth step free (floor `P1`), and a flat patch never makes it infinite (ceiling `P1(1+α)`) — and
the 9:1 ratio between the two is a single interpretable number. `β = 10` on a 0–255 scale means the modulation
is essentially spent by ΔI ≈ 30, i.e. it responds to *real* colour edges and ignores noise. We have all of this:
plate colour on the band, and a join cost that currently ignores it entirely.

### 5. Their post-filter is PatchMatch's, again

§4.4: neighbourhood `N_p` = pixels within `ε_p = 5` whose confidence exceeds `ε_ρ = 0.1` **and** whose intensity
is within `ε_I = 10` of the centre; then `d̄_p = median_{q∈N_p} d̂_q`.

> *"The filter essentially computes a median on the selective set of neighborhood pixels N_p which have high
> confidence and similar color as the center pixel p."*

That is a **colour-and-confidence-gated median**, i.e. PatchMatch §2.3's weighted median with a hard gate and a
confidence term added. Two papers, seven years apart, different lineages, both end their pipeline with the same
object. And §5.2 on its worth: *"While the biggest accuracy improvement stems from the initial fusion step, the
final filtering further improves the results by eliminating spatially inconsistent outliers."* — secondary, but
real, and cheap.

**We already have the confidence channel** (`_geoFarConf`, built from `farAxV` on the reveal scale). So our
version of this filter is: median the band's far-field values over a 5-px neighbourhood, gated on plate colour
similarity and on `_geoFarConf`. Every input exists today.

### 6. What does *not* transfer

The core method is supervised — a random forest over a 72-d feature of per-direction WTA disparities and their
cross-costs `K_m(p, d*_p(n))`, trained on benchmark ground truth. **The feature is built from cost volumes we do
not have.** Every entry is "what does direction m think of direction n's answer", which requires a data cost.
Our only analogue is each candidate's own extrapolation uncertainty, which is not the same object and is much
weaker evidence.

Worth recording that they tried the alternatives: *"k-NN search, SVMs, (gradient boosted) decision trees,
AdaBoost, neural nets"*; MLP was close, forest won on CPU efficiency; *"even a single decision tree improved
upon baseline SGM"*. If we ever do get a band-side data term, a **single decision tree over a handful of
per-candidate features** is the cheapest published thing that beats fixed arbitration.

### 7. Revised verdict on Sprint 31

**Do not build multi-direction cost aggregation.** Published measurement says summation fails in our regime and
robust statistics across directions fail worse.

Build instead, in this order, all of which this paper supports and none of which needs a cost volume:

1. **Sprint 30 as revised** — cap the join cost, exponential contrast modulation `P2 = P1(1 + α e^{−|ΔI|/β})`,
   sweep α and β (Scharstein & Szeliski's warning that λ/γ tuning dominates applies).
2. **The gated median post-filter** — colour + `_geoFarConf` gated, band-only, valid texels untouched
   (PatchMatch §2.3 ∩ Schönberger §4.4). Smallest change in the corpus with two independent endorsements.
3. **Only then**, and only if 1–2 leave class 1 alive: revisit arbitration as *per-texel selection among
   candidates*, which is what the far-side law already is, rather than as aggregation.

Hirschmüller's §II-E.3 8-direction propagation stays on the list but **demoted and with its null hypothesis
flipped** — measured against our 2-direction baseline, not assumed better.

### 8. Incidental: a lead on missing paper #19

Refs [13] and [14] are **Hermann & Klette**, "Iterative semi-global matching for robust driver assistance
systems" (ACCV 2012) and "Inclusion of a second-order prior into semi-global matching" (PSIVT 2009). One of
these is probably what I half-remembered as "a review and evaluation of penalty functions for SGM". Also ref [7],
**Facciolo, de Franchis & Meinhardt, "MGM: A Significantly More Global Matching for Stereovision" (BMVC 2015)**,
which by its title is precisely the "fix the cross-line coupling in SGM" paper and is a better #19 than the one I
asked for.

---

## 5. Zhang & Tam, "Stereoscopic Image Generation Based on Depth Images for 3D TV", IEEE T-Broadcasting 51(2), 2005 [485 lines] DONE

Read in full. I asked for this as "either an important counterweight or an instructive dead end". **It is
mostly a dead end for us, for one specific and checkable reason — but it leaves behind one number worth
stealing and one diagnosis worth keeping.**

### 1. What they do

Pre-smooth the depth map with separable Gaussians before warping, `σ_h` ≠ `σ_v`, window `w = 3σ`. That is the
whole method. §II-C's hole-filling is *"averaging textures from neighborhood pixels"* — they make no attempt to
fill well, because the point is to have almost nothing to fill.

Their own framing of why, §I: they cite LDI [7] as the accurate alternative and reject it — *"while this
approach is likely to produce very accurate virtual images, it is more computationally demanding and it
requires more bandwidth for transmission."* **We took the LDI branch** (plate 1 / plate 2). This paper is the
road not taken, argued on 2005 bandwidth grounds that do not apply to us.

### 2. The one number worth stealing

§III: *"the minimum depth smoothing strength to reach a constant value of newly exposed areas is dependent on
the baseline distances … For the test image 'Interview,' **it is approximately one quarter of the baseline
distance**."*

A closed-form relation between the warp magnitude and the σ that kills the band. In our terms the baseline is
the reveal, and we have the reveal field per texel (S48). So the analogous rule is **σ(p) ≈ reveal(p)/4**, a
per-texel smoothing radius rather than a global one. Their residual — the constant floor the curve flattens to
— is *"simply due to the persistence of newly exposed areas at the image margins"*, which for us is the frame
edge, which the margin strips already handle. **So if we ever wanted the band gone rather than filled, this says
exactly how hard to blur and confirms the frame edge is the irreducible part.** That is a real result and I did
not have it.

### 3. The reason it does not transfer — and it is our envelope, not our taste

Their entire justification for asymmetry, §IV:

> *"The concept of asymmetric smoothing is consistent with known characteristics of the binocular system of the
> human eyes. **The human visual system obtains depth cues from disparity mainly from horizontal differences
> rather than vertical differences** between the images that are projected to the left and the right eyes. This
> allows us to filter the depth map stronger in the vertical than in the horizontal direction."*

That holds for a **fixed stereo pair**: the two cameras are displaced horizontally and only horizontally, so
vertical depth structure is never expressed as parallax and can be destroyed for free.

**Our envelope is ±45° horizontal and ±30° vertical.** Vertical head motion produces real vertical parallax that
the viewer sees directly — it is not a binocular cue being discarded, it is motion parallax being rendered. So
smoothing `σ_v = 5σ_h` (their §V-B setting) would apply their *geometric distortion* — §IV: *"vertically
straight object boundaries now can become curved"*, the curved table leg — squarely into the axis where we
still move. The trick's own stated premise is false in a head-tracked portal.

It is not a hypothetical: the artefact they document under **symmetric** smoothing is the one we would get in
the vertical direction under **asymmetric** smoothing, because we have not given up that axis. S54's hope that
this was "a fundamentally different lever" is right about the lever and wrong about whether we can pull it.

### 4. And their measurement cannot settle it anyway

Table II, mean opinion 0–100 over ten viewers, DSCQS (ITU-R BT.500):

| smoothing | None | Mild | Strong |
|---|---|---|---|
| symmetric | 44.8 | 52.9 | 62.1 |
| asymmetric | 48.6 (SE 6.6) | 58.0 (SE 3.6) | 68.4 (SE 1.9) |

Two problems. First, the **"None" column should be identical** — σ_h = σ_v = 0 is the same stimulus under both
labels — and it differs by 3.8 with SE 6.6. That sets the noise floor of the study, and the asymmetric
advantage (3.8, 5.1, 6.3) never clearly exceeds it. Second, baseline was fixed at 36 px ≈ *"1° disparity or
approximately 5% of the width"*, chosen for viewing comfort. **Our envelope is an order of magnitude more
motion**, and monotone-in-σ quality at 1° says nothing about 45°.

They concede the cost themselves: *"smoothing of depth maps, while attenuating some artifacts, will lead to a
diminution of the depth resolution contained in the rendered stereoscopic views. Future studies will be
required to examine this trade-off more closely."*

### 5. Where this leaves the 2× depth arm

Our largest measured motion win this session was a **sharper** map (`da2x`, DA at 2× short side, temporal step
−8.4%). This paper argues for deliberate blurring. They are not actually in contradiction, and the reconciliation
is the useful part:

- Their blur is applied **to get a smaller band**, accepting a wrong-but-smooth geometry. It is a *trade of
  depth fidelity for hole area*.
- Our 2× map **gets a more accurate band boundary**, which reduces flicker because the boundary stops moving
  between frames. It is not a trade; it is better input.
- We ruled out the flatness confound directly (2× map sd ratio 0.982, p90−p10 ratio 1.106 — **the 2× map is not
  smoother**), so `da2x`'s win cannot be a covert instance of their effect.

**Verdict: do not implement asymmetric pre-smoothing.** Record σ ≈ reveal/4 as the band-elimination relation in
case we ever want a "comfort mode" that trades geometry for a clean image at reduced envelope, and record the
cardboard-effect note (§V-E.2) as a named risk of *any* depth smoothing we do: *"this removal of 'crispness' at
the borders of objects reduces chances of perceiving the 'cardboard effect'"* — they count it as a benefit; for
a portal whose whole claim is solidity, flattening objects toward cardboard is a cost.

---

## 6. Ndjiki-Nya, Köppel, Doshkov, Lakshman, Merkle, Müller & Wiegand, "Depth Image-Based Rendering With Advanced Texture Synthesis for 3-D Video", IEEE TMM 13(3), 2011 [713 lines] DONE

Read in full. This is the DIBR lineage answering the question S54 never asked, and **it answers it against the
paper I read just before it.**

### 1. The field's own taxonomy, and its verdict on Zhang & Tam

§I: *"In the literature, **two basic options** are described to address the disocclusion problem. Either the
missing image regions are replaced by plausible color information [20] or the depth map is preprocessed in a way
that no disocclusions appear in the rendered image [21]. The latter technique will be referred to as
**'disocclusion elimination'**."*

And then, of that second branch — which is Zhang & Tam's, cited here as [12], [13]:

> *"Disocclusion elimination methods usually apply a lowpass filter to preprocess depth maps. A Gaussian low-pass
> filter [21] or, alternatively, **an asymmetric filter [12], [13]** is often used. This depth prefiltering step
> corresponds to smoothing depth data across the edges and thus lowering the depth gradients in the virtual view.
> … **foreground objects can be considerably distorted by this approach, which is subjectively quite
> disturbing** [11]–[13], [21]."*

Six years later, from the institute that supplied Zhang & Tam's own test footage, the pre-smoothing branch is
described as a known-bad option, and Table II measures against Fehn [21] (the Gaussian version) as a baseline to
beat. **That settles §5 of my Zhang & Tam note independently**: the DIBR field did not settle on pre-smoothing.
It settled on colour filling, with the background favoured.

### 2. Line-wise filling named and condemned — and it is our far-side law

> *"Another simple approach repeats the last valid background sample line-wise into the unknown area [8].
> **Filling methods based on this approach suffer from severe artifacts when structured backgrounds and dominant
> vertical edges are present** [cf. Fig. 2(g)]."*

**"Dominant vertical edges."** That is class 1 stated in DIBR's vocabulary rather than stereo's: fill each row
independently, and any structure running across rows is destroyed. Fourth lineage, fourth naming of the same
artefact. Figure 2(g) is captioned *"Result of line-wise filling approach (see artifacts at the person's
back)"*.

### 3. Their fix for the rim estimate — robustify it, do not trust one texel

§III. Two parts, both applicable to us.

**(a) Blob removal.** *"Due to inaccuracies in depth estimation, FG object boundary samples may be warped into
[the hole] (denoted as 'blobs')… small blobs up to τ samples are assigned to [the hole]"* — i.e. foreground
fragments that land inside the band are *deleted* before they can be used as fill sources. That is our
silhouette-fringe problem (S17), and they solve it by size threshold on connected components.

**(b) k-means on the rim neighbourhood instead of the nearest value.** *"It is assumed that **relying on a
single value of D_i can be error-prone.** Hence, the spatial neighborhood surrounding location i is clustered
into two depth classes, whose centroids are represented by c_min and c_max. They represent FG and BG depth
values respectively."* Window M×N = 32×32, k = 2, fill from the **background** centroid.

This is a **robust far-side rim estimate**: not "the nearest valid texel across the rim" (one sample, which is
what our law takes) but "the background mode of a 32×32 neighbourhood". It is the same instinct as PatchMatch's
weighted median and Schönberger's gated median — *never let one texel decide* — applied at the rim rather than
after the fill.

### 4. But their own ablation says it is objectively a tie — and that is the honest part

§VII-B, on exactly this: *"It can be seen that **all filling methods** (line-wise without blob removal (LW) and
k-means clustering with different window sizes (32×32, 48×48, 64×64)) **perform similarly.** Note that line-wise
filling without blob removal gives **slightly better objective results** than line-wise filling with blob
removal."*

They adopt k-means anyway, on subjective grounds: *"Therefore, subjective results are taken into consideration to
find the optimal filling method… distortions can be observed for the LW approach, while k-means clustering
generates good results."*

**This is the pattern this whole project has been living inside, published in 2011.** PSNR and SSIM cannot see
the artefact; the artefact is what ruins the picture; the authors trust their eyes and say so in print. It is
direct support for our position that the motion metrics (LPIPS, temporal step) and the sheets have to be read
together, and that a null result on an aggregate metric is not a null result. Their conclusion says it outright:
*"the lack of an adequate perceptual measure for 3-D content hampers a fully optimized configuration of our view
synthesis algorithm."*

### 5. A third median, and a filling order

§V, the initialisation before synthesis: *"the median estimator is used, which is the standard measure of
location used in case of skewed distributions. A window of samples sized **32 × 32** … For each unknown sample, a
measure N is set equal to the number of known samples that are classified as BG in the current window. **The
unknown samples are visited in decreasing order of N.** A 2-D median filter operates on the BG samples in the
current window."*

So: median over background-classified neighbours only, and **process the best-supported texels first**, which
grows the estimate inward from where the evidence is strongest. We have the ingredients — a band, a
carrier/plate classification, and `_geoFarConf` — and no ordering at all; our fill is simultaneous. That is a
concrete gap.

§VI adds the direction rule: Criminisi's priority, *"enhanced in two ways… First, the gradient is calculated for
the original **as well as the initialized samples**. This leads to a better isophote direction… Second, **the
filling order is steered such that the synthesis starts from the BG area towards the FG objects.**"*

Background-outward-to-foreground is S45's far-side rule and Hirschmüller's *"only from the occludee"* — now
three times, from three fields.

### 6. Depth-gated source selection — the one we have already half-built

*"All sample positions in A with depth values higher than d_center + δ are excluded from the source area… the
likelihood of selecting patches with depth values much higher than the current region to be filled is
reduced."*

This is the occluder-informed inpainting arm (R8 item 5, our `plane_object_ids` channel and dilated mask), but
imposed as a *hard exclusion on the exemplar search* rather than as a hint to a learned model. If we ever run an
exemplar fill rather than LaMa, this is the gate.

### 7. Their measured parameter sensitivities, for the record

| parameter | finding | setting |
|---|---|---|
| search area `A` | *"performance is not very sensitive to the size of the search area"* | 80×80, subsample 2 |
| patch size `L×Q` | *"No significant difference"* objectively; subjectively 9×9 ≫ 25×25 — *"FG colors have been copied into the BG area with a patch size of 25×25"* | 9×9 |
| init weight `w_Ω` | 0 → 0.2 gives **+3 dB PSNR, +0.02 SSIM**; *"Increasing w_Ω further does not yield further gains"* | 0.2 |
| k-means window | tie objectively, 32 best subjectively | 32×32 |

Only one of the four moves the objective numbers at all, and it is the one that lets the coarse estimate vote in
the patch cost — i.e. *the initialisation is what matters, not the synthesis*. For us, the initialisation is the
far-side law. That is a useful re-weighting of where effort belongs.

### 8. Temporal consistency: their central contribution, which we get for free

The background sprite accumulates BG colour and depth across frames; holes are filled from the sprite first,
synthesis only for what remains; the sprite is updated with the synthesised result. *"all approaches considered
so far render the new images frame by frame, ignoring the temporal correlation of the filled areas, and
therefore causing typical **flickering artifacts** in the virtual view."*

**Our baked plate is exactly this sprite, and it is static.** We fill once at bake time and re-render the same
plate at every pose, so the band cannot flicker from re-synthesis — which is why our temporal-step metric is
measuring *geometry* moving, not *content* being re-invented. Worth stating plainly in S54's rewrite: the
DIBR field's hardest problem in this paper is one our architecture does not have, and that is a genuine
difference in our favour, not a gap.

Their caveat applies to us though: *"If unreliable DMs are used, inappropriate image information can be falsely
copied into the sprite and propagate to subsequent frames."* Baked in once = baked in forever. Our sprite's
errors are permanent, which raises rather than lowers the bar on the bake.

### 9. Where they land

Table II, PSNR (local, defect area only) and SSIM (whole image) against MPEG VSRS 3.5 and Fehn: they win on
"Book arrival" and "Mobile" (highly structured background) on both measures; VSRS wins PSNR on two "Lovebird1"
configurations (*"the VSRS rendering is blurrier, while our results are sharper but noisier"* — the
sharpness/PSNR trade in one sentence); and they **lose** on "Newspaper" because *"all our modules rely on the DM
and the DM of 'Newspaper' is particularly unreliable."*

Sharper-but-noisier losing on PSNR, and the whole method's quality tracking depth-map quality, are both results
we have reproduced independently.

---

## 7. Criminisi, Pérez & Toyama, "Region Filling and Object Removal by Exemplar-Based Image Inpainting", IEEE TIP 13(9), 2004 [697 lines] DONE

Read in full. I asked for this because *"our band fill has no notion of what order to fill in, and this is the
canonical answer"*. That is right, and the paper is sharper than I expected about **why** order matters — sharp
enough to make a falsifiable prediction about our band.

### 1. The skeleton diagnosis — the most useful sentence in the paper for us

Fig. 20's caption, on filling a sea-and-sky hole by concentric layers:

> *"**The deformation of the horizon is caused by the fact that in the concentric-layer filling sky and sea grow
> inwards at uniform speed. Thus, the reconstructed sky–sea boundary tends to follow the _skeleton_ of the
> selected target region.**"*

That is a complete mechanism, not a description. **Any fill that advances at uniform speed from the whole rim
reconstructs interior structure along the hole's medial axis, whatever the real structure was.** The hole's
shape wins over the image's content.

**Prediction for us.** Our band is a long, thin, roughly rim-parallel region, and our far-side fill is
*simultaneous* — every texel solved at once, no ordering at all. Its medial axis runs **along** the band,
parallel to the rim. So this predicts that structure crossing the band gets bent toward the band's own
centreline, i.e. toward rim-parallel — and rim-parallel disagreement between adjacent lines is exactly what
class 1 looks like. I cannot claim the mechanisms are identical (ours extrapolates depth from a fitted plane,
theirs copies colour patches), but **the prediction is testable on data we already have**: measure, for band
texels where truth is known, whether the error's direction correlates with the local medial axis of the band.
If it does, ordering is a lever we have never pulled. Added as a Sprint 31 sub-item.

§IV, on the same figure: *"in the presence of concave target regions, the 'onion peel' filling may lead to
visible artefacts such as unrealistically **broken structures** (see the pole in fig. 11f)."*

### 2. The priority, and why it must be a product

Eq (1): `P(p) = C(p) · D(p)`, with

```
C(p) = ( Σ_{q ∈ Ψp ∩ (I−Ω)} C(q) ) / |Ψp|            confidence
D(p) = | ∇I⊥_p · n_p | / α                            data (isophote ⟂ hitting the front)
```

`C = 0` inside the hole, `1` outside, at init; frozen once a texel is filled; and after a patch is filled every
new texel inherits `C(p̂)`, so confidence decays inward.

The two terms pull opposite ways and both are needed:

- `C` alone *"approximately enforces the desirable concentric fill order"* and *"smooth[s] the contour of the
  target region by removing sharp appendices"* — i.e. degenerates to onion-peel, with the skeleton artefact.
- `D` alone gives the **overshoot** artefact, Fig. 10: *"some edges may grow indiscriminately."*
- Product: *"the 'push' due to image edges is mitigated by the confidence term"* — edges advance into the hole
  first, but only while they are still well-supported.

**We have both ingredients and use neither for ordering.** `_geoFarConf` is a confidence field (built on the
reveal scale), and the plate colour gives isophotes at the rim. What we lack is the loop: we solve the band in
one shot. Ndjiki-Nya's §V does the same thing in cheaper form (visit unknown samples in decreasing order of
known-background-neighbour count) and cites this paper for it.

### 3. The order is *necessary and sufficient* — their claim, and it bears on S51

§V: *"Comparative experiments show that **a simple selection of the fill order is necessary _and_ sufficient to
handle this task**."*

And the anti-segmentation stance, §III, which is the part that speaks to S51's failure:

> *"It must be stressed that our algorithm **does not use explicit nor implicit segmentation at any stage**. For
> instance, the gradient operator in (1) is **never thresholded** and real valued numbers are employed."*

They make this a selling point against Jia et al., whose method *"requires (i) an expensive segmentation step,
and (ii) a hard decision about what constitutes a boundary between two textures"*, and against the *"automatic
switching between 'pure texture-' and 'pure structure-mode'"* of [24].

**S51 was a labelling — a hard decision about which texels join.** It came out 0.0005 sFD from wash, the
closest arm in the study, and it made real steps 11% worse. This paper's position is that the hard decision was
never needed: a **continuous priority** does the same work without a threshold to get wrong. That is a genuinely
different reading of why S51 was inert than the one in S53, and a better one. Sprint 30's cap and Sprint 31's
gated median are both continuous; that is now a point in their favour rather than an accident.

### 4. One sentence that cuts against the gated median, and how I read it

§III-2: *"we note that **any further manipulation of the pixel values (e.g., adding noise, smoothing etc.) that
does not explicitly depend upon statistics of the source region, is more likely to degrade visual similarity
between the filled region and the source region, than to improve it.**"*

Taken flatly, that argues against PatchMatch §2.3's and Schönberger §4.4's post-filters. I do not think it
does, and the qualifier is the reason: *"that does not explicitly depend upon statistics of the source
region."* Both of those filters **are** conditioned on source statistics — the colour gate is the plate's own
colour, the confidence gate is the estimate's own support. A blind median would be what Criminisi warns against;
PatchMatch's is explicitly *weighted by eq (4)'s colour similarity*, and §2.3 leaves valid texels untouched.

Recording the tension because it is real, and because it sets a design constraint I should not violate: **the
band post-filter must be gated on the plate, never a plain blur.** Our own history agrees — S22 median-filtered
plane parameters with no data gate and failed.

### 5. Parameters and details worth keeping

- Patch 9×9 default, *"slightly larger than the largest distinguishable texture element"* — same 9×9 that
  Ndjiki-Nya's sweep independently landed on.
- Match by SSD over already-filled texels only, in **CIE Lab**: *"Euclidean distances in Lab colour space are
  more meaningful than in RGB."* Our return-path work compares in RGB.
- `n_p` from Gaussian-smoothed contour control points; `∇I_p` = *"the maximum value of the image gradient in
  Ψp ∩ I"* — a max, not a mean, so a single strong edge carries the patch.
- Source region may be *"a dilated band around the target region"* rather than the whole image (Fig. 21 uses
  this) — which is our plate-adjacent sampling, already.
- Speed: 2 s vs Harrison's 45 s on 200×200; 18 s vs 10 min on the bungee photograph.

### 6. What this paper does *not* give us

Everything here fills **colour**, guided by colour. Our hard problem is **depth** in a region with no colour
either — the colour is synthesised downstream by LaMa from the same band. The isophote data term needs an image
gradient at the fill front, and at our band's far rim the only gradient available is the plate's, which is the
*occluder's* colour on one side. Using it naïvely would propagate foreground structure into the band, which is
precisely what Hirschmüller, PatchMatch and Ndjiki-Nya all forbid ("only from the occludee").

So the transferable part is **the ordering principle and the product form of the priority**, with `D` built from
the far-side (occludee) rim only. The exemplar machinery underneath it is for the colour stage, where we already
use a learned inpainter instead.

---

## 8. Shade, Gortler, He & Szeliski, "Layered Depth Images", SIGGRAPH 1998 [619 lines] DONE

Read in full. I asked for this because *"our plate-1/plate-2 is an LDI in all but name"*. That is correct, and
the paper turns out to contain **the architecture we independently rebuilt, the sampling question our truth kit
independently answers, and a stated limitation we have independently measured.** Very little to act on; a great
deal to align with.

### 1. The primitive ladder is our architecture, from 1998

Figure 1 and §1 order image-based primitives by distance and internal depth variation:

| their primitive | our component |
|---|---|
| environment map — *"invariant to translation and simply translates as a whole on the screen based on the rotation"* | the sky layer at infinity (`_skyInf`) |
| planar sprite / image cache | — |
| **Sprite with Depth** — *"capable of displaying internal parallax but cannot deal with disocclusions"* | plate 1 |
| **Layered Depth Image** — *"deal[s] with both parallax and disocclusions"* | plate 1 + plate 2 |
| polygons | — |

Their stated reason for the environment map is exactly our reason for treating sky as a plane at infinity, and
their stated *failure* of Sprite-with-Depth ("cannot deal with disocclusions") is exactly the band. The layering
was not a novel invention on our side; it is the standard answer, and we arrived at it by the same route.

### 2. §4.1: class 2 is a connectivity decision, and here is the canonical form of it

> *"If, during the warp from the input camera to the LDI camera, two or more pixels map to the same layered
> depth pixel, **their Z values are compared. If the Z values differ by more than a preset epsilon, a new layer
> is added** to that layered depth pixel for each distinct Z value … otherwise the values are averaged resulting
> in a single depth pixel."*

That is **task #57 — "class 2 as a tear, not a ramp"** — in one sentence, from the paper that defined the
representation. Two samples either become **two layers** (a tear: they are different surfaces) or **one averaged
sample** (a ramp: same surface, noise). One threshold, `epsilon`, decides.

We currently have no such decision in the band: every class-2 real step (median jump **31** steps, 26.1% of wall
length) is drawn as rubber between rim and rim. The LDI answer is that it should have become a second layer.
§4.2 repeats the rule for the ray-traced construction: *"If the new sample is within an epsilon tolerance in
depth of an existing depth pixel, the color of the new sample is averaged … Otherwise, the color, normal, and
distance to the sample create a new depth pixel that is inserted."*

**Note the tension with Criminisi**, recorded honestly: this *is* a hard threshold, the thing Criminisi argues is
never necessary. I think both are right and they are about different stages — a *representation* must make a
discrete commitment (a texel is either one surface or two; there is no continuous middle), whereas a *fill
order* need not. S51 failed because it put a hard decision in the fill. Class 2 wants one in the representation.
That distinction is the most useful thing I have got out of putting these two papers next to each other, and it
is the argument for doing #57 as a plate-2 question rather than another labelling of the band.

Also: we have the threshold already. **The cliff tolerance in screen pixels (Sprint 26) is our `epsilon`**,
derived rather than preset, which is better than the paper's.

### 3. §4.2: the sampling question, which is our envelope — and our truth kit is their answer

> *"**What set of rays should we trace to sample the scene, to best approximate the distribution of rays from
> all possible viewpoints we are interested in?** For simplicity, we have chosen to use a **cubical region of
> empty space surrounding the LDI center to represent the region that the viewer is able to move in.** Each face
> of the viewing cube defines a 90 degree frustum."*
>
> *"Given no a priori knowledge of the geometry in the scene, we assume that every ray intersecting the cube is
> equally important. To achieve a uniform density of rays we sample the positional coordinates uniformly. A
> uniform distribution over the hemisphere of directions requires that the probability of choosing a direction is
> **proportional to the projected area** in that direction. Thus, the direction is weighted by the **cosine of
> the angle off the normal** to the cube face."*

This is the truth kit's design argument, published. We declare a viewing envelope (±45° h, ±30° v — their 90°
frustum is the same order), and we score against ground truth gathered **over that envelope** rather than at a
single pose (`env45`). What the paper adds that we do not have is the **cosine weighting**: they argue the
importance of a direction is proportional to its projected area, so grazing directions should be *down*-weighted
in the sample density. Our env45 grids weight poses by the envelope's fade, not by projected area. Worth
checking whether the two agree; if they do not, the paper's is the principled one. Small note, added to the
truth-kit backlog rather than a sprint.

### 4. The limitation they state, which is our fold problem, named in 1998

§4.2 lists the two things that go wrong as the viewpoint moves:

> *"(1) **disocclusions** as the viewpoint changes, and (2) **surfaces that grow in terms of screen space.** For
> example, when a surface is edge on to the LDI, it covers no area. Later, it may face the new viewpoint and thus
> cover some screen space."*

And the honest consequence: *"We could simply allow the rays emanating from the center of the LDI to pierce
surfaces, recording each hit along the way. **This would solve the disocclusion problem but would not
effectively sample surfaces edge on to the LDI.**"*

**Our plate 2 is built from arrival order along the ray — i.e. exactly the ray-piercing construction — so by
their analysis it solves (1) and not (2).** That is precisely what we measured: the stretched-plate work
(Sprint 17a, per-fragment fold alpha on the a165 ratio) exists because edge-on plate texels magnify into skins
at far poses, and no amount of second-layer depth fixes it. Their answer is to sample *rays*, not *texels* —
cosine-weighted over the viewing cube, 32⁴ strata × 16 rays ≈ 16 M rays per face — which we cannot do from a
photograph, since we have one view and a monocular depth map, not a scene to trace.

So this is a **structural limit of the single-view case, not a defect of our implementation**, and it is worth
saying so plainly in S54's rewrite: the fold/skin artefact is the part of the problem that the LDI literature
solves with more input, and we do not have more input.

§7 concedes it too: *"if some surface is seen at a glancing angle in the LDI's view the depth complexity for
that LDI increases, **while the spatial sampling resolution over that surface degrades.** The sampling and
aliasing issues involved in our layered depth image approach are **still not fully understood**; a formal
analysis of these issues would be helpful."* Twenty-eight years on, still the open problem, and still ours.

### 5. The splat-size formula — the principled version of our fold ratio

§5.3, the projected area of a warped pixel:

```
sqrt(size) ≈ (d1 / d2) · sqrt( cos(θ2) / cos(θ1) ) · sqrt(res2/res1) · ( tan(fov1/2) / tan(fov2/2) )
```

with `θ` the angle between the surface normal and the line of sight to each camera. The `cos(θ2)/cos(θ1)` factor
is the stretch: a texel seen edge-on from the LDI camera and face-on from the output camera blows up. Our fold
alpha uses a ratio measured from the warped positions (a165); this is the closed form of the same quantity, and
it decomposes the stretch into *surface orientation* and *distance* terms separately. If the fold alpha ever
needs a principled threshold rather than a tuned one, this is where it comes from.

Implementation detail worth stealing if performance ever matters: four splat sizes (1×1, 3×3, 5×5, 7×7), alphas
rounded to 1, ½, ¼ so blending is integer shifts, and an 11-bit lookup table (5 bits `d1` + 6 bits normal)
recomputed per frame.

### 6. Numbers, for the record

- **Average depth complexity 1.24** for the Chicken LDI built from 3 input images — *"the use of three input
  images only increases the rendering cost by 24 percent."* A useful sanity number: even with real multi-view
  input, the second layer is thin. Our plate 2's coverage being small is normal, not a failure.
- Chestnut tree: 16 M rays, 7 hours on a 250 MHz Indigo2, 1.1 M depth pixels, 4–10 fps on a 300 MHz Pentium II.
- Depth pixel packed to 8 bytes (20-bit Z + 11-bit splat index + RGBA) to fit four per 32-byte cache line —
  *"this seemingly small optimization yielded a 25 percent improvement in rendering speed."*

### 7. One idea from the Sprites-with-Depth half worth keeping

§7: *"a forward mapped **displacement map does not have to be as accurate as a forward mapped color image**. If
the displacement map is smooth, the inaccuracies in the warped displacement map result in only sub-pixel errors
in the final color pixel sample positions."*

Hence their two-pass scheme: forward-map the *depth* (cheap, tolerant), then **backward**-map the *colour* using
it (accurate, filtered). Gaps then arise only in the first pass, on the displacement map, where they are easy to
fill — *"it can handle large changes in view with only a small amount of gap filling."* Frame rates on
256×256: 30 Hz no parallax, 21 Hz crude one-pass, 16 Hz two-pass with bilinear.

We forward-map both together. Whether a backward colour fetch would reduce the band's *colour* artefacts
independently of its depth is not something this project has ever tested, and it is cheap to try. Noted, not
scheduled — the band's problem is that there is no colour to fetch, so the gain would be confined to the
stretched/fold region rather than the band proper.
