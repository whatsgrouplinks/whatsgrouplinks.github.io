#!/usr/bin/env python3
"""team23 miner: fetch directory pages, extract chat.whatsapp.com codes + nearby names."""
import re, json, sys, time, html
import requests
from urllib.parse import urljoin

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{15,30})")

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip(" |-\u2013\u2014:;")
    return s

def extract(html_text, page_url):
    """Return list of (code, name_guess) using table rows / anchor context."""
    out = []
    # Table rows: <tr>...name...chat.whatsapp.com/CODE...</tr>
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html_text, re.S | re.I):
        m = CODE_RE.search(tr)
        if not m:
            continue
        # name = first cell text
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)
        name = ""
        for c in cells:
            t = clean(c)
            if t and "join" not in t.lower() and "click" not in t.lower():
                name = t
                break
        out.append((m.group(1), name))
    # List items: <li>...name...code...</li>
    for li in re.findall(r"<li[^>]*>(.*?)</li>", html_text, re.S | re.I):
        m = CODE_RE.search(li)
        if not m:
            continue
        # anchor text before the link
        t = clean(li)
        t = re.sub(r"(?i)\b(join|click here|join group|join now)\b.*$", "", t).strip(" |-\u2013")
        out.append((m.group(1), t))
    # Fallback: any code with preceding text window
    seen = {c for c, _ in out}
    for m in CODE_RE.finditer(html_text):
        code = m.group(1)
        if code in seen:
            continue
        window = html_text[max(0, m.start()-400):m.start()]
        # last plausible name-ish text: strip tags, take tail
        t = clean(window)
        # take last 60 chars as name guess
        name = t[-60:].strip()
        out.append((code, name))
    return out

def fetch(sess, url, tag):
    try:
        r = sess.get(url, headers=UA, timeout=60)
        print(f"[{tag}] {url} -> {r.status_code} len={len(r.text)}")
        return r.status_code, r.text
    except Exception as e:
        print(f"[{tag}] {url} -> ERROR {e}")
        return None, ""

if __name__ == "__main__":
    sites = json.load(open(f"{WD}/team23_targets.json"))
    sess = requests.Session()
    all_found = {}  # code -> {name, page, site}
    report = []
    for site in sites:
        for url in site["urls"]:
            st, text = fetch(sess, url, site["site"])
            time.sleep(1.5)
            if not text:
                report.append({"site": site["site"], "url": url, "status": st, "codes": 0, "note": "fetch failed/empty"})
                continue
            fn = f"{WD}/team23_{site['tag']}_{abs(hash(url))%100000}.html"
            open(fn, "w", encoding="utf-8").write(text)
            items = extract(text, url)
            n_new = 0
            for code, name in items:
                if code not in all_found:
                    all_found[code] = {"name": name, "page": url, "site": site["site"]}
            report.append({"site": site["site"], "url": url, "status": st,
                           "codes": len(set(c for c, _ in items)),
                           "fresh_vs_union": sum(1 for c, _ in set(items) if c not in union),
                           "note": f"saved {fn}"})
    json.dump({c: v for c, v in all_found.items()}, open(f"{WD}/team23_raw.json", "w"), ensure_ascii=False, indent=1)
    json.dump(report, open(f"{WD}/team23_fetch_report.json", "w"), indent=1)
    fresh = [c for c in all_found if c not in union]
    print("TOTAL unique codes:", len(all_found), "FRESH vs union:", len(fresh))
    print(json.dumps(report, indent=1))
