#!/bin/bash
# S35 §30: when the forest truths (L1, L4) land, score comp / reach / reach-group / reach-things on them with the reach diagnostic
cd /home/user/moebius/research/s35
G=/home/user/moebiusv2/harness/shots; K=/home/user/moebiusv2/harness/truthkit/out; SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad
LOG=$SP/kitL_reach.log; : > $LOG
run() { echo "### $1 $(date +%T)" >> $LOG; shift; "$@" 2>&1 | grep -E "^stop|reach diag|j/E|reach by group|Trace|Error" >> $LOG; }
for S in L1 L4; do
  while ! grep -q "$S ALL DONE" $SP/kitL_$S.log 2>/dev/null; do sleep 60; done
  Q=$(awk -v s=$S '$1==s{print $2}' $SP/kitL_steps.txt | tail -1); [ -z "$Q" ] && Q=2.042e-3
  D=$G/a257probe/${S}_16plane
  (cd /home/user/moebiusv2/harness/truthkit && python3 check_app_band.py out/${S}_env45/scope_gt.npz ../shots/a257probe/${S}_16plane out/$S/rest_rgb.png out/$S/check_app16plane.png 2>&1 | tail -2 >> $LOG)
  for A in comp:"--closure comp" R:"--closure comp --reach" RG:"--closure comp --reach-group" RT:"--closure comp --reach-things"; do IFS=: read N F <<< "$A"
    run "$S $N" python3 sheets.py $D --truth $K/${S}_env45/scope_gt.npz --step $Q --q $Q --tag ${S}_$N --no-tps --things --mask $K/$S/truth_ids.png $F --reach-diag --out $D/s35_$N
    python3 bleed/kit_look.py $S $D $SP/${S}_$N.png s35_$N 2>&1 | grep class >> $LOG
  done
done
echo KITL_REACH_DONE >> $LOG
