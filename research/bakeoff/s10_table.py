#!/usr/bin/env python3
"""S10 table: DA3 8-bit (photo_bo_da3mono) | DA3 16-bit raw (photo_da3_16) | DA3 16-bit + noise term (photo_da3_16n) | DA2 8-bit (photo_16q8) | DA2 16-bit raw (photo_16bit) | DA2 16-bit + noise (photo_da2_16n)"""
import re, subprocess, os, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/bakeoff')
SP='/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'; A='/home/user/moebiusv2/harness/shots/a257probe/'; U='/home/user/moebiusv2/harness/shots/ui_path/'
from bo_table import parse, logpart
cols=[('DA3 8-bit', parse(logpart(SP+'/bakeoff/logs/chain.log','probe da3mono')), 'photo_bo_da3mono', 'ui_bo_da3mono', '255'),
      ('DA3 16-bit, 1/255 fallback (§13)', parse(logpart(SP+'/s9_chain.log','probe da3_16 ')), 'photo_da3_16', 'ui_da3_16', '255'),
      ('DA3 16-bit, grid only (1/65535; floor off)', parse(logpart(SP+'/s10d_chain.log','probe da3_s10g')), 'photo_da3_s10g', 'ui_da3_s10g', '65535'),
      ('DA3 16-bit, visible-step floor (final)', parse(logpart(SP+'/s10d_chain.log','probe da3_s10d')), 'photo_da3_s10d', 'ui_da3_s10d', 'VIS'),
      ('DA3 16-bit, floor + a86 at step (removed)', parse(logpart(SP+'/s10_chain.log','probe da3_s10b')), 'photo_da3_s10b', 'ui_da3_s10b', 'VIS'),
      ('DA2 8-bit', parse(logpart(SP+'/s16real_chain.log','Q8')), 'photo_16q8', 'ui_16q8', '255'),
      ('DA2 16-bit, 1/255 fallback', parse(logpart(SP+'/s16real_chain.log','16BIT')), 'photo_16bit', 'ui_16bit', '255'),
      ('DA2 16-bit, visible step, a86 at grid', parse(logpart(SP+'/s10_chain.log','probe da2_s10a')), 'photo_da2_s10a', 'ui_da2_s10a', 'VIS')]
for name,r,d,ui,lv in cols:
    sec=(logpart(SP+'/s10d_chain.log','probe '+d.replace('photo_','')) if ('s10d' in d or 's10g' in d) else logpart(SP+'/s10_chain.log','probe '+d.replace('photo_',''))) if 's10' in d else ''
    m10=re.search(r'\[S10\] visible step 1/k = ([0-9.e+-]+) depth \(k = (\d+) px[^)]*\)[^;]*; effective quantum ([0-9.e+-]+)', sec)
    r['s9']=f"1/k {m10[1]} (k {m10[2]} px); q_eff {m10[3]}" if m10 else '(before S10)'
    if lv=='VIS': lv=str(int(round(1/float(m10[3])))) if m10 else '255'
    if not os.path.exists(A+d+'/meta.json'): r['seams']='not run'; continue
    out=subprocess.run(['python3',SP+'/seam_audit.py',A+d,lv],capture_output=True,text=True).stdout
    m=re.search(r'unjoined carrier-carrier plate edges: (\d+)', out); r['seams']=m[1] if m else '?'
    m=re.search(r'jump in units of tol: median ([\d.]+)', out); r['jump']=m[1] if m else '?'
    m=re.search(r'\| same axis \| same kind \| across lines \| same sheet \| (\d+) \|', out); r['xline']=m[1] if m else '?'
    m=re.search(r'source sheets.*?: (\d+)', out); r['sheets']=m[1] if m else '?'
    if os.path.isdir(U+ui):
        h=subprocess.run(['python3',SP+'/ui_holes.py',U+ui],capture_output=True,text=True).stdout
        r['holes']=' / '.join(l.split('|')[4].strip() for l in h.splitlines() if l.startswith('| 0.'))
keys=[('[S10] line','s9'),('source sheets under the join law','sheets'),('runs per row (median length)',None),('runs per column (median length)',None),('texels with a far side','far'),('  same-plane pairs','same'),('  crossings','cross'),('thin candidates / all','thin'),('second-layer texels','l2'),('reach % of plate','reach_pct'),('band at 15° / 25° / 35° / 45°',None),('carrier–carrier seams','seams'),('  same axis, same kind, across lines','xline'),('  jump median (tol)','jump'),('plate triangles torn','torn'),('holes on the path (px, seams stretched)','holes')]
print('| | '+' | '.join(c[0] for c in cols)+' |'); print('|---|'+'---|'*len(cols))
for label,k in keys:
    vals=[]
    for name,r,d,ui,lv in cols:
        if k=='thin': vals.append(f"{r.get('thin','?')} / {r.get('cand','?')}")
        elif label.startswith('runs per row'): vals.append(f"{r.get('rows_per','?')} ({r.get('row_med','?')})")
        elif label.startswith('runs per column'): vals.append(f"{r.get('cols_per','?')} ({r.get('col_med','?')})")
        elif label.startswith('band at'): vals.append(f"{r.get('b15','?')} / {r.get('b25','?')} / {r.get('b35','?')} / {r.get('b45','?')}")
        else: vals.append(str(r.get(k,'?')))
    print(f'| {label} | '+' | '.join(vals)+' |')
