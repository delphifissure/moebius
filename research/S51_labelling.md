# S51 — Sprint 27: the cross-line labelling, with the reveal field as the join cost (2026-09-21)

> **Solved exactly 2026-09-23 (S58).** ICM stopped 23.9 % above this energy's true minimum. At the exact optimum the
> artefact wall falls 52.0 % (class 3 −79.7 %, class 1 −8.4 %) while real steps fall 21.3 %. The "the search is the
> limitation" correction below was right for the total and for class 3; for class 1 the oracle bound was loose and
> the label set is the limit, as the Standing section says.

S33 measured that **74 % of the troll's visible streak length is the far field disagreeing with itself**, and S50
confirmed the consequence: Sprint 26's cliff rules were all choosing how to draw a wall that should not exist. S22 named
the construction never attempted — a consistent *choice* across lines, a labelling over candidates with a join cost —
and said it was blocked on needing a weight between evidence and cross-line agreement "that nothing in the scene
supplies". S48's reveal field is that weight. This sprint builds it and measures it.

Instrument: `moebiusv2/harness/s51_label.js`. Nothing is built in the app.

## The formulation

The far-side law already emits, per texel, a **row-axis** and a **column-axis** continuation (`_geoFarAxV`) with each
one's own uncertainty (`_geoFarAxS`, the S7b audit: half the rim tolerance plus the slope uncertainty times the
distance). The arbitration picks one *per texel, independently*, which is why neighbours disagree. So:

> minimise over per-texel axis choices  Σᵢ data(i, lᵢ)  +  λ · Σᵢ~ⱼ revealPx(vᵢ, vⱼ)

Both terms in **screen pixels at the rim**. The smoothness term *is* the visible wall the eye integrates; the data term
prices a candidate's uncertainty through the same field. **λ = ∞ is parameter-free** — least visible wall subject to the
evidence — and is read first. Vertical pairs separate under the vertical half-angle and horizontal pairs under the
horizontal, because the envelope is rectangular.

Scoring uses S33's classification computed on the **original** choice, so the question is conservative: did the walls
that *were* artefacts get shorter, and did the real steps survive.

## Two instrument failures before any number was readable

**1. A unit error that produced a plausible table.** The first run reported the artefact wall rising 992 %. The cause:
`_geoFarAxV` holds the extrapolated **disparity**, not normalised depth — the law converts it afterwards by bisection on
the rim law's table and clamps at the texel's visible depth. `before` was scored in d and `after` in disparity. The
diagnostic that gave it away was one I had printed almost by accident: *"field moved: mean 2.69 in d"*, in a quantity
bounded by [0, 1].

**2. The guards that now make it self-checking.** A **seed identity** — at the law's own labelling the reconstructed
field must equal `ff`, printed every run and fatal above 1e-3 — and a **range check** on the field movement. The
corrected run reports `max |cand[law choice] − ff| = 2.98e-8`.

This is the third instrument defect in two sprints that produced readable-looking numbers from a broken state (after
S50's inert `fold` arm and S48's degenerate-form solve). Each now has a guard; the pattern is recorded in the plan.

## The result, λ = ∞ (troll, 258 610 band texels, 60.0 % with both candidates)

ICM, red-black, 25 sweeps to convergence; 17 947 texels relabelled (11.6 % of the free set). Field moved a mean of
0.00395 in d.

| | before | after | change |
|---|---|---|---|
| **class 1** — same surface, two depths | 113 720 px (41 144 bends) | 108 474 px (38 863) | **−4.6 %** |
| class 2 — a real step (must survive) | 223 098 px (18 655) | 198 745 px (16 946) | −10.9 % |
| **class 3** — axis arbitration flipping | 179 081 px (19 908) | 87 609 px (10 893) | **−51.1 %** |
| **artefact (1 + 3)** | **292 801 px** | **196 083 px** | **−33.0 %** |
| total visible wall | 558 462 px | 438 955 px | −21.4 % |

**The bar was 50 % on the artefact classes with class 2 surviving. It misses, at 33 %.**

## What the composition says, which matters more than the miss

1. **Class 3 halved. The mechanism works exactly where it was designed to.** Making the row/column choice spatially
   coherent removes half the arbitration seams — and class 3 is only 12.3 % of bends by count but **35.1 % by wall
   length**, the long walls. So the labelling attacks the long-streak component of the texture.
2. **Class 1 barely moved (−4.6 %), and it is 77 % of bends by count.** The hypothesis stated in advance — that for a
   vertical bend the column candidate is continuous by construction, so switching axis removes the disagreement — **is
   not borne out**. When two rows both extrapolate along the row axis and disagree, the column candidate is usually not
   better, so a two-label choice cannot reach it. **Class 1 is not an axis-choice problem.**
3. **Class 2 fell 10.9 %, more than class 1.** λ = ∞ erodes real steps faster than it fixes same-surface disagreement.
   That is precisely the failure the class-2 column exists to catch, and it is the argument for a finite λ.

## CORRECTION — the conclusion above was wrong, and the oracle bound says so

The paragraph that stood here concluded that **"nothing in the candidate set reaches class 1"** and that three
constructions had now failed for the same structural reason. **That was drawn from one greedy search and it is wrong.**

The check that settles it is an **oracle bound**: for each visible bend, take the best of the four label combinations
*for that pair alone*, ignoring that neighbours share labels. That is a strict upper bound on what any labelling could
achieve, a perfect optimiser included.

| class | wall now | best possible | headroom |
|---|---|---|---|
| 1 — same surface, two depths | 113 720 | 44 544 | **60.8 %** |
| 2 — real step | 223 098 | 158 611 | 28.9 % |
| 3 — axis flip | 179 081 | 11 936 | **93.3 %** |
| **artefact (1 + 3)** | **292 801** | **56 480** | **80.7 %** |

**Class 1 has 60.8 % of headroom inside the existing candidate set**, and the ICM found 4.6 % of it. So the label set is
not the limitation — the search is. The structural claim was a generalisation from a weak optimiser, and it should have
been checked with this bound *before* it was written, not after.

**What is established, and what is not.**

- *Established*: the reveal field works as a join cost, class 3 halves under a greedy search, and λ is inert (∞, 1 and
  0.25 give 33.0 / 32.8 / 33.0 %). **That inertness retires S22's stated blocker** — it said this construction needed a
  weight between evidence and agreement "that nothing in the scene supplies", and the construction turns out not to
  depend on that weight at all.
- *Not established*: whether the construction clears the 50 % bar. ICM gives 33 %; the bound allows 80.7 %; restarts
  from eight seeds do not improve on the law's own (energy 438 955 against 440 523 all-row, 507 839 all-column,
  458–464 k random), so the law's choice is already the best basin found by descent.

**The exact answer is available and cheap in principle.** If each texel's two candidates are ordered by value (label 0 =
the smaller), the pairwise term |v_i − v_j| satisfies the Monge condition and the binary energy is **submodular**, so a
single s–t min-cut gives the **global** optimum rather than a local one. That converts "ICM got 33 %, the bound allows
80.7 %" into a number, and it is the difference between shelving this construction and porting it.

## The verdict: measured improvement, no visible improvement

Ported behind `window._farLabel` (off by default, ~40 lines at a clean integration point) and rendered on the troll at
45 degrees against the shipped per-line field.

| | per-line (shipped) | cross-line labelling |
|---|---|---|
| placeholder | 34.882 % | 34.461 % |
| hole | 30.652 % | 30.651 % |
| bounded hole | 0.0113 % | 0.0106 % |
| leaks (T=1) | 16 | 15 |
| **pixels differing between the two frames** | — | **1.39 %** |

**The frames are indistinguishable.** A 21 % cut in total wall length and a halving of the long-wall class produce a
0.42-point change in placeholder, no change in hole, and nothing the eye can find. `research/s51_ab.png`.

**Why, and it is the sprint's real output.** The visible hatching is **class 1**, and class 1 is precisely what a
consistent axis choice does not fix in practice (-4.6 %). The class the labelling does halve, class 3, was not what was
visible. And the area instruments cannot see the change at all, because wall length is a property of the plate's
*shape* while placeholder and hole are properties of its *coverage*.

## This reverses the sprint order, and the reversal is evidence-driven

S49 put the geometry ahead of the inpaint on the argument that "painting content into a band whose geometry still combs
leaves the outline ragged". **That argument is not testable in the current state.** Invented colour is smooth enough to
hide a 21 % change in the plate's shape, so a geometry fix cannot be judged on screen while the band is a wash.

**Content first.** Not because the geometry does not matter — class 1 will shear visibly once there is real texture on
that surface, and the fix becomes judgeable then — but because right now it is unfalsifiable by the only authority the
project recognises.

## Standing

- `window._farLabel` stays, off, with its numbers in the code comment. It did not earn a default on this evidence and
  may earn one once the band carries content.
- **S22's stated blocker is retired**: lambda is inert from 0.25 to infinity, so the construction never needed the
  weight S22 said nothing in the scene supplies.
- **Class 1 remains open after three constructions** (S22 parameter smoothing, S32 field smoothing, S51 labelling). The
  label set holds 60.8 % of headroom on it that consistent labelling cannot realise, so the next attempt must change
  what the candidates *are* — that is, stop extrapolating per line — which is what S33 said a week before this sprint.
