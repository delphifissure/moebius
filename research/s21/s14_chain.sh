#!/bin/bash
# S14: per-region noise map (window._noiseTiles=1). Kit identity/score, troll DA3-16 vs the S10 baseline, the six pictures (probe + UI shots).
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s14.log; : > $LOG
: > $SP/kit_s14.log; TAGSUF=_s14 EXTRA=,_noiseTiles=1 bash $SP/kit_s7b3_chain.sh S15 S32 S31 S2 S11 S7
echo "=== probe troll da3_16 s14 $(date +%T)" >> $LOG
IMG=defaultImgColor.png,depth_da3mono16.png TAG=photo_da3_s14 FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2,_noiseTiles=1 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
echo "=== ui troll da3_16 s14 $(date +%T)" >> $LOG
IMG=defaultImgColor.png,depth_da3mono16.png TAG=ui_da3_s14 OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim,_noiseTiles=1 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
for P in bristlecone octopus room silverwarrior starwatcher vermeer; do
  echo "=== probe $P s14 $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=b_${P}_da3s14 FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2,_noiseTiles=1 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
  echo "=== ui $P s14 $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=ub_${P}_da3s14 OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim,_noiseTiles=1 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
done
echo "=== S14 DONE $(date +%T)" >> $LOG
