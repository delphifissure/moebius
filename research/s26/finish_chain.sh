#!/bin/bash
cd /tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/ds
until grep -q "S1_CHAIN_DONE" dl_s1_chain.log; do sleep 20; done
python3 ds_score.py > score_final.txt 2>&1
python3 ds_sheet.py S2 S15 S26 S16 S11 S27 S12 S31 S32 S5 S7 S9 S10 P1 P2 P3 P4 P5 P6 > sheet_final.log 2>&1
python3 ds_table.py > table_final.log 2>&1
echo FINISH_DONE
