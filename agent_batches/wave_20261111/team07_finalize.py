#!/usr/bin/env python3
"""TEAM 07 — finalize: build leads file + summary from current outputs."""
import json, collections
from urllib.parse import urlparse

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
CANON = {"Education", "Jobs", "Entertainment", "Islamic", "News", "Sports", "Technology",
         "Health", "Business", "Gaming", "Friendship", "Community & Social", "Online Earning",
         "Crypto", "Cooking", "Poetry", "Travel", "Scholarship", "Freelance", "Real Estate",
         "Buy Sell", "Finance", "Funny"}

verified = json.load(open(f"{WAVE}/team07-leads-slice7.json"))
pending = json.load(open(f"{WAVE}/team07-leads-slice7-pending.json"))
failed = json.load(open(f"{WAVE}/team07-failed.json"))
exclusions = json.load(open(f"{WAVE}/team07-exclusions.json"))
prog = json.load(open(f"{WAVE}/team07-mined-progress.json"))
cands = json.load(open(f"{WAVE}/team07-candidates.json"))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))

# sanity checks on verified
bad_cat = [v for v in verified if v["category"] not in CANON]
dup_inv = [k for k, n in collections.Counter(v["invite"] for v in verified).items() if n > 1]
overlap = [v for v in verified if v["invite"].rsplit("/", 1)[-1] in existing]
missing = [v for v in verified if not all(k in v for k in ("name", "category", "country", "description", "invite"))]
print(f"verified={len(verified)} bad_cat={len(bad_cat)} dup_invites={len(dup_inv)} overlap_existing={len(overlap)} missing_fields={len(missing)}")

# leads: unique failed listing pages, deduped by effective URL
seen_eff, leads = set(), []
for f in failed:
    eff = f.get("effective_url") or f["url"]
    if eff in seen_eff:
        continue
    seen_eff.add(eff)
    leads.append(f["url"])
leads = sorted(set(leads))
with open(f"{WAVE}/team07-leads-slice7-leads.json", "w") as fh:
    json.dump(leads, fh, ensure_ascii=False, indent=1)

# dead count: pass-1 dead (278) + recheck dead_now (progress file) + exclusions handled separately
dead = 278
try:
    rp = json.load(open(f"{WAVE}/team07-recheck-progress.json"))
    dead += rp.get("dead_now", 0)
except FileNotFoundError:
    pass

sources = collections.Counter()
for c in cands:
    sources[urlparse(c["source_url"]).netloc] += 1

summary = {
    "team": "team07",
    "slice": "leads_slice7",
    "sources": dict(sources),
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads),
    "dead": dead,
    "exclusions": exclusions,
    "resume": ("Mining complete (3600/3600 effective listing URLs processed; 10912 raw codes mined, "
               "1073 new vs existing). Verification pass 1 complete. Pending recheck in progress/finished "
               "per team07-recheck-progress.json. Remaining leads file = failed listing pages to retry next wave."),
    "notes": (
        "Slice had 3603 raw URLs -> 3600 effective (3 share/intent URLs unwrapped to their embedded listing pages: "
        "grupbul.com group pages, wglfinder, hubrecipes). wagroupnest.com (149 failed) and wagroupshub.com (115 failed) "
        "listing pages mostly timed out under shared-egress load and are in the leads file for retry. "
        "chat.whatsapp.com checks were slow (18-45s/request) with heavy transport failures during the wave-wide "
        "verification storm; pending codes are transport failures only, NOT dead codes. "
        "Live rate among new codes was low (~2-3%): most new codes return HTTP 200 with empty og:title = DEAD per rule. "
        "No merge into groups.json, no generate.py, no deploy (per assignment). "
        "Files: team07-leads-slice7.json (verified), team07-leads-slice7-pending.json (pending), "
        "team07-leads-slice7-leads.json (unmined listing URLs), team07-leads-slice7-summary.json (this file)."
    ),
}
with open(f"{WAVE}/team07-leads-slice7-summary.json", "w") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1)
print(f"SUMMARY verified={len(verified)} pending={len(pending)} leads={len(leads)} dead={dead} exclusions={len(exclusions)}")
print("by category:", dict(collections.Counter(v['category'] for v in verified)))
print("by country:", dict(collections.Counter(v['country'] for v in verified if v['country'])))
