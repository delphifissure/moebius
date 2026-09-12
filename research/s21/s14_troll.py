#!/usr/bin/env python3
"""S14 troll DA3-16: the S10 baseline (global floor, sigma > 0) vs the per-tile map."""
import re, subprocess, json, os, sys
SP='/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; A='/home/user/moebiusv2/harness/shots/a257probe/'; U='/home/user/moebiusv2/harness/shots/ui_path/'
exec(open(SP+'/b_table.py').read().split('SP = ')[0].split('import re')[1].join(['import re','']) if False else '')
def logpart(log, tag):
    s=open(log).read(); i=s.find('=== '+tag); j=s.find('\n=== ', i+4); return s[i:j if j>0 else None] if i>=0 else ''
def parse(s):
    r={}
    m=re.search(r'\[S3\] far side by the plane law: (\d+) row runs \(([\d.]+)/row, median length (\d+)\), (\d+) column runs \(([\d.]+)/col, median (\d+)\); texels with a far side (\d+) \(single (\d+), same plane (\d+), crossing (\d+), midpoint (\d+)\); (\d+) of (\d+) candidate extrapolations', s)
    if m: r.update(rows_per=m[2], row_med=m[3], cols_per=m[5], col_med=m[6], far=m[7], same=m[9], cross=m[10], thin=m[12], cand=m[13])
    m=re.findall(r'plate torn at its own rims: (\d+) of', s); r['torn']=m[-1] if m else '?'
    m=re.search(r'second layer: (\d+) texels have one', s); r['l2']=m[1] if m else '?'
    m=re.search(r'band by first-uncover angle: 15.?.?: (\d+), 25.?.?: (\d+), 35.?.?: (\d+), 45.?.?: (\d+)', s)
    if m: r.update(b15=m[1], b25=m[2], b35=m[3], b45=m[4])
    m=re.search(r'\[S14\] noise tiles: (\d+) of (\d+) \(([\d.]+)%\)', s); r['tiles']=(m[3]+'%') if m else '-'
    return r
cols=[('S10 baseline (global floor)', parse(logpart(SP+'/s10d_chain.log','probe da3_s10d')), 'photo_da3_s10d', 'ui_da3_s10d'),
      ('S14 rule 1 (sigma3 level)', parse(logpart(SP+'/s14.log','probe troll da3_16 s14')), 'photo_da3_s14', 'ui_da3_s14'),
      ('S14 rule 2 (gate per tile)', parse(logpart(SP+'/s14.log','probe troll da3_16 s14b')), 'photo_da3_s14b', 'ui_da3_s14b')]
for name,r,d,ui in cols:
    if not os.path.exists(A+d+'/meta.json'): r['seams']='not run'; continue
    m=json.load(open(A+d+'/meta.json')); r['clones']=str(m.get('cloneCount'))
    out=subprocess.run(['python3',SP+'/seam_audit.py',A+d,'568'],capture_output=True,text=True).stdout   # 1/1.76e-3 = the visible step
    mm=re.search(r'unjoined carrier-carrier plate edges: (\d+)', out); r['seams']=mm[1] if mm else '?'
    if os.path.isdir(U+ui):
        h=subprocess.run(['python3',SP+'/b_holes.py',U+ui],capture_output=True,text=True).stdout.splitlines(); r['holes']=' / '.join(l.split('|')[2].strip() for l in h if '|' in l)
keys=[('noise tiles','tiles'),('runs per row (median length)',None),('runs per column (median length)',None),('texels with a far side','far'),('same-plane pairs','same'),('thin candidates / all',None),('second-layer texels','l2'),('band 15/25/35/45',None),('plate triangles torn','torn'),('carrier-carrier seams','seams'),('clones (colour stage)','clones'),('interior holes on the path (0.05/0.1/0.2/0.301,0.068/0.26,0.088 m)','holes')]
print('| | '+' | '.join(c[0] for c in cols)+' |'); print('|---|---|---|---|')
for label,k in keys:
    v=[]
    for name,r,d,ui in cols:
        if label.startswith('runs per row'): v.append(f"{r.get('rows_per','?')} ({r.get('row_med','?')})")
        elif label.startswith('runs per col'): v.append(f"{r.get('cols_per','?')} ({r.get('col_med','?')})")
        elif label.startswith('thin'): v.append(f"{r.get('thin','?')} / {r.get('cand','?')}")
        elif label.startswith('band'): v.append(f"{r.get('b15','?')} / {r.get('b25','?')} / {r.get('b35','?')} / {r.get('b45','?')}")
        else: v.append(str(r.get(k,'?')))
    print(f'| {label} | '+' | '.join(v)+' |')
