#!/usr/bin/env python3
"""Extract chat.whatsapp.com codes from fetched page text, dedupe vs union set."""
import sys, re, json

DUP = set()
with open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030/dedupe_union_codes.txt") as f:
    for line in f:
        line = line.strip()
        if line:
            DUP.add(line)

page_url = sys.argv[1] if len(sys.argv) > 1 else ""
text = sys.stdin.read()

codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9]{22})", text)
seen = []
for c in codes:
    if c not in DUP and c not in seen:
        seen.append(c)

# Also capture near-miss codes (21/23 chars) for pending file
near = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9]{21}|[A-Za-z0-9]{23})\b", text)
near = [c for c in near if c not in DUP]

out = {"page": page_url, "fresh_22": seen, "near_miss": near}
print(json.dumps(out, indent=1))
