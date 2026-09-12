#!/bin/bash
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; A=/home/user/moebiusv2/harness/shots/a257probe; K=/home/user/moebiusv2/harness/truthkit/out; LOG=$SP/s15.log
while ! grep -q "=== S15 DONE" $LOG; do sleep 15; done
for X in "S15 $A/S15_16planesky_s12 65535 1 $K/S15_env45/scope_gt.npz" "S2 $A/S2_16plane_s12 65535 0 $K/S2_env45/scope_gt.npz" "S16 $A/S16_16plane_s12 65535 0 $K/S16_env45/scope_gt.npz" "photo8 $A/photo_bo_da3mono 255 0 " "photo16 $A/photo_da3_s10d 568 0 "; do set -- $X; echo "=== $1 both $(date +%T)" >> $LOG; MODE=both SKY=$4 python3 $SP/sheetfield3.py $2 $3 $5 >> $LOG 2>&1; done
echo "=== S15B DONE $(date +%T)" >> $LOG
