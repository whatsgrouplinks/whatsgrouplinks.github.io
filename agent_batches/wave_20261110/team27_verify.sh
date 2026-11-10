#!/bin/bash
# verify one code: $1 = code; prints TSV: code \t http \t ogtitle
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
code="$1"
body=$(curl -s -L --max-time 15 -A "$UA" "https://chat.whatsapp.com/$code" -w "\n__HTTP:%{http_code}" 2>&1)
http=$(echo "$body" | grep -o '__HTTP:[0-9]*' | tail -1 | cut -d: -f2)
if [ -z "$http" ] || [ "$http" = "000" ]; then echo -e "$code\t0\t"; exit 0; fi
title=$(echo "$body" | grep -o '<meta property="og:title" content="[^"]*"' | head -1 | sed 's/.*content="//; s/"$//')
echo -e "$code\t$http\t$title"
