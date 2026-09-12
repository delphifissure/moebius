#!/usr/bin/env python3
"""B table: one row per picture x arm from b_chain.log, the probe dumps and the UI-path shots."""
import re, subprocess, json, os, sys, numpy as np
def logpart(log, tag):
    s = open(log).read(); i = s.find('=== ' + tag); j = s.find('\n=== ', i + 4); return s[i:j if j > 0 else None] if i >= 0 else ''
def parse(s):
    r = {}
    m = re.search(r'\[S3\] far side by the plane law: (\d+) row runs \(([\d.]+)/row, median length (\d+)\), (\d+) column runs \(([\d.]+)/col, median (\d+)\); texels with a far side (\d+) \(single (\d+), same plane (\d+), crossing (\d+), midpoint (\d+)\); (\d+) of (\d+) candidate extrapolations', s)
    if m: r.update(rows_per=m[2], row_med=m[3], cols_per=m[5], col_med=m[6], far=m[7], same=m[9], cross=m[10], thin=m[12], cand=m[13])
    m = re.findall(r'plate torn at its own rims: (\d+) of', s); r['torn'] = m[-1] if m else '?'
    m = re.search(r'second layer: (\d+) texels have one', s); r['l2'] = m[1] if m else '?'
    m = re.search(r'band by first-uncover angle: 15.?.?: (\d+), 25.?.?: (\d+), 35.?.?: (\d+), 45.?.?: (\d+)', s)
    if m: r.update(b15=m[1], b25=m[2], b35=m[3], b45=m[4])
    return r
SP = '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; A = '/home/user/moebiusv2/harness/shots/a257probe/'; U = '/home/user/moebiusv2/harness/shots/ui_path/'
LOG = SP + '/b_chain.log'; prep = json.load(open('/home/user/moebiusv2/harness/batchB/prepare_log.json'))
PICS = ['bristlecone', 'octopus', 'room', 'silverwarrior', 'starwatcher', 'vermeer']; ARMS = ['da3', 'da3s14', 'da3s14b', 'da3lines', 'da3f', 'repo8', 'repo8inv', 'da3sky']
rows = []
for P in PICS:
    for arm in ARMS:
        d = A + f'b_{P}_{arm}'; ui = U + f'ub_{P}_{arm}'
        if not os.path.exists(d + '/meta.json'): continue
        sec = logpart(SP + '/s13a.log', f'probe {P} lines') if arm == 'da3lines' else (logpart(SP + '/s14.log', f'probe {P} s14') if arm == 'da3s14' else (logpart(SP + '/s14.log', f'probe {P} s14b') if arm == 'da3s14b' else logpart(LOG, f'probe {P} {arm}'))); r = parse(sec)
        m14 = re.search(r'\[S14\] noise tiles: (\d+) of (\d+) \(([\d.]+)%\)[^;]*; per-texel quantum = ([0-9.e+-]+) \(the floor\) on ([\d.]+)% of texels', sec); r['tiles'] = (f'{m14[3]}% tiles, floor on {m14[5]}% texels' if m14 else '')
        mk = re.search(r'\[S13\] (\d+) minority texels kept', sec); r['kept'] = mk[1] if mk else ''; m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']; N = pw * ph
        r['pic'] = P; r['arm'] = arm; r['size'] = f'{pw}x{ph}'
        m10 = re.search(r'\[S10\] visible step 1/k = ([0-9.e+-]+) depth \(k = (\d+) px[^)]*\)[^;]*; effective quantum ([0-9.e+-]+)', sec)
        ma = re.search(r'a89: [^\n]*?grid[^\n]*', sec)
        r['q'] = (f'1/k {float(m10[1]):.2e}, k {m10[2]} px, q_eff {float(m10[3]):.2e}' if m10 else '?')
        ms = re.search(r'source noise \(diagnostic\)[^\n]*?sigma[^\d]*([0-9.e+-]+)', sec); r['sigma'] = ms[1] if ms else '?'
        dis = np.fromfile(d + '/disocc.u8', np.uint8) if os.path.exists(d + '/disocc.u8') else None; car = np.fromfile(d + '/carrier.u8', np.uint8) if os.path.exists(d + '/carrier.u8') else None
        r['band_pct'] = f'{100 * dis.mean():.1f}' if dis is not None else '?'; r['car_pct'] = f'{100 * car.mean():.1f}' if car is not None else '?'
        r['clones'] = str(m.get('cloneCount')); r['clonesF'] = str(m.get('cloneCountFinal'))
        lv = str(int(round(1 / float(m10[3])))) if m10 else '255'
        out = subprocess.run(['python3', SP + '/seam_audit.py', d, lv], capture_output=True, text=True).stdout
        ms = re.search(r'unjoined carrier-carrier plate edges: (\d+)', out); r['seams'] = ms[1] if ms else '?'
        ms = re.search(r'source sheets.*?: (\d+)', out); r['sheets'] = ms[1] if ms else '?'
        if os.path.isdir(ui):
            h = subprocess.run(['python3', SP + '/b_holes.py', ui], capture_output=True, text=True).stdout.splitlines()
            r['holes'] = ' / '.join(l.split('|')[2].strip() for l in h if '|' in l); r['dark'] = ' / '.join(l.split('|')[3].strip() for l in h if '|' in l)
        r['t_probe'] = ''
        rows.append(r)
cols = [('picture', 'pic'), ('arm', 'arm'), ('plate', 'size'), ('sheets', 'sheets'), ('far-side texels', 'far'), ('thin / cand', None), ('layer 2', 'l2'), ('band %', 'band_pct'), ('carriers %', 'car_pct'),
        ('band 15/25/35/45', None), ('torn', 'torn'), ('seams', 'seams'), ('clones (colour / final)', None), ('interior holes on the path (alpha 0 not touching the picture edge; offsets 0.05/0.1/0.2/0.301,0.068/0.26,0.088 m)', 'holes'), ('edge-connected alpha 0', 'dark'), ('quantum', 'q'), ('line rule kept', 'kept'), ('S14 noise tiles', 'tiles')]
print('| ' + ' | '.join(c[0] for c in cols) + ' |'); print('|' + '---|' * len(cols))
for r in rows:
    v = []
    for lab, k in cols:
        if lab == 'thin / cand': v.append(f"{r.get('thin','?')} / {r.get('cand','?')}")
        elif lab.startswith('band 15'): v.append(f"{r.get('b15','?')} / {r.get('b25','?')} / {r.get('b35','?')} / {r.get('b45','?')}")
        elif lab.startswith('clones'): v.append(f"{r.get('clones')} / {r.get('clonesF')}")
        else: v.append(str(r.get(k, '?')))
    print('| ' + ' | '.join(v) + ' |')
