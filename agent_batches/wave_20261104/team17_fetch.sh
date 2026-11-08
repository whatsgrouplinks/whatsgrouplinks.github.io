#!/bin/bash
cd /home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for slug in "$@"; do
  out="team17_cat_${slug}.html"
  if [ -s "$out" ] && [ $(stat -c%s "$out") -gt 100000 ]; then echo "SKIP $slug (have $(stat -c%s "$out")b)"; continue; fi
  echo "FETCH $slug ..."
  curl -s --max-time 180 --retry 2 --retry-delay 5 -A "$UA" "https://www.groupor.link/group/category/${slug}" -o "$out" -w "$slug: %{http_code} %{size_download}b %{time_total}s\n" || echo "$slug: CURL_FAIL"
  sleep 2
done
echo DONE
