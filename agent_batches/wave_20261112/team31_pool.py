#!/usr/bin/env python3
"""TEAM31 pool rebuild: <li>NAME - <a href=chat.whatsapp.com/CODE>Join</a></li> pattern."""
import json, re, os
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")
LI_RE = re.compile(
    r"<li[^>]*>\s*(?:<strong>)?([^<]{1,120}?)(?:</strong>)?\s*[–\-—:]\s*"
    r"<a[^>]*href=\"https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})\"",
    re.S)

def clean(n):
    n = re.sub(r"\s+", " ", unescape(n)).strip(" –—-: \t")
    return n

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
pool = {}
files = []
for d in ["team31_raw", "team31_raw/detail"]:
    for fn in sorted(os.listdir(os.path.join(WAVE, d))):
        if fn.endswith(".html"):
            files.append((d, fn))
for d, fn in files:
    html = open(os.path.join(WAVE, d, fn), encoding="utf-8", errors="ignore").read()
    src = fn.replace(".html", "").replace("_", "/")
    for m in LI_RE.finditer(html):
        name, code = clean(m.group(1)), m.group(2)
        if code not in pool:
            pool[code] = {"name": name, "source": fn, "cat_hint": ""}
    for code in CODE_RE.findall(html):
        if code not in pool:
            pool[code] = {"name": "", "source": fn, "cat_hint": ""}

fresh = {c: v for c, v in pool.items() if c not in union}
print("files:", len(files), "pool:", len(pool), "fresh:", len(fresh), "in-union:", len(pool) - len(fresh), flush=True)
print("fresh without name:", sum(1 for v in fresh.values() if not v["name"]), flush=True)
json.dump(pool, open(os.path.join(WAVE, "team31_pool.json"), "w"), indent=1)
json.dump(fresh, open(os.path.join(WAVE, "team31_fresh.json"), "w"), indent=1)
for c, v in sorted(fresh.items()):
    print(" FRESH", c, "|", repr(v["name"][:70]), "|", v["source"][:60], flush=True)
