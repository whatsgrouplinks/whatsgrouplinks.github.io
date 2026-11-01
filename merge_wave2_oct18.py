#!/usr/bin/env python3
"""Wave 2 merge: fresh scraper outputs -> dedupe vs groups.json -> v2 porn filter.
Output: wave2_new_oct18.json"""
import json, os, sys

SITE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SITE)
from merge_queued_oct18 import canon_code, canon_invite, is_adult, norm_cat

WAVE2_FILES = [
    'team105-static-dirs.json', 'team106-wagroupslink.json',
    'team109-invitegroups.json', 'team110-reddit.json', 'team111-social.json',
    'team112-niche-jobs.json', 'team113-niche-study.json',
    'team114-niche-crypto.json',
]

def main():
    existing = json.load(open(os.path.join(SITE, 'groups.json')))
    existing_codes = {canon_code(g.get('invite', '')) for g in existing}
    # also exclude wave-1 queued candidates already being verified
    qpath = os.path.join(SITE, 'queued_new_oct18.json')
    if os.path.exists(qpath):
        for c in json.load(open(qpath)):
            existing_codes.add(canon_code(c.get('invite', '')))

    seen, stats = {}, {'records': 0, 'no_code': 0, 'dup': 0, 'adult': 0}
    for f in WAVE2_FILES:
        p = os.path.join(SITE, 'scraped', f)
        if not os.path.exists(p):
            print(f'  MISSING {f}'); continue
        for g in json.load(open(p)):
            stats['records'] += 1
            code = canon_code(g.get('invite', ''))
            if not code or len(code) < 10:
                stats['no_code'] += 1; continue
            if code in seen or code in existing_codes:
                stats['dup'] += 1; continue
            name = (g.get('name') or '').strip()
            desc = (g.get('description') or g.get('desc') or '').strip()
            if is_adult(name, desc):
                stats['adult'] += 1; continue
            seen[code] = {
                'name': name or f'WhatsApp Group {code[:8]}',
                'category': norm_cat(g.get('category')),
                'description': desc,
                'image': (g.get('image') or '').strip(),
                'invite': canon_invite(code),
                'country': (g.get('country') or '').strip(),
            }
            existing_codes.add(code)

    cands = list(seen.values())
    out = os.path.join(SITE, 'wave2_new_oct18.json')
    json.dump(cands, open(out, 'w'), ensure_ascii=False)
    print(f'records={stats["records"]} no_code={stats["no_code"]} '
          f'dup={stats["dup"]} adult={stats["adult"]}')
    print(f'WAVE2 CANDIDATES: {len(cands)} -> {out}')

if __name__ == '__main__':
    main()
