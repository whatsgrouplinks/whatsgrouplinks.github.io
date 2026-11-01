#!/usr/bin/env python3
"""Team 18 round 4: IPL + dream11 pages."""
import json, os, time
from harvest import load_dedupe, parse_jina, PORN, verify

WORK = os.path.dirname(os.path.abspath(__file__))

def main():
    dedupe = load_dedupe()
    cand = []
    cand += parse_jina(os.path.join(WORK, 'ipl_jina.txt'),
                       'https://whatgroups.com/ipl-whatsapp-group-links/', 'IN')
    cand += parse_jina(os.path.join(WORK, 'dream11_jina.txt'),
                       'https://whatstele.com/whatsapp/group-links/dream11/', 'IN')
    print('raw candidates:', len(cand))
    fresh, seen = [], set()
    for c in cand:
        code = c['code']
        if code in dedupe or code in seen:
            continue
        seen.add(code)
        if PORN.search(c['name']):
            continue
        fresh.append(c)
    print('fresh:', len(fresh))
    json.dump(fresh, open(os.path.join(WORK, 'candidates4.json'), 'w'), ensure_ascii=False, indent=1)
    results = []
    for i, c in enumerate(fresh):
        alive, title = verify(c['code'])
        results.append({**c, 'alive': alive, 'og_title': title})
        if (i + 1) % 25 == 0:
            print(f'verified {i+1}/{len(fresh)}')
        time.sleep(0.5)
    print('alive:', sum(1 for r in results if r['alive']))
    json.dump(results, open(os.path.join(WORK, 'verify_results4.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
