#!/usr/bin/env python3
"""Criterion 2/3 table over probes photo_bo_<m> (+ baselines photo_s7b0 = old map, photo_16q8 = DA2-Large at 8 bits)."""
import re, subprocess, json, sys, os, numpy as np
SP='/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; A='/home/user/moebiusv2/harness/shots/a257probe/'; U='/home/user/moebiusv2/harness/shots/ui_path/'
def logpart(log, tag):
    s=open(log).read()
    if tag: i=s.find('=== '+tag); j=s.find('\n=== ', i+4); s=s[i:j if j>0 else None]
    return s
def parse(s):
    r={}
    m=re.search(r'\[S3\] far side by the plane law: (\d+) row runs \(([\d.]+)/row, median length (\d+)\), (\d+) column runs \(([\d.]+)/col, median (\d+)\); texels with a far side (\d+) \(single (\d+), same plane (\d+), crossing (\d+), midpoint (\d+)\); (\d+) of (\d+) candidate', s)
    if m: r.update(rows_per=m[2], row_med=m[3], cols_per=m[5], col_med=m[6], far=m[7], same=m[9], cross=m[10], thin=m[12], cand=m[13])
    m=re.findall(r'plate torn at its own rims: (\d+) of', s); r['torn']=m[-1] if m else '?'
    m=re.search(r'\[S2b\] reach: (\d+) unjoined edges, (\d+) texels within.*?\(([\d.]+)% of the plate\)', s)
    if m: r['reach_pct']=m[3]
    m=re.search(r'second layer: (\d+) texels have one', s); r['l2']=m[1] if m else '?'
    m=re.search(r'band by first-uncover angle: 15.?.?: (\d+), 25.?.?: (\d+), 35.?.?: (\d+), 45.?.?: (\d+)', s)
    if m: r.update(b15=m[1], b25=m[2], b35=m[3], b45=m[4])
    m=re.search(r'sky class[^\n]*?(\d+)', s); 
    return r
cols=[('old map (Space model), 8-bit', parse(logpart(SP+'/s7b0_chain.log', None)), 'photo_s7b0', None),
      ('DA2-Large, 8-bit', parse(logpart(SP+'/s16real_chain.log','Q8')), 'photo_16q8', 'ui_16q8')]
for m in sys.argv[1:]:
    cols.append((m+', 8-bit', parse(logpart(SP+'/bakeoff/logs/chain.log', 'probe '+m)), 'photo_bo_'+m, 'ui_bo_'+m))
for name,r,d,ui in cols:
    if not os.path.exists(A+d+'/meta.json'): r['seams']='not run'; continue
    out=subprocess.run(['python3',SP+'/seam_audit.py',A+d,'255'],capture_output=True,text=True).stdout
    m=re.search(r'unjoined carrier-carrier plate edges: (\d+)', out); r['seams']=m[1] if m else '?'
    m=re.search(r'jump in units of tol: median ([\d.]+)', out); r['jump']=m[1] if m else '?'
    m=re.search(r'\| same axis \| same kind \| across lines \| same sheet \| (\d+) \|', out); r['xline']=m[1] if m else '?'
    m=re.search(r'source sheets.*?: (\d+)', out); r['sheets']=m[1] if m else '?'
    if ui and os.path.isdir(U+ui):
        h=subprocess.run(['python3',SP+'/ui_holes.py',U+ui],capture_output=True,text=True).stdout
        r['holes']=' / '.join(l.split('|')[4].strip() for l in h.splitlines() if l.startswith('| 0.'))
keys=[('source sheets under the join law','sheets'),('runs per row (median length)',None),('runs per column (median length)',None),('texels with a far side','far'),('  same-plane pairs','same'),('  crossings','cross'),('thin candidates / all','thin'),('second-layer texels','l2'),('reach % of plate','reach_pct'),('band at 15° / 25° / 35° / 45°',None),('carrier–carrier seams','seams'),('  same axis, same kind, across lines','xline'),('  jump median (tol)','jump'),('plate triangles torn','torn'),('holes on the path (px, seams stretched)','holes')]
print('| | '+' | '.join(c[0] for c in cols)+' |'); print('|---|'+'---|'*len(cols))
for label,k in keys:
    vals=[]
    for name,r,d,ui in cols:
        if k=='thin': vals.append(f"{r.get('thin','?')} / {r.get('cand','?')}")
        elif label.startswith('runs per row'): vals.append(f"{r.get('rows_per','?')} ({r.get('row_med','?')})")
        elif label.startswith('runs per column'): vals.append(f"{r.get('cols_per','?')} ({r.get('col_med','?')})")
        elif label.startswith('band at'): vals.append(f"{r.get('b15','?')} / {r.get('b25','?')} / {r.get('b35','?')} / {r.get('b45','?')}")
        else: vals.append(str(r.get(k,'?')))
    print(f'| {label} | '+' | '.join(vals)+' |')
