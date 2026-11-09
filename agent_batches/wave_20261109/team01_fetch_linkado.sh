#!/usr/bin/env bash
# Team 01 wave 20261109 - step 1b: fetch linkado /grupo/ detail pages (3 parallel), extract invite codes.
set -u
WAVE="$HOME/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
RAW="$WAVE/team01_raw_linkado"
mkdir -p "$RAW"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
fetch_one() {
  local idx="$1" url="$2"
  local out="$RAW/g$idx.html"
  if [ -s "$out" ]; then echo "cached $idx"; return 0; fi
  curl -s -L -A "$UA" --max-time 30 -o "$out" -w "%{http_code}" "$url" > "$RAW/g$idx.code" 2>/dev/null
  sleep 0.5
}
export -f fetch_one
export RAW UA
# args: file with one URL per line
cat "$1" | nl -ba | sed 's/^[[:space:]]*//' | tr '\t' ' ' | xargs -P 3 -n 2 bash -c 'fetch_one "$0" "$1"' 2>/dev/null
echo DONE
