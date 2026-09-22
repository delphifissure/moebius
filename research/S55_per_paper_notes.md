# S55 — per-paper notes, the stereo/DIBR corpus read first-hand (2026-09-22)

Companion to `S54_s33_directed_search.md`, which was search-level. These notes are from reading each supplied file
beginning to end. Quotations are transcribed from the text; equation numbers are the papers' own. Where the
PDF→markdown conversion mangled equations into one-symbol-per-line, I have reassembled them and say so.

**Corpus supplied: 17 files in the first archive, 6 in the second (23 files, 22 papers).** The first archive's
Bornemann & März was truncated (abstract plus two paragraphs); the full text came in the second archive and is §21.
Daribo ×2, Gautier, Sun et al. and the SGM penalty-function review also came in the second archive. Every section
below was re-checked against its paper in a verification pass (`S55_verification.md`). Hirschmüller &
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
> or background. The median is used instead of the mean for maintaining discontinuities in cases where the
> mismatched area is at an object border."*
>
> And the rule for the ring between the two classes (verification pass, missed first time): *"For interpolation
> purposes, **mismatched pixel areas that are direct neighbors of occluded pixels are treated as occlusions**,
> because these pixels must also be extrapolated from valid background pixels."* — i.e. the uncertain ring beside
> a disocclusion takes the background rule too, which is what our rim-adjacent band texels should do.

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

Constants he states: the mean-shift radiometric bandwidth is *"set to P1, which is usually 4"* (intensity levels);
spatial bandwidth 5; intensity segments under 100 px ignored; disparity sub-segments of ≤ 12 px ignored as
hypotheses; aerial runs raise the peak-filter threshold to 300 px. All tuned per data set, none derived.

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

## 2. Scharstein, Szeliski & Zabih, "A Taxonomy and Evaluation of Dense Two-Frame Stereo Correspondence Algorithms", IEEE SMBV workshop 2001 [1014 lines] DONE

*(Verification pass: the supplied file is the 2001 workshop paper, three authors, 8 pages — not the IJCV 2002
journal version, which it cites as the tech report [64]. Section numbers below are the workshop paper's.)*

The field's framing document. Read in full. Three things matter to us; the rest is a taxonomy of a matching
problem we do not have.

### 1. Streaking again, and the same remedy, from a different lineage

§6.2, on their own implementations: *"All three global algorithms perform quite well, but **both DP and SO show
the 'streaking' characteristic for scanline-based algorithms**. The graph-cut algorithm performs best, both
quantitatively and qualitatively."*

And the mechanism, §4: *"Both DP and SO algorithms suffer from the well-known difficulty of enforcing
inter-scanline consistency, resulting in horizontal 'streaks' in the computed disparity map."*

Three papers now, three lineages, same word. This is not a coincidence of vocabulary — it is that **any method
that solves each line independently produces our class 1**, and everyone who has built one has seen it.

### 2. The sentence that sizes Sprint 31 exactly

> *"The SO algorithm solves the same optimization problem as the graph-cut algorithm described below, **except
> that vertical smoothness terms are ignored**."*

That is the whole difference between the streaking method and the best method in their table: **one term**. Not
a different model, not a data term, not a segmentation — the cross-line coupling. Table 1, bad-pixel percentages
on Tsukuba: SAD 12.87, SAD/MF 12.43 (their local baselines), **DP 9.52, SO 9.76, GC 6.46**.

**Correction (verification pass).** The first version of this note said the vertical term was "worth a third of
the error, and it is the only structural change". The table does not isolate that: it reports each algorithm's
*best run*, and Fig. 3 gives the settings — **SO λ = 100, γ = 0; GC λ = 1000, γ = 2**. So SO → GC changes the
vertical term, the intensity modulation (off → on) and the overall scale at once. What the paper supports is
the qualitative statement (SO streaks, GC does not, GC scores best); the one-third figure is an upper bound on the
vertical term's share, not its measured size.

For us: our far-side law is SO-like — each line alone, no vertical term. The cross-line coupling is the missing
structural piece; how much it is worth on its own is not answered here.

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
to the tuning of the smoothness cost, in particular to parameters λ and γ."* The first version of this note said
"Sprint 30 should sweep γ". Under rule 2 that is the wrong conclusion (S57 C1): the sensitivity is a reason to
DERIVE γ (e.g. from the image's own contrast statistics, as Szeliski et al. 2008 §4.3 does) and to sweep only as a
sensitivity check on the derived value.

### 4. What does not transfer, said plainly

Their DP charges a fixed `opt_occst` for occluded states and enforces the ordering constraint. SO drops both:
*"unlike in traditional (symmetric) DP algorithms, the ordering constraint does not need to be enforced, and no
occlusion cost parameter is necessary."* Hirschmüller drops them for the same reason (non-epipolar paths). **We
must drop them too** — our band has no second view to be occluded in. The three-state M/L/R machinery is dead
weight for us; the smoothness term is not.

### 4b. Two things missed on the first read (verification pass)

- §3.4, on quantised disparity: *"for image-based rendering, such quantized maps lead to very unappealing view
  synthesis results (**the scene appears to be made up of many thin shearing layers**)."* That is REVIEW A93's
  8-bit terrace banding, named in 2001 — the field's reason for sub-pixel disparity is our reason for 16-bit depth.
- §5, the evaluation regions: statistics are reported over the whole image **and** separately over textureless,
  occluded and depth-discontinuity regions and their complements — the split S41 Sprint 23 asked for
  (interior / exterior / whole), with the same motive: a method must not win on one region while losing another.

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
- **Colour-weighted**, with eq (4)'s bilateral weight `w(p,q) = exp(−‖I_p − I_q‖/γ)`. Same γ **and the same
  window size** as the matching step — two parameters, not one (verification pass). Both are tuned per data set:
  γ = 10 and a 35 × 35 window on Middlebury, a 71 × 71 × 3 window on 1024-wide video "to account for the high
  resolution". Under rule 2 the window must be a fraction of the frame (or derived), and γ derived.
- **Median, not mean** — the paper gives no reason; Hirschmüller's (a median maintains discontinuities) is the
  standard one and applies, so a class-2 real step inside the neighbourhood is not smeared into a ramp.

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

Our plane far rule is the slanted-window answer, already. **Correction (verification pass):** the first version
said the gain from "constant → plane" was 7.6× on Venus. The table has three arms, and most of that is sub-pixel,
not slant: integer fronto-parallel 7.57 → **sub-pixel** fronto-parallel 1.73 (4.4×) → slanted 1.00 (a further
1.7×). The slant's own contribution is ~1.7× on Venus at 0.5 px (at 1 px it is 0.25 → 0.21), and larger on Teddy's
ground plane (1 px, non-occluded: 5.52 → 2.99). Either way it is orthogonal to the streaking fix. They needed both.

### 4. What they concede about untextured regions

*"Local adaptive support weight methods are starting to outperform global methods on Middlebury … However, we
believe that this is only because the Middlebury images are ideal for local methods, i.e., **almost no
untextured regions**. Global methods still make sense, because they allow occlusion handling directly in the
matching process and can **treat large untextured regions**."* Figure 6d/6e: their local method **fails** on the
Plastic set; the global one succeeds.

Our band is a large region with no data. On their own analysis we are in the regime where the local method is
the wrong tool. (That this is where S33's class 1 lives is our inference from their global-vs-local argument, not
their statement.)

### 5. Missed on the first read (verification pass)

- **Propagation is itself directional.** Spatial propagation checks only the left and upper neighbours on even
  iterations and the right and lower on odd ones, in row-major sweeps alternating from the top-left and the
  bottom-right corners (three iterations). A plane travels along the sweep, so an unlucky sweep order can still
  leave row structure; the alternation is what averages it out.
- Their global variant (§2.4, footnote 15) failed with a *pixel-wise* data term partly because the optimiser
  (QPBO) left a large share of pixels unlabelled — a solver effect, recorded here because Szeliski et al. 2008
  (§10) makes the same point: the solver can dominate a comparison.

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

---

## 9. Shih, Su, Kopf & Huang, "3D Photography using Context-aware Layered Depth Inpainting", CVPR 2020 [781 lines] DONE

Read in full. **The closest paper in the corpus to what this project is**: single RGB-D input, monocular depth
allowed, LDI representation, novel views with parallax, rendered as a mesh by a standard engine. It contains one
ablation number that independently validates an arm we measured, one architectural criticism that lands on us,
and one gap in our pipeline I had not identified.

### 1. Explicit connectivity — task #57's representation, stated exactly

> *"An LDI is similar to a regular 4-connected image, except at every position in the pixel lattice it can hold
> any number of pixels… Unlike the original LDI work [51], **we explicitly represent the local connectivity of
> pixels: each pixel stores pointers to either zero or at most one direct neighbor in each of the four cardinal
> directions** (left, right, top, bottom). **LDI pixels are 4-connected like normal image pixels within smooth
> regions, but do not have neighbors across depth discontinuities.**"*

So class 2 is not a fill rule at all — it is **an edge deleted from the mesh graph**. The algorithm's first act
on each depth edge is literally *"we first cut the LDI pixel connections across the depth"* (Fig. 3b). Four
pointers per texel is the whole representation change.

This is a better target for #57 than "draw a tear instead of a ramp". Shade's `epsilon` test decides *whether*
two samples are one surface; this stores the answer as structure the renderer can act on, and it costs 4 bits
per texel.

### 2. The criticism of rigid layers lands on us

> *"Several recent learning-based methods also use similar multi-layer image representations. However, these
> methods use **'rigid' layer structures, in the sense that every pixel in the image has the same (fixed and
> predetermined) number of layers.** At every pixel, they store the nearest surface in the first layer, the
> second-nearest in the next layer, etc. **This is problematic, because across depth discontinuities the content
> within a layer changes abruptly**, which destroys locality in receptive fields of convolution kernels."*

**Our plate 1 / plate 2 is precisely that rigid structure**: first arrival, second arrival, two layers
everywhere, no more. Recording it honestly rather than filing it away. Two qualifications, though:

- Their stated harm is specific to *applying a CNN across the layer*. We do apply a CNN across plate 1 (LaMa),
  so the criticism does bite there; we do not for depth, where the plane law is local.
- Their alternative needs *variable* depth complexity, which their §3.3 gets by **recursion** — see §5 below.
  Shade's own measurement was 1.24 average layers, so two is rarely the binding constraint. The binding
  constraint is whether the second layer's *content* is right, not whether a third exists.

### 3. §3.2: the context region is the gap in our pipeline

> *"One important difference to our work is that **these image holes were always fully surrounded by known
> content, which constrained the synthesis.** In our case, however, the inpainting is performed on a connected
> layer of LDI pixels, and it should only be constrained by surrounding pixels that are **directly connected**
> to it. **Any other region in the LDI, for example on other foreground or background layer, is entirely
> irrelevant for this synthesis unit, and should not constrain or influence it in any way.**"*
>
> *"Our inpainting networks only considers the content in the context region and does not see any other parts of
> the LDI… this algorithm selects actual LDI pixels and **follows their connection links, so the context region
> expansion halts at silhouettes**."*

**We hand LaMa the whole plate.** The occluder's colour is in the receptive field of every band texel we ask it
to fill, and nothing stops it being copied in. Every paper in this corpus forbids exactly that — Hirschmüller
*"only from the occludee"*, PatchMatch *"occlusion occurs at the background"*, Ndjiki-Nya's background-outward
filling order, Criminisi's source region — and this one enforces it *structurally*, by walking the connectivity
graph so the context physically cannot cross the silhouette.

That is a concrete, unbuilt item, and it is cheap: we already compute the rim and the carrier classification, so
a **connectivity-limited context mask** (flood-fill from the band's far rim, halting at cliff-tolerance
discontinuities) could be passed to LaMa as the valid-context channel. New task.

Their loop, for reference: synthesis region = step one pixel off each background silhouette texel, then expand
**40** iterations; context region = expand **100** iterations following links; *"we do not step back across the
silhouette, so the synthesis region remains strictly in the occluded part of the image."*

### 4. THE ABLATION: dilation is worth more than the learned inpainter

Table 3, RealEstate10K, 130 triplets. Parenthesised figures are **in the disoccluded region only** — the number
that matters:

| method | SSIM ↑ | PSNR ↑ | LPIPS ↓ |
|---|---|---|---|
| diffusion (the dumb baseline) | 0.8661 (**0.6215**) | 25.90 (**18.78**) | 0.088 |
| learned inpaint, **no** dilation | 0.8643 (**0.5573**) | 25.56 (**17.14**) | 0.085 |
| learned inpaint, **with** 5 px dilation | 0.8666 (**0.6265**) | 25.97 (**18.98**) | 0.083 |

**Without the dilation heuristic the learned inpainter is worse than diffusion in the hole** — 0.5573 vs 0.6215
SSIM, 17.14 vs 18.78 dB, a 1.6 dB deficit — and the entire margin over diffusion comes from dilating the
synthesis region by five pixels. Their stated reason, §3.2: *"In practice, the silhouette pixels may not align
well with the actual occluding boundaries due to imperfect depth estimation."*

**This independently validates R8 item 5.** We built dilated-mask arms and measured `armD` (dilation 4) at
−1.8% temporal step and `armE` (dilation 12) at −0.6% — i.e. a real effect, and **4 better than 12**. Their
tuned value is 5 px at 1024 px long side; our plate is ~1008 px wide, so 4–5 px is the same operating point,
arrived at independently on a different metric. That is the most direct cross-validation in the whole corpus,
and it upgrades `armD` from "a small measured win" to "the published mechanism, reproduced."

It also explains *why* it works, which our measurement could not: it is not that a bigger mask gives the
inpainter more room, it is that **the depth edge is mislocated by a few pixels and the dilation buys back the
misalignment.** That predicts the optimum should scale with depth-edge localisation error, not with band width
— checkable against the 2× depth map, where edges are better localised and the optimal dilation should
therefore be *smaller*. Worth one run.

### 5. Their headline component is worth 0.01 dB, and they say so

Table 2, edge-guided depth inpainting — the paper's "core technical novelty":

| | SSIM ↑ | PSNR ↑ | LPIPS ↓ |
|---|---|---|---|
| diffusion | 0.8665 (0.6237) | 25.95 (18.91) | 0.084 |
| inpaint w/o edge | 0.8665 (0.6247) | 25.96 (18.94) | 0.084 |
| inpaint **w/ edge** | 0.8666 (0.6265) | 25.97 (18.98) | 0.083 |

*"The results show that our proposed edge-guided inpainting leads to **minor improvement in numerical
metrics**."*

0.0001 SSIM. 0.01 dB. 0.001 LPIPS. A CVPR 2020 paper's named contribution, reported honestly as negligible on
the numbers and defended on the figures (Fig. 7, T-junctions).

**This is the answer to the question asked earlier in this project** — "I'm shocked that in hardly any of the
literature their methods aren't helping." They mostly *aren't*, by these metrics, and the good papers say so.
Our string of small-or-null measured effects is not evidence that we are doing something wrong; it is what this
literature's own ablation tables look like when you read them instead of the abstracts. Table 1 is the same
story: they win LPIPS 0.0724 and PSNR 27.29 but **lose SSIM** to Stereo-Mag (0.8887 vs 0.8906).

### 6. Recursion: inpainted depth makes new edges, which make new holes

> *"In depth-complex scenarios, applying our inpainting model once is not sufficient as **we can still see the
> hole through the discontinuity created by the _inpainted_ depth edges.** We thus apply our inpainting model
> **until no further inpainted depth edges are generated.**"*

Fig. 8: none / once / twice, and twice is needed. **We run one pass.** Our band fill can perfectly well
introduce a new cliff that opens a new band at a further pose, and we have never looked for it. Cheap to check:
run the cliff detector on the *filled* plate and count texels above tolerance that were not cliffs before. If
the count is non-trivial, a second pass is indicated and it is the honest form of "variable depth complexity"
that §2's criticism was really about.

### 7. Preprocessing details worth copying

- **Depth normalisation: min/max of _disparity_ (1/depth) to 0/1.** Same convention as our law — good, no
  conversion needed to compare with their thresholds.
- **Bilateral median filter to sharpen the depth map before finding edges**: 7×7, `σ_spatial = 4.0`,
  `σ_intensity = 0.5`. Stated reason: *"discontinuities are blurred across multiple pixels, making it difficult
  to precisely localize them."* This is a *sharpening* preprocess, the opposite of Zhang & Tam, and for the
  same underlying reason our 2× depth arm won: **edge localisation is what matters**, and both blurring it away
  (Zhang & Tam) and leaving it blurred (raw monocular depth) cost you.
- Discontinuities by thresholding disparity difference, then connected components into *"linked depth edges"*,
  separated at junctions by local connectivity, then **short segments (<10 px) removed** — *"We determine the
  threshold 10 by conducting five-fold cross-validation with LPIPS on 50 samples."* That is our despeckle
  (Sprint 13) and our thin-evidence rule, with the threshold *tuned against a perceptual metric* rather than
  reasoned. Ours is derived from the reveal field, which I prefer, but it is worth knowing theirs was fitted.
- All spatial parameters tuned for **1024 px long side**, *"and should be adjusted proportionally"* — so 5 px
  dilation, 10 px minimum edge, 40/100 flood iterations all scale.

### 8. Training-data trick, if we ever train anything

*"We apply the pre-trained MegaDepth on the COCO dataset to obtain pseudo ground truth depth maps. We extract
context/synthesis regions to form a pool. We then **randomly sample and place these context-synthesis regions on
_different_ images**… We thus can obtain the ground truth content (RGB-D) from the _simulated_ occluded
region."*

No annotation, no multi-view capture: take a real hole's *shape* and paste it somewhere the answer is known.
Our truth kit does the rigorous version (exact multi-hit ray casting), but this is how to get volume if a
learned band-depth model is ever wanted. 118k COCO images, ≤3 region pairs each, 5–10 epochs.

---

## 10. Szeliski, Zabih, Scharstein, Veksler, Kolmogorov, Agarwala, Tappen & Rother, "A Comparative Study of Energy Minimization Methods for Markov Random Fields" [327 lines] DONE

Read in full. Arrived as the **ECCV 2006** version rather than the PAMI 2008 "…with Smoothness-Based Priors";
complete (ends at reference 44 and Fig. 6's caption) and the same study, so no need to re-source.

I asked for this to settle S54 §4 — *"the claim that the solver is not our bottleneck"* — noting that *"ICM is
famously the worst performer in that study, so the claim deserves the check rather than my assertion."*
**The claim survives, and the paper states it in one sentence.**

### 1. The sentence

§6: *"In light of these results, it is clear that **for the models we have considered better minimization
techniques are unlikely to produce significantly more accurate labelings.**"*

With the measured basis, §5:

> *"For all of these examples, **the best methods achieved results that are extremely close to the global
> minimum, with less than 1 percent error.** For example, on 'Tsukuba', expansion moves and TRW-S got to within
> **0.27%** of the optimum, while on 'Penguin' TRW-S was within **0.13%**, and on 'Panorama' expansion moves was
> within **0.78%**."*

and on Teddy, TRW-S *"achieves the best energy of any algorithm on any of our stereo benchmarks, **within
0.018% of the global minimum**."* On binary segmentation LBP comes *"under 0.04% error"* without ever reaching
it.

Then the visual verdict, §5: *"In terms of visual quality, **the ICM results looked noticeably worse, but the
others were difficult to distinguish on most of our benchmarks.**"*

**This is S51's result, published.** Our evidence that the solver is not the problem — λ inert across its range,
five random seeds converging to the same answer, sFD 0.0005 from wash — is the signature of an energy whose
minimum is being found and is simply not where we want it. The study says that once you are past ICM, everyone
finds essentially the same minimum, and the remaining differences are in the model. S54's §4 was right and is
now first-hand.

The caveat they attach, which I should keep: *"it is still important to compare energy minimization algorithms
using the energy they produce as a benchmark. **Creating more accurate models will not lead to better results if
good labelings under these models cannot be found.**"* Fair. But our minimisation is a per-texel closed form
over four candidates; there is no risk we are failing to find its minimum.

### 2. Our capped join cost has a canonical name and parameterisation

§2:

```
V(Δl) = min( |Δl|^k , V_max ),   k ∈ {1, 2}
```

*"a simple **clipped monomial** form… If we set V_max = 1.0, we get the **Potts model**, V(Δl) = 1 − δ(Δl),
which penalizes any pair of different labels uniformly."*

Sprint 30's cap is exactly this with **k = 1** and **V_max = the cliff tolerance in screen pixels**. Our current
S51 cost is the `k=1, V_max=∞` case — the one member of the family with no discontinuity preservation at all.
Worth using their notation in the sprint so the sweep is over a named parameter rather than an ad-hoc one.

Two consequences I had not worked out:

- **Potts is the far end of the same knob.** `V_max → 0⁺` (relative to the smallest step) makes every
  disagreement cost the same, which is "any join is a join". Sweeping `V_max` sweeps continuously from our
  current unbounded linear cost to Potts, and S51 and a pure labelling are the two endpoints of one line. That
  is a much better-shaped experiment than the one I had planned.
- **A clipped cost may not be a metric.** §6: *"The benchmarks that were most challenging for the expansion move
  algorithm ('Venus', 'Penguin') **use a V which is not a metric**."* Both use truncated L2. If we ever move
  from our closed form to graph cuts, the cap is precisely what breaks the metric condition
  `V(α,α) + V(β,γ) ≤ V(α,γ) + V(β,α)`, and terms would need truncating. Not an issue today; noted so it is not a
  surprise later.

### 3. The "Penguin" benchmark is our band, and it is the one where the solver *does* matter

§4.4, image restoration and inpainting: *"we added random noise to each pixel, and also obscured a portion of
the image… **pixels in the obscured portion have a data cost of 0 for any intensity.**"*

**A region with zero data cost is our band.** This is the only benchmark in the study with that property, and it
behaves differently from the rest:

- *"On figure 4, **the swap move algorithm has serious problems**, probably due to the fact that it considers
  all pairs of labels."*
- *"On the penguin benchmark, **TRW-S is the winner**."*
- And it is one of the two that is *"most challenging for the expansion move algorithm."*

So in the no-data-term case the spread between methods is wider than elsewhere, and the winner is different
from the stereo winner. That does not overturn §1 — TRW-S still lands within 0.13% — but it is the honest
qualification: **the "solver doesn't matter" result is measured mostly on problems with data everywhere, and our
problem is the one benchmark in the set that isn't.** If we ever do build a real energy over the band, TRW-S is
the indicated method and expansion moves are not, which is the opposite of what the stereo literature would
suggest.

### 4. A fourth form of contrast modulation, and it is astonishingly crude

§4.1, their stereo smoothness weights: *"we computed `w_pq` by comparing the intensities of p and q in the left
image, and **if this was small we set `w_pq` = 3 for 'Teddy' and `w_pq` = 2 for 'Tsukuba'**."*

A threshold and a factor of 2 or 3 — no functional form at all. Set beside the other three now in hand
(Hirschmüller's `P2′/|ΔI|`, Scharstein & Szeliski's `1/(1+γ|ΔI|)`, Schönberger's `P1(1+αe^{−|ΔI|/β})`), the
spread of "how much should colour modulate the smoothness penalty" across four papers by overlapping authors is
from *binary ×3* to *bounded exponential with two fitted parameters*. **Nobody has settled this.** It reinforces
Scharstein & Szeliski's own warning that λ and γ tuning dominates, and it means Sprint 30 should sweep rather
than adopt — and that a crude two-level version is a legitimate arm, not a strawman.

§4.3's binary segmentation uses yet another: `V_pq = exp(−β‖x_i − x_j‖²) + λ₂`, `λ = 50`, `λ₂ = 10`, with
`β = (2⟨‖x_i − x_j‖²⟩)⁻¹` — **β set from the image's own average squared intensity difference**. That is the
one self-calibrating form in the set, and it is the one to prefer if we do not want to sweep: it makes the
contrast scale adapt to the picture instead of being tuned on the troll and carried to the others. Their stated
purpose for `λ₂` is *"to remove small and isolated areas which have high contrast"* — a floor, which is our
despeckle in the energy rather than as a post-process.

### 5. Practical notes

- ICM initialised winner-take-all *"resulted in significantly better performance"* than a bad init — *"the
  results are extremely sensitive to the initial estimate, especially in high-dimensional spaces with non-convex
  energies."* Our far-side law is the WTA init; that is the right shape.
- *"there never seems to be any reason to use swap moves instead of expansion moves."*
- LBP *"performed surprisingly poorly (the only method it consistently outperformed was ICM)"*, and made gross
  errors on Photomontage — *"leaving slices of several people floating in the air."* The authors hedge that this
  may be their message schedule.
- TRW-S gives a **lower bound on the optimal energy**, which they use to normalise every plot: *"this lower
  bound can serve as a confidence measure, providing assurance that the solution obtained has near-optimal
  energy."* If we ever want to prove our band solution is not solver-limited rather than arguing it from seed
  agreement, that is the instrument.
- Energy is `E = E_d + λ E_s` throughout, 4-connected grid, and the study's whole point is that the API lets one
  energy be minimised by every method — *"almost no one in vision has ever answered questions like 'how would
  your results look if you used LBP instead of graph cuts to minimize your E?'"*

---

## 11. Jakubowska, Zięba & Spurek, "ORCA: Occlusion-Aware Refinement and Completion for Novel View Synthesis", 2026 (arXiv 2609.17450) [314 lines] DONE

Read in full. I asked one question of this paper: *"I want to know whether their size threshold is **derived or
tuned**, because ours is derived and that is the part worth defending."*

### 1. The answer: tuned. Three hardcoded numbers, no derivation.

§4.2, verbatim:

> *"A missing region is considered for generative completion only if it contains **at least 9,000 pixels**,
> occupies **at least 45% of its bounding box**, and the shorter side of the bounding box is **at least 64
> pixels**."*

No justification, no ablation, no sensitivity analysis, no statement of how the three were chosen. And the
budget is cruder still:

> *"We allow **at most two generative inpainting operations per reconstructed scene**. After this budget is
> exhausted, remaining regions are handled using the local geometry-based repair."*

So the criterion is not even purely a property of the region — after two calls the same region gets a different
treatment. That is a compute budget dressed as a decision rule.

**Our hybrid's threshold is derived** — from the reveal field, `reveal = |Z_a/(D+Z_a) − Z_b/(D+Z_b)| · |ex| ·
pxPerWorld`, converted to the cliff tolerance in screen pixels (Sprint 26), so it answers "will a viewer see an
unpainted pixel here" rather than "is this blob big". That difference is real and it is now defensible against
the one published method that arrives at the same architecture. It is the clearest win the corpus has given us.

Honest caveat: their thresholds are tuned on a task with no ground truth at all (see §4 below), so "tuned"
here does not even mean "fitted to data" — it means chosen.

### 2. But their *shape* test is something we do not have, and it points the other way from our design

> *"we select the view with the largest detected disocclusion and split its repair mask into connected
> components. **Small or elongated components are treated as local geometric gaps, while large and compact
> components are considered for generative completion.**"*

Size **and compactness**: `area/bbox ≥ 45%`. Our hybrid thresholds on reveal magnitude alone and has no notion
of a region's shape.

This matters because **our band is, by construction, long and thin.** Under their rule almost the whole of it
would be classed "elongated" and sent to local repair, never to the generative model — the opposite of our
`H_rev1` arm, which sends 27.5% of the band to generation. Two readings, and I cannot settle between them from
the paper:

- Their rule is a proxy for ours done badly: an elongated region is one where both rims are close, i.e. **small
  reveal**, so compactness is a shape-based estimate of the quantity we measure directly. On this reading their
  test agrees with ours and we do it better.
- Or shape carries information reveal does not: a compact hole has an interior far from *any* rim, where no
  extrapolation can reach, while a thin one is everywhere within reach of a rim. That is a **distance-to-rim**
  criterion, not a reveal criterion, and we do not compute it.

The second reading is testable and cheap: add the band's distance transform to the hybrid's decision and see
whether it moves the measured temporal step beyond what reveal alone achieves. Worth one arm in Sprint 29's
successor, because the two quantities genuinely differ — a wide slow ramp has large distance-to-rim and small
reveal.

### 3. The occludee rule, for the sixth time, with a percentile

> *"We first extract a **ring of valid pixels** around the repair region and **select donors from the farther
> part of the local depth distribution. Using the nearest depth at an occlusion boundary can incorrectly extend
> the foreground surface into the missing region.** Selecting farther background samples reduces this effect and
> places the added geometry behind the foreground object."*

Six papers, six lineages, same rule — Hirschmüller's *"only from the occludee"*, PatchMatch's *"select the lower
of the two"*, Ndjiki-Nya's k-means background centroid, Criminisi's source region, Shih's background silhouette,
and now this. Our S45 far-side rim filter (worth 5.1×, 0.1776 → 0.0349) is the most-independently-confirmed
thing in the project.

Their implementation is the closest to ours and gives concrete numbers worth comparing against:

| | ORCA | ours |
|---|---|---|
| donor ring | inner radius **3**, outer **28** px | rim-adjacent, 1 texel |
| minimum donors | **32** valid pixels | 1 (nearest valid rim texel) |
| background selection | **78th depth percentile** of the ring | crossing rule over 4 candidates |
| fallback | nearest-neighbour fill | thin-evidence rule |

**The 78th-percentile-over-a-ring is the same robustification Ndjiki-Nya reached by k-means over 32×32**, and
both are doing what our law does not: taking a *distribution* over a neighbourhood rather than a *value* at the
nearest texel. That is now three papers (Ndjiki-Nya, PatchMatch's weighted median, ORCA) saying the rim estimate
should be a robust statistic of a neighbourhood. It is the same conclusion Sprint 31's re-scoping reached from
the other end, and it raises my confidence in that sprint.

### 4. The evidence base is weak, and this bears on how much of the above to believe

Every headline metric is **no-reference**: MUSIQ, CLIP-IQA, and five LLaVA-IQA criteria. There is no ground
truth anywhere in the evaluation — the input is a single image and the novel views have no reference. So the
numbers measure *whether a model thinks the frame looks good*, not whether it is right.

DIV2K, 99 images (one excluded because *"VistaDream failed to produce a valid reconstruction for one
sky-dominated image"*): MUSIQ 61.60 → 68.71, CLIP-IQA 0.474 → 0.574, Quality 0.407 → 0.630.

The LLaVA-IQA columns should not be trusted. Table 2's per-scene values are saturated at 0.00 and 1.00 all over
— `steampunk` scores Edge 0.00 and Structure 0.00 for **both** methods; `car` scores Structure 0.00 and Edge
0.00 for both, and overall Quality goes **0.02 → 0.00**, i.e. ORCA is worse, on a criterion that is pinned at
the floor. A metric that returns exactly zero for both arms is not measuring anything.

The one number I do credit is **TSED** (cross-view geometric consistency, which checks correspondences against
the known camera geometry rather than asking a model): **DIV2K 0.8265 → 0.9980**, RealmDreamer 0.9864 → 1.0000.
That is a real, reference-free-but-geometric measurement and a large effect, and it is the same *kind* of thing
our temporal-step metric measures. It supports the architecture — reuse the scene where you can — without
supporting any particular threshold.

### 5. Their depth handling, which is ours

- Depth Pro for monocular depth; **inverse depth normalised between robust quantiles** `q_far`, `q_near` —
  *"reduces the influence of extreme depth predictions"*. Same normalised-disparity convention as our law, with
  the quantile clipping we do via the noise/effective-quantum work.
- Gaussians displaced **along their original camera rays**, not in z: *"Changing only the z-coordinate would
  move a Gaussian away from its original viewing ray."* Our plate texels displace along rays for the same
  reason.
- For generated regions, `d_aligned = a·d_pred + b` fitted on valid background pixels around the repair, with
  outlier rejection, then blended with the reconstructed depth near the boundary. **That is our return path's
  alignment step** (Sprint 25/S27's supplied-depth alignment on the visible front), same affine form, same
  fit-on-the-ring.
- Depth is used *only* to deform geometry before fine-tuning — *"is not used as a direct supervision signal."*

### 6. Remaining parameters, for the record

Initial Gaussians ≤30k iterations, early stop on smoothed PSNR (min improvement 0.03 dB, patience 4); fine-tune
≤20k; SD 1.5 inpainting, 30 steps, guidance 7.0, ≤512 px crop; new Gaussians covariance scale ×1.7, minimum
opacity 0.9, ≤5000 per local repair, ≤24 optimisation steps; single A40, also runs on an RTX 4060.

The covariance ×1.7 is their fold fix: *"We use **wider, overlapping Gaussians** for these local repairs to
reduce thin gaps that can remain visible after a viewpoint change."* A splat-size fudge for the same artefact
Shade's §5.3 formula describes and our fold alpha addresses — three different treatments of one problem, none
principled except Shade's.

### 7. Verdict

Architecturally they land where we did, from Gaussian splatting rather than from a baked plate: **repair from
the scene where the scene knows the answer, generate only where it cannot.** That independent arrival is worth
having. But the paper does not advance our decision rule — its criterion is three chosen constants plus a
two-call budget, evaluated with no ground truth — and the one thing it has that we lack is the *shape* test,
which is worth one arm to check and may simply be a worse proxy for the reveal field we already compute.

---

## 12. Sinha, Steedly & Szeliski, "Piecewise Planar Stereo for Image-based Rendering", ICCV 2009 [335 lines] DONE

Read in full. Tier 3, "if it is easy" — and it turns out to contain **the correct taxonomy for S33's three
classes**, which is worth more than most of Tier 1.

### 1. Crease edges vs occlusion edges: S33 class 3 and class 2, named and distinguished

§4.2:

> *"Piecewise planar depth maps can contain two types of discontinuities – **occlusion edges** and **crease
> edges**. Both plane labels **and scene depths** differ at pixels across an occlusion edge while **only the
> plane label differs** for pixels across a crease edge. A crease edge between a pair of plane labels coincides
> with the projection of the 3D intersection line of the two corresponding planes and is therefore **always a
> straight line segment**. Occlusion edges on the other hand can occur anywhere in the image."*

Set against S33's classes:

| S33 class | count | **wall length** | median jump | this paper's name |
|---|---|---|---|---|
| 1 — same surface, law disagrees | 77.2% | 38.8% | 3.3 | *spurious* — neither; an artefact |
| 2 — real step | 10.4% | 26.1% | 31 | **occlusion edge** (depth differs) |
| 3 — axis change | 12.3% | **35.1%** | 25 | **crease edge** (label differs, depth **continuous**) |

**Class 3 should have continuous depth.** At a crease two planes *meet*; the surface is C⁰ and only the gradient
breaks. Our measured median jump at class 3 is **25 steps** — so our law is opening a depth gap where the
geometry says there should be none. That is not a smoothness-penalty problem at all; it is a missing constraint.

Sinha's contribution is precisely to add it: *"This allows us to **enforce C⁰ continuity between planes that
meet**."* Mechanically, they precompute the crease line `L_ij` for every plane pair, collect the neighbouring
pixel pairs straddling it into a set `S1`, and make label changes *there* cheap.

And the second structural fact we have never used: **a crease is always straight**, because it is the projection
of a 3D line. Class 3 is 35.1% of wall length — the largest single share — and the literature says those walls
should be (a) depth-continuous and (b) straight. Both are checkable against the probe dumps we already have, and
both are new constraints. **This reopens class 3 as its own item rather than a sub-case of the join cost**, and
it is a better-founded target than anything else in the backlog.

### 2. Their smoothness term is four discrete levels keyed to geometry

`V_pq = 0` when `l_p = l_q`; otherwise, by which set the pair falls in:

| pair straddles | λ |
|---|---|
| a **crease line** (S1) | **1000** — cheapest to cross |
| a vanishing-direction-aligned line, occluder in front (S2) | 1200 |
| any other detected 2D line segment (S3) | 2000 |
| nothing (implicitly) | most expensive |

*"Suitable values for the λ's were chosen empirically."*

This is a fifth form of contrast/structure modulation, and it is **structural rather than photometric** — the
cost depends on whether a *geometric* feature runs between the two texels, not on how different their colours
are. We have geometric features available on the plate (the rim, the carrier classification, the reveal field)
that we currently do not use in the join cost at all.

### 3. The framing for Sprint 32, and it matches what we already do

§2: *"The key difference is that in our MRF, **we consider a small discrete set of plane hypotheses for each
pixel, instead of finely discretizing the disparity space**."*

Our far-side law computes **four** candidates and arbitrates. That is already the small-discrete-hypothesis-set
design; Sprint 32 is not a new architecture, it is a better arbitration over the set we have. Worth stating,
because "per-texel plane labels" sounded like a rebuild and is not.

### 4. Two perceptual claims that bear on our metrics

§1: *"During view interpolation, **humans are sensitive to the motion of high-contrast edges and straight
lines** in the scene. Our approach aims at preserving such features and minimizing parallax error, which
produces perceptible ghosting. **The lack of surface detail is rarely noticeable during viewpoint
transitions.**"*

That is the justification for measuring what we measure. Our temporal-step metric is an edge-motion proxy, and
this says edge motion is the thing — while surface fidelity, which PSNR and SSIM mostly measure, is *"rarely
noticeable"*. Another reason our aggregate-metric nulls are not damning.

§5, on cross-fading during interpolation: *"**Cross-fading in this manner is crucial to prevent the eye from
being drawn to disoccluded regions** of an image that are filled in by the other. With simple linear crossfades,
the alpha values in the rendered image would have **disturbing step discontinuities at occlusion
boundaries.**"* Their fix is binary opacities `α1, α2` so single-source pixels stay at full opacity throughout.
We have an envelope fade; whether it steps at occlusion boundaries is worth one look.

### 5. What does not transfer

Everything upstream of the MRF needs structure-from-motion over an unordered photo collection: 3D points with
covariances, reconstructed 3D line segments verified in ≥4 views, vanishing directions by mean-shift on a
sphere. From one photograph none of it exists. Runtimes 28–145 minutes; 2–3 Mpixel images; 33–127 planes per
dataset.

The one piece that might: they compute a **ground plane** by finding the up-vector orthogonal to most cameras'
side-vectors, then the plane with 95% of points above it, plus per-camera **back-planes** along the optical
axis. We already have a ground plane in the bundle meta (`ground {a,b,c}`); the back-plane idea — a far
bounding plane per view — is close to our sky-at-infinity and may be the better construction for the
*non*-sky far field.

---

## 13. Gallup, Frahm & Pollefeys, "Piecewise Planar and Non-Planar Stereo for Urban Scene Reconstruction", CVPR 2010 [414 lines] DONE

Read in full. I asked for this as *"how to decide **where** the planar assumption applies, which is our
thin-evidence rule in another guise."* It is exactly that — and it contains **a threshold-free version of our
hybrid**, which is the best single idea I have taken from Tier 3.

### 1. The non-plane label: our thin-evidence rule as a term in the energy

> *"The key difference in our approach is the addition of a **non-plane label** which represents the input
> stereo depthmap. Label likelihoods are defined as the photoconsistency of the plane, in case of a plane label,
> or of the depthmap, in case of the non-plane label. **In the spirit of model selection, the non-plane label
> incurs an additional penalty, due to the higher degrees of freedom** in the depthmap surface."*

Our thin-evidence rule is a *procedural* guard — no ramps from short runs, fall back to constant. Theirs is the
same judgement expressed as **model selection**: the richer model is always available, and always costs
`ρ_bias` extra, so it wins only where it earns its complexity. `ρ_bias = 0.5` against `ρ_max = 6`, so the
penalty is ~8% of the maximum data cost.

The honest framing of why, §3.4: *"**It may very well be that a plane fits a bush or sloping ground, at least
within the uncertainty of the stereo reconstruction.** It is in fact the appearance of these image regions that
indicate they are non-planar."* Fit is not the same as appropriateness — the thin-evidence rule's whole premise,
stated by someone else.

### 2. THE IDEA: the discard label makes size-dependence *emerge* instead of being thresholded

> *"the **discard label** indicates no reliable reconstruction could be obtained… **The discard label receives
> slightly less penalty than maximum. Thus small poorly matching regions will be labeled according to their
> surroundings due to the smoothness term, but large poorly matching regions will incur enough cost to be
> discarded.**"*

Read that mechanism carefully. Discarding a region of area `A` costs about `c·A`. *Not* discarding it costs the
mismatch plus the smoothness penalty on its perimeter, ~`λ·P`. So discard wins when `A/P` is large — **which is
exactly "large and compact"**, ORCA's hand-tuned rule (≥9000 px, ≥45% of bounding box, shorter side ≥64 px),
falling out of a two-parameter energy rather than being chosen.

**This is a better hybrid than ours.** Our reveal threshold is derived, which beats ORCA's three constants, but
it is still a threshold on a per-texel quantity, applied per texel. Gallup's construction says: give "hand this
to the generative inpainter" a **per-texel cost**, let the smoothness term pay for the boundary, and the
decision about *which regions* go to generation — including their size and shape — emerges from the
minimisation. No size threshold, no compactness threshold, and the reveal field can set the per-texel cost so
the derivation we already have is retained rather than replaced.

That is a concrete redesign of the hybrid and it subsumes both the §2 concern I raised about ORCA (shape vs
reveal) and Sprint 29's open hybrid decision. New task.

### 3. Their smoothness has a floor as well as a cap — and the floor is anti-class-1

```
E_smooth ∝ λ_smooth · f( clamp(d, d_min, d_max) ) · g(image gradient)
```

> *"where **d is the distance between the 3D neighboring points according to their labels**, and g is the image
> gradient magnitude between the two neighbors. **`d_min` incurs a minimum penalty in order to prevent spurious
> transitions between planes that are close in 3D.** `d_max` makes the penalty robust to discontinuities."*
> `λ_smooth = 5`, `d_min = 2`, `d_max = 0.2 m`, `γ = 10`.

`d_max` is Sprint 30's cap, confirmed for the fourth time. **`d_min` is new and it is aimed straight at class
1.**

Our S51 join cost is `revealPx`, which **goes to zero when the two candidates agree**. Two planes that predict
nearly the same depth can therefore be swapped between freely, texel by texel, at no cost — and adjacent lines
choosing differently at no cost is the *definition* of class 1 (77.2% of cliffs, median jump 3.3 steps, i.e.
tiny disagreements). Gallup names this failure mode exactly — *"spurious transitions between planes that are
close in 3D"* — and fixes it with a floor.

**So Sprint 30 should clamp both ends, not one.** `V = clamp(reveal_px, floor, cap)`. The cap stops a real step
being over-penalised (class 2); the floor stops a near-tie being under-penalised (class 1). That the same
two-sided clamp answers both of our large classes, from one published formula, is the tidiest result of this
reading. Sprint 30's description updated.

### 4. The plane at infinity is a label

*"We add to each set **the plane at infinity, denoted π∞**, which is useful for labeling sky or distant surfaces
which are not reconstructed by stereo."* Our `_skyInf` layer, as one more candidate in the hypothesis set rather
than a special-cased stage. If Sprint 32 ever does become a labelling, sky should be a label in it.

### 5. RANSAC for *locally* fit planes — the recipe, if we want more candidates

*"Typically one seeks to find a single model to fit all the data, but **our objective is to find multiple
locally fit models**."* Three things make it work:

- **Sampling**: first point uniform over the image; the other two from normals centred on it with `σ = 8 px`.
- **Scoring**: only points within `M = 100 px` of the first sample; MLESAC likelihood, not inlier count.
- **Contiguity**: inliers restricted to points *connected to the initial sample through the image graph*, then
  refit and repeat.

Then remove the inliers and repeat, to `N = 20` planes. Our far-side law generates candidates from runs along
two axes; this is how to generate them from a 2-D neighbourhood, and the contiguity constraint is our
persistent-departure segmentation (Sprint 16) in another form.

### 6. Parameter sensitivity — a useful counterweight to Scharstein & Szeliski

§4: *"For all our experiments we have used the same parameters… **Parameters were chosen empirically and without
much difficulty. The fact that we used the same set of parameters for several diverse datasets indicates that
the parameters are not overly sensitive.**"*

Scharstein & Szeliski warned that λ and γ tuning dominates. Gallup reports the opposite on a harder, more varied
dataset. The difference is probably that Gallup's costs are **clamped at both ends and truncated**
(`ρ_max = 6`), which bounds how much any one parameter can matter. Another argument for the two-sided clamp:
it should make Sprint 30 *less* tuning-sensitive, not more.

Accuracy of the final labelling against 22,700 hand-labelled segments in 28 images: **94.7% of planar and 97.2%
of non-planar segments correct.**

### 7. The appearance classifier — noted, not scheduled

Colour and texture features per **16×16 grid cell** (they tried superpixels and *"in the end we preferred the
regular grid… it ensures segments of a regular size and density"*): mean RGB, mean HSV, 5-bin hue histogram,
and from the edge-orientation histogram its entropy, maximum and number of modes — *"man-made objects tend to
have only a few consistent edge orientations, while natural objects have a less structured appearance."* kNN
over ~5000 hand-labelled segments, `λ_class = 2`, and crucially *"no hard decision is made until the final plane
labeling"* — the classifier contributes a **probability to the data term**, not a mask.

We have SAM 2.1 running in the browser and an object map. Asking "should this surface be planar?" from
appearance is available to us in principle, and the soft-evidence-into-the-energy pattern is the right one. But
it needs labelled training data we do not have, and the corpus has given us several cheaper things first.
Recorded, not scheduled.

### 8. Metrication, turned into a feature

*"One limitation of graph-cuts, and the discrete MRF in general, is that of **metrication**, which follows a
manhattan distance, not a euclidean one. This leads to **stair-case** and other artifacts. However, we use this
to our advantage… rectify [the image] so that the horizontal and vertical vanishing points correspond to the x
and y axes. Then the Manhattan distance metrication actually helps to enforce that label boundaries follow
vertical and horizontal lines."*

Worth knowing that a 4-connected grid MRF has an inherent axis bias that produces staircases. **We are on a
4-connected texel grid and our class 3 is literally "axis change".** Whether any part of class 3 is metrication
artefact rather than real geometry is a question I cannot answer from here, but it is now a question — and it
argues for checking class 3 against Sinha's straightness prediction before building anything for it.

---

# Part II — the second archive (2026-09-22, six further papers)

The four outstanding items all arrived, plus two extras. Nothing from the original 20 is missing now:
**#10 Daribo** (both the T-BC 2011 and MMSP 2010 versions), **#16 Bornemann** complete (3456 lines, replacing
the 26-line truncation), **#17 Sun et al.**, and **#19** — which turns out to be **Banz, Pirsch & Blume,
"Evaluation of Penalty Functions for Semi-Global Matching Cost Aggregation", ISPRS 2012**, the citation I could
not pin down. Bonus: **Gautier, Le Meur & Guillemot, "Depth-Based Image Completion for View Synthesis",
3DTV 2011**.

---

## 14. Banz, Pirsch & Blume, "Evaluation of Penalty Functions for Semi-Global Matching Cost Aggregation", ISPRS XXXIX-B3, 2012 [814 lines] DONE

Read in full. **This is the paper Sprint 30 needed and the reason it was worth chasing #19.** It is a systematic
sweep of exactly the question the other five papers each answered differently — *what shape should the
discontinuity penalty have, and how much does it matter* — and it changes my recommendation.

### 1. The four candidate forms, in their notation

> *"(a) empirically determined constant value: `P2,c = const.`
> (b) **negatively proportional** to the absolute luminous intensity gradient of the currently processed pixels
> along the path: **`P2,l = −α·|I(p) − I(p−r)| + γ`**
> (c) **inversely proportional** to the absolute intensity gradient. **This follows the original proposal from
> SGM**: `P2,i = α/(|I(p) − I(p−r)| + β) + γ`
> (d) negatively proportional to the **variance** of the luminous intensity in a local window:
> `P2,v = −α·Var(A(p)) + γ`"*

So the corpus's five forms reduce to three shapes — constant, linear ramp, reciprocal — plus a variance variant,
and this paper measures all of them against each other. Nobody else in the corpus does.

### 2. Result: the reciprocal buys nothing over a straight line

Table 1, census transform, error at 1 px in non-occluded areas, each function optimally parametrised:

| penalty | Cones | Teddy | Venus | Tsukuba |
|---|---|---|---|---|
| `P2,c` constant | 5.38% | 10.40% | 2.53% | 8.35% |
| **`P2,l` linear** | **5.23%** | **9.03%** | **1.92%** | **7.45%** |
| `P2,i` reciprocal (SGM's own) | 5.43% | 9.30% | 2.06% | 7.55% |
| `P2,v` variance | 5.28% | 10.79% | 2.55% | 8.54% |

And the conclusion, stated flatly:

> *"**Using inversely proportional penalty functions, as originally proposed with SGM, does not result in any
> performance improvement compared to linear dependencies**, which is of interest for computationally limited
> implementations."*

Abstract: the two best are *"equally with 6.05% and 5.91% average error"*.

**This changes Sprint 30's recommendation.** After Schönberger I wrote that the bounded exponential
`P1(1+αe^{−|ΔI|/β})` was the form to implement. On this evidence it is over-engineered: a **negatively linear
ramp with a floor** performs identically to the reciprocal on four images and two cost functions, has one fewer
parameter (they note (b) *"does not require a parameter β… This is implicitly done by adjusting γ"*), and is
trivially cheap. Sprint 30 should use `V = clamp(γ − α·|ΔI|, floor, cap)`.

**One qualification, and it is the one that matters most to us.** §3.1, on the visual comparison behind
Table 1: *"**Using `P2,i` the small structures in Cones are retained**, otherwise there is no significant
difference between `P2,l` and `P2,i`."*

The reciprocal's only measured advantage is on **thin structures** — and thin structures are our worst
documented failure. S5's poles (0.5–3 px wide) score **P 0.489, R 0.514**: half the hidden pixels missed, the
one limitation recorded in S18 without a fix. Figure 6 shows why the two forms differ there: plotted together
over `ΔI ∈ [0,100]` they are *"obvious[ly] similar"* in shape, but the reciprocal's `α/(|ΔI|+β)` falls steeply
in the first few grey levels where the linear ramp is still near `γ`, so at a thin structure's weak, narrow
colour edge the reciprocal has already dropped the penalty and the linear form has not.

So: **sweep both**, with the linear as the default and the reciprocal as the arm to check specifically against
the pole scenes. Also note the rank-transform rows, where *"in opposite to census, `P2,l` always outperforms
`P2,i`; in 3 cases quite significantly"* — which form wins depends on the matching cost, and since we have no
matching cost at all, neither result transfers cleanly. The linear default rests on parsimony and the
census-transform tie, not on a measurement in our regime.

The variance form fails, and the stated reason matters to us:

> *"This could be due to the fact that **`P2,v` does not calculate penalties along the currently processed path
> but from the local window, giving the same penalty value for all path directions.**"*

**Directional, not isotropic.** The colour difference must be measured *between the two texels being joined*,
along the join, not as a neighbourhood statistic. That is the natural thing for us anyway — our join cost is
already defined on a texel pair — but it is worth knowing the isotropic alternative was tried and lost.

### 3. The clipping: floor explicit, cap implicit — and why ours needs both

> *"In all cases it has to be ensured that `P2 ≥ P1`. Therefore, **a lower bound is introduced `P2,min` to which
> the values are clipped. An upper bound is not required** because penalty higher than `C_max + P1` cause that
> value never to be taken in the outer min-term in Eq. (5)."*

This is a correction to what I wrote in the Gallup note, where I said "Sprint 30 should clamp both ends" as
though both needed coding. In **SGM** only the floor needs coding: the recursion takes a `min` over the cost
volume, so once `P2` exceeds `C_max + P1` the branch is never selected and the cap is structural.

**Our construction has no such min.** The join cost enters our energy directly, not as one branch of a minimum
over a cost volume, so nothing bounds it above. So: SGM gets its cap free and ours does not, and we must clamp
both ends explicitly. The conclusion in the Gallup note stands; the reasoning needed this correction. Four
papers now agree the cap exists (Hirschmüller's "constant penalty for all larger changes", Gallup's `d_max`,
Scharstein's `V_max`, Banz's implicit bound) and two that the floor matters (Gallup's `d_min`, Banz's
`P2,min`).

### 4. The strongest result: adaptivity barely matters on clean images and matters enormously on noisy ones

Table 2, Cones under degradation, census, optimally parametrised in each case:

| penalty | baseline | **AWGN (12 dB)** | salt & pepper 14% | shadow | gamma |
|---|---|---|---|---|---|
| `P2,c` constant | 5.38% | **26.35%** | 7.63% | 7.86% | 5.41% |
| `P2,l` linear | 5.23% | **18.91%** | 8.27% | 7.27% | 5.27% |
| `P2,i` reciprocal | 5.43% | **18.94%** | 7.40% | 7.26% | 5.30% |
| `P2,v` variance | 5.28% | **30.70%** | 8.40% | 8.16% | 5.45% |

On clean Cones the spread between constant and best adaptive is **0.15 percentage points**. Under Gaussian
noise it is **7.4 points**, and the constant penalty nearly quintuples its error. Their conclusion:

> *"While for highly structured images taken under near ideal conditions constant penalty functions perform
> well, **they tend to become overfitted to the particular imaging conditions and performance is not stable over
> different conditions**… **adaptive penalty terms [are] mandatory for robust disparity estimation.**"*

**This is the argument that Sprint 30's contrast term is worth building at all.** Our input is a monocular depth
map from a photograph — we built a whole per-tile noise estimator and effective-quantum machinery (Sprint 14)
because the noise is real and spatially varying. Middlebury-clean is not our regime; the degraded rows are. So
the expected gain from the adaptive term is the 7-point column, not the 0.15-point one.

### 5. Tune on the hardest picture, not the cleanest — a direct instruction for the sweep

Their parameter transfer, stated with numbers. Best `P2,l` configuration on clean Cones:
`{P1=11, P2,min=17, γ=35, α=0.5}` → 5.23%. Under AWGN: `{P1=20, P2,min=24, γ=70, α=0.5}`. Under salt-and-pepper:
`{P1=14, P2,min=24, γ=40, α=0.5}`.

Note `α = 0.5` throughout — the *slope* is stable and only the offsets move. And:

> *"comparing good configurations to configurations from the non-degenerated images shows that now **higher
> dynamic range and higher penalties are chosen**… **Since parametrization using difficult images results in
> more robust parameter sets, real world systems should [be] parametrized under these conditions.**"*

Confirmed on real imagery without ground truth: *"Generally, **better results were obtained when using the
configurations from the degenerated images**."*

**Actionable, and it changes how I would have run the sweep.** I would have tuned on the troll, which is our
cleanest and best-characterised case. This says: tune on the noisiest of the seven pictures, accept a small loss
on the clean ones, and the result will transfer. We can even pick the target objectively — the per-tile σ from
Sprint 14 ranks our pictures by noise already.

### 6. This settles the tuning-sensitivity disagreement in the corpus

Scharstein & Szeliski warned that *"the algorithms are currently fairly sensitive to the tuning of the smoothness
cost, in particular to parameters λ and γ."* Gallup reported the opposite — same parameters across diverse
datasets, *"not overly sensitive."* Banz explains both:

> *"Setting `P2` constant performs well if carefully adjusted to the particular image but **quality degrades
> quickly as these values are changed**… All [adaptive] functions are insensitive to a certain degree of
> non-optimal parametrization."*

and on transfer between images:

> *"**performance of a particular configuration coincides across all images.** Further, the best configuration
> for one image is usually found for the other images when allowing a minimal **0.5 percentage point** error
> margin."*

**Constant penalties are brittle; adaptive penalties transfer.** Scharstein & Szeliski's DP/SO used a fixed λ
scaled by `ρ_I`; Gallup's was clamped at both ends and truncated. The disagreement was about which regime each
was in, and the adaptive-plus-clamped regime — which is what Sprint 30 will be — is the robust one. That is a
second reason to expect the sweep to be well-behaved.

### 7. Sprint 30, as the reading now leaves it

```
V(p,q) = clamp( γ − α·|I(p) − I(q)| ,  floor ,  cap )
```

- **linear** by default, not exponential — Banz Table 1, equal performance to the reciprocal, fewer parameters —
  but **carry the reciprocal as a second arm and judge it on the pole scenes**, where it is the only form Banz
  found to retain small structures (§3.1), and where S5 scores P 0.489
- **|ΔI| measured between the two joined texels**, directionally, not as a local variance — Banz §3.1
- **floor** — against class 1's near-ties (Gallup's `d_min`: *"prevent spurious transitions between planes that
  are close in 3D"*; Banz's `P2,min`)
- **cap** — against class 2's real steps (Hirschmüller's flat large-change penalty), explicit for us because our
  energy has no min-over-cost-volume to impose it structurally
- **sweep α, γ, floor, cap on the noisiest picture**, not the troll — Banz §3.2
- expected effect small on clean input, large on noisy — and our input is noisy

Also worth recording: they apply **no post-processing at all** — *"no post-processing steps, e.g. hole-filling
or interpolation, are performed"* — and evaluate only non-occluded pixels, *"Otherwise, the results would be
biased by the quality of the hole interpolation algorithm."* So these numbers isolate the penalty's effect on
matching, with our problem (the holes) deliberately excluded. The transfer to our band is by analogy of the
energy, not of the measurement, and I should not overstate it.

---

## 15–17. The Criminisi → Oh → Daribo → Gautier lineage: what DIBR actually settled on

Read in full: **Daribo & Pesquet-Popescu, "Depth-aided image inpainting for Novel View Synthesis", MMSP 2010**
[194 lines]; **Daribo & Saito, "A Novel Inpainting-Based Layered Depth Video for 3DTV", IEEE T-BC 57(2), 2011**
[246 lines]; **Gautier, Le Meur & Guillemot, "Depth-Based Image Completion for View Synthesis", 3DTV 2011**
[130 lines].

The two Daribo papers share one method — the 2011 journal version applies the 2010 method to residual-layer
generation for LDV coding and adds a comparison against Oh — so I treat them together. Gautier is the direct
successor, cites both, and thanks Daribo for the source code. **Together with Ndjiki-Nya these four papers are
the answer to the question S54 never asked: what did the DIBR field settle on.**

### 1. The lineage, and its single shared conclusion

Every paper in this chain starts from Criminisi and adds *one* thing: depth, used to keep the fill in the
background. They differ only in how forcefully.

| | how the occludee rule is enforced |
|---|---|
| Criminisi 2004 | not at all — *"makes no distinction between the two"* (Daribo's words) |
| Oh 2009 | **replace** the foreground boundary with the background one copied from the opposite side, then inpaint |
| Daribo 2010/11 | a third multiplicative priority term `L(p)`, plus depth in the patch distance |
| Gautier 2011 | **zero priority** on the occluder side, depth weighted ×3 in the match, 3-D structure tensor |

So the answer is: **DIBR settled on exemplar-based inpainting with the fill forced to come from the background,
and it converged on that within about two years.** Not pre-smoothing (Ndjiki-Nya §I records that branch as
known-bad), not LDI (rejected on bandwidth), not diffusion. That is now the **seventh and eighth** independent
statement of the rule behind our S45 far-side rim filter.

### 2. Daribo's `L(p)`: the depth-variance priority, and why I think the stated justification is wrong

Priority becomes a product of **three** terms, `P(p) = C(p)·D(p)·L(p)`, with

```
L(p) = |Z_p| / ( |Z_p| + Σ_{q ∈ Z_p ∩ Φ} ( Z_p(q) − mean(Z_p) )² )
```

— the **inverse variance of the depth patch**. Their claim: *"we give more priority to patch overlaying at the
same depth level, **which naturally favors background pixels over foreground ones**."*

**The second half of that does not follow.** Low depth variance selects patches that are *depth-homogeneous*. A
patch lying wholly in the foreground is just as homogeneous as one lying wholly in the background; both get high
priority. What `L(p)` actually suppresses is patches that **straddle** the foreground/background boundary. That
is useful — it defers the ambiguous patches until their neighbours are resolved — but it is not a background
preference, and the paper asserts that it is, twice, in both versions.

Gautier apparently agrees, because his fix is to zero the foreground side outright rather than rely on variance.
Worth recording as an instance of a plausible-sounding surrogate standing in for the property actually wanted —
the same failure mode as ORCA's compactness test standing in for reveal.

Patch matching is the sound part: `Ψ_q̂ = argmin { d(Ψ_p̂,Ψ_q) + β·d(Z_p̂,Z_q) }` — depth distance added to the
colour SSD, *"which enables control [of] the importance given to the depth distance minimization."*

### 3. Daribo's depth inpainting: the assumption this whole project exists to disprove

> *"Due to its smooth nature, **depth disocclusions can be straightforwardly inpainted through isotropic
> diffusion, since the assumption of smoothness inside disoccluded regions is verified.**… **The texture-less
> nature of the depth map enables an efficient hole-filling.**"*

They fill the band's depth with Navier–Stokes diffusion (Bertalmío), in one line, as a preliminary, and spend
the paper on colour.

**This is the clearest statement in the corpus of the assumption our results contradict.** S33 measures what
diffusing depth into the band produces: class 2, a real step (median jump **31**, 26.1% of wall length) drawn as
a smooth ramp. Smoothness inside the disoccluded region is *not* verified — it is verified only where the
disocclusion is small enough that the wrong answer is invisible.

And that is exactly the difference in regime. Their baseline is ~65 mm between adjacent MVD cameras; the "large
baseline" case they make a point of is **twice** that. Our envelope is ±45° horizontal and ±30° vertical. At a
few pixels of reveal, diffusion is fine and the hard part is colour texture. At ours, the depth is the hard part
and diffusion is the artefact.

**So the DIBR lineage treats depth completion as the easy preliminary and colour as the problem; we have found
the reverse.** That is not a disagreement about method — it is the same inversion S54 §1 identified between our
regime and stereo's, showing up again, and it explains why so little of this literature has transferred. It
belongs in S54's rewrite as the headline reconciliation.

Daribo does state the condition that makes our case hard, in the 2011 version: *"**only one reference view is
available** (i.e., the central view), leading to **large disocclusions, in which conventional inpainting methods
tend to be ineffective**."* Most related work, he notes, warps two reference views so *"fewer disocclusions were
revealed, and the disoccluded regions were smaller."* One view, large holes — that is us, and the person who
built the method says conventional inpainting is ineffective there.

### 4. Gautier's three additions, all of which we could use

**(a) The structure tensor instead of the gradient.** Criminisi's `D(p)` uses `∇I⊥·n`, a single gradient
(and, per his §III, the *maximum* over the patch). Gautier replaces it with the Di Zenzo matrix
`J = Σ_{l=R,G,B} ∇I_l ∇I_l^T`, Gaussian-smoothed to `J_σ`, and

```
D(p) = α + (1 − α)·exp( −C / (λ1 − λ2)² )
```

> *"**Flat regions (when λ1 ≈ λ2) do not favor any direction, it is isotropic, while with strong edges
> (λ1 ≫ λ2) the propagation begins along the isophote.**"*

A proper measure of *how oriented* the local structure is, and colour-channel-coherent, which a per-channel
gradient is not.

**(b) The 3-D tensor — depth as a fourth channel.**

```
J = Σ_{l = R,G,B,Z} ∇I_l ∇I_l^T
```

> *"The 3D tensor allows the diffusion of structure not only along color but also along depth information.
> **It is critical to jointly favor color structure as well as geometric structure.**"*

This is the cleanest formulation in the corpus of something we do piecemeal: our colour–depth edge alignment
(`return_align.py`) checks agreement *after the fact*, and S51's join cost uses depth alone. A structure tensor
over (R,G,B,Z) makes "the colour edge and the depth edge point the same way" a single quantity, computed once,
usable as a weight anywhere. It is also the principled version of the contrast modulation that Banz measures —
instead of `|ΔI|` along the join, the tensor gives the *orientation and coherence* of the joint colour-and-depth
structure.

**(c) One-side-only priority — the occludee rule at its strongest.**

> *"for a camera moving to the right, the disocclusion holes will appear to the right of foreground objects…
> We then want to prevent structure propagation from foreground by supporting the directional background
> propagation… **The patch priority is calculated along this border, the rest of the top, bottom and left
> patches being set to zero.**"*

Not a weight, not a percentile, not a variance surrogate — **zero**, on the occluder side, chosen by the sign of
the camera motion. Eight papers now, and this is the most absolute form.

For us the twist is that **our camera moves in both directions**, over ±45° horizontal *and* ±30° vertical. So
there is no single "right side" — the occluder side of a given rim depends on the pose, and the bake is one
artefact serving the whole envelope. Our far-side law resolves this per texel from the geometry rather than per
image from the motion sign, which is the correct generalisation and one of the few places our construction is
*more* general than the literature's rather than less. Worth saying so in S54's rewrite.

**(d) K-nearest combination, and the first honest statement of its cost.** Depth weighted `α_Z = 3` against
`α_RGB = 1` in the SSD, then *"a **combination of the best candidates** to fill in the target patch shows more
robustness than just duplicating one. We use a weighted combination of the K-best patches depending on their
exponential SSD distances"*, `K = 5`, citing Wexler–Shechtman–Irani.

This is the **fifth** "robust statistic over a neighbourhood rather than a single nearest value" in the corpus —
after PatchMatch's weighted median, Ndjiki-Nya's k-means centroid, Schönberger's gated median, and ORCA's 78th
percentile. That is now overwhelming, and Sprint 31's re-scoping rests on it.

But Gautier is the only one to name the price: *"**The counterpart of the patch combination is the smoothing
effect** appearing on the bottom part of this area. By taking different numbers of patches for combination, it
is possible to limit this effect."*

**K is a sharpness/robustness dial, and it must be swept, not assumed.** That is the direct counterweight to
Criminisi's warning against post-hoc smoothing, and it sets Sprint 31's experiment: sweep the gated median's
neighbourhood size and watch the band's sharpness alongside the temporal step, because the robustification buys
stability with blur.

### 5. Gautier's anti-ghosting is Shih's dilation, with the mechanism stated

> *"we suppress certain ghosting effects present on the borders of disoccluded area in the background: the
> **background ghosting**. Indeed, as we start the filling process by searching from the border, it is of
> importance to **delete ghostings containing inadequate foreground color values**. A **Canny edge detection on
> the original depth map, followed by a deletion of color pixels located behind that dilated border**
> successfully removes this ghosting."*

Detect the depth edge, dilate it, **delete** what lies behind it before filling. Shih's 5-px synthesis-region
dilation does the same job by a different route (grow the hole rather than delete the fringe), and Shih's
Table 3 shows it is worth more than his learned inpainter. Ndjiki-Nya's blob removal is a third route to the
same end.

**Three independent mechanisms for one problem — mislocated foreground colour at the rim — and it is our
silhouette fringe (S17) and our `armD` dilation arm.** The convergence is strong enough that this should be
treated as settled practice rather than a tuning choice: *something* must remove the occluder's colour from the
rim before the fill, and the only open question is which of the three costs least.

### 6. Gautier's criticism of Oh names a failure mode we should check for

> *"[Oh's] algorithm relies on an **assumption of connexity between disoccluded and foreground regions**, which
> may not be verified for high camera baseline configurations. Indeed, **upon a certain angle and depth, the
> foreground object does not border the disoccluded part anymore.**"*

At a large enough angle, the hole **separates from its occluder**. Any rule phrased as "the near rim is the
occluder, so take the far one" quietly assumes they are still adjacent.

**Our envelope is ±45°, which is the large-angle case by any standard in this corpus.** Whether our band ever
detaches from the object that cast it is a question we have never asked, and it is answerable from the probe
dumps: for each band component, is the near rim still in contact with the occluding surface at the envelope
edge? If a non-trivial fraction detaches, the rim classification has a blind spot at exactly the poses that
matter most. Added as a check, not a sprint — it is a measurement on data we hold.

### 7. Evidence, and another admission about metrics

Daribo reports PSNR **computed only on the disoccluded areas** — *"In order not to introduce in the objective
PSNR measurement the warping-induced distortion, and so to consider only the inpainting-induced distortion"* —
which is the right methodology and the same one Shih uses for his parenthesised columns. Ballet sits around
38–43 dB, Breakdancers 48–54 dB, with the proposed method above Criminisi throughout by a visually small margin
on the plotted curves.

Gautier reports **no numbers at all**, and says why: *"The results can indeed be essentially address[ed]
visually, as argued by [Kawai et al.]."*

That is the fourth paper in this corpus — after Ndjiki-Nya's k-means tie, Shih's 0.0001 SSIM, and ORCA's
saturated no-reference scores — to concede that the measurements do not capture what the method is for. It is
not an excuse for our own null results, but it is the context for them, and it is why the sheets have earned
their place beside the metrics in this project.

---

## 18. Sun, Yuan, Jia & Shum, "Image Completion with Structure Propagation", SIGGRAPH 2005 [390 lines] DONE

Read in full. I requested it because *"our rim law already knows where the structure is, which makes the manual
half free."* That is confirmed — and the paper turns out to contain **the cleanest statement in the corpus of
what it would actually cost to go from per-line to cross-line**, which is the class-1 question.

### 1. DP and BP are the same update — one on a chain, one on a graph

§3.3. Dynamic programming, written as a message:

```
M_{i−1,i} = min_{x_{i−1}} { E1(x_{i−1}) + E2(x_{i−1}, x_i) + M_{i−2,i−1} }        (9)
```

Belief propagation:

```
M^t_ij = min_{x_i} { E1(x_i) + E2(x_i, x_j) + Σ_{k≠j, k∈N(i)} M^{t−1}_ki }        (5)
```

> *"**Equation (9) and the message update equation (5) in belief propagation are in fact equivalent when the
> graph is a single chain.** Therefore, in a single chain, the cumulative minimal cost is an alternative
> interpretation of the message in belief propagation. **Belief propagation can be viewed as a 'parallel'
> generalization of dynamic programming on a general graph.**"*

**This is the third and most explicit version of the same point.** Scharstein & Szeliski: SO solves the same
problem as graph cuts *"except that vertical smoothness terms are ignored."* Hirschmüller: streaking comes from
*"very strong constraints in one direction… combined with none or much weaker constraints in the other."* Sun:
the two algorithms are **the same recursion**, and the only difference is whether the neighbour set `N(i)` is
`{i−1, i+1}` or the full graph.

So the class-1 fix is not a different method. It is our existing per-line recursion with cross-line edges added
to `N(i)` and the messages summed over all neighbours instead of one. That is a much smaller change than
"implement belief propagation" sounds, and it is the correct way to frame whatever eventually replaces the
per-line law.

**And the cost is bounded and known.** §3.2: standard BP on a loop-free graph is `O(2T·L·N²)`, but *"each
message can be updated only when all necessary neighboring messages are converged"*, so attaching a binary
converged-flag to each message reduces it to **`O(2LN²)`, independent of the number of intersection nodes**.
*"For a typical value of N = 10³, the running time of belief propagation is about a few seconds, while dynamic
programming might take hours."* (DP on a graph with `K` intersections is `O(LN^{2+K})` — it explodes; BP does
not.)

One caution, recorded because the corpus disagrees with itself here: Sun reports loopy BP working well —
*"belief propagation is often a very good approximation even for graphs with thousands of loops"* — while the
Szeliski MRF study (note 10) found LBP *"performed surprisingly poorly (the only method it consistently
outperformed was ICM)"* and producing gross errors on Photomontage. Szeliski hedges that this may be their
message schedule. Sun's graphs are sparse and nearly loop-free, Szeliski's are dense 4-connected grids. **Ours
would be a dense grid**, which is Szeliski's regime, not Sun's. So take the *equivalence* from Sun and the
*performance expectation* from Szeliski: if we ever build this, TRW-S rather than LBP.

### 2. Structure first, texture second — which is already our architecture

> *"Note that we **completely separate structure propagation and texture propagation and perform structure
> propagation first**. Compared with previous methods, this completion process largely reduce the breaking of
> salient structures which human eyes are sensitive to."*

Their second stated observation: *"There exists a synthesis ordering for image completion: **the regions with
salient structures should be completed before filling in other regions.**"*

We fill **depth** (structure) with the far-side law, then hand the band to LaMa for **colour** (texture). Shih
does the same with three sub-networks (edge → colour, depth). Three independent architectures, same ordering.
This is one of the places our pipeline is already aligned with settled practice, and it is worth saying so in
S54's rewrite rather than only cataloguing gaps.

### 3. Partitioned texture propagation — task #59, from a fourth direction

§4.1: *"applying texture synthesis directly may produce poor results, as the synthesis process may **sample
irrelevant texture information from the entire known region**."*

Their fix: the user curves partition both known and unknown regions into matched subregions, and *"**each
unknown subregion is completed only using the samples in its corresponding known subregion**."*

Four mechanisms for one principle now:

| paper | how the source is restricted |
|---|---|
| Criminisi 2004 | source region = a dilated band around the hole |
| Sun 2005 | partition by user curves; each subregion draws only from its pair |
| Shih 2020 | context region follows LDI connectivity links, halts at silhouettes |
| Gautier 2011 | zero priority on the occluder side |

**We hand LaMa the whole plate.** Task #59 is confirmed four times over and is the best-supported unbuilt item
in the backlog.

### 4. The energy, and a weight ratio worth noticing

```
E(X) = Σ_{i∈V} E1(x_i) + Σ_{(i,j)∈E} E2(x_i, x_j),    E1(x_i) = k_s·E_S(x_i) + k_i·E_I(x_i)
```

- `E_S` — structure similarity, a **symmetric** curve distance `d(c_i, c^x_i) + d(c^x_i, c_i)`, each term the
  sum of squared shortest distances from every point on one segment to the other, normalised by point count.
- `E_I` — boundary match, SSD against the known pixels, **and zero for every patch not on the boundary**.
- `E2` — coherence, normalised SSD over the overlap of adjacent patches.

§5: ***"The weights `k_s` and `k_i` are 50 and 2 respectively in all our experiments."***

**Structure is weighted 25× the boundary fit.** For a method whose entire output is patches pasted into a hole,
"match the curve the user drew" dominates "match the pixels at the edge of the hole" by a factor of 25 — and
the same two numbers are used for every image in the paper. That is a strong prior about what a viewer notices,
and it agrees with Sinha's *"humans are sensitive to the motion of high-contrast edges and straight lines…
the lack of surface detail is rarely noticeable."*

For us it is an argument about where to spend the join cost's budget: getting the *structure* of the band right
(continuous at creases, torn at steps) should outrank getting the rim values to match smoothly. Our current
`revealPx` cost is entirely the latter.

### 5. The limitation, which is our architecture proposed as future work

> *"**Our approach only encourages a coherent completion result but has no ability to handle depth ambiguity.**
> The visibility order is determined by the samples that can be found. In our method, **we only treat it as a
> planar graph without consideration of occlusions. Introducing the concept of layers is one of the possible
> solutions to handle depth ambiguity**, as shown in Figure 10. We complete the missing region in **three
> separate layers**: vertical trunk, horizontal trunk and background layer… The final completion results are
> the composition of the three layers **from back to front**."*

Plate 1 / plate 2 / background, composited back to front — posed as the open problem in 2005, demonstrated once
by hand with Bayesian matting and two user-drawn curve pairs. We build it automatically from arrival order.
Together with the LDI note (§1 of note 8) this is the second paper to independently arrive at our layer stack,
and the first to arrive at it *as the answer to an inpainting failure* rather than as a rendering
representation.

### 6. Parameters and the rest

- Patch size *"greater than the largest structure in the image"* — same rule as Criminisi's and Ndjiki-Nya's;
  used 9 up to 27×31.
- Anchor points sampled along the curve at **half the patch size**, *"to guarantee sufficient overlaps."*
- Sample set = all patches centred within a **1–5 pixel band along the curve**; `N` in the hundreds to
  thousands.
- **Sample transformation** (§4.3), for when the image does not contain what is needed: flip, fixed 90°
  rotation, or a per-node optimal rotation `θ* = argmin_θ {d(R(c^x_i;θ), c_i) + d(c_i, R(c^x_i;θ))}` aligning
  the source curve to the target curve. An honest admission that exemplar methods run out of material —
  *"if there are not enough samples in the image, it will be impossible to synthesize the desired structure or
  texture."*
- **Photometric correction** by Poisson reconstruction with the gradient zeroed across the patch seam, Dirichlet
  boundary on the patch interior, channels corrected independently. *"such seams cannot be easily removed by
  simple blending or by graph-cut."* This is the third gradient-domain seam fix in the corpus (Ndjiki-Nya's
  covariant cloning, our own bi-directional gradient means from R8 item 2).
- Timings: structure propagation *"fewer than 3 seconds for each curve"*, 6 s for the two-X-junction hawk;
  texture propagation 2–20 s per subregion; 2.8 GHz PC.
- Against Criminisi (Figure 7): *"Previously developed automatic image completion algorithms may not be able to
  generate good quality results for the examples shown… **High-level human knowledge is required** to complete
  these images."*

### 7. What I take from it

The manual half really is free for us — we compute automatically what their user draws by hand (the rim, and
per Sinha the crease lines, which are straight by construction). But the transferable content is the
**framing**, not the method: structure before texture (we do it), restricted source regions (we do not — task
#59), and above all the DP↔BP equivalence, which says the per-line to cross-line step is an edge-set change to
a recursion we already run, at `O(2LN²)`, rather than a new algorithm.

---

## 19. Hirschmüller & Scharstein, "Evaluation of Cost Functions for Stereo Matching", CVPR 2007 [316 lines] DONE

Read in full. This arrived in place of the PAMI 2009 version and I flagged it as *"only if the P1/P2 question
turns into a 'which cost' question."* It did not — **we have no matching cost at all**, so the paper's substance
(BT, LoG, Rank, Mean, HMI, NCC compared under gain, gamma, vignetting and noise) does not transfer. Three
things in it do, and one is a real caution for Sprint 30.

### 1. The caution: the best penalty shape depended on the *solver*, not just the images

§2.2, on the graph-cut implementation:

> *"**We tried to use the same energy function E(D) as for SGM. However, we found that for GC it gives better
> results to adapt the cost P2 not linearly with the intensity gradient, but rather to double the value of P2
> for gradients below a given threshold.**"*

Hirschmüller — the author of the `P2 = P2′/|I_bp − I_bq|` form — found that his own form was **not** the right
one once the optimiser changed, and replaced it with a two-level step (×2 below a gradient threshold). That is a
**sixth** shape in the corpus, and it is the same crude binary weighting Szeliski et al. used (`w_pq` = 2 or 3
below a threshold).

So the six forms now on record are:

| source | form | fitted for |
|---|---|---|
| Hirschmüller 2008 | `P2′/|ΔI|` | SGM's 1-D recursion |
| **Hirschmüller & Scharstein 2007** | **×2 below a gradient threshold** | **graph cuts** |
| Szeliski et al. 2006 | `w_pq` = 2 or 3 below a threshold | graph cuts / BP / TRW |
| Scharstein & Szeliski 2002 | `1/(1+γ|ΔI|)` | DP / SO |
| Schönberger 2018 | `P1(1+αe^{−|ΔI|/β})` | SGM |
| Banz 2012 | `γ − α|ΔI|`, clipped below | SGM, both cost functions |

**The shape is not a property of the problem; it is fitted to the optimiser.** Our arbitration is a per-texel
closed form over four candidates — neither a 1-D recursion nor a global minimisation — so *none* of these
transfers with confidence. That is the strongest argument yet that Sprint 30 must **sweep** the shape rather
than adopt one, and it retrospectively justifies carrying both the linear and reciprocal arms (per the Banz
amendment above) rather than picking.

### 2. The robustness/sharpness trade, for the fourth time — and here it is the paper's closing open problem

§4: *"the filter-based costs (LoG, Rank and Mean) **tend to blur object boundaries**… the blurring effect is
clearly visible for pixel-based matching methods such as SGM and GC. For such methods, the results of BT and
HMI appeared best."*

§3.1 gives the mechanism: *"Rank also **reduces the effect of outliers near depth discontinuities**. This is
important for a window-based method, but less so for pixel-based methods."*

And the paper ends on exactly this wish:

> *"**It would be nice if the advantages of the different costs could be combined to get a matching cost that is
> able to handle local radiometric transformations like Rank and LoG while still maintaining sharp depth
> discontinuities like HMI.**"*

That is the fourth independent statement of the trade Sprint 31 is about — after Gautier's K-patch smoothing,
Ndjiki-Nya's 9×9-beats-25×25, and Banz's census-over-rank *"less edge blurring because census transform retains
spatial information."* **A neighbourhood statistic buys outlier resistance and pays in boundary blur, and in
2007 two of the field's principals named combining the two as open.**

For Sprint 31 this settles the experimental design: the gated median's neighbourhood size is not a parameter to
optimise against the temporal step alone, because the metric that would catch its cost — band sharpness at the
rim — is a different measurement. Both must be reported per arm.

### 3. The occludee rule, ninth time, as the unremarked default

§2.2, describing the *baseline* post-processing of their local method: *"Invalid disparity areas are filled by
**propagating neighboring small (i.e., background) disparity values**."* And for SGM: *"Disparity segments below
the size of 20 pixels are invalidated"* (160 pixels for the correlation method) — a despeckle threshold, ours is
Sprint 13's.

By 2007 "fill from the background" is not a contribution, it is the sentence you write about your baseline. Nine
statements now.

### 4. Two notes worth keeping

**Their tuning protocol is the one Banz later contradicts.** §2.2: *"We manually tuned the smoothness parameters
of SGM and GC individually for each cost **using images without radiometric differences**. After the tuning
phase, all parameters were kept constant for all images and experiments."* Banz (2012, note 14) measures that
parameters tuned on clean images fail under noise while parameters tuned on degraded images transfer to both,
and verifies it on real imagery. **Banz's protocol supersedes this one**, and it is Banz's that Sprint 30 should
follow — tune on the noisiest picture.

**The realistic-data penalty is 3× .** §3.2: their six new datasets (Art, Books, Dolls, Laundry, **Moebius**,
Reindeer — the coincidence of names is worth a smile) are *"more challenging… due to the increased disparity
range, lack of texture, and the more complicated scene geometry. This is reflected in the higher matching
errors: **the best methods now have errors of about 10%, as opposed to about 3% before**."* Every Middlebury
number quoted elsewhere in these notes is from the easy set. Worth remembering when any of them is used as a
bar.

These six datasets are public with ground truth at `vision.middlebury.edu/stereo/data/`, 7 rectified views each,
3 exposures × 3 lightings. Not obviously useful to us — they are stereo pairs, not single photographs with
hidden geometry — but noted in case a depth-estimator comparison ever wants controlled radiometric variation.

### 5. What does not transfer, stated plainly

The whole of §3. Rank beats HMI for correlation; HMI beats Rank for SGM and GC under global brightness change
and noise; Rank and LoG beat HMI under vignetting and moving light sources because *"[HMI's] cost is explicitly
based on the assumption of a complex, but **global** radiometric transformation"*; NCC degrades under gamma;
*"None of the matching costs we compared was very successful at handling strong local radiometric changes."*
All of it is about comparing two views of the same scene. We have one view, and our band has no correspondent
anywhere. Recorded so the note is complete, not because it bears on anything we will build.

---

## 20. Boykov, Veksler & Zabih, "Fast Approximate Energy Minimization via Graph Cuts", PAMI 23(11), 2001 [1041 lines] DONE

Read in full, including the graph constructions of §§4–5, the optimality proofs of §6, and the NP-hardness
appendix. R7 and R8 both named this as missing-by-citation; it is now read. **It contains the controlled
measurement of Sprint 30's cap that nothing else in the corpus provides.**

### 1. The definition of "discontinuity preserving" *is* the cap

§1:

> *"Informally, a discontinuity preserving interaction term should have **a bound on the largest possible
> penalty. This avoids overpenalizing sharp jumps between the labels of neighboring pixels.**"*

with the canonical examples: truncated quadratic `V(α,β) = min(K, |α−β|²)` (a semi-metric), truncated absolute
`V(α,β) = min(K, |α−β|)` (a metric), and Potts `V(α,β) = K·T(α≠β)` (a metric).

**Our S51 join cost is `revealPx` — unbounded, therefore by this definition not discontinuity-preserving at
all.** And the named failure mode, *"overpenalizing sharp jumps"*, is precisely the 11% real-step damage S51
recorded. The prediction S54 made from Hirschmüller is here derived from the definition rather than inferred
from a sentence.

### 2. §8.6 — the measurement, and it is 5.3×

Image restoration, constant-intensity regions corrupted by `N(0,100)` noise, **same solver, same data, only the
penalty shape differing**:

| smoothness | average absolute error | time |
|---|---|---|
| **truncated** absolute difference `80·min(3, |f_p − f_q|)` | **0.34** | 38 s |
| plain absolute difference `15·|f_p − f_q|` | **1.8** | 237 s |

*"For both models we chose parameters which minimize the average absolute error"* — so both are optimally
tuned. *"The results in (b,c) were histogram equalized to reveal **oversmoothing** in (c), which does not happen
in (b). **Similar oversmoothing for the absolute difference model occurs in stereo.**"*

**A 5.3× error reduction from capping the penalty, and the uncapped failure mode is oversmoothing — which is
class 2 exactly: a real step drawn as a ramp.** This is the single strongest piece of support for Sprint 30 in
the corpus, and unlike the others it is a clean A/B on one variable.

**And the sharper twist:** the uncapped model is *convex*, so *"for the absolute difference model we can find
the **exact** solution"* — while the truncated model is NP-hard and only approximately minimised. **The exact
minimum of the uncapped energy is 5.3× worse than an approximate minimum of the capped one.** That is Szeliski's
"the solver is not the bottleneck" conclusion in its strongest possible form: better minimisation of the wrong
energy loses to worse minimisation of the right one, by a factor of five, on the same data.

### 3. Capping also restores the optimality guarantee — which unbounded costs do not have

§6.1, Theorem 6.1: a local minimum under expansion moves satisfies `E(f̂) ≤ 2c·E(f*)`, where

```
c = ( max_{α≠β} V(α,β) ) / ( min_{α≠β} V(α,β) )
```

For Potts `c = 1`, giving the factor 2 — *"by definition c ≥ 1, so this is the energy function with the best
bound."*

**An unbounded `V` has `c → ∞` and therefore no bound at all.** So the cap does two things at once: it fixes the
energy's shape *and* it makes the approximation guarantee finite, tightening as the cap tightens. I had not seen
that the two were connected. If Sprint 30's capped cost is ever moved into an expansion-move framework, the cap
is what makes the framework applicable; without it there is no guarantee to appeal to.

(Caveat kept: `min(K,|Δ|)` is a metric, so expansion moves apply; `min(K,|Δ|²)` is only a **semi-metric**, so it
needs swap moves — or the Potts approximation of §6.2, which still yields the `2c` bound. Our clamped-both-ends
cost would need checking against the triangle inequality before assuming expansion moves are legal. This is the
same point Szeliski et al. make about "Venus" and "Penguin" using a non-metric `V`.)

### 4. Seed-insensitivity, with 100 seeds — and what it does and does not prove

§8.3: *"for our algorithms **the starting point is unimportant**. The results differ by less than 1% of image
pixels from any starting point that we have tried. **We also run 100 tests with randomly generated initial
labelings.** Final solutions produced by our expansion and swap algorithms had the average energy of **252,157
and 252,108**, correspondingly, while the **standard deviations were only 1,308 and 459**."*

That is sd/mean of 0.5% and 0.2% over 100 random initialisations. **S51's five-seed convergence is the same
signature, measured 20× more thoroughly here.**

The useful distinction, which I should have drawn earlier: they present seed-insensitivity as evidence the
*minimisation* is reliable. It is not evidence the *minimum is right*. Our S51 evidence — λ inert across its
range **and** seeds converging **and** sFD 0.0005 from wash — is therefore correctly read as "we are reliably
finding the minimum of an energy that does not say what we want", which is exactly what §8.6 says happens when
the penalty shape is wrong. The two results reinforce each other.

### 5. Static cues — a seventh contrast form, and a fifth metric-versus-eye statement

§8.2: `u_{p,q}` smaller where `|I_p − I_q|` is larger — *"two neighboring pixels p and q are much more likely to
have the same disparity if we know that I(p) ≈ I(q)."* They also suggest `u_{p,q}` could be set *"according to
an output of an edge detector"* or from segmentation.

The synthetic white-rectangle-on-black example is the clearest argument for the term I have seen: with uniform
`u`, the smoothness minimum places the disparity boundary *wherever the region geometry makes it cheapest* —
determined by *"the relationship between the height of the square and the height of the background"*, not by the
image. With contrast weighting the boundary lands on the intensity edge, and *"this result is much closer to
human perception."*

**That is Hirschmüller's §II-E.2 objection** (*"E(D) does not differentiate between placing a disparity step
correctly just next to a foreground object or a bit further away"*) demonstrated on a two-region toy.

Measured worth, Fig. 12: expansion algorithm **7.2%** total errors with static cues, **7.6%** without. Then:

> *"Without the static cues, **a corner of size approximately 800 pixels gets broken off and is assigned to the
> wrong disparity**… The percentage improvement may not seem too significant, however **visually it is very
> noticeable**, since without the static cues a large block of pixels is misplaced."*

Fifth paper in this corpus to say the aggregate number understates what the eye sees — and the first to
quantify the exchange rate: **0.4 percentage points = one 800-pixel block in the wrong place.** That is a
genuinely useful calibration for reading our own null results. A change of a few tenths of a percent on a
whole-image metric can be a single large, obvious, ruinous artefact.

### 6. Parameter stability — the sweep shape to expect

Fig. 14, expansion algorithm, varying the Potts parameter `K`:

| K | 5 | 10 | 20 | 30 | 50 | 100 | 500 |
|---|---|---|---|---|---|---|---|
| total errors % | 13.0 | **7.0** | 7.6 | 7.9 | 8.8 | 10.4 | 16.3 |
| errors >±1 % | 4.5 | 2.3 | **2.1** | 2.3 | 2.3 | 2.9 | 8.2 |

*"For small K there are many errors because the data term is overemphasized, for large K there are many errors
because the smoothness term is overemphasized. **However for a large interval of K values the results are
good.**"*

A broad basin across a factor of ~3 in `K`, failing at both ends over two decades. **So Sprint 30's sweep should
be logarithmic and coarse** — a factor-of-2 or -3 grid across two decades will find the basin, and a fine grid
would waste bakes. Note also the two columns disagree about the optimum (10 vs 20), by amounts smaller than the
basin's width; worth remembering when our own arms differ by less than their spread.

### 7. Smaller things worth keeping

- **99% of the progress in the first iteration** (8 s of 25 s to convergence); running time linear in the number
  of labels (Fig. 15, 15→75 labels: 8→35 s per iteration), accuracy degrading only slightly with more labels
  (7.3%→8.3%).
- **Expansion vs swap**: 7.2% vs 7.0%, *"the observed difference in errors is insignificant, less than 1%"*,
  expansion **1.4× faster**. Expansion requires `V` metric; swap needs only semi-metric but *"a local minimum
  when the swap moves are allowed can be **arbitrarily far** from the global minimum"* (Fig. 8's three-pixel
  counterexample). Szeliski's later *"there never seems to be any reason to use swap moves"* is consistent.
- Against simulated annealing on Tsukuba: 7.2% vs **20.3%**, 25 s vs 1200 s; normalised correlation 24.7%. The
  smoothness energy reached is 160,000 vs annealing's 330,000 after four hours — *"twice as bad."*
- §8.4, the SRI tree pair: the ground is slanted, so *"a piecewise constant model (Potts model) does not work as
  well"* and they switch to `V = 15·min(3,|f_p − f_q|)`; *"the Potts model tends to produce **large regions with
  the same disparity**."* The fronto-parallel/staircase bias again, now as a property of the *penalty* rather
  than of the window — Potts is the limit where every disagreement costs the same, so nothing distinguishes a
  ramp from a step and the cheapest answer is a constant. **Directly relevant**: this is the far end of the
  `V_max` knob identified in note 10, and it tells us what over-capping looks like — our class-1 disagreements
  would be suppressed at the cost of flattening class-3 creases into constants. The basin has two walls.
- Data term robustness: `D_p(f_p) = min(|f_p − I_p|², const)` with `const = 20` — *"if we set const to infinity,
  the results are mostly the same except they become **speckled** by a few noisy pixels."* A truncation on the
  data term as well as the smoothness term; ours is the thin-evidence rule.
- Minimising even the Potts energy is **NP-hard** (appendix, via reduction to multiway cut, construction due to
  Kleinberg), *"and it is possible to extend this proof to the case when P is a planar grid."*

### 8. What this changes

Sprint 30 was already the best-supported item in the backlog. §8.6 raises it from "five papers agree on the
shape" to **"one controlled experiment measures 5.3× on exactly this variable, and the uncapped failure mode is
named as oversmoothing."** It also supplies the sweep design (logarithmic, coarse, two decades), the warning
that over-capping collapses toward Potts and flattens slanted surfaces, and the observation that the cap is
what makes any optimality guarantee possible at all.

---

## 21. Bornemann & März, "Fast Image Inpainting Based on Coherence Transport", J. Math. Imaging Vis. 28, 2007 [3456 lines] DONE

Read in full — the analysis of §§2–4, the three theorems and their proofs, the coherence construction of §5, the
implementation of §6, and all of §7's comparisons. (The PDF→markdown conversion mangled the equations into
roughly one symbol per line; I have reassembled them below and say so.) R4 cited this and it was never read
here; the first archive's copy was truncated to one page. **It is the most mathematically substantial paper in
the corpus and it derives, from first principles, the artefact Criminisi observed empirically.**

### 1. Telea's algorithm *is* onion-peel, and its limit equation explains the skeleton artefact

Telea fills in order of distance-to-boundary (fast marching, `|∇T| = 1`, `T|∂D = 0`), taking weighted means of
already-filled neighbours. Theorem 1 computes the high-resolution vanishing-viscosity limit of that scheme, and
for Telea's weight it is

```
n(x) · ∇u(x) = 0   on D∖𝒮,     u|∂D = u⁰|∂D        n = ∇T
```

i.e. **transport purely along the gradient of the distance map**, with the algorithm's plain-English content
spelled out:

> *"The known image value u⁰(x) of a boundary point x ∈ ∂D is transported along the straight line of the normal
> pointing inwards into the inpainting domain D **until this normal meets the skeleton 𝒮**, that is, until it
> intersects with a different normal transporting different image values. **There is no transport of information
> across 𝒮.**"*

where the skeleton `𝒮` is *"the set of singularities (locations of the ridges) of the distance map"* — the
medial axis.

**This is Criminisi's Fig. 20 observation, derived rather than observed.** He wrote that concentric filling makes
the reconstructed sky–sea boundary *"follow the skeleton of the selected target region"*; Bornemann proves that
the limit of distance-ordered weighted-mean filling transports strictly along `∇T` and that information cannot
cross the skeleton at all. Two papers, three years apart, one empirical and one analytic, on the same object.

And Bertalmio had already rejected this direction: *"This transport direction has already been identified by
Bertalmio et al. as being **an unsuccessful choice** for the propagation of image information."*

**The prediction I logged against Criminisi's note now has a second, stronger basis** — and it sharpens. Our band
is long and thin, so the level lines of its distance map run *along* the band and `n = ∇T` points *across* it,
rim toward centreline. A distance-ordered mean fill would therefore transport across the band (fine) but be
unable to carry anything across the centreline (not fine), producing a seam on the medial axis. Whether our
simultaneous solve has an analogous locus is exactly the measurement I proposed; this gives it a predicted
location — the band's medial axis — rather than only a direction.

### 2. Their fix: steer the transport by reshaping the weight, and it has a knob we already have

Theorem 2's exponentially confined weight (reassembled):

```
w(x,y) = ( √(π/2) · μ / |x−y| ) · exp( − (μ² / 2ε²) · |c⊥(x)·(x−y)|² )
```

As `μ → ∞` the limit direction `c*` tends to `±c`, the desired direction — so **the weight function of a
single-pass fill can be made to realise an arbitrary transport field**, keeping Telea's speed while getting
Bertalmio's quality. The deviation angle has the asymptotic form
`ϑ(θ) = √(2/π)·log(tan(θ/2 + π/4))·μ⁻¹ + O(μ⁻²)`.

Then §5 makes `μ` **per-texel**, from the structure tensor's eigenvalues:

```
μ(x) = 1                                           if λ₁ = λ₂
     = 1 + κ · exp( − δ⁴_quant / (λ₂ − λ₁)² )       otherwise          (1 ≤ μ ≤ κ+1)
```

> *"using large values of μ … allows to faithfully following the given vector field c **with just a small amount
> of diffusion**, whereas small values (μ ≈ 1) yield a **considerable amount of diffusion**. Since the first
> behavior is desirable for strong coherence and the second for a weak one, we suggest taking the image-adapted
> parameter μ = μ(x)."*

**That is a per-texel continuous dial between directional transport and isotropic diffusion, driven by a
confidence measure — which is precisely the shape of the per-texel λ we built in `_screenedPoissonBand` and of
`_geoFarConf`.** We arrived at "blend between the structured answer and the smooth answer according to local
confidence" independently; this is the published version, with the confidence derived from the structure
tensor's eigenvalue gap and normalised by the quantisation step `δ_quant` to make it scale-free. **The
normalisation by the quantum is worth stealing outright** — we have a per-tile effective quantum from Sprint 14
and currently do not use it to set the blend.

### 3. THE FINDING: the modified structure tensor, and the spurious-edge trap

§5, "Boundary Effects". To compute the coherence direction at the fill front you must estimate a structure tensor
from the *already filled* region, but the Gaussians `K_σ`, `K_ρ` reach into the not-yet-filled part. Continuing
by zero:

> *"in general, this makes ∂Ω(x) **a spurious edge, aligning the coherence flow tangentially to it** … Since we
> know from Sect. 4 that a tangential vector field c is rotated into the normal direction c* = n, **we would
> basically end up with Telea's algorithm once again.**"*

And symmetry/Neumann conditions fail too, the other way: *"They tend to align the coherence flow field with the
**normal** to the boundary… once more, we would obtain a vector field c that yields c* ≈ n."*

The fix, equation (21) — **normalised convolution**:

```
v_σ      = ( K_σ ⋆ (1_Ω · u) ) / ( K_σ ⋆ 1_Ω )
Ĵ_σ,ρ(x) = ( K_ρ ⋆ (1_Ω · ∇v_σ ⊗ ∇v_σ) )(x) / ( K_ρ ⋆ 1_Ω )(x)
```

Divide every smoothed quantity by the identically-smoothed **validity mask**.

**Two things follow for us, and the second is the more important.**

**(a) A class of bug to audit.** Any filter we run near the band's rim that does not normalise by the valid mask
is treating unfilled texels as zeros and manufacturing an edge at the rim. `return_grad.py` (bi-directional
gradient means) and `return_align.py` (colour–depth edge alignment) both operate exactly there. Worth checking;
`return_grad`'s self-test asserts a no-op on a *dense* field, which would not catch this.

**(b) A third mechanism that produces rim-parallel structure.** A hole treated as content makes its own boundary
into an edge, and the fill then runs *along* that edge. So rim-parallel artefacts can arise from (i) per-line
independence — our class 1; (ii) uniform-speed filling following the medial axis — Criminisi/Bornemann; and now
(iii) the hole's own boundary read as a spurious edge. **This bears directly on task #59**: LaMa receives the
band as a masked region, and if its effective context straddles the rim the same trap is available. That
strengthens the case for a connectivity-limited context and adds a specific thing to look for in the output.

### 4. The tunnel metaphor, which is our two-rim problem stated exactly

§1: *"Of course, this transport along characteristics will cross somewhere. However, if we are lucky, crossing
characteristics might carry similar information. **(Like two teams digging a tunnel from both ends are meant to
meet somewhere.)**"*

Footnote 9, less optimistically: *"The closing of edges at the skeleton is comparable to the digging of a tunnel
from two ends: **if the measurements, the plan, and the performance were good the digging teams will meet
somewhere in the middle (at the skeleton). If not, they will fail badly.**"*

That is the far-side law's situation in one image: two rims, each extrapolating inward, required to agree at the
middle. Fig. 8(b) shows what failure looks like — **a shock on the non-transparent part of the skeleton**, i.e. a
visible seam down the band's centreline. And §4 gives a computable criterion, the *transparency* of a skeleton
point: a point where the two sides' characteristics can be continued through each other. Our class-1
disagreements are, in this language, non-transparent skeleton points.

### 5. The failure mode they call unavoidable — and it may be part of class 1

Theorem 2's limit (14): `c* → c` when `n·c > 0`, `→ −c` when `n·c < 0`, and **`→ n` when `c ⊥ n`**.

> *"The price to pay for it is, by continuity, the **unavoidable** sudden rotation of c* into the perpendicular
> direction n if the flow generated by c becomes **close to tangential to the level lines of the distance
> map**."*

Fig. 8 measures the degradation as the edge's slope `α` falls: `α = 18.2°` closes perfectly; `11.3°` perfect;
**`5.7°` a clearly visible shock**; `0°` reproduces Telea's behaviour exactly.

For an elongated band, `n` points across it, so `c ⊥ n` means **structure running along the band**. So:
structure crossing the band steeply is recoverable; **structure crossing at a shallow angle to the rim is
not, and degrades to distance-normal transport.** That is a specific, testable sub-population of class 1 — and
it predicts the error should correlate with the *angle between the local structure and the rim*, which we can
measure from the probe dumps alongside the medial-axis test. Added to the same check.

### 6. The maximum principle — a guarantee we gave up and should know we gave up

§2: the generic single-pass algorithm, being a weighted mean, satisfies a **comparison principle** —
*"If the data image satisfies u_min ≤ u⁰ ≤ u_max … the inpainting result satisfies the same inequalities"* — and
is `l∞`-stable. *"Note that the comparison principle still holds if w_h depends on u_h"*, so it survives the
nonlinear coherence weighting.

**Our far-side law fits and extrapolates planes, so it has no such bound.** A plane fitted to a noisy run and
extended across a gap can and does overshoot the range of its own evidence. That is the price of the slanted
model, and PatchMatch's 7.6× on Venus is the reason we pay it — but it is worth stating plainly that we traded a
maximum principle for slant, and that a bound on the band's output against its own rim values is therefore
something we must impose explicitly rather than inherit. Cheap to add, and the kind of guard that catches
exactly the class-2 blow-ups.

### 7. Parameters, and one design rule worth keeping

Four parameters: `ε` averaging radius, `κ` sharpness, `σ` and `ρ` the pre- and post-smoothing scales.

> *"For inpainting problems with **narrow (that is, about 10 px) but elongated inpainting domains** … a good
> start is made with the default parameters `(ε, κ, σ, ρ) = (5 px, 25, 1.4 px, 4 px)`."*

**"Narrow but elongated" is our band's shape**, so that default is the relevant one, not the ones tuned for
compact holes (`ε=14, κ=250, σ=1.2, ρ=7` for the parrot cage; `ε=6, κ=125, σ=12, ρ=18` to close a circle).

And the cross-gap rule, from the circle-closure discussion:

> *"at the inpainting of a point x ∈ D the modified coherence flow field **starts communicating between opposite
> sides of the yet-to-be-inpainted domain if their distance is below 4ρ**."*

So `ρ` sets the range at which the two rims can see each other: **`ρ ≳ bandwidth / 4`** for a band fill to couple
its two sides at all. With their default `ρ = 4 px` that is an 16 px reach, consistent with the ~10 px domains.
A concrete sizing rule if we ever build a coherence-steered band fill, and a diagnostic if we do not: any method
whose smoothing scale is below a quarter of the local band width **cannot** be coupling the rims.

### 8. Why nobody uses the variational methods, with numbers

§1's iteration-count argument: explicit time stepping needs `τ ∝ h^ν`, so `#iterations ∝ (#pixels)^{ν/2}`.

- Bertalmio's transport equation has `ν = 1` → order **10³** iterations; *"Bertalmio et al. report to have used
  **3000 time steps**."*
- Chan et al.'s **Elastica** has `ν = 4` → order **10⁷**; *"[12], Fig. 6.9, reports to have used **12 000 000
  time steps**"* to reproduce a 140×32 px detail.

**Sprint 17b's mathematics note proposed elastica for hidden contours.** This is the number that should sit
beside that proposal: twelve million time steps for a 140×32 patch. Chan & Shen themselves list *"fast and
efficient digital realization"* of these methods as a major open problem. Recorded against S17b — the
formulation stays interesting, the explicit scheme is not viable, and if elastica is ever wanted it needs a
non-iterative or implicit route.

Against which: their own method is **0.4 s** for 241×159, **0.5 s** for a 483×405 scratch removal, **20 s** for
the parrot cage where Tschumperlé needed 4 min 11 s, and *"at least an order of magnitude faster"* than
Bertalmio at comparable quality.

### 9. Smaller things

- **Edge-detection flow `c = ∇⊥u_σ` is rejected in favour of the coherence direction** (minimal eigenvector of
  the structure tensor): on an unprocessed fingerprint the edge flow *"closely follows minor local features; it
  looses relation with the global coherent flow of information… **edge detection flow, like edge detection
  itself, has problems with its robustness**."* The coherence flow is near-identical on the raw and the
  shock-filtered image. Another instance of "a second-moment statistic beats a first-moment one", now for
  *direction* rather than value — and a reason to prefer Gautier's tensor over Criminisi's gradient.
- **Colour**: one shared coherence direction for all three channels, from a common structure tensor combined with
  the luminance weights `0.299/0.587/0.114`. *"color images take just about twice the CPU time needed for
  inpainting the corresponding luminance image."*
- **Implementation**: the structure tensor is the bottleneck and is maintained by an **incremental update** as
  the front advances — `v̂_σ(y) ← v̂_σ(y) + K_σ(x−y)·u(x)`, `χ_σ(y) ← χ_σ(y) + K_σ(x−y)` over the `4σ`-wide
  quadratic mask — rather than recomputed. Relevant if we ever run an ordered fill at plate resolution.
- **μ cannot be raised without limit in practice**: beyond some point *"values of μ which are too large simply
  result, by **underflow**, in a weight w that is identical to a floating point zero"*, because only finitely
  many discrete directions `x−y` exist in the neighbourhood. A discretisation ceiling on how sharply any such
  weight can steer.
- Shocks in the discrete algorithm sit *"not exactly located at the skeleton but have an offset of ε = 6 px"* —
  the seam lands a radius away from where the theory puts it.
- Their §7 denoising application: Lena with **80% salt-and-pepper noise** inpainted in 20 s by masking the 0 and
  255 levels and treating the result as a hole. A reminder that "inpainting" and "denoising a heavily corrupted
  image" are the same operation, which is a fair description of what a noisy monocular depth map needs.

---

## 22. Taniai, Matsushita, Sato & Naemura, "Continuous 3D Label Stereo Matching using Local Expansion Moves", TPAMI 2018 (arXiv 1603.08328v3) [3750 lines] DONE

Read in full, including Appendix A's submodularity proof and Appendix B's per-image convergence study. (Lines
2488–3750 are the axis data for Appendix B's fifteen plots.) **The last of the twenty-three, and it settles
Sprint 32 — mostly by showing that the part we can use is the energy, not the optimiser.**

### 1. The smoothness term is the two-sided clamp, already assembled — and it is a *curvature* penalty

Equations (10)–(12), reassembled:

```
ψ_pq(f_p, f_q) = max(w_pq, ε) · min( ψ̄_pq(f_p, f_q), τ_dis )

w_pq            = exp( −‖I_L(p) − I_L(q)‖₁ / γ )                     contrast weight
ψ̄_pq(f_p, f_q)  = |d_p(f_p) − d_p(f_q)| + |d_q(f_q) − d_q(f_p)|      curvature
```

with `{λ, τ_dis, ε, γ} = {1, 1, 0.01, 10}`, eight neighbours.

**This is exactly the design I assembled across Gallup, Banz and Boykov–Veksler–Zabih, in one formula, in the
most recent paper in the corpus:**

- **cap** — `min(ψ̄, τ_dis)`, *"truncated at τ_dis to allow sharp jumps in disparity at depth edges"* (class 2);
- **floor** — `max(w_pq, ε)`, *"ε is a small constant value that gives a lower bound to the weight ω_pq to
  increase the robustness to image noise"* (class 1's near-ties);
- **contrast modulation** — the eighth form in the corpus, and an exponential decay like Schönberger's.

That the synthesis I built from three older papers turns out to be the current state of the art's actual
smoothness term is the strongest possible confirmation of Sprint 30's revised design. Nothing left to argue.

**And `ψ̄` is the piece we do not have.** It evaluates *each plane at both pixels* and sums the disagreements, so
it is zero iff the two planes agree at p **and** at q — i.e. iff they are the same plane. It therefore penalises
**a change of slope**, not merely a change of value. They note it *"naturally extends the traditional truncated
linear model"* since `ψ̄ = 2|c_p − c_q|` when `a = b = 0` is forced — *"although the latter has a
fronto-parallel bias and should be avoided."*

Our S51 join cost is `revealPx`: a **value** difference at the join. So two planes that meet at the same depth
but at different angles — **a crease, which is Sinha's class 3, 35.1% of wall length** — cost us nothing. The
curvature form is precisely the object that distinguishes a crease from a step, and it is the one we are
missing.

This does not contradict the Sinha note, it completes it. Sinha says class 3 *should* be depth-continuous and
we measure a median jump of 25 steps there. So our class-3 walls are value jumps *where the geometry says there
should be none* — the law is manufacturing a step at a crease. The curvature penalty is what would make a
crease cheap and a step expensive, which is the discrimination class 3 needs. **That makes "add a curvature term
to the join cost" a concrete Sprint 30 addition rather than a vague Sprint 32 aspiration.**

### 2. Local expansion moves: the idea is good, the machinery needs a data term we do not have

The contribution is a way to get PatchMatch's spatial propagation *inside* graph cuts. Rather than one global
α-expansion per label, define a grid of cells; at each cell `(i,j)`, take **`α_ij` = the current label of a
randomly chosen pixel in the centre cell** `C_ij`, optionally perturbed, and run a binary min-cut over the
**3×3 expansion region** `R_ij`:

```
f ← argmin E( f′ | f′_p ∈ {f_p, α_ij},  p ∈ R_ij )
```

> *"making the expansion region R_ij larger than the label selection region C_ij is the key idea for achieving
> spatial propagation… a current label f_p in the centre region C_ij can be propagated for its nearby pixels in
> R_ij as the candidate label α_ij."*

Algorithm 1 has three proposers: **propagation** (`Δ = 0`, `K_prop` times), an optional **RANSAC** plane fit to
the current labels in the cell, and **refinement** (perturbation halved each round, `K_rand` times) — the same
exponentially-shrinking schedule PatchMatch uses.

Scheduling: cells grouped by `k = 4(j mod 4) + (i mod 4)`, giving **16 groups of mutually disjoint expansions**
with a one-cell gap between neighbours. The gaps buy two things — submodularity (so plain graph cuts suffice
rather than QPBO) and independence (so the group runs in parallel). Lemma 3's proof is neat: two expansion
regions cannot interact because any chain of pairwise terms between them *"inevitably contains constant or unary
terms at a gap."*

**The whole construction is a move-making scheme for minimising an energy whose data term is photo-consistency.
Our band has no data term.** With `φ_p ≡ 0` every labelling in the expansion region is equally good on the data
and the minimisation is driven entirely by the smoothness term — which, being minimised, would collapse the band
to whatever is smoothest. Sprint 32 as "port local expansion moves" is therefore not available to us, and this
confirms from the other end what the Szeliski study said: **our problem is the energy, and we do not have half
of theirs.**

What *is* available: the **label space** (per-texel `(a,b,c)` planes), the **curvature smoothness term**, the
**random-plane initialisation** (pick disparity `z₀` uniformly, a random unit normal `n`, convert), and the
**halving perturbation schedule**. Those are the parts our far-side law could adopt without a photo-consistency
cost.

### 3. Their multi-scale grid is a measured result worth copying in spirit

Three grid levels, cell sizes **5×5, 15×15, 25×25 px** (or 1%, 3%, 9% of image width on V3), iterated
`{K_prop, K_rand}` = `{1,7}` for the finest and `{2,0}` for the other two.

> *"the size of cells **balances between the level of localization and the range of spatial propagation**.
> Smaller sizes of cells can achieve finer localization but result in shorter ranges of spatial propagation."*

§4.3 measures it (Reindeer, no post-processing, and Appendix B repeats it on all fifteen V3 training pairs):
(S,M,L) beats (S,M,M), (S,S,S), (M,M,M), (L,L,L) *"for most of the image pairs"*. *"The use of larger grid-cells
helps to obtain smoother disparities, and it is especially effective for **occluded regions**."* And
small-only is *slower*, not faster: *"the use of the small-size cells is inefficient due to the increased
overhead in cost filtering."*

**Larger neighbourhoods help most in occluded regions** — which is our band entirely. That is a third argument,
after PatchMatch's weighted median and Schönberger's gated median, for Sprint 31's neighbourhood being
generous rather than minimal, and for sweeping its size over a *range of scales* rather than picking one.

### 4. Numbers, and the honest ones

- **Middlebury V2, 0.5 px**: best average rank **3.9**, bad-pixel **5.97%** among >150 methods.
- **Middlebury V3, bad 2.0 nonocc**: first of 64 methods, and first *"for all combinations of
  {bad 0.5, 1.0, 2.0, 4.0} × {nonocc, all} except for bad 4.0 – all."*
- **Seed stability** (Table 3, ten random initialisations): **6.63 ± 0.12** nonocc, **12.3 ± 0.2** all —
  *"our inference is stable by different random initializations."* The third paper in this corpus to measure
  seed-insensitivity and report it as a property of a good optimiser (after Boykov's 100 seeds and our own S51's
  five). The pattern is now unmistakable: **a well-posed energy is seed-insensitive, and seed-insensitivity
  says nothing about whether the energy is right.**
- **Ablation, Table 3** (15 V3 training pairs, nonocc): full **6.52**, without RANSAC proposer 6.65, **without
  post-processing 7.72**. So post-processing — left/right check plus weighted median filtering — is worth
  **1.2 points**, roughly ten times the RANSAC proposer's 0.13. The largest single component in their ablation
  is the **weighted median post-filter**, which is PatchMatch §2.3's, which is Sprint 31's.
- **Table 4** against Olsson (same energy, different optimiser): Teddy nonocc 3.98 vs 5.21; and *"without
  regularization"* 5.47 — so their regulariser is worth 1.5 points on Teddy and **17 points on Vintage**
  (5.65 vs 22.8), a large texture-less scene. Texture-less is our regime.
- Speed: 3.5–3.8× from four CPU cores, 19× from GPU unary costs, **5.3× from cost filtering**; the CPU
  guided-filter version matches the GPU bilateral one. Against PMBP: faster convergence, lower energy, better
  accuracy. Against PMF (local, no explicit smoothness): *"although energies are reduced almost monotonically in
  PMF, **the transitions of accuracies are not stable and even degrade after many iterations**"* — a local
  method converging to a bad minimum, visible only because they plot accuracy against time rather than reporting
  the endpoint.

### 5. Two remarks that bear on our architecture

**Propagation is itself a smoothness prior.** §4.7: *"**Spatial label propagation not only accelerates inference
but also introduces an implicit smoothness effect**, which helps our method to find smoother surfaces."* And
Fig. 15: Olsson's fusion result, *on the same energy*, is *"strongly biased to piecewise planar surfaces"* while
theirs is not. **The inference procedure leaves its own fingerprint on the answer, independently of the
energy** — which is the same lesson as Criminisi's fill order and Bornemann's skeleton, arriving for the third
time from a third direction. Our far-side law's propagation pattern (along lines, two axes, hand-built
arbitration) is therefore part of our prior whether we intend it or not.

**The slanted term is a second-order prior by itself.** *"The slanted patch matching term alone has an implicit
second-order smoothness effect, and the regularizer further enforces it especially for occluded or texture-less
regions."* Our plane far-side rule is the same kind of object: fitting planes rather than constants already
encodes "surfaces are locally flat", before any smoothness term is added. Worth knowing when reading Sprint 30's
results — part of the smoothness is already in the model.

### 6. Verdict on Sprint 32

**Re-scope it.** "Per-texel plane labels with propagation" as a port of this method is not available: it is a
move-making scheme for an energy with a photo-consistency data term, and the band has none. What transfers is
the **energy**, and the energy's transferable half is the curvature smoothness term `ψ̄` with its two-sided
clamp — which belongs in Sprint 30, not a separate sprint. The remainder of Sprint 32 (random plane
initialisation, halving perturbation, multi-scale neighbourhoods) is a set of tactics for Sprint 31's
neighbourhood design rather than a sprint of its own.

Which leaves the backlog: **Sprint 30** (capped, floored, contrast-modulated, *and curvature-aware* join cost),
**Sprint 31** (gated median, neighbourhood swept over scales), **#57** (class 2 as a connectivity cut, per
Shih/Shade), **#59** (connectivity-limited inpainting context), **#60** (second-pass cliff check), plus the new
class-3 crease item from Sinha. Sprint 32 dissolves into the others.
