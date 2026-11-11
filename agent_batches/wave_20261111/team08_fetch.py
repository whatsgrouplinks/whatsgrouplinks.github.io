#!/usr/bin/env python3
"""TEAM 08 wave 20261111 leads slice 8 — fetch listing pages, extract invite codes + names.
Saves checkpoints in the wave dir. Fetch only (no verification here)."""
import json, re, html, os, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{18,30})(?![A-Za-z0-9_-])")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")

def norm_url(u):
    u = u.split("#")[0].strip()
    u = u.replace("whtsagrouplinks.com//", "whtsagrouplinks.com/")
    if u.endswith("/feed") or u.endswith("/feed/"):
        return None  # RSS duplicate of same article
    if "googletagmanager.com" in u or "wp-json/oembed" in u:
        return None  # not a listing page
    return u.rstrip("/") or u

def clean_text(s):
    s = html.unescape(TAG_RE.sub(" ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s

def guess_name(h, mstart):
    # look back up to 900 chars; prefer enclosing <li>...</li> or table row
    win = h[max(0, mstart-900):mstart]
    win = re.sub(r"<[^>]*$", "", win)  # drop trailing partial tag cut by the window edge
    # last <li ...> opening
    for tag in ("<li", "<tr", "<h3", "<h2", "<td", "<div"):
        idx = win.lower().rfind(tag)
        if idx >= 0:
            seg = clean_text(win[idx:])
            break
    else:
        seg = clean_text(win)
    # name is usually last line/segment before the link; strip trailing Join/dash
    seg = re.sub(r"(?i)\s*(join|join group|join now|join chat|click here|👉|➡️)\s*$", "", seg)
    seg = re.sub(r"[\-–—:|•·»]+\s*$", "", seg).strip()
    # take last sentence-ish chunk if very long
    if len(seg) > 120:
        parts = re.split(r"[|\n]", seg)
        seg = parts[-1].strip() if parts else seg
    if len(seg) > 120:
        seg = seg[-120:]
    return seg

def fetch_one(url):
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        if r.status_code != 200 or not r.text:
            return url, r.status_code, [], "", 0
        h = r.text
        title = clean_text(TITLE_RE.search(h).group(1)) if TITLE_RE.search(h) else ""
        cands = []
        seen = set()
        for m in CODE_RE.finditer(h):
            code = m.group(1)
            if code in seen or code.lower() in ("invite",):
                continue
            seen.add(code)
            cands.append({"code": code, "name": guess_name(h, m.start()),
                          "listing": url, "page_title": title[:160]})
        return url, r.status_code, cands, title[:160], len(h)
    except Exception as e:
        return url, 0, [], str(e)[:120], 0

def main():
    urls = json.load(open(os.path.join(WAVE, "leads_slice8.json")))
    uniq, seen = [], set()
    for u in urls:
        n = norm_url(u)
        if n and n not in seen:
            seen.add(n); uniq.append(n)
    print(f"input {len(urls)} unique-normalized {len(uniq)}", flush=True)
    done_file = os.path.join(WAVE, "team08_fetch_log.json")
    cand_file = os.path.join(WAVE, "team08_raw_candidates.json")
    done, cands = {}, []
    if os.path.exists(done_file):
        done = {d["url"]: d for d in json.load(open(done_file))}
    if os.path.exists(cand_file):
        cands = json.load(open(cand_file))
    todo = [u for u in uniq if u not in done]
    print(f"already fetched {len(done)} todo {len(todo)} existing candidates {len(cands)}", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(fetch_one, u): u for u in todo}
        for i, f in enumerate(as_completed(futs)):
            url, status, cs, title, size = f.result()
            done[url] = {"url": url, "status": status, "codes": len(cs), "title": title, "size": size}
            cands.extend(cs)
            if (i+1) % 200 == 0:
                json.dump(list(done.values()), open(done_file, "w"), ensure_ascii=False)
                json.dump(cands, open(cand_file, "w"), ensure_ascii=False)
                print(f"{i+1}/{len(todo)} fetched in {time.time()-t0:.0f}s codes-so-far {len(cands)}", flush=True)
    json.dump(list(done.values()), open(done_file, "w"), ensure_ascii=False)
    json.dump(cands, open(cand_file, "w"), ensure_ascii=False)
    ok = sum(1 for d in done.values() if d["status"] == 200)
    print(f"DONE fetched={len(done)} http200={ok} total-candidates={len(cands)} unique-codes={len(set(c['code'] for c in cands))} elapsed={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
