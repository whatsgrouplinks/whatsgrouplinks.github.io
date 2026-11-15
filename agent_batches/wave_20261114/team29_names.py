#!/usr/bin/env python3
"""team29: fetch source pages of fresh codes, extract a listing name per code."""
import json, re, os, time, html
from team29_lib import fetch

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
fresh = json.load(open(os.path.join(WAVE, "team29-fresh-raw.json")))
mined = json.load(open(os.path.join(WAVE, "team29-mined-set.json")))

# union of sources that produced fresh codes
srcs = sorted({s for c, v in fresh.items() for s in v["sources"]})
print("fresh:", len(fresh), "source pages:", len(srcs), flush=True)
pages = {}
for i, url in enumerate(srcs):
    fn = os.path.join(WAVE, f"team29-src-{i}.html")
    if os.path.exists(fn):
        pages[url] = open(fn, encoding="utf-8", errors="ignore").read()
        print("cached", url, flush=True)
        continue
    try:
        r = fetch(url)
        open(fn, "w", encoding="utf-8").write(r.text)
        pages[url] = r.text
        print("fetched", url, r.status_code, len(r.text), flush=True)
    except Exception as e:
        print("ERR", url, repr(e), flush=True)
    time.sleep(1.5)

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'\s+', ' ', s).strip(' \t\r\n-–—:|»➠➾➡•·')
    return s.strip()

def name_for(code, page_html):
    # find all occurrences; prefer one inside a table row / list item
    out = []
    for m in re.finditer(re.escape(code), page_html):
        start = m.start()
        # look back up to 600 chars for enclosing <tr> or <li>
        window = page_html[max(0, start-700):start]
        # last <td>...</td> or <li> text before the link
        tds = re.findall(r'<td[^>]*>(.*?)</td>', window, re.S | re.I)
        if tds:
            cand = clean(tds[-1])
            if cand and len(cand) <= 90:
                out.append(cand)
                continue
        lis = re.findall(r'<li[^>]*>(.*?)<a\s', window, re.S | re.I)
        if lis:
            cand = clean(lis[-1])
            if cand and len(cand) <= 90:
                out.append(cand)
                continue
        # paragraph text before link
        ps = re.findall(r'<p[^>]*>(.*?)<a\s', window, re.S | re.I)
        if ps:
            cand = clean(ps[-1])
            if cand and len(cand) <= 90:
                out.append(cand)
                continue
        # groupwa data attributes: data-cat / data-desc near code
        dm = re.search(r'data-cat="([^"]*)"[^>]*data-desc="([^"]*)"', page_html[max(0, start-400):start+50], re.S)
        if dm:
            out.append(clean(dm.group(1)) + " | " + clean(dm.group(2)))
            continue
        # fallback: last 120 chars of stripped text
        txt = clean(window[-200:])
        out.append(txt[-90:])
    return out

named = {}
for code, v in fresh.items():
    cands = []
    for url in v["sources"]:
        if url in pages:
            cands += name_for(code, pages[url])
    # pick most common / first non-empty
    best = ""
    for c in cands:
        if c and c not in ("Join Link", "Join", "WhatsApp Group", "Group"):
            best = c
            break
    named[code] = {"name_guess": best, "candidates": cands[:4], "sources": v["sources"]}
    print(code, "=>", repr(best), flush=True)

json.dump(named, open(os.path.join(WAVE, "team29-fresh-named.json"), "w"), indent=1, ensure_ascii=False)
print("saved", len(named))
