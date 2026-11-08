#!/usr/bin/env python3
"""TEAM17 wrap-up: bank everything RIGHT NOW.
Merges verified items + unverified candidates (not yet attempted) into the
team17 output files. Called on coordinator wrap-up order."""
import json, re, os, html as ihtml, unicodedata as _u

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
import sys
sys.path.insert(0, BASE)
import importlib.util
spec = importlib.util.spec_from_file_location("fin", os.path.join(BASE, "team17_finalize.py"))
fin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fin)

prog = json.load(open(os.path.join(BASE, "team17-progress.json")))
verified = prog["verified"]
old_pending = prog["pending"]
porn = prog.get("porn_drops", 0)

# candidates never verified (wrap-up stop): not in verified and not in old pending
seen_codes = {v["invite"].split("/")[-1] for v in verified} | {p.get("code") for p in old_pending}
cands = json.load(open(os.path.join(BASE, "team17-candidates.json")))["candidates"]
new_pending = []
for r in cands:
    if r["code"] in seen_codes:
        continue
    r2 = dict(r)
    r2["note"] = "wrap-up stop — not yet attempted"
    new_pending.append(r2)
    seen_codes.add(r["code"])

all_pending = old_pending + new_pending
print(f"verified={len(verified)} old_pending={len(old_pending)} "
      f"new_pending={len(new_pending)} porn={porn}")

out, seen = [], set()
dropped = 0
for i, x in enumerate(verified):
    meta = x.get("_meta", {})
    name = fin.clean_name(x["name"], meta.get("title", ""))
    code = x["invite"].split("/")[-1]
    if code in seen:
        dropped += 1; continue
    if not name or len(name) < 3 or fin.BAD_NAME.match(name):
        dropped += 1; continue
    if fin.PORN_RE.search(name) or fin.EMOJI_RE.search(name):
        porn += 1; dropped += 1; continue
    if fin.DROP_RE.search(name):
        dropped += 1; continue
    cat = fin.classify(name + " " + meta.get("desc", "") + " " + meta.get("tag", ""))
    ctry = x["country"]
    cname = fin.COUNTRY_NAME.get(ctry, ctry)
    desc = fin.DESC[cat][i % 2].format(c=cname)
    if fin.PORN_RE.search(desc):
        desc = fin.DESC["Other"][i % 2].format(c=cname)
    seen.add(code)
    out.append({"name": name, "category": cat, "country": ctry,
                "description": desc, "invite": x["invite"], "image": ""})

json.dump(out, open(os.path.join(BASE, "team17-igrupos-latam2.json"), "w"),
          ensure_ascii=False, indent=1)

pend = []
for r in all_pending:
    pend.append({"name": r.get("title", ""), "category": "Other",
                 "country": r.get("iso", ""), "description": "",
                 "invite": f"https://chat.whatsapp.com/{r['code']}",
                 "image": "", "note": r.get("note", "")})
json.dump(pend, open(os.path.join(BASE, "team17-unverified-pending.json"), "w"),
          ensure_ascii=False, indent=1)

print(f"final verified={len(out)} dropped={dropped} porn_total={porn} pending={len(pend)}")
cats = {}
for x in out: cats[x["category"]] = cats.get(x["category"], 0) + 1
print(sorted(cats.items()))
