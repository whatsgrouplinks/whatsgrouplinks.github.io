#!/usr/bin/env python3
"""Team 18 round 2: football sources harvest + verify."""
import re, json, pickle, os, time
from harvest import load_dedupe, parse_jina, PORN, infer_country, describe, verify

WORK = os.path.dirname(os.path.abspath(__file__))

def main():
    dedupe = load_dedupe()
    cand = []
    cand += parse_jina(os.path.join(WORK, 'appgrouplink_jina.txt'),
                       'https://appgrouplink.com/football-whatsapp-group-links/', 'XX')
    cand += parse_jina(os.path.join(WORK, 'messi_jina.txt'),
                       'https://wagrouplinks.net/lionel-messi-fans-whatsapp-group-links/', 'XX')
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
    json.dump(fresh, open(os.path.join(WORK, 'candidates2.json'), 'w'), ensure_ascii=False, indent=1)
    results = []
    for i, c in enumerate(fresh):
        alive, title = verify(c['code'])
        results.append({**c, 'alive': alive, 'og_title': title})
        if (i + 1) % 20 == 0:
            print(f'verified {i+1}/{len(fresh)}')
        time.sleep(0.5)
    print('alive:', sum(1 for r in results if r['alive']))
    json.dump(results, open(os.path.join(WORK, 'verify_results2.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
