#!/usr/bin/env python3
"""TEAM 18 — wglfinder.com COUNTRY/REGIONAL pages scrape."""
import re, json, time, html as h, sys
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HEAD = {"User-Agent": UA, "Accept": "text/html,*/*;q=0.9"}

PAGES = [
    ("pakistani-whatsapp-group-link", "PK"),
    ("indian-whatsapp-group-link", "IN"),
    ("india-whatsapp-group-link-2026", "IN"),
    ("indian-whatsapp-group-link", "IN"),  # same as idx1, dedupe by slug later
    ("kenya-whatsapp-group-link", "KE"),
    ("kuwait-whatsapp-group-link", "KW"),
    ("uk-whatsapp-group-link", "GB"),
    ("germany-whatsapp-group-link", "DE"),
    ("canada-whatsapp-group-link", "CA"),
    ("bangladesh-whatsapp-group-link", "BD"),
    ("arabic-whatsapp-group-link", "SA"),
    ("america-whatsapp-group-link", "US"),
    ("china-whatsapp-group-link", "CN"),
    ("dubai-whatsapp-group-link", "AE"),
    ("bangalore-whatsapp-group-link", "IN"),
    ("tamil-whatsapp-group-link", "IN"),
    ("telegu-whatsapp-group-link", "IN"),
    ("kannada-whatsapp-group-link", "IN"),
]

PORN_RE = re.compile(
    r'porn|pornhub|\bxxx\b|nude|sex\s*video|escort|call\s*girl|\bfuck\b|dick|pussy|boobs|\banal\b|🥵|🍆|🍑|🔞|💦|👅|👄|💋',
    re.I)

def fetch(url, tries=4):
    for a in range(tries):
        try:
            r = requests.get(url, headers=HEAD, timeout=25)
            if r.status_code == 200 and r.text:
                return r.text
        except Exception as e:
            print(f"  fetch try{a} fail {type(e).__name__}", flush=True)
        time.sleep(3)
    return None

def parse_rows(page_html):
    """Extract (name, code) from <li> rows with data-group-link."""
    rows = []
    for li in re.finditer(r'<li>(.*?)</li>', page_html, re.S):
        block = li.group(1)
        m = re.search(r'data-group-link="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', block)
        if not m:
            continue
        code = m.group(1)
        # name = text before the anchor tag
        pre = block.split('<a ')[0]
        name = h.unescape(re.sub(r'<[^>]+>', '', pre))
        name = re.sub(r'[⇒=>\-\|·:]+$', '', name).strip()
        name = re.sub(r'\s+', ' ', name).strip()
        rows.append((name, code))
    return rows

def is_porn(name):
    return bool(PORN_RE.search(name))

# load union
union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
print("union size:", len(union), flush=True)

seen = set()
candidates = []  # (name, code, country, slug)
slugs_done = set()
for slug, country in PAGES:
    if slug in slugs_done:
        continue
    slugs_done.add(slug)
    url = f"https://wglfinder.com/{slug}/"
    print("FETCH", slug, flush=True)
    pg = fetch(url)
    if not pg:
        print("  FAILED -> pending as lead", flush=True)
        continue
    rows = parse_rows(pg)
    print(f"  rows: {len(rows)}", flush=True)
    for name, code in rows:
        if code in union or code in seen:
            continue
        seen.add(code)
        candidates.append((name, code, country, slug))
        if is_porn(name):
            print("  PORN DROP (name)", name[:40], flush=True)

json.dump(candidates, open(f"{WAVE}/team18-candidates-raw.json", "w"), ensure_ascii=False)
print("candidates:", len(candidates), flush=True)
