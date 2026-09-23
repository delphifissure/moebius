# S58 — S51's labelling solved exactly: the solver was a limit, and the energy still misses class 1 (2026-09-23)

**Question.** S51 (Sprint 27) chose, per band texel, between the far-side law's row and column continuations,
minimising the visible wall with ICM. It reached 33 % of the artefact wall against a 50 % bar. The paper
verification (S55, notes 10 and 20) found that result could not be read: ICM is the weak method in both
energy-minimisation papers we hold, and S51's restarts did not agree. Was the construction short, or was the
search?

**Method.** S51's energy is two-label and, with each texel's labels ordered by screen position, submodular, so one
s–t min-cut gives its **global** minimum. `moebiusv2/harness/s51_label.js` (new `DUMP=1`) writes the exact
quantities its own energy uses; `moebiusv2/harness/s51_mincut.py` builds the cut (PyMaxflow) and scores the result
with S51's own classes and visibility threshold. Troll, start-up defaults, the same bake S51 used.

**Guards, all passed.** The rerun reproduces S51 (before table identical; best ICM energy 437 677 in both runs;
seed identity 2.98e-8). Python's energy of ICM's labelling equals the JS energy (437 677.2 vs 437 677). Every pair
term checked submodular. The cut's value equals the energy of the labelling it returns. The cut is not worse than
ICM or the law on its own objective.

## Result

Visible wall in screen px at the rim, by S33 class (partition from the law's own choice):

| arm | class 1 (artefact) | class 2 (real step) | class 3 (artefact) | total wall | artefact 1+3 |
|---|---|---|---|---|---|
| the law (before) | 113 720 | 223 098 | 179 081 | 558 462 | — |
| ICM, best of 5 restarts (S51) | 107 329 (−5.6 %) | 198 664 (−11.0 %) | 87 491 (−51.1 %) | 437 677 | **−33.5 %** |
| **min-cut, λ = ∞ (exact)** | 104 128 (**−8.4 %**) | 175 524 (**−21.3 %**) | 36 284 (**−79.7 %**) | **353 333** | **−52.0 %** |
| min-cut, λ = 1 | 104 742 (−7.9 %) | 175 263 (−21.4 %) | 36 244 (−79.8 %) | 353 510 | −51.8 % |
| min-cut, λ = 0.25 | 105 569 (−7.2 %) | 175 456 (−21.4 %) | 37 103 (−79.3 %) | 355 575 | −51.3 % |

About 73 000 texels (47 % of the free ones) take a different axis from the law in the exact solution; ICM moved
18 145.

## What it settles

1. **The solver was a real limit.** ICM stopped 23.9 % above the true minimum of its own energy (437 677 vs
   353 333). The correction made in S55 notes 10/20 and S54 §4 was right: the "solver is not the bottleneck"
   reading was wrong.
2. **Numerically the construction clears the 50 % bar (52.0 %), but it fails the other half of the bar: real steps
   must survive, and they shrink 21.3 %** (twice ICM's 11.0 %). The exact minimum of a *wall-length* energy
   shortens every wall it can, real steps included — nothing in this energy says a class-2 step should stay.
   That is the failure Boykov, Veksler & Zabih §8.6 measure for uncapped penalties (oversmoothing), and it points
   at a capped join cost as the missing piece of the energy. That is a reading, not yet a test.
3. **Class 1 is not an axis-choice problem — now proven, not inferred.** S51's oracle bound said the candidate set
   held 60.8 % of class-1 headroom; the exact optimum reaches 8.4 %. The bound was loose (per-pair optima conflict),
   so for class 1 it was the label set, not the search. S51's standing conclusion stands with a firmer basis:
   class 1 needs different *candidates*, i.e. replacing the per-line law, which is what the sheet A/B (#63) tests.
4. **Almost all of the gain is class 3** (−79.7 %): making the row/column choice consistent removes most
   arbitration walls. S51 found class 3 was not what the eye saw on the troll (its A/B frames were
   indistinguishable at a 21 % wall cut).
5. **λ is inert again** (−52.0 / −51.8 / −51.3 %): the data term barely moves the answer.

## What it does not settle

Nothing here is on screen. S51's ported arm (`window._farLabel`, off) uses ICM; the exact labels are saved as
`shots/s51_label/troll/mincut_labels_*.npy` (not committed, `harness/shots/` is ignored) and could be rendered
against the law if wanted. Given point 2 (real steps eroded) and point 3 (class 1 untouched), it does not change the
course set in S57: the sheet A/B comes first. A capped join cost on the per-line law (Sprint 30, on hold) would now
be a meaningful test on this exact solver, since the solver can no longer hide the energy's behaviour.
