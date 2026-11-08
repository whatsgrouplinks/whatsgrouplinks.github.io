#!/usr/bin/env python3
"""Team 28 second pass: additional fresh listicle pages."""
import json, re, html
import requests

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PAGES = [
    ("https://wtgrouplinks.com/engineering-students-whatsapp-group-link/", "Education", "International"),
    ("https://www.sarvgyan.com/articles/best-whatsapp-group-for-jee-main", "Education", "IN"),
    ("https://whatsgroupslinkspk.com/", "Education", "PK"),
    ("https://wagroupshub.com/usa-whatsapp-group-links/", "Islamic", "US"),
    ("https://nearpeer.org/blog/css/pms-punjab-2027-revised-syllabus-new-exam-pattern-reforms-complete-guide-for-aspirants", "Education", "PK"),
]

union = set(json.load(open(f"{WORK}/dedupe_union.json")))
code_re = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
title_re = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)

s = requests.Session()
s.headers.update({"User-Agent": UA})

candidates = []
seen = set()

def clean(t):
    t = html.unescape(t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

for url, cat, country in PAGES:
    try:
        r = s.get(url, timeout=50, allow_redirects=True)
        page_html = r.text
        status = r.status_code
    except Exception as e:
        print(f"FETCH-FAIL {url}: {e}")
        continue
    page_title = clean(title_re.search(page_html).group(1)) if title_re.search(page_html) else ""
    print(f"FETCH {url} -> {status}, len={len(page_html)} title={page_title[:60]}")
    a_re = re.compile(
        r'<a[^>]*href=["\']([^"\']*chat\.whatsapp\.com/[^"\']*)["\'][^>]*>(.*?)</a>',
        re.I | re.S)
    found = 0
    for m in a_re.finditer(page_html):
        href, label = m.group(1), m.group(2)
        if '/invite/' in href:
            continue
        cm = code_re.search(href)
        if not cm:
            continue
        code = cm.group(1)
        label = clean(label)
        if not label or len(label) < 3:
            prev = clean(page_html[max(0, m.start()-600):m.start()])
            label = ' '.join(prev.split()[-8:])
        if code in union or code in seen:
            continue
        seen.add(code)
        candidates.append({"code": code, "page": url, "cat": cat,
                           "country": country, "ctx": label[:120],
                           "page_title": page_title[:80]})
        found += 1
    print(f"  -> {found} fresh candidates")

json.dump(candidates, open(f"{WORK}/team28-candidates2.json", "w"), ensure_ascii=False, indent=1)
print(f"TOTAL fresh candidates pass2: {len(candidates)}")
