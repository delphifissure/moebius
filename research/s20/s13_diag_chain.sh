#!/bin/bash
# S13b diagnosis: sweep class maps at the far poses on the three pictures with interior holes (fractions of the 45-degree rim:
# 1:0 = 0.2 m; 1.3:0.44 = (0.26, 0.088) m; 1.505:0.589 = (0.301, 0.068) m)
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s13_diag.log; : > $LOG
for P in silverwarrior vermeer room; do
  echo "=== probe $P $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=s13_${P} FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2 POSES=1:0,1.3:0.44,1.505:0.589,-1:0 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
done
echo "=== DIAG DONE $(date +%T)" >> $LOG
