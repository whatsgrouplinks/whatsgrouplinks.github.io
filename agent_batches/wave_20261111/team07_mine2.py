#!/usr/bin/env python3
"""TEAM 07 wave 20261111 — Phase 1 v2: mine leads_slice7.json (24 workers, resume-safe)."""
import json, re, html, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, unquote
import requests
from requests.adapters import HTTPAdapter

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})')
TAG_RE = re.compile(r'<[^>]+>')
SHARE_DOMAINS = {"t.me", "telegram.me", "twitter.com", "x.com", "pinterest.com", "reddit.com"}

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
raw_urls = json.load(open(f"{WAVE}/leads_slice7.json"))

def unwrap(u):
    """Share/intent URLs embed the real listing page in ?url= — mine that instead."""
    p = urlparse(u)
    if p.netloc in SHARE_DOMAINS:
        qs = parse_qs(p.query)
        tgt = qs.get("url", [None])[0]
        if tgt:
            tgt = unquote(tgt).replace("&amp;", "&")
            if tgt.startswith("http"):
                return tgt
    return u

# effective listing URL -> original URL (for leads bookkeeping)
eff_map = {}
for u in raw_urls:
    e = unwrap(u)
    eff_map.setdefault(e, u)
urls = list(eff_map.keys())
print(f"raw={len(raw_urls)} effective={len(urls)} existing={len(existing)}", flush=True)

# resume: candidates already mined in v1 run
candidates = {}
done_urls = set()
try:
    for c in json.load(open(f"{WAVE}/team07-candidates.json")):
        candidates[c["code"]] = c
        done_urls.add(c["source_url"])
    print(f"resumed {len(candidates)} candidates from {len(done_urls)} done urls", flush=True)
except FileNotFoundError:
    pass
try:
    prog = json.load(open(f"{WAVE}/team07-mined-progress.json"))
    for u in prog.get("done_urls", []):
        done_urls.add(u)
except FileNotFoundError:
    pass

todo = [u for u in urls if u not in done_urls]
failed = []
try:
    failed = json.load(open(f"{WAVE}/team07-failed.json"))
except FileNotFoundError:
    pass
print(f"todo={len(todo)}", flush=True)

def clean_text(s):
    s = html.unescape(TAG_RE.sub(' ', s))
    return re.sub(r'\s+', ' ', s).strip()

def page_title(t):
    m = re.search(r'<title>(.*?)</title>', t, re.S | re.I)
    if m:
        x = clean_text(m.group(1))
        return re.sub(r'\s*[-|–—]\s*(WhatsApp.*|Wa Groups.*)$', '', x, flags=re.I)[:120]
    m = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S | re.I)
    return clean_text(m.group(1))[:120] if m else ""

def name_near(t, pos, fallback):
    txt = clean_text(t[max(0, pos-4000):pos])
    parts = [p.strip() for p in re.split(r'[|\n]', txt) if p.strip()]
    cands = [p for p in parts[-6:] if 3 <= len(p) <= 90 and not p.lower().startswith(('http', 'join', 'click', 'whatsapp group link'))]
    return cands[-1][:100] if cands else fallback

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=0))
session.mount("http://", HTTPAdapter(max_retries=0))

def fetch(url):
    for attempt in range(2):
        try:
            r = session.get(url, headers=UA, timeout=30, allow_redirects=True)
            if r.status_code == 200 and r.text:
                return url, 200, r.text
            if r.status_code in (403, 429) and attempt == 0:
                time.sleep(5); continue
            return url, r.status_code, r.text or ""
        except Exception:
            if attempt == 0:
                time.sleep(2); continue
            return url, 0, ""
    return url, 0, ""

done = 0
t0 = time.time()

def save_checkpoint():
    with open(f"{WAVE}/team07-candidates.json", "w") as f:
        json.dump(list(candidates.values()), f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-failed.json", "w") as f:
        json.dump(failed, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-mined-progress.json", "w") as f:
        json.dump({"done": len(done_urls), "total": len(urls), "todo_left": len(todo)-done,
                   "candidates": len(candidates), "failed": len(failed),
                   "elapsed_s": round(time.time()-t0, 1),
                   "done_urls": sorted(done_urls)}, f, indent=1)

with ThreadPoolExecutor(max_workers=24) as ex:
    futs = {ex.submit(fetch, u): u for u in todo}
    for fut in as_completed(futs):
        url, status, text = fut.result()
        done += 1
        done_urls.add(url)
        if status != 200 or not text:
            failed.append({"url": eff_map.get(url, url), "effective_url": url, "reason": f"fetch status {status}"})
        else:
            title = page_title(text)
            seen = set()
            for m in CODE_RE.finditer(text):
                code = m.group(1)
                if code in seen or code in candidates:
                    continue
                seen.add(code)
                candidates[code] = {"code": code, "name": name_near(text, m.start(), title),
                                    "source_url": url, "page_title": title}
        if done % 100 == 0:
            save_checkpoint()
            print(f"done={done}/{len(todo)} total_done_urls={len(done_urls)} candidates={len(candidates)} failed={len(failed)} elapsed={time.time()-t0:.0f}s", flush=True)

save_checkpoint()
new_codes = [c for c in candidates if c not in existing]
print(f"FINISHED todo={done} raw_candidates={len(candidates)} new_vs_existing={len(new_codes)} failed={len(failed)} elapsed={time.time()-t0:.0f}s")
