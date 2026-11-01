#!/usr/bin/env python3
"""team15 stage 1: fetch archives 31-49 + all posts, extract NEW (name,code) candidates."""
import json, re, subprocess, sys, time, os
from html import unescape
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://whtspgrouplink.com/category/latest-whatsapp-group-links"
PAGES = range(31, 50)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
DIR = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261023b"
CAND = os.path.join(DIR, "team15_candidates.json")

EXISTING = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
PORN_RE = re.compile(r"\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b", re.I)
PHONE_RE = re.compile(r"^\+?[\d][\d\s\-]{7,}[\d]$")

def fetch(url, timeout=25):
    try:
        p = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", UA, url],
                           capture_output=True, timeout=timeout + 10)
        return p.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def post_urls(html):
    urls = []
    for m in re.finditer(r'href="(https://whtspgrouplink\.com/([^"#?/]+)/)"', html):
        full, slug = m.group(1), m.group(2)
        if slug in ("about", "contact-us", "privacy-policy", "disclaimer", "terms-and-conditions",
                    "submit-your-whatsapp-group-link-here", "author", "category") or slug.startswith("page"):
            continue
        if full not in urls:
            urls.append(full)
    return urls

def groups_from_post(html):
    out = []
    for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        row = tr.group(1)
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
        if len(tds) < 2:
            continue
        name = unescape(re.sub(r"<[^>]+>", "", tds[0])).strip()
        name = re.sub(r"\s+", " ", name)
        m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})", row)
        if not m or not name or len(name) < 3 or len(name) > 120:
            continue
        if PHONE_RE.match(name) or PORN_RE.search(name):
            continue
        out.append((name, m.group(1)))
    return out

def main():
    t0 = time.time()
    postlist = []
    def get_arch(pg):
        html = fetch(f"{BASE}/page/{pg}/")
        return post_urls(html) if html else []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(get_arch, pg): pg for pg in PAGES}
        for f in as_completed(futs):
            postlist.extend(f.result())
    postlist = list(dict.fromkeys(postlist))
    print(f"archive fetch done in {time.time()-t0:.0f}s, {len(postlist)} posts", flush=True)

    cands = {}
    seen = set()
    def get_post(url):
        html = fetch(url)
        if not html:
            return url, [], ""
        tm = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S | re.I)
        title = unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
        return url, groups_from_post(html), title
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(get_post, u): u for u in postlist}
        for f in as_completed(futs):
            url, rows, title = f.result()
            for name, code in rows:
                if code in EXISTING or code in seen:
                    continue
                seen.add(code)
                cands[code] = {"name": name, "code": code, "title": title, "post": url}
    lst = list(cands.values())
    json.dump(lst, open(CAND, "w"), ensure_ascii=False)
    print(f"candidates: {len(lst)} new (elapsed {time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
