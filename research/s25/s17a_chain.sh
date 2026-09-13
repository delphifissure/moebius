#!/bin/bash
# Sprint 17a verification (after add_rules_select.py and add_plate_fold.py are applied):
#  - rules select: OPTS 9th value 'new' must reproduce the FLAGS cand arm (a134: the panel path and the flag path are the same bake)
#  - plate fold-alpha: transparent (fold1) and the magenta check view (fold2) at the 45-degree and 60-degree bakes on the two
#    far-pose-hole pictures; holes by b_holes, spaghetti pixels by p_spaghetti
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/s17a_chain.log; : > $LOG
OFFS=0.05:0,0.1:0,0.2:0,0.301:0.068,0.26:0.088
run() { # pic tag env opts flags
  echo "=== ui $1 $2 $(date +%T)" >> $LOG
  IMG=harness/batchB/$1_color.png,harness/batchB/$1_da3_16.png TAG=ul_$1_$2 ENV=$3 OPTS=$4 FLAGS=$5 OFFS=$OFFS timeout 1500 node harness/ui_path.js >> $LOG 2>&1
}
# the rules select against the flag arm (silverwarrior; the cand arm's shots exist from the live chain)
run silverwarrior rulesnew 0 plane,wash,picture,off,35,off,stretched,off,new _tearLaw=rim
# fold-alpha arms: current seams (stretched) + the fold law on the plate; 45 and 60 degree bakes
for P in silverwarrior vermeer; do
  run $P fold1_45 0  plane,wash,picture,off,35,off,stretched,off,new _tearLaw=rim,_plateFoldAlpha=1
  run $P fold2_45 0  plane,wash,picture,off,35,off,stretched,off,new _tearLaw=rim,_plateFoldAlpha=2
  run $P fold1_60 60 plane,wash,picture,off,35,off,stretched,off,new _tearLaw=rim,_plateFoldAlpha=1
  run $P fold2_60 60 plane,wash,picture,off,35,off,stretched,off,new _tearLaw=rim,_plateFoldAlpha=2
done
# the magenta check view on the plain stretched arm at 60 degrees tells how much spaghetti the 60-degree bake still draws
echo "=== S17A DONE $(date +%T)" >> $LOG
