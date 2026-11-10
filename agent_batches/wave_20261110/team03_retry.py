#!/usr/bin/env python3
"""Retry pass for team03 wave 20261110: re-fetch GI detail-failed listings
and GCC go.php recovery failures (congestion timeouts, not dead listings)."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110")
import team03_run as T
from concurrent.futures import ThreadPoolExecutor

BASE = T.BASE
raw = json.load(open(f"{BASE}/team03-raw.json"))
by_url = {r["listing_url"]: r for r in raw}
leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_03.json"))
lead_by_url = {x["url"]: x for x in leads}

targets = []
for r in raw:
    if r.get("error") == "detail fetch failed" and r["source"] == "groupsinvite.link":
        targets.append(("gi", r["listing_url"]))
    elif r.get("error", "").startswith("go.php recovery failed"):
        targets.append(("gcc", r["listing_url"]))
print("retry targets:", len(targets), flush=True)

def gcc_recover2(n):
    # variant A: join.php with -L, final effective URL
    for url in (f"https://groupchatconnect.info/join.php?id={n}",
                f"https://groupchatconnect.info/go.php?id={n}",
                f"https://groupchatconnect.info/go?id={n}"):
        try:
            r = subprocess.run(["curl", "-s", "-A", T.UA, "--max-time", "25", "-L",
                                "-o", "/dev/null", "-w", "%{url_effective}", url],
                               capture_output=True, timeout=35)
            final = r.stdout.decode("utf-8", errors="replace").strip()
            m = re.search(r"groupsor\.link/group/join/([A-Za-z0-9]+)", final)
            if m:
                rules = T.fetch(f"https://groupsor.link/group/rules/{m.group(1)}/")
                c = T.code_in(rules)
                if c:
                    return c, None
            m2 = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})", final)
            if m2:
                return m2.group(1), None
        except Exception as e:
            continue
    return None, "join.php/go.php did not resolve to groupsor or chat link"

def work(t):
    kind, url = t
    item = lead_by_url[url]
    if kind == "gi":
        recs, lds = T.process_gi(item)
        return url, recs[0], lds
    rec = by_url[url]
    n = url.rstrip("/").split("/")[-1]
    c, err = gcc_recover2(n)
    if c:
        rec2 = dict(rec); rec2["code"] = c; rec2.pop("error", None)
        rec2["recovered_via"] = "go.php retry v2"
        return url, rec2, []
    rec2 = dict(rec); rec2["error"] = f"go.php recovery failed: {err}"
    return url, rec2, []

new_leads = []
with ThreadPoolExecutor(max_workers=3) as ex:
    for url, rec, lds in ex.map(work, targets):
        by_url[url] = rec
        new_leads.extend(lds)
        print(("OK  " if rec.get("code") else "FAIL"), url, "|", rec.get("code") or rec.get("error"), flush=True)

raw2 = list(by_url.values())
json.dump(raw2, open(f"{BASE}/team03-raw.json", "w"), ensure_ascii=False, indent=1)
# recompute fresh vs union
existing = set(json.load(open(f"{T.SITE}/.existing_codes.json")))
groups = json.load(open(f"{T.SITE}/groups.json"))
gcodes = set()
for r in groups:
    m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)", r.get("invite", ""))
    if m:
        gcodes.add(m.group(1))
union = existing | gcodes
seen, fresh = set(), []
for r in raw2:
    c = T.norm_code(r.get("code")); r["code"] = c
    if not c or c in union or c in seen:
        continue
    seen.add(c); fresh.append(r)
json.dump(fresh, open(f"{BASE}/team03-fresh.json", "w"), ensure_ascii=False, indent=1)
disc = json.load(open(f"{BASE}/team03-discovered-leads.json"))
slice_urls = {x["url"] for x in leads}
have = {l["url"] for l in disc}
for l in new_leads:
    if l["url"] not in slice_urls and l["url"] not in have:
        have.add(l["url"]); disc.append(l)
json.dump(disc, open(f"{BASE}/team03-discovered-leads.json", "w"), ensure_ascii=False, indent=1)
print(f"after retry: records={len(raw2)} fresh_unique={len(fresh)} discovered={len(disc)}", flush=True)
