#!/bin/bash
# S13b, second look: which plate option closes the far-pose holes — step faces (rim step gaps), margin=window (frame edge), seams torn vs stretched.
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s13b2.log; : > $LOG
while ! grep -q "=== S13A DONE" $SP/s13a.log; do sleep 20; done
for P in silverwarrior vermeer room; do for V in faces=on margin=window; do
  echo "=== ui $P $V $(date +%T)" >> $LOG
  IMG=harness/batchB/${P}_color.png,harness/batchB/${P}_da3_16.png TAG=s13b_${P}_${V/=/_} OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim OFFS=0.1:0,0.2:0,0.301:0.068,0.26:0.088 THEN=$V timeout 1500 node harness/ui_path.js >> $LOG 2>&1
done; done
echo "=== S13B2 DONE $(date +%T)" >> $LOG
