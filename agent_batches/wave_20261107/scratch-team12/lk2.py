#!/usr/bin/env python3
"""Team 12: Linkado grupo re-harvest with fixed RSC parser."""
import json, re, html, requests, time
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261107/"
SCRATCH = WAVE + "scratch-team12/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})\b")

lk_ids = json.load(open(SCRATCH + "lk_ids.json"))
print("grupo ids:", len(lk_ids), flush=True)

def clean_name(n):
    n = html.unescape(n or "").strip()
    n = re.sub(r"\s+", " ", n)
    return n

def parse_lk_grupo(text):
    m = CODE_RE.search(text)
    if not m:
        return None
    code = m.group(1)
    name = ""
    # breadcrumb JSON-LD: position 4 = group name
    bm = re.search(r'"position":4,"name":"((?:[^"\\]|\\.)*)"', text)
    if bm:
        name = clean_name(bm.group(1))
    if not name:
        og = re.search(r'"property":"og:title","content":"((?:[^"\\]|\\.)*)"', text)
        if not og:
            og = re.search(r'<meta property="og:title" content="([^"]*)"', text)
        if og:
            name = clean_name(og.group(1))
            name = re.sub(r"^Grupo de WhatsApp\s+", "", name, flags=re.I)
            name = re.sub(r"\s+-\s+(Links?|Linkado|Grupos? de WhatsApp.*)$", "", name, flags=re.I)
    desc = ""
    dm = re.search(r'"property":"og:description","content":"((?:[^"\\]|\\.)*)"', text)
    if dm:
        desc = clean_name(dm.group(1))[:300]
    if not desc:
        dm2 = re.search(r'<meta property="og:description" content="([^"]*)"', text)
        if dm2:
            desc = clean_name(dm2.group(1))[:300]
    return {"name": name, "code": code, "desc": desc}

def fetch_grupo(gid):
    url = f"https://linkado.app/grupo/{gid}"
    for attempt in range(2):
        try:
            s = requests.Session()
            r = s.get(url, headers={**UA, "RSC": "1"}, timeout=45)
            if r.status_code == 200 and len(r.content) > 500:
                return r.text
        except Exception:
            pass
        time.sleep(1)
    return None

def fetch_one(item):
    gid, cat = item
    t = fetch_grupo(gid)
    if t is None:
        return None
    p = parse_lk_grupo(t)
    if p and p["name"]:
        p["category"] = cat
        return p
    return None

lk_raw = {}
gids = list(lk_ids.items())
with ThreadPoolExecutor(max_workers=8) as ex:
    for n, p in enumerate(ex.map(fetch_one, gids), 1):
        if p and p["code"] not in lk_raw:
            lk_raw[p["code"]] = p
        if n % 100 == 0:
            print(f"progress {n}/{len(gids)} raw={len(lk_raw)}", flush=True)
print("LK unique named records:", len(lk_raw), flush=True)
json.dump(lk_raw, open(SCRATCH + "lk_raw.json", "w"), ensure_ascii=False, indent=1)
print("LK2 DONE", flush=True)
