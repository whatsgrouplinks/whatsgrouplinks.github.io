#!/usr/bin/env python3
"""Team 01 wave 20261110 slice 1 - bonus: fetch linkado /grupo/ detail pages discovered
on the slice's category/populares pages (their invite codes are in the HTML)."""
import json, os, re, subprocess, time, html as htmlmod
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261110")
RAW = os.path.join(WAVE, "team01_raw")
GRAW = os.path.join(WAVE, "team01_raw_grupo")
os.makedirs(GRAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_01.json"))
existing = set(json.load(open(os.path.join(BASE, ".existing_codes.json"))))
groups = json.load(open(os.path.join(BASE, "groups.json")))
for it in groups:
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)', it.get('invite', ''))
    if m:
        existing.add(m.group(1))

# --- build target list: grupo urls from populares + category raws ---
targets = {}  # url -> category slug
order = []
# populares first (idx 63), then categories 64..83
for i in [63] + list(range(64, 84)):
    fn = os.path.join(RAW, f"p{i:03d}.html")
    if not os.path.exists(fn):
        continue
    html = open(fn, encoding="utf-8", errors="ignore").read()
    cat = ""
    m = re.search(r'/categoria/([a-z\-]+)', leads[i]["url"])
    if m:
        cat = m.group(1)
    elif "populares" in leads[i]["url"]:
        cat = "populares"
    for g in re.findall(r'href="(/grupo/[0-9a-f]{24})"', html):
        u = "https://linkado.app" + g
        if u not in targets:
            targets[u] = cat
            order.append(u)
print("grupo targets found:", len(order), flush=True)
targets = order[:150]
print("fetching first:", len(targets), flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com(?:/|\\u002f|\\/|%2F)+(?:invite/)?([A-Za-z0-9_\-]{8,})")

def fetch_one(args):
    i, url = args
    fn = os.path.join(GRAW, f"g{i:03d}.html")
    if os.path.exists(fn) and os.path.getsize(fn) > 500:
        return i, "cached", fn
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "40",
                            "-o", fn, "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=55)
        return i, r.stdout.strip(), fn
    except Exception as e:
        return i, f"ERR {e}", fn

def clean_text(s):
    s = htmlmod.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

fresh = {}
ctx = {}
results = []
t0 = time.time()
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(fetch_one, (i, u)): i for i, u in enumerate(targets)}
    for fut in futs:
        i, status, fn = fut.result()
        url = targets[i]
        try:
            html = open(fn, encoding="utf-8", errors="ignore").read()
        except Exception:
            html = ""
        t = re.search(r'<title>(.*?)</title>', html, re.S)
        name = clean_text(t.group(1)) if t else ""
        name = re.sub(r'\s*-\s*Amizade.*$', '', name).strip()
        name = re.sub(r'\s*\|\s*Linkado.*$', '', name).strip()
        dm = re.search(r'<meta name="description" content="([^"]*)"', html)
        codes = set()
        for m in CODE_RE.finditer(html):
            c = m.group(1)
            if len(c) > 22:
                c = c[:22]
            codes.add(c)
        fresh_here = [c for c in codes if c not in existing]
        for c in fresh_here:
            fresh.setdefault(c, url)
            ctx.setdefault(c, {"name": name, "description": clean_text(dm.group(1)) if dm else "",
                               "category_raw": targets.get(url, ""), "country": "BR",
                               "listing_url": url, "source": "linkado grupo detail"})
        results.append({"idx": i, "url": url, "fetch": status, "bytes": len(html),
                        "codes_found": len(codes), "fresh": len(fresh_here),
                        "fresh_codes": sorted(fresh_here)})
        print(f"{i:3d} {status} bytes={len(html)} codes={len(codes)} fresh={len(fresh_here)} {url} [{len(results)}/{len(targets)} {time.time()-t0:.0f}s]", flush=True)
        if len(results) % 10 == 0:
            json.dump(results, open(os.path.join(WAVE, "team01_grupo_fetch_log.json"), "w"), indent=1)

json.dump(results, open(os.path.join(WAVE, "team01_grupo_fetch_log.json"), "w"), indent=1)
json.dump({c: u for c, u in sorted(fresh.items())},
          open(os.path.join(WAVE, "team01_grupo_fresh_codes.json"), "w"), indent=1)
json.dump(ctx, open(os.path.join(WAVE, "team01_grupo_context.json"), "w"), indent=1, ensure_ascii=False)
print("TOTAL grupo fresh unique codes:", len(fresh))
print("ELAPSED", round(time.time() - t0, 1))
