#!/usr/bin/env python3
"""team14: build pending file from the 92 transport-failed codes.
Names looked up from pending_in.json (team16's 398). Category/country are
provisional (funny / International) — the code is the authoritative part."""
import json

base = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106'
unk = json.load(open(f'{base}/scratch14/pending_unknown_in.json', encoding='utf-8'))
pin = json.load(open(f'{base}/scratch14/pending_in.json', encoding='utf-8'))
names = {x['code']: x.get('name', '') for x in pin}
out = []
missing = []
for x in unk:
    code = x['code']
    if code not in names:
        missing.append(code)
    out.append({"code": code, "name": names.get(code, ""), "category": "funny",
                "country": "International",
                "invite": f"https://chat.whatsapp.com/{code}"})
dest = f'{base}/team14-p5-gjl-funny-health-pending.json'
with open(dest, 'w', encoding='utf-8') as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
    f.write('\n')
print(f"WROTE {len(out)} pending, missing-names {missing} -> {dest}")
