#!/bin/bash
# S13a: the line-aware despeckle (window._despeckleLines=1) vs the current rule. Starts after the S13b diagnosis chain.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s13a.log; : > $LOG
while ! grep -q "=== DIAG DONE" $SP/s13_diag.log; do sleep 20; done
# 1. S5 poles (the motivating case) with the flag; the truth exists; tag _s13
: > $SP/kit_s13.log; TAGSUF=_s13 EXTRA=,_despeckleLines=1 bash $SP/kit_s7b3_chain.sh S5 S9 S11
# 2. the troll (striation combs, the rule's reason to exist): UI-path shots, both arms
for ARM in base lines; do FL=_tearLaw=rim; [ $ARM = lines ] && FL=$FL,_despeckleLines=1
  echo "=== ui troll $ARM $(date +%T)" >> $LOG
  IMG=defaultImgColor.png,defaultImgDepth.png TAG=s13_troll_$ARM OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=$FL OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
  echo "=== probe troll $ARM $(date +%T)" >> $LOG
  IMG=defaultImgColor.png,defaultImgDepth.png TAG=s13_troll_$ARM FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2$( [ $ARM = lines ] && echo ,_despeckleLines=1 ) timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
done
# 3. the six pictures with the flag (probe: clones, band, seams; the log line says how many texels the rule kept)
for P in bristlecone octopus room silverwarrior starwatcher vermeer; do
  echo "=== probe $P lines $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=b_${P}_da3lines FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2,_despeckleLines=1 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
done
echo "=== S13A DONE $(date +%T)" >> $LOG
