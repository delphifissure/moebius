"""fillcheck.py <probe dir> <step> <dir>... : band texels whose fill is not behind the occluder (ff >= dQ - step: impossible), sky-valued
fill (< 0.02) share, and the share below the frame's lower third that is sky-valued (a ground that should be there)"""
import sys, json, numpy as np
P=sys.argv[1]; step=float(sys.argv[2]); m=json.load(open(P+'/meta.json')); pw,ph=m['pw'],m['ph']
band=np.fromfile(P+'/disocc.u8',np.uint8).reshape(ph,pw)>0; dQ=np.fromfile(P+'/dQ.f32',np.float32).reshape(ph,pw)
low=np.zeros((ph,pw),bool); low[2*ph//3:,:]=True
for d in sys.argv[3:]:
    try: ff=np.fromfile(f'{P}/{d}/farField_stop.f32',np.float32).reshape(ph,pw)
    except Exception: print(d,'missing'); continue
    try: who=np.fromfile(f'{P}/{d}/who_stop.i32',np.int32).reshape(ph,pw)
    except Exception: who=np.zeros((ph,pw),np.int32)
    unr=band&(who<0); imp=band&(who>=0)&(ff>=dQ-step); sky=band&(ff<0.02); print(f'{d:10}: band {int(band.sum())}; unreached {100*unr.sum()/band.sum():.1f} %; not behind occluder {int(imp.sum())} ({100*imp.sum()/band.sum():.1f} %); sky-valued {100*sky.sum()/band.sum():.1f} %; sky-valued in lower third {100*(sky&low).sum()/max(1,(band&low).sum()):.1f} % of {int((band&low).sum())}; fill median {np.median(ff[band]):.3f}')
