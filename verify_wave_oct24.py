#!/usr/bin/env python3
"""Parent-side verification gate for wave_20261024 unverified candidates + spot-check.
Usage: python3 verify_wave_oct24.py
Reads agent_batches/wave_20261024/merged_wave_20261024_unverified.json
and merged_wave_20261024_verified.json; writes *_parent_verified.json,
*_parent_dead.json, and spotcheck results to stdout."""
import json, re, subprocess, random, os
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__)) + '/agent_batches/wave_20261024'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

def check(item):
    url = item['invite']
    try:
        out = subprocess.run(['curl', '-s', '-L', '--max-time', '25', '-A', UA, url],
                             capture_output=True, text=True, timeout=30).stdout
        m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', out)
        title = m.group(1) if m else ''
        import html as _h
        title = _h.unescape(title).strip()
        return item, bool(title), title
    except Exception:
        return item, False, ''

def main():
    unver = json.load(open(f'{BASE}/merged_wave_20261024_unverified.json'))
    ver = json.load(open(f'{BASE}/merged_wave_20261024_verified.json'))
    results, dead = [], []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for item, ok, title in ex.map(check, unver):
            if ok:
                results.append(item)
            else:
                dead.append(item)
    json.dump(results, open(f'{BASE}/unverified_parent_verified.json', 'w'), ensure_ascii=False)
    json.dump(dead, open(f'{BASE}/unverified_parent_dead.json', 'w'), ensure_ascii=False)
    print(f"UNVERIFIED SET: {len(unver)} -> verified {len(results)}, dead/blocked {len(dead)}")

    random.seed(20261024)
    sample = random.sample(ver, min(30, len(ver)))
    okc = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for item, ok, title in ex.map(check, sample):
            okc += 1 if ok else 0
            if not ok:
                print('SPOTCHECK FAIL:', item['name'], item['invite'])
    print(f"SPOTCHECK verified-set: {okc}/{len(sample)} passed")

if __name__ == '__main__':
    main()
