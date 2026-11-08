#!/usr/bin/env python3
"""Team 06 phase 1b: re-fetch slice pages (parallel) and harvest NEW listing-page leads.
Listing hrefs on appgrouplink are often UNQUOTED, so match both forms."""
import json, re, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
leads = json.load(open(BASE / 'leads_slice_06.json'))
slice_urls = {e['url'].rstrip('/') for e in leads}
LINK = re.compile(r'appgrouplink\.com/([a-z0-9\-/]+?whatsapp-group-links?/?)(?:["\'\s>#]|$)', re.I)

def fetch(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        found = set()
        for m in LINK.finditer(r.text):
            p = m.group(1).rstrip('/')
            u = f'https://appgrouplink.com/{p}/'
            if u.rstrip('/') not in slice_urls:
                found.add(u)
        return found
    except Exception as e:
        return set()

new = set()
with ThreadPoolExecutor(max_workers=8) as ex:
    for s in ex.map(fetch, [e['url'] for e in leads]):
        new |= s
print('new listing leads:', len(new))
for u in sorted(new):
    print(u)
json.dump(sorted(new), open(BASE / 'team06-scratch-newleads.json', 'w'), indent=1)
