#!/usr/bin/env python3
"""TEAM32 step 4: keep only in-slice sources; fix feed#19 names; dedupe vs union + team27 pool."""
import json, re, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
W11 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
# team27's already-verified pool codes (all sources)
t27 = set()
for fn in ["team27_pool.json", "team27_pool2.json", "team27_pool3.json"]:
    try:
        d = json.load(open(W11 + fn))
        if isinstance(d, dict):
            t27.update(d.keys())
        elif isinstance(d, list):
            for it in d:
                if isinstance(it, dict) and "code" in it: t27.add(it["code"])
                elif isinstance(it, str): t27.add(it)
    except Exception as e:
        print("t27 load", fn, e)
print("union:", len(union), "team27 pool codes:", len(t27))

pool = json.load(open(WAVE + "team32_pool_raw.json"))
# drop out-of-slice feed posts: keep only sources virenial, grouplink_intl, techsslash, groupwa, and feed post #19
kept = [p for p in pool if not p["source"].startswith("grouplinksforyou:") or "Bisnis Indonesia" in p["source"]]
print("after slice filter:", len(kept), "dropped:", len(pool) - len(kept))

# Fix feed #19 names: parse post content anchors properly
g = open(WAVE + "team32_raw/grouplinksforyou_feed.html", encoding="utf-8").read()
data = json.loads(g)
post19 = data["feed"]["entry"][19]
content = post19["content"]["$t"]
# find all anchors with chat.whatsapp links; name = anchor inner text stripped, or preceding heading/td text
names19 = {}
for m in re.finditer(r'<a[^>]*href="https://chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})"[^>]*>(.*?)</a>', content, re.S):
    code, inner = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
    inner = html.unescape(inner).strip()
    if inner and inner.lower() not in ("join group", "join now", "join", "click here"):
        names19[code] = inner
print("feed19 anchors with real names:", len(names19), "of", len(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', content))))
# sample of anchor inners
for m in list(re.finditer(r'<a[^>]*href="https://chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})"[^>]*>(.*?)</a>', content, re.S))[:5]:
    print("  ", m.group(1), "|", repr(re.sub(r"<[^>]+>", "", m.group(2)))[:80])
# also check post #18 international business names
post18 = data["feed"]["entry"][18]
c18 = post18["content"]["$t"]
print("post18 codes:", sorted(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', c18))))
for m in re.finditer(r'<a[^>]*href="https://chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})"[^>]*>(.*?)</a>', c18, re.S):
    print("  18:", m.group(1), "|", repr(re.sub(r"<[^>]+>", "", m.group(2)))[:80])

for p in kept:
    if p["code"] in names19:
        p["name"] = names19[p["code"]]

# dedupe vs union + team27 pool
fresh, in_union, in_t27 = [], [], []
for p in kept:
    if p["code"] in union: in_union.append(p)
    elif p["code"] in t27: in_t27.append(p)
    else: fresh.append(p)
print(f"fresh={len(fresh)} in_union={len(in_union)} in_team27_pool={len(in_t27)}")
from collections import Counter
print("fresh by source:", Counter(p["source"].split(':')[0] for p in fresh))
print("in_union by source:", Counter(p["source"].split(':')[0] for p in in_union))
print("in_t27 by source:", Counter(p["source"].split(':')[0] for p in in_t27))
json.dump(fresh, open(WAVE + "team32_pool_fresh.json", "w"), indent=1, ensure_ascii=False)
json.dump({"in_union": [p["code"] for p in in_union], "in_team27": [p["code"] for p in in_t27]},
          open(WAVE + "team32_pool_dropped_dedupe.json", "w"), indent=1)
