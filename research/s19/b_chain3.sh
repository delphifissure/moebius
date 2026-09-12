#!/bin/bash
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/b_chain.log
while ! grep -q "=== B2 DONE" $LOG; do sleep 20; done
P=bristlecone; A=repo8inv; D=harness/batchB/${P}_repo8inv.png
echo "=== probe $P $A $(date +%T)" >> $LOG
IMG=harness/batchB/${P}_color.png,$D TAG=b_${P}_${A} FLUSH=1 OBS=1 GATEA=1 FLAGS=_tearLaw=rim,_farRule=plane,_plugMargin=2 timeout 1500 node harness/a257_probe.js >> $LOG 2>&1
echo "=== ui $P $A $(date +%T)" >> $LOG
IMG=harness/batchB/${P}_color.png,$D TAG=ub_${P}_${A} OPTS=plane,wash,picture,off,35,off,stretched,off FLAGS=_tearLaw=rim OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088 timeout 1500 node harness/ui_path.js >> $LOG 2>&1
echo "=== B3 DONE $(date +%T)" >> $LOG
