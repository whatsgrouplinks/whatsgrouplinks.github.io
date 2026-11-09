#!/usr/bin/env python3
"""Team 13 step 2b: parse CACHED group pages, resolve redirects (HEAD only), incremental save."""
import json, os, re, subprocess, time, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team13_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

step1 = json.load(open(os.path.join(WAVE, "team13_step1.json")))
groups = step1["groups"]
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

def parse_group(gid, html):
    info = {"gid": gid, "bytes": len(html)}
    m = re.search(r"<title>(.*?)\s*\[WhatsApp Group\]", html)
    info["name"] = m.group(1).strip() if m else ""
    m = re.search(r'href="/redirect/(\d+)/(\d+)"', html)
    info["redirect"] = f"/redirect/{m.group(1)}/{m.group(2)}" if m else ""
    m = re.search(r"/en/category/whatsapp/\d+/([^\"']+)", html)
    info["own_cat_slug"] = m.group(1) if m else ""
    m = re.search(r'<h1 class="text-center my-3">.*?</h1>(.*?)<h3 class="mb-0">Similar', html, re.S)
    if m:
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        info["desc"] = re.sub(r"\s+", " ", t).strip()[:600]
    else:
        info["desc"] = ""
    info["similar_ids"] = sorted(set(re.findall(r"/group/(\d+)", html)) - {gid})
    return info

parsed = {}
for fn in sorted(os.listdir(RAW)):
    if fn.startswith("group-") and fn.endswith(".html"):
        gid = fn[6:-5]
        html = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
        if len(html) < 500:
            print("SHORT", gid, len(html), flush=True)
            continue
        parsed[gid] = parse_group(gid, html)
        if gid not in groups:
            groups[gid] = {"gid": gid, "cat": "Unknown-similar", "from": "similar-carousel", "list_name": "", "list_desc": ""}
print("parsed cached group pages:", len(parsed), flush=True)
print("names missing:", sum(1 for p in parsed.values() if not p["name"]),
      "redirects missing:", sum(1 for p in parsed.values() if not p["redirect"]), flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})")
def resolve_one(gid):
    redir = parsed[gid].get("redirect", "")
    if not redir:
        return gid, ""
    url = "https://grupbul.com" + redir
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "12", "-A", UA, "-D", "-", "-o", "/dev/null", url],
                           capture_output=True, text=True, timeout=20)
        m = CODE_RE.search(r.stdout or "")
        if m:
            return gid, m.group(1)
        return gid, ""
    except Exception:
        return gid, ""

codes = {}
gids = sorted(parsed.keys())
# resume support
if os.path.exists(os.path.join(WAVE, "team13_codes.json")):
    codes = json.load(open(os.path.join(WAVE, "team13_codes.json")))
    print("resumed codes:", len(codes), flush=True)
todo = [g for g in gids if g not in codes]
print("to resolve:", len(todo), flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    for i, (gid, code) in enumerate(ex.map(resolve_one, todo)):
        codes[gid] = code
        if code:
            print(f"{i+1}/{len(todo)} CODE {gid} {code}", flush=True)
        if (i + 1) % 10 == 0:
            json.dump(codes, open(os.path.join(WAVE, "team13_codes.json"), "w"))
            print(f"  ... saved {len(codes)} ({i+1}/{len(todo)})", flush=True)
        time.sleep(0.2)
json.dump(codes, open(os.path.join(WAVE, "team13_codes.json"), "w"))
json.dump({"groups": groups, "parsed": parsed, "codes": codes},
          open(os.path.join(WAVE, "team13_step2.json"), "w"), indent=1)
fresh = {g: c for g, c in codes.items() if c and c not in existing}
print("resolved:", sum(1 for c in codes.values() if c), "/", len(codes))
print("fresh (not in existing):", len(fresh))
print("dup vs existing:", sum(1 for c in codes.values() if c and c in existing))
print("unresolved (no code):", sum(1 for c in codes.values() if not c))
