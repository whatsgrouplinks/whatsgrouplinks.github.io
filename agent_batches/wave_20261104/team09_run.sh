#!/bin/bash
# Team09 orchestrator: wait for egress, run stage1 + stage2, flag done.
cd ~/workspace/whatsapp-groups-site/agent_batches/wave_20261104
FLAG=team09_egress.ok
LOG=team09_run.log
: > $LOG
echo "[$(date -u +%FT%TZ)] waiting for egress" | tee -a $LOG
TRIES=0
while [ $TRIES -lt 45 ]; do
  if curl -s -o /dev/null -m 15 -A "Mozilla/5.0" "https://example.com" 2>/dev/null; then
    echo "[$(date -u +%FT%TZ)] egress OK after $TRIES tries" | tee -a $LOG
    touch $FLAG
    break
  fi
  TRIES=$((TRIES+1))
  sleep 90
done
if [ ! -f $FLAG ]; then
  echo "[$(date -u +%FT%TZ)] egress never recovered" | tee -a $LOG
  exit 2
fi
echo "[$(date -u +%FT%TZ)] stage1 start" | tee -a $LOG
python3 team09_stage1.py >> $LOG 2>&1
echo "[$(date -u +%FT%TZ)] stage1 done rc=$?" | tee -a $LOG
echo "[$(date -u +%FT%TZ)] stage2 start" | tee -a $LOG
python3 team09_stage2.py >> $LOG 2>&1
echo "[$(date -u +%FT%TZ)] stage2 done rc=$?" | tee -a $LOG
touch team09_pipeline.done
