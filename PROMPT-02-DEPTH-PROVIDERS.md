# Brief — in-app depth and mask generation

A major addition, and a deliberate one. Read the scope bound in §2 before
starting: the deliverable of phase 1 is **a decision**, not a better renderer.

This does **not** block completion extent (a)/(b). Run it alongside or after,
but do not sequence the renderer work behind it.

## 1. Why

You established last round that the repository cannot say where the four depth
maps came from — no PNG metadata, no estimator named anywhere, no float sources,
bulk commits. They are 8-bit, and a133 prints that the geometry needs ~569
levels against the 255 the source carries.

But bit depth is the *least* interesting part. Count what in this arc is
renderer-side compensation for estimator error: stroke-depth repair (A34, 37,
39–42, 50, 51), the adopt-map, the footing rule, the wire rule,
ink-follows-layer, the star-party class (A55, A57b), the staff-lantern streak
(A57), cave-class ground collapse (A73), and the standing "troll-class assets
remain depth-limited — soft ramps, arm at BG depth" ceiling (A44, A47). That is
the single largest category of work in the arc.

The stop-list said quit doing renderer-side estimator repair. That is only
honest advice if the depth can improve — and right now it cannot, because the
depth cannot be regenerated at all.

So: bring depth and mask generation into the app, behind a provider
abstraction, with provenance enforced.

## 2. Scope bound — read this first

**Phase 1 is done when a human can open a comparison sheet and pick a depth
provider.** That is the whole deliverable.

Explicitly out of scope for phase 1:
- Do not switch the default asset depth.
- Do not re-pin `regress.js` bands.
- Do not touch the renderer, the bake, or the plate.
- Do not tune anything against a new depth map.
- Do not add a model because it is interesting. Two working providers plus
  legacy is enough to make the decision.

If phase 1 grows past "generate, compare, decide", stop and report.

## 3. Non-negotiables

**Float end to end, from the first byte.** A provider returns a `Float32Array`
plus dimensions. Never a PNG, never a canvas readback, never an 8-bit
intermediate. a99's float ingest is the consumer. **Run a89 on every provider
output and log the measured quantum** — a89 measures information, not container,
so it will catch any provider that silently round-trips through 8 bits. If a
provider's output measures as 8-bit, that is a bug in the provider, not a
property of the model.

**Provenance is mandatory and enforced.** Every generated depth carries a
sidecar record:

```json
{
  "providerId": "...", "modelId": "...", "revision": "...",
  "weightsSha256": "...", "licence": "Apache-2.0",
  "inputWidth": 851, "inputHeight": 1023,
  "modelInputWidth": 518, "preprocessing": "...",
  "settings": { }, "outputRange": "affine-invariant-inverse-depth",
  "generatedAt": "...", "appBuild": "v3.13.25-aNNN"
}
```

A depth map with no provenance record is loadable but **logs a loud warning at
bake time**. This is the gap you just found; close it permanently rather than
promising to remember.

**The legacy arm survives.** The four existing maps stay, registered as a
provider `legacy-8bit` with a provenance record that says `"unknown"` honestly.
The suite must be able to run both arms so nothing in the arc's history becomes
incomparable, and so any future change can be attributed to the depth or to the
code rather than being confounded.

**Licence is a first-class field.** Each provider declares its licence. The UI
shows it. A `permissiveOnly` toggle, **on by default**, hides anything that is
not OSI-permissive. CC-BY-NC models must be reachable for research comparison
but must never be the silent default.

## 4. The provider interfaces

Keep them small.

```
DepthProvider {
  id, displayName, licence, backend: 'onnx-web' | 'sidecar',
  available(): Promise<boolean>        // weights present / sidecar reachable
  estimate(imageBitmap, opts): Promise<{
      depth: Float32Array, width, height,
      convention: 'inverse-depth' | 'depth',
      provenance: {...}
  }>
}

MaskProvider {
  id, displayName, licence, backend,
  available(): Promise<boolean>
  segment(imageBitmap, opts): Promise<{
      masks: Array<{ rle | bitmap, score, bbox }>,
      provenance: {...}
  }>
}
```

Register implementations; do not hardwire a model anywhere else in the codebase.

### Phase 1 providers — in-browser

Run via ONNX Runtime Web (WebGPU with WASM fallback), most likely through
transformers.js since it already wraps the depth-estimation and SAM pipelines.
**Verify each model id and licence before wiring it** — do not take my names on
trust:

- **Depth Anything V2 Small** — Apache-2.0, ~25M params, ONNX available. The
  workhorse. *(Note: V2 Base/Large/Giant are CC-BY-NC — do not ship those as
  defaults.)*
- **DPT / MiDaS** — MIT, code and weights. The control arm; its mixed-dataset
  scale-shift-invariant training is precisely why it generalises off-domain, so
  it is a meaningful floor rather than a filler.
- **SAM 2 tiny** (or MobileSAM / SlimSAM if SAM 2 web inference proves too
  heavy) — Apache-2.0. Automatic mask generation, not interactive prompting, for
  phase 1.

### Phase 2 providers — sidecar

Define the contract in phase 1 so these plug in without a redesign; do not build
them yet. A minimal local HTTP endpoint, configurable URL, disabled by default:
POST an image, receive a float array plus provenance.

- **MoGe / MoGe-2** — MIT. Point map, normals, **and field of view**. The FOV
  output separately retires the frustum/lens/subject-pin guesswork (A67's "the
  mesh-scale law was wrong"). Highest-value phase-2 target.
- **Marigold** — Apache-2.0, synthetic-only training data, the literature's
  strongest generaliser to painted input. Multi-step diffusion, so sidecar only.
- **Depth Anything 3 Base / Mono-L** — Apache-2.0.

## 5. The comparison harness — this is the deliverable

Two halves: a number and a picture.

### 5a. The number — mask/depth boundary agreement

This is the point of generating masks in phase 1 even though nothing consumes
them yet. **SAM is good at finding boundaries on art; depth models are bad at
it.** So use the masks as the reference for *where* boundaries are, and measure
whether each depth provider puts a cliff there.

For every SAM mask edge pixel, find the nearest local maximum of |∇depth|:

- **median offset**, in px — how far the depth boundary sits from the object
  boundary. This is the "ink outline at background depth" and "the estimator
  smears the boundary" families (A34, A40, A57, A62, A69), as one number.
- **orphan rate** — fraction of mask edge pixels with no depth cliff within N px.
  This is D3's "45–92% of occluding edges never seed a band" recast against
  *object* boundaries instead of a depth threshold, which is the honest version
  of that measurement.

Report both per asset per provider. That turns "which estimator is better on
painted art" from an aesthetic judgement into a table.

### 5b. The picture — a fixed crop registry

Define the crops **once, as data**, so every comparison produces the same views
and the comparison is reproducible rather than ad hoc. Six per the arc's own
documented failures:

| crop | asset | what it tests | citation |
|---|---|---|---|
| troll arm | troll | arm entered at BG depth | A47, A76 |
| ink outline | frazetta / troll | thick ink at BG depth | A40, A41, A50 |
| star party | starwatcher | seated figures at 0.12 vs astronaut 0.307 | A55 |
| staff / lantern | starwatcher | 2px feature smearing to BG | A57, A84 |
| ground ramp | troll | ramp vs terraces | A73 |
| glider / thin | starwatcher | thin structure survival | D1, D7 |

Output a contact sheet: rows = providers (including `legacy-8bit`), columns =
crops, each cell showing depth-as-greyscale and a depth-gradient overlay. Plus
the 5a table underneath.

### 5c. The resolution control

Free, and it may change the answer. Run each provider at its **native model
input** and at **asset native**, and put both rows on the sheet. "The estimator
smears the boundary" recurs throughout the arc and may be an upsampling artifact
rather than a model-quality one. If native fixes it, that is a win independent
of which model wins — and it may make the incumbent look better than expected.

## 6. What a null result looks like, and why it is fine

If every provider scores about the same on 5a and nobody gets the troll's arm,
**that is the answer**: the depth ceiling on this asset class is real, no
estimator swap fixes it, and the priority shifts to ownership — segmentation and
layer-index — rather than a better depth model. Say so plainly. It is a cheap
and valuable thing to discover, and it is a legitimate outcome of phase 1.

## 7. Acceptance criteria

1. Two in-browser depth providers plus `legacy-8bit` produce float output on all
   four assets, with a89 confirming a sub-8-bit quantum on the new ones.
2. A mask provider produces masks on all four assets.
3. Every generated map has a complete provenance record; a map without one warns
   loudly at bake time.
4. `permissiveOnly` defaults on and hides non-permissive providers.
5. The comparison sheet renders: 5a table, 5b crops, 5c resolution rows.
6. `regress.js masks` ALL PASS, unchanged — because nothing in the renderer moved.
7. abguard applies: any provider A/B is void unless the arms diverge on a witness
   taken from inside the inference path.

## 8. Reporting

Report the 5a table and the contact sheet, and state a recommendation with the
reasoning — but **do not switch the default**. The pick is the user's; they are
the one who can look at the troll's arm and say whether it is right.
