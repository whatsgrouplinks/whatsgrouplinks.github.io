import json, re
fresh=json.load(open('team19_fresh_raw.json'))
DROP_RE = re.compile(r'\b(xxx|porn|sex|sexy|escort|cam[- ]?girl|hookup|hook[- ]?up|nude|naked|erotic|adult\s*(video|pic|content)|b-?love|forsage|sheyi|airdrop|free\s*money|earn\s*\$?\s*100|double\s*(your|the)\s*money|investment\s*double|onlyfans|call\s*girl|randi|desi\s*sex|hot\s*girl|hot\s*video|leak(ed)?\s*(video|mms)|mms\s*leak)\b', re.I)
# strip prohibition sentences before screening
PROHIB = re.compile(r'[^.!?\n]*(inappropriate|porn|xxx|sex|adult|abuse|spam|link share|promotion)[^.!?\n]*(na karein|not allowed|prohibited|mana hai|not allow|strictly prohibited|is not allowed)[^.!?\n]*[.!?\n]?', re.I)
kept, dropped = [], []
for r in fresh:
    text = (r.get('name','')+' '+r.get('heading','')+' '+r.get('desc',''))
    cleaned = PROHIB.sub(' ', text)
    if DROP_RE.search(cleaned):
        dropped.append({**r,'drop_reason':'keyword: '+DROP_RE.search(cleaned).group(0)})
    else:
        kept.append(r)
print("fresh:", len(fresh), "kept:", len(kept), "dropped:", len(dropped))
from collections import Counter
print("dropped by source:", Counter(d['source'] for d in dropped))
for d in dropped[:25]: print(" DROP", d['code'], "|", d['name'][:60], "|", d['heading'][:40], "|", d.get('drop_reason'))
json.dump(kept, open('team19_to_verify.json','w'), ensure_ascii=False, indent=1)
json.dump(dropped, open('team19_dropped_prescreen.json','w'), ensure_ascii=False, indent=1)
