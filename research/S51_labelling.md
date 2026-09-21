# S51 — Sprint 27: the cross-line labelling, with the reveal field as the join cost (2026-09-21)

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

**The refined diagnosis.** The streaky texture has two components with different causes:
- **long walls** — the axis arbitration flipping between neighbours. *This labelling halves them.*
- **fine horizontal hatching** — adjacent rows of one surface given two depths, median wall 3.3 px. **Nothing in the
  candidate set reaches this**, because both candidates are computed per line and the disagreement is between lines.

S22 tried to fix the second by regularising the law's parameters across lines and failed the bar; S32 tried smoothing
the field and made it worse; this sprint tried choosing between per-line candidates and does not reach it either.
**Three different constructions have now failed on class 1, and all three shared an assumption: that the fix can be made
downstream of a per-line extrapolation.** S33 said this in one line and it is worth quoting exactly: *"the fix is
upstream of any solve."*
