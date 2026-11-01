#!/usr/bin/env python3
"""TEAM 219 add-on batch 4."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

ADD = [
("Islamabad Rawalpindi friends.", "LSZMdzh6GNaBvtlNxN1B0c", "Islamabad Rawalpindi friendship group"),
("WORLD WIDE FRIENDS", "CBdGpxR1FXuHuRuucA67cD", "Worldwide friends group"),
("Only Pakistani gairls com", "FrOvr23ZxRn6hwuM76A4FE", "Pakistani girls friendship group"),
]

PORN = re.compile(r'(?i)\b(porn|pornhub|xxx|sexy|nudes?\b|escorts?|call\s*girls?|adult\s*(video|chat|dating)|hentai|onlyfans|cam\s*girls?|paid\s*girl|hotel\s*girl|girl\s*(photo|number|phone))\b')
added = skipped_seen = 0
for name, code, desc in ADD:
    code = code.strip()
    if code in have:
        skipped_seen += 1
        continue
    if PORN.search(name + ' ' + desc):
        continue
    have.add(code)
    existing.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}", "desc": desc, "cat": "Friendship"})
    added += 1

json.dump(existing, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"added={added} skipped_seen={skipped_seen} total={len(existing)}")
