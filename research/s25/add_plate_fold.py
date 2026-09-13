#!/usr/bin/env python3
"""Sprint 17a: stretched plate pixels transparent. The A241 per-fragment stretch law (mode 1) already exists for the
foreground and the object-back layer; the plate was exempt (a126: the plate is the backstop). Behind window._plateFoldAlpha
the plate obeys the same law: a fragment whose cell is stretched past the fold (shift span > its own extent, i.e. stretch
> 2 relative to rest, A212/a102 — not a tuned constant) or is back-facing is discarded (value 1) or painted magenta as a
check view (value 2, to count spaghetti pixels on any arm). Atomic writes."""
import os, sys
R = '/home/user/moebiusv2'


def patch(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        if s.count(old) != 1: sys.exit(f'{path}: anchor count {s.count(old)} for: {old[:80]}')
        s = s.replace(old, new)
    tmp = path + '.tmp'; open(tmp, 'w').write(s); os.replace(tmp, path); print('patched', path)


patch(f'{R}/moebius.js', [
    # uniform table
    ("        u_fragTear: { value: 0.0 },\n        u_backTear: { value: 0.0 },",
     "        u_fragTear: { value: 0.0 },\n        u_plateFold: { value: 0.0 },          // Sprint 17a (window._plateFoldAlpha): the PLATE obeys the A241 stretch law too — 1 discard, 2 magenta check view\n        u_backTear: { value: 0.0 },"),
    # colour shader declarations
    ("        uniform float u_fragTear; uniform float u_fragTearGate; uniform float u_fragTearFactor; uniform float u_texelsPerPxRest; uniform float u_poseFrac;   // A241",
     "        uniform float u_fragTear; uniform float u_fragTearGate; uniform float u_fragTearFactor; uniform float u_texelsPerPxRest; uniform float u_poseFrac; uniform float u_plateFold;   // A241; Sprint 17a"),
    # colour shader: the plate joins the stretch law
    ("        } else if (u_fragTear > 0.5 && (!u_isBackgroundLayer || u_backTear > 0.5) && !isGap) {   // A257g: the object-back layer obeys the same stretch law as the foreground",
     "        } else if (u_fragTear > 0.5 && (!u_isBackgroundLayer || u_backTear > 0.5 || u_plateFold > 0.5) && !isGap) {   // A257g: the object-back layer obeys the same stretch law as the foreground; Sprint 17a: so does the plate when armed"),
    # colour shader: the plate discards (or paints magenta) a folded fragment
    ("        if (isGap && !u_isBackgroundLayer) discard;\n    `;",
     "        if (isGap && !u_isBackgroundLayer) discard;\n"
     "        // Sprint 17a: a plate cell stretched past the fold is not a surface (it is the spaghetti between a far carrier and\n"
     "        // its neighbour); with the fold-alpha armed it is transparent — what lies behind (plate 2, or nothing) shows —\n"
     "        // or magenta in the check view so the spaghetti pixels of any arm can be counted.\n"
     "        if (isGap && u_isBackgroundLayer && u_plateFold > 0.5) { if (u_plateFold > 1.5) { gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0); return; } discard; }\n    `;"),
    # depth pass declarations and law
    ("                    uniform float u_fragTear; uniform float u_fragTearGate; uniform float u_fragTearFactor; uniform float u_texelsPerPxRest; uniform float u_poseFrac; uniform float u_pxScale;",
     "                    uniform float u_fragTear; uniform float u_fragTearGate; uniform float u_fragTearFactor; uniform float u_texelsPerPxRest; uniform float u_poseFrac; uniform float u_pxScale; uniform float u_plateFold;"),
    ("                            if (u_backTear > 0.5 && u_fragTear > 0.5) {   // A257g: the same stretch law as the colour pass",
     "                            if ((u_backTear > 0.5 || u_plateFold > 0.5) && u_fragTear > 0.5) {   // A257g: the same stretch law as the colour pass; Sprint 17a: the plate too"),
    # arming on the plate material (plate 2 and the ring are clones of / share matQ)
    ("            matQ.uniforms.u_isBackgroundLayer.value = true;\n            matQ.uniforms.u_useEdgeMask.value = false;",
     "            matQ.uniforms.u_isBackgroundLayer.value = true;\n            matQ.uniforms.u_useEdgeMask.value = false;\n"
     "            // Sprint 17a (window._plateFoldAlpha = 1 | 2): the plate obeys the A241 stretch law — the same rest texel density and\n"
     "            // fold factor as the foreground (A212's criterion: shift span > cell extent <=> stretched past 2x at the fold), ungated.\n"
     "            if (window._plateFoldAlpha && matQ.uniforms.u_plateFold) {\n"
     "                const layerAspectP = pw / ph, frameAspectP = terrariumWidth / terrariumHeight; const layerWfP = (layerAspectP > frameAspectP) ? 1.0 : (layerAspectP / frameAspectP);\n"
     "                const plateScrPxP = Math.max(1, renderer.domElement.width * layerWfP);\n"
     "                matQ.uniforms.u_plateFold.value = (window._plateFoldAlpha === 2) ? 2.0 : 1.0; matQ.uniforms.u_fragTear.value = 1.0; matQ.uniforms.u_fragTearGate.value = 0.0;\n"
     "                matQ.uniforms.u_texelsPerPxRest.value = pw / plateScrPxP; matQ.uniforms.u_fragTearFactor.value = 2.0;\n"
     "                console.log('[S17a] plate fold-alpha armed (' + (window._plateFoldAlpha === 2 ? 'magenta check view' : 'transparent') + '): rest density ' + (pw / plateScrPxP).toFixed(3) + ' texels/px, fold at stretch 2');\n"
     "            } else if (matQ.uniforms.u_plateFold) { matQ.uniforms.u_plateFold.value = 0.0; }"),
])
