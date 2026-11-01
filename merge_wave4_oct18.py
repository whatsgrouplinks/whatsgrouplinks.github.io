#!/usr/bin/env python3
"""Wave 4 merge (massive scrape Oct 18): team230-237 outputs + any new additions
in team220-229 files -> dedupe vs groups.json -> v3 porn filter (girls allowed).
Output: wave4_new_oct18.json"""
import json, os, sys, glob

SITE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SITE)
from merge_queued_oct18 import canon_code, canon_invite, is_adult, norm_cat

def main():
    existing = json.load(open(os.path.join(SITE, 'groups.json')))
    existing_codes = {canon_code(g.get('invite', '')) for g in existing}

    files = sorted(glob.glob(os.path.join(SITE, 'scraped', 'team2*.json')))
    seen, stats = {}, {'records': 0, 'no_code': 0, 'dup': 0, 'adult': 0, 'files': 0}
    for p in files:
        stats['files'] += 1
        try:
            data = json.load(open(p))
        except Exception as e:
            print(f'  ERROR {p}: {e}'); continue
        items = data if isinstance(data, list) else data.get('groups', data.get('items', []))
        for g in items:
            if not isinstance(g, dict):
                continue
            stats['records'] += 1
            code = canon_code(g.get('invite', '') or g.get('url', '') or g.get('link', ''))
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
                'category': norm_cat(g.get('category') or g.get('cat', '')),
                'description': desc,
                'image': (g.get('image') or '').strip(),
                'invite': canon_invite(code),
                'country': (g.get('country') or '').strip(),
            }
            existing_codes.add(code)

    cands = list(seen.values())
    out = os.path.join(SITE, 'wave4_new_oct18.json')
    json.dump(cands, open(out, 'w'), ensure_ascii=False)
    print(f'files={stats["files"]} records={stats["records"]} no_code={stats["no_code"]} '
          f'dup={stats["dup"]} adult={stats["adult"]}')
    print(f'WAVE4 CANDIDATES: {len(cands)} -> {out}')

if __name__ == '__main__':
    main()
