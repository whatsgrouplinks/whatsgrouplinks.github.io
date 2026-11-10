#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
code="$1"
f="team27_raw/verify_${code}.html"
curl -s -L --max-time 15 -A "$UA" "https://chat.whatsapp.com/$code" -o "$f" -w "%{http_code}"
echo " $code"
