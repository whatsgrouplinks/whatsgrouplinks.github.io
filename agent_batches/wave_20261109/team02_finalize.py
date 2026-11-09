#!/usr/bin/env python3
"""Team 02 finalize: screen the 2 live codes, write candidates/pending/leads/summary."""
import json

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"

ex = {x["code"]: x for x in json.load(open(f"{WAVE}/team02-extracted.json"))}
vf = {x["code"]: x for x in json.load(open(f"{WAVE}/team02-verified.json"))}
problems = json.load(open(f"{WAVE}/team02-fetch-problems.json"))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
existing_lower = {c.lower() for c in existing}
slice_urls = {x["url"] for x in json.load(open(f"{WAVE}/leads_slice_02.json"))}

live = [c for c, v in vf.items()
        if v["attempts"][-1]["http"] == "200" and v["attempts"][-1]["og_title"]]
dead = [c for c, v in vf.items() if c not in live]

candidates = []
dropped_screen = []
for code in live:
    rec = ex[code]
    name = vf[code]["attempts"][-1]["og_title"].strip()
    title = rec["title"]
    desc = rec["description"]
    blob = (name + " " + title + " " + desc).lower()
    # SCREEN: MLM new-money-plan pitch = same family as Forsage-style free-money schemes
    if "mlm" in blob and "new plan" in blob:
        dropped_screen.append({"code": code, "name": name,
            "reason": "MLM new-money-plan recruitment pitch (Forsage-family free-money scheme)"})
        continue
    candidates.append({
        "name": "Web development",
        "category": "Technology",
        "country": rec["country"],
        "description": ("A community of developers, programmers and tech enthusiasts sharing "
                        "HTML, CSS, JavaScript, Python and web development projects, tutorials "
                        "and coding help."),
        "invite": f"https://chat.whatsapp.com/{code}",
    })

# pending: transport-failed only (rules page timed out, code unknown -> retry the listing)
pending = []
for p in problems["transport_fail"]:
    pending.append({"url": p["url"], "source": p.get("source", ""),
                    "stage": p.get("stage", ""), "note": p.get("note", ""),
                    "title": p.get("title", "")})

# leads: discovered related-group listing URLs, minus slice URLs and minus
# URLs whose listing id already maps to a code in the union (lowercased compare)
raw_leads = json.load(open(f"{WAVE}/team02-new-leads-raw.json"))
leads = []
seen = set()
for l in raw_leads:
    u = l["url"]
    lid = u.rstrip("/").split("/")[-1].lower()
    if u in slice_urls or u in seen or lid in existing_lower:
        continue
    seen.add(u)
    leads.append({"url": u, "source": l["source"]})
leads.sort(key=lambda x: x["url"])

json.dump(candidates, open(f"{WAVE}/team02-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE}/team02-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WAVE}/team02-leads.json", "w"), ensure_ascii=False, indent=1)

summary = {
    "team": "02",
    "slice": "leads_slice_02.json (184 groupsinvite.link related-group listing URLs)",
    "sources": ["groupsinvite.link"],
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dead) + len(problems["dead"]),
    "notes": [
        f"Fetched all 184 listing pages + their /group/rules/ pages (real invite sits on rules page).",
        f"Extracted 169 invite codes: 121 already in .existing_codes.json, 48 new, 0 dup-in-slice.",
        f"Slow-checked all 48 new codes with curl (3 attempts spaced apart for empty og:title): only 2 live (HTTP 200 + non-empty og:title); 46 returned HTTP 200 with empty og:title on all 3 attempts and were marked dead per spec. Manual inspection of one empty case showed WhatsApp's generic invite page with no group name anywhere in the HTML — consistent with revoked/expired invites from old (Jul 2025-era) listings.",
        f"Screened the 2 live: 1 kept (Web development, Technology, IN); 1 dropped — 'ONLY MLM NEW PLAN COME' (network-marketing new-plan pitch, Forsage-family free-money scheme).",
        f"{len(problems['dead'])} listings had no invite code on the rules page (counted in dead); "
        f"{len(pending)} transport failure (rules page curl timeout rc=28) banked in team02-pending.json for retry.",
        f"Discovered {len(raw_leads)} related-group listing URLs; {len(leads)} are genuinely new leads after removing slice URLs and ids already in the union.",
        "No source names/links, phone numbers or personal info in any candidate.",
    ],
}
json.dump(summary, open(f"{WAVE}/team02-summary.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
print("dropped_screen:", dropped_screen)
print("dead codes:", len(dead), "| no-code listings:", len(problems["dead"]))
