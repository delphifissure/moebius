#!/bin/bash
# Sprint 16: probe + score each porous scene as soon as its truth exists (serial browser use)
cd /home/user/moebiusv2 || exit 1
SP=/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad; LOG=$SP/p_probe.log; : > $LOG
done_list=""
while true; do
  for S in P5 P6 P1 P2 P3 P4; do
    case " $done_list " in *" $S "*) continue;; esac
    if [ -f harness/truthkit/out/${S}_env45/scope_gt.npz ] && ! pgrep -f "scope.py $S " > /dev/null; then
      echo "=== scene $S $(date +%T)" >> $LOG; TAGSUF=_c EXTRA= bash $SP/kit_s7b3_chain.sh $S >> $LOG 2>&1; done_list="$done_list $S"
    fi
  done
  n=$(echo $done_list | wc -w); [ "$n" -ge 6 ] && break
  grep -q "=== P TRUTH DONE" $SP/p_truth_A.log 2>/dev/null && [ "$n" -lt 6 ] && sleep 30 && continue
  sleep 60
done
echo "=== P PROBES DONE $(date +%T)" >> $LOG
