#!/usr/bin/env python3
"""TEAM 07 wave 20261111 — Phase 1: mine leads_slice7.json listing pages for invite codes."""
import json, re, html, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})')
TAG_RE = re.compile(r'<[^>]+>')

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
urls = json.load(open(f"{WAVE}/leads_slice7.json"))
print(f"total urls={len(urls)} existing={len(existing)}", flush=True)

def clean_text(s):
    s = html.unescape(TAG_RE.sub(' ', s))
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def page_title(html_text):
    m = re.search(r'<title>(.*?)</title>', html_text, re.S | re.I)
    if m:
        t = clean_text(m.group(1))
        t = re.sub(r'\s*[-|–—]\s*(WhatsApp.*|Wa Groups.*|WhatsApp Group.*)$', '', t, flags=re.I)
        return t[:120]
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html_text, re.S | re.I)
    return clean_text(m.group(1))[:120] if m else ""

def name_near(html_text, pos, fallback):
    window = html_text[max(0, pos-4000):pos]
    # prefer last table cell / heading / strong text before the link
    txt = clean_text(window)
    # take last chunk after common separators
    parts = [p.strip() for p in re.split(r'[|\n]', txt) if p.strip()]
    cands = [p for p in parts[-6:] if 3 <= len(p) <= 90 and not p.lower().startswith(('http', 'join', 'click', 'whatsapp group link'))]
    if cands:
        return cands[-1][:100]
    return fallback

def fetch(url):
    for attempt in range(2):
        try:
            r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
            if r.status_code == 200 and r.text:
                return url, r.status_code, r.text
            if r.status_code in (403, 429) and attempt == 0:
                time.sleep(3); continue
            return url, r.status_code, r.text or ""
        except Exception as e:
            if attempt == 0:
                time.sleep(2); continue
            return url, 0, ""
    return url, 0, ""

candidates = {}   # code -> {code, name, source_url, page_title}
failed = []       # (url, reason)
done = 0
t0 = time.time()

def save_checkpoint():
    with open(f"{WAVE}/team07-candidates.json", "w") as f:
        json.dump(list(candidates.values()), f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-mined-progress.json", "w") as f:
        json.dump({"done": done, "total": len(urls), "candidates": len(candidates),
                   "failed": len(failed), "elapsed_s": round(time.time()-t0, 1)}, f, indent=1)

with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in urls}
    for fut in as_completed(futs):
        url, status, text = fut.result()
        done += 1
        if status != 200 or not text:
            failed.append({"url": url, "reason": f"fetch status {status}"})
        else:
            codes = CODE_RE.findall(text)
            title = page_title(text)
            seen_pos = set()
            for m in CODE_RE.finditer(text):
                code = m.group(1)
                if code in seen_pos:
                    continue
                seen_pos.add(code)
                if code in candidates:
                    continue
                name = name_near(text, m.start(), title)
                candidates[code] = {"code": code, "name": name, "source_url": url, "page_title": title}
        if done % 200 == 0:
            save_checkpoint()
            print(f"done={done}/{len(urls)} candidates={len(candidates)} failed={len(failed)} elapsed={time.time()-t0:.0f}s", flush=True)

save_checkpoint()
with open(f"{WAVE}/team07-failed.json", "w") as f:
    json.dump(failed, f, ensure_ascii=False, indent=1)
new_codes = [c for c in candidates if c not in existing]
print(f"FINISHED done={done} raw_candidates={len(candidates)} new_vs_existing={len(new_codes)} failed={len(failed)} elapsed={time.time()-t0:.0f}s")
