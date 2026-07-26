# Reply 02 — the screenshots, and 634 vs 63

Your point 5 is the headline of your whole message and it is sitting at
position five. Everything black in the user's four shots is that number.

## 1. What the shots show

Confident reads:

- **Large black regions, far bigger than any band.** Not 63 px of anything.
- **Black speckle in discrete trails** along the figure's left contour and the
  staff — dots, not regions. Torn quads with nothing behind them.
- **Bright smeared bands** through the figure in the two extreme poses — cliffs
  that did *not* tear, rubber-sheeting.
- **Enormous letterbox** at the extreme poses, content at ~40% of frame. That
  is the solid-angle collapse your HUD now measures (Ω 84%, subtense 43.6 →
  34.0). Expected, not a defect — worth telling the user so it stops reading
  as breakage.
- **Curved, curling frame edges.** Do not diagnose this yet — per your point 3
  it is a strong pre-distortion candidate. **Ask for the sim-view counterpart of
  these exact four poses before touching it.**

## 2. 634 vs 63 is not a parameter, it is the architecture

> *"At the 45° rim the reveal needs 634 source px of completion and the
> mark-dilation shader can carry 63 — 16×, not 1.1×."*

That is D2, measured at the live cone with the shipped code. The completion
machinery covers **one sixteenth** of the required extent, which is why the
black regions are large rather than fringe-sized.

The trap: 16× is not a dilation radius to raise. A 634 px dilation of a
silhouette produces 634 px of smear — a confident wrong answer, arguably worse
than black. **A dilation band cannot do this job at any radius**, because its
source is the silhouette rather than the background. The completion source has
to be the whole under-occluder region: `REVIEW.md` §4's "world without the
foreground", still not built.

## 3. The speckle and the tunnelling are one defect

Your point 8 supplies the mechanism: `fgTearStep = 0.06` is a hardcoded constant
and it is the cliff criterion, **0× with the cone**.

At k = 568 that threshold means a cliff must open ≥ **34 px** of reveal before
it tears. So:

- Cliffs **below** it never tear → the FG stays a connected rubber sheet →
  **the bright smeared bands**. D3 measured this population at 45–92% of all
  genuine occluding edges depending on asset.
- Cliffs **above** it tear → and open onto a plate that reaches 63 px →
  **the speckle and the black**.

One cone-blind constant, failing in both directions in the same frame.

**The correct threshold is not in depth units at all.** It is the reveal-benefit
gate: `Δδ·k ≥ 1 px`, i.e. Δδ ≥ 0.0018 at k = 568 — **33× lower than 0.06**.
Essentially every real edge should tear.

**But do not lower it yet.** a117 already measured what happens when you tear
aggressively without backing: 40% of the mesh dropped and a comb. The ordering
is forced:

> **Complete the plate → then lower the tear threshold.** Not the reverse.

Which makes completion extent, not the tear criterion, the next real work item.

## 4. a128 — your result stands, and the mechanism generalises

Accepted. Comb agrees with black, so the reopening fails and the stale step
ships. Your mechanism is the interesting part:

> *"at k=568 the fold-safe step is 0.00176 and one 8-bit quantum is 0.00392 —
> the fold-correct step is less than half the smallest step the source can
> express, so enforcing it flattens rather than protects."*

That is a general rule worth recording: **a constraint finer than the data
quantum is not correctness, it is noise amplification.** You cannot enforce a
limit your input cannot represent; enforcing it flattens everything that merely
*looks* steep because of quantisation. 71% of the plate lowered by up to half
the depth range is that, exactly.

So the reconciliation is: black% *was* blind (that stands), and the fold-correct
step loses *anyway*, for a reason neither of us had — the constraint is below the
quantum.

**One follow-up, and it may reverse the result:** is a99's float depth ingest
actually live on the plate path? If the plate is still built from an 8-bit
source, the fold-correct step will over-flatten by construction and can never
win. Worth one printed line — if float ingest is live and the quantum is
genuinely 0.00392, then the source itself is 8-bit upstream of the ingest, which
is a different and larger finding. Re-test a128 only after that is settled.

## 5. The SD bundle dependency — hoist it, don't keep v1

Good catch, and it is a one-line dependency rather than a reason to keep the
path. `bgExtendExport` being assigned only inside the v1 scene-extension block
is an accident of where the code grew, not a design. Hoist the assignment out;
the outpaint trio then emits regardless of which bake produced the plate.

Order stands: hoist the flag → repoint the 57 harness drivers at v2 → flag v1
off. The drivers are still the real work item and still not started.

## 6. Two dead flags in two sessions is a pattern

`_coneWide` read into a module-load `const`, then a flag that does not exist at
all. Both produced tables of identical numbers, and both were caught by a log
line rather than by the numbers looking wrong — because **a dead flag and a null
result are indistinguishable in the output.**

Standing precondition, cheap, and it is A2 generalised: **an A/B must prove its
arms differ before its numbers are read.** Not by logging the flag's value — by
logging a value *downstream* of the flag that differs between arms. If that
value is identical, the run is void and no table gets printed.

## 7. Revised next

The do-list order was written before 634-vs-63 was measured. Promoting one item:

1. **§4.4 ordering clamp** — unchanged. Cheap, unconditional, and it retires the
   backstop sweep's 60 s. Do it.
2. **Completion extent** — promoted to next. Make the plate the full
   under-occluder region rather than a dilation band. This is the change that
   turns the black in those shots into content, *and* the one that unblocks
   lowering the tear threshold to kill the smearing. It is `REVIEW.md` §4's
   original recommendation and it is still the largest unbuilt thing.
3. Then §4.5 / §4.6 / §4.7 as written.

`fgTearStep` becoming cone-derived is real and worth logging now, but do not
change its value until the plate can back it.

## 8. Credit where it is due

A1 catching a live fault on its first run — the camera restored before the check
read it, so every readout described a pose the frame was not rendered from — is
the amendment paying for itself immediately. Anchor drift 0.0000 px over 34
poses and A2's perturbation at ratio 1.0000 is a properly qualified instrument,
which this codebase has not always had.

And recording that the mode flatters the render (1.68 vs 3.16) instead of
enjoying it is the right call. The rule you drew — **sim viewer for shape,
hole accounting stays on pass 1** — should go in the process list.
