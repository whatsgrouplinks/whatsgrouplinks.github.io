#!/bin/bash
# TEAM37 — fetch all wglfinder listing pages via curl --resolve (bypasses sinkholed DNS)
W=~/workspace/whatsapp-groups-site/agent_batches/wave_20261104
mkdir -p "$W/team37_pages"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
RES="--resolve wglfinder.com:443:172.67.162.205"
SLUGS="
pune-whatsapp-group-link
cricket-whatsapp-group-link
ipl-2026-schedule-whatsapp-group-links
ssc-gd-whatsapp-group-link
indian-whatsapp-group-link
gk-whatsapp-group-link
government-job-whatsapp-group-link
private-job-whatsapp-group-link
shree-ram-sena-whatsapp-group-link-2026
republic-day-whatsapp-group-link-2026
ayodhya-whatsapp-group-link-2026
kenya-whatsapp-group-link
ms-dhoni-fans-whatsapp-group-link
india-whatsapp-group-link-2026
kuwait-whatsapp-group-link
bjp-whatsapp-group-link
uk-whatsapp-group-link
ayodhya-darshan-whatsapp-group-link
college-whatsapp-group-link
adre-whatsapp-group-link
upsc-whatsapp-group-link
valentines-day-whatsapp-group-links-2026
funny-whatsapp-group-link
tamil-whatsapp-group-link
bajrang-dal-indore-whatsapp-group-link-2026
germany-whatsapp-group-link
telegu-whatsapp-group-link
canada-whatsapp-group-link
bangladesh-whatsapp-group-link
arabic-whatsapp-group-link
delhi-job-whatsapp-group-link
daily-newspaper-whatsapp-group-link
bangalore-whatsapp-group-link
pakistani-whatsapp-group-link
bajrang-dal-whatsapp-group-link
binance-whatsapp-group-link
job-whatsapp-group-link
america-whatsapp-group-link
active-whatsapp-group-links
china-toys-whatsapp-group-link
china-whatsapp-group-link
dubai-whatsapp-group-link
kannada-whatsapp-group-link
bangalore-jobs-whatsapp-group-link
user-submitted-groups
"
echo "$SLUGS" | grep -v '^$' > "$W/team37_pages/slug_list.txt"
n=0; ok=0
while read -r slug; do
  n=$((n+1))
  out="$W/team37_pages/${slug}.html"
  code=$(curl -s $RES --max-time 40 -L -A "$UA" -o "$out" -w "%{http_code}" "https://wglfinder.com/${slug}/")
  sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
  if [ "$code" = "200" ] && [ "$sz" -gt 5000 ]; then ok=$((ok+1)); echo "OK  $slug ($sz)"; else echo "FAIL $slug code=$code size=$sz"; fi
done < "$W/team37_pages/slug_list.txt"
echo "fetched $ok/$n"
