#!/bin/bash
# The hole contract test: bake the three far-pose-hole pictures with the band built to a 60-degree envelope (the shots at
# 52/24 and 56/19 degrees then lie INSIDE the envelope the band was built for) — recommended rules on, seams stretched,
# margin picture — and count holes at the same five poses as the live chain's cur/cand arms.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/env60_chain.log
while ! grep -q "=== LIVE DONE" $SP/live_chain.log 2>/dev/null; do sleep 30; done
: > $LOG
for P in silverwarrior vermeer room; do
  echo "=== ui $P env60 $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=ul_${P}_env60 ENV=60 OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim,_ceilCut=1,_despeckleLines=1 OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
done
echo "=== ENV60 DONE $(date +%T)" >> $LOG
