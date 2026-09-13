#!/usr/bin/env python3
"""Live pass: a bake-panel select for the two recommended rules (ceiling cut, line-aware despeckle) so they can be tried on
screen without the console. Atomic writes (temp + os.replace) so a harness page never loads a half-written file."""
import os, sys
R = '/home/user/moebiusv2'


def patch(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        if old not in s: sys.exit(f'{path}: anchor not found: {old[:70]}')
        if s.count(old) != 1: sys.exit(f'{path}: anchor not unique: {old[:70]}')
        s = s.replace(old, new)
    tmp = path + '.tmp'; open(tmp, 'w').write(s); os.replace(tmp, path); print('patched', path)


SEL = ('<select id="bgPlateRulesSel" title="rules under review for the live pass (S20, S23): the ceiling cut (a wall continued above a '
       'ceiling is cut to it — the ground cut\'s mirror; S7 P 0.65 -> 0.86, inert without a ceiling) and the line-aware despeckle (a one-texel '
       'line of the 5x5 window\'s own length is not a fleck; S5 poles recall 0.51 -> 0.98)"><option value="cur" selected>rules: current</option>'
       '<option value="ceil">+ ceiling cut</option><option value="new">+ ceiling cut + line despeckle</option></select>')
JOIN_ANCHOR = '<option value="on">far field joined</option></select>'
for html in [f'{R}/moebius.html', f'{R}/harness/scratch_moebius.html']:
    patch(html, [(JOIN_ANCHOR + '</span>', JOIN_ANCHOR + '\n            ' + SEL + '</span>')])

patch(f'{R}/moebius.js', [
    ("band: 'bgPlateBandSel', sky: 'bgPlateSkySel', seams: 'bgPlateSeamSel', join: 'bgPlateJoinSel' };\n        const els = {};",
     "band: 'bgPlateBandSel', sky: 'bgPlateSkySel', seams: 'bgPlateSeamSel', join: 'bgPlateJoinSel', rules: 'bgPlateRulesSel' };\n        const els = {};"),
    ("band: 'all', sky: 'off', seams: 'torn', join: 'off' };", "band: 'all', sky: 'off', seams: 'torn', join: 'off', rules: 'cur' };"),
    ("            window._bgPlateOptions = Object.assign({}, opt);   // debug-sheet / HUD stamp\n        };",
     "            // live pass (S20 / S23): the two recommended rules as one select — current | + ceiling cut | + ceiling cut + line despeckle\n"
     "            window._ceilCut = (opt.rules === 'ceil' || opt.rules === 'new') ? 1 : 0;\n"
     "            window._despeckleLines = opt.rules === 'new' ? 1 : 0;\n"
     "            window._bgPlateOptions = Object.assign({}, opt);   // debug-sheet / HUD stamp\n        };"),
])
# harness: the UI-path driver's OPTS list gains the ninth select
patch(f'{R}/harness/ui_path.js', [
    ("'bgPlateSkySel', 'bgPlateSeamSel', 'bgPlateJoinSel'];   // OPTS may give 6 or 8 (seams, join)",
     "'bgPlateSkySel', 'bgPlateSeamSel', 'bgPlateJoinSel', 'bgPlateRulesSel'];   // OPTS may give 6, 8 or 9 (seams, join, rules)"),
    ("far: 'bgPlateFarSel', fill: 'bgPlateFillSel', margin: 'bgPlateMarginSel', faces: 'bgPlateFacesSel', band: 'bgPlateBandSel', sky: 'bgPlateSkySel', seams: 'bgPlateSeamSel', join: 'bgPlateJoinSel' }[k]",
     "far: 'bgPlateFarSel', fill: 'bgPlateFillSel', margin: 'bgPlateMarginSel', faces: 'bgPlateFacesSel', band: 'bgPlateBandSel', sky: 'bgPlateSkySel', seams: 'bgPlateSeamSel', join: 'bgPlateJoinSel', rules: 'bgPlateRulesSel' }[k]"),
])
