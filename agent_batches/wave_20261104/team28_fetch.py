#!/usr/bin/env python3
"""Team 28: fetch candidate listicle pages, extract chat.whatsapp.com codes, dedupe vs union."""
import json, re, sys, html
import requests

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PAGES = [
    ("https://whatgroups.com/islamic-whatsapp-group-link/", "Islamic", "International"),
    ("https://whatgroups.com/online-quran-students-whatsapp-group-links/", "Islamic", "International"),
    ("https://newgrouplinks.pk/", "Education", "PK"),
    ("https://whgroups.link/pakistan-jobs-whatsapp-group-links/", "Jobs", "PK"),
    ("https://www.sarkarijobsinfo.in/govt-jobs-whatsapp-group-link/?lcp_page0=27", "Jobs", "IN"),
    ("https://www.wemakescholars.com/blog/whatsapp-group-for-ms-in-us-fall", "Education", "US"),
    ("https://www.wemakescholars.com/blog/uk-university-whatsapp-group-links", "Education", "GB"),
    ("https://www.wemakescholars.com/blog/70-study-abroad-whatsapp-groups-for-students", "Education", "International"),
    ("https://wahublink.com/education-whatsapp-group-links/", "Education", "International"),
]

union = set(json.load(open(f"{WORK}/dedupe_union.json")))
code_re = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
title_re = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)

s = requests.Session()
s.headers.update({"User-Agent": UA})

candidates = []   # (code, page_url, cat, country, ctx_name)
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
    # find links with nearby text: pattern <a ... href="...chat.whatsapp.com/CODE...">label</a>
    a_re = re.compile(
        r'<a[^>]*href=["\']([^"\']*chat\.whatsapp\.com/[^"\']*)["\'][^>]*>(.*?)</a>',
        re.I | re.S)
    found = 0
    for m in a_re.finditer(page_html):
        href, label = m.group(1), m.group(2)
        if '/invite/' in href:
            continue  # channels — never include
        cm = code_re.search(href)
        if not cm:
            continue
        code = cm.group(1)
        label = clean(label)
        # skip JS-gated "Join" only with no name -> try preceding text
        if not label or len(label) < 3:
            prev = clean(page_html[max(0, m.start()-600):m.start()])
            words = prev.split()[-8:]
            label = ' '.join(words)
        if code in union or code in seen:
            continue
        seen.add(code)
        candidates.append({"code": code, "page": url, "cat": cat,
                           "country": country, "ctx": label[:120],
                           "page_title": page_title[:80]})
        found += 1
    print(f"  -> {found} fresh candidates")

json.dump(candidates, open(f"{WORK}/team28-candidates.json", "w"), ensure_ascii=False, indent=1)
print(f"TOTAL fresh candidates: {len(candidates)}")
