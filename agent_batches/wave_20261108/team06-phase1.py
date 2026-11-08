#!/usr/bin/env python3
"""Team 06 harvest — phase 1: extract (name, code) from all slice pages."""
import json, re, html, time, requests
from pathlib import Path

BASE = Path('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

leads = json.load(open(BASE / 'leads_slice_06.json'))
union = set(json.load(open(BASE / 'dedupe_union.json')))

ROW = re.compile(
    r'<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{20,24})',
    re.S | re.I)
GENERIC = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{20,24})', re.I)
LISTING = re.compile(r'href=["\'](https://appgrouplink\.com/[^"\']*whatsapp-group-links?/?)["\']', re.I)

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

extracted = []          # {name, code, page}
seen = set()
new_leads = set()
attempted, failed_pages = [], []

for i, entry in enumerate(leads):
    url = entry['url']
    attempted.append(url)
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        page_html = r.text
    except Exception as e:
        failed_pages.append((url, str(e)[:120]))
        continue
    for m in LISTING.finditer(page_html):
        u = m.group(1)
        if u.rstrip('/') != url.rstrip('/'):
            new_leads.add(u)
    rows = ROW.findall(page_html)
    found = set()
    for name, code in rows:
        name = clean(name)
        if len(code) != 22:
            continue
        found.add(code)
        if code in union or code in seen:
            continue
        seen.add(code)
        extracted.append({'name': name, 'code': code, 'page': url})
    # fallback: codes not in table rows (name unknown)
    for code in GENERIC.findall(page_html):
        if len(code) != 22 or code in found or code in union or code in seen:
            continue
        seen.add(code)
        extracted.append({'name': '', 'code': code, 'page': url})
    if (i + 1) % 20 == 0:
        print(f'{i+1}/{len(leads)} pages, extracted so far: {len(extracted)}', flush=True)
    time.sleep(0.3)

print('pages attempted:', len(attempted), 'failed:', len(failed_pages))
for u, e in failed_pages:
    print('FAILED', u, e)
print('unique new codes extracted:', len(extracted))
print('new listing leads found:', len(new_leads))
json.dump({'extracted': extracted, 'failed_pages': failed_pages,
           'new_leads': sorted(new_leads), 'attempted': attempted},
          open(BASE / 'team06-scratch-extract.json', 'w'), indent=1)
print('saved scratch')
