# S23 — Sprint 16: the persistent-departure segmentation reopened; the porous-silhouette scene set (2026-09-12)

## 1. Persistent departure, along the line (a different criterion from §15's)

§15 closed the *cross-line* version at step 0: 99.6 % of DA3-16's run breaks are already supported by a break on an
adjacent line within one position — the surplus over 8 bits is coherent creases, not isolated triples. The reopened
criterion is **along** the line and needs no neighbour: a departure of one sample that the next sample does not continue
is an outlier, not a break, because one sample cannot establish a new line (two define one). The run's last two samples
predict the sample after the departure as 3·D[a] − 2·D[c]; three samples each within q/2 of the truth put that two-step
prediction within 1.5 tol (tol bounds one step, 2q of slope; two steps, 3q). If the prediction holds, the departing sample
is skipped — masked out of the run's fits — and the run continues through it. No constant beyond the law's own tolerance.

Offline in the reproduction of the law (`s23/sheetfield3.py`, `SEG=persist`), against the app's own segmentation:

| source | breaks skipped | runs per row / column | same-sheet seams (reproduction's own → persist) | truth |
|---|---:|---|---|---|
| photograph DA3 16-bit (visible-step quantum) | 394 | 10.3 / 9.6 → 10.2 / 9.4 | 27 782 → **29 983 (+8 %)** | — |
| photograph DA3 8-bit | 1 275 | 7.7 / 7.2 → 7.5 / 6.8 | 38 114 → 38 397 (+1 %) | — |
| S15 hill + tree | 218 | 20.8 / 16.2 → 20.7 / 16.1 | 2 465 → 2 468 | median 0.237 → 0.238 m |
| S2, S26 | 0 | unchanged | unchanged | unchanged |

Single-sample departures are rare on every source (3.7 % of the 16-bit troll's breaks, 1.6 % of the 8-bit's, 1 % on
S15, none on the planar scenes), which is §15's finding seen from the other side: the breaks are creases that persist.
Skipping the few that do not persist shortens no runs worth speaking of and adds seams, since a run that now spans a
skipped sample fits a slightly different line than its neighbours' runs do. **Falsified; nothing built in the app.** With
this, both readings of "persistent departure" — supported across lines (§15) and persisting along the line (here) — are
closed by measurement: the run structure on a DA3 map is what the map's creases dictate, not what a segmentation rule
leaves in.

## 2. The porous-silhouette scene set

*(truth builds running; results follow)*
