#!/bin/bash
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; A=/home/user/moebiusv2/harness/shots/a257probe; K=/home/user/moebiusv2/harness/truthkit/out; LOG=$SP/s16seg.log; : > $LOG
for X in "photo16 $A/photo_da3_s10d 568 0 " "photo8 $A/photo_bo_da3mono 255 0 " "S15 $A/S15_16planesky_s12 65535 1 $K/S15_env45/scope_gt.npz" "S2 $A/S2_16plane_s12 65535 0 $K/S2_env45/scope_gt.npz" "S26 $A/S26_16plane_s12 65535 0 $K/S26_env45/scope_gt.npz"; do set -- $X
  for SEG in none persist; do echo "=== $1 $SEG $(date +%T)" >> $LOG; MODE=own SEG=$SEG SKY=$4 python3 $SP/sheetfield3.py $2 $3 $5 >> $LOG 2>&1; done
done
echo "=== SEG DONE $(date +%T)" >> $LOG
