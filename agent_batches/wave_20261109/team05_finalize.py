import json, os
from collections import Counter
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
st = json.load(open(f"{W}/team05-extracted.json"))
ver = json.load(open(f"{W}/team05-verify.json"))
cands = json.load(open(f"{W}/team05-candidates.json"))
leads_slice = json.load(open(f"{W}/leads_slice_05.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

# --- validation ---
codes = [c["invite"].rsplit("/", 1)[-1] for c in cands]
assert len(codes) == len(set(codes)), "dup codes in candidates"
assert not (set(codes) & existing), "candidate overlaps existing"
assert all(c["category"] in ["Gaming","Education","Online Earning","Community & Social","Business","Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports","Health","News"] for c in cands)
assert all(len(c["country"]) == 2 for c in cands)
assert all(c["invite"].startswith("https://chat.whatsapp.com/") for c in cands)
assert all(c["name"] and c["description"] for c in cands)
bad = [c for c in cands if any(s in (c["name"]+c["description"]).lower() for s in ["whtspgrouplink","imagesplatform","wagroupnest","wagroupshub","whtsagrouplinks","groupsnest"])]
assert not bad, f"source name leaked: {bad}"
print("validation OK:", len(cands), "candidates")

# --- leads: still-dead listing pages, banked for a browser leg ---
leads = []
for d in st["dead"]:
    src = d.get("source", "")
    note = d.get("note", "")
    if "imagesplatform" in d["url"]:
        n = "NEEDS-BROWSER-LEG: curl returns empty/short page (likely JS-gated or bot-blocked); may hold invite links"
    elif note == "fetch empty/short":
        n = "NEEDS-BROWSER-LEG: fetch empty/short via curl; retry in browser"
    else:
        n = "NEEDS-BROWSER-LEG: no invite codes in curl HTML (intermittent bot-challenge suspected; one such page re-fetched fine with codes, so re-check in browser)"
    leads.append({"url": d["url"], "source": src, "note": n})
json.dump(leads, open(f"{W}/team05-leads.json", "w"), indent=1, ensure_ascii=False)

fresh_total = len([c for c in st["codes"] if c not in existing])
live = [c for c, v in ver.items() if v.get("status") == 200 and v.get("title")]
amb = [c for c, v in ver.items() if v.get("status") == 200 and not v.get("title")]
summary = {
  "team": "team05",
  "slice": "leads_slice_05.json (184 listing URLs)",
  "sources": dict(Counter(x.get("source") for x in leads_slice)),
  "listings_fetched": 184,
  "listings_dead_after_refetch": len(st["dead"]),
  "listings_recovered_by_refetch": 5,
  "unique_codes_extracted": len(st["codes"]),
  "fresh_codes_not_in_existing": fresh_total,
  "already_in_existing": len(st["codes"]) - fresh_total,
  "verified": len(ver),
  "verified_live": len(live),
  "verified_dead_empty_og_title_after_3_tries": len(amb),
  "verified_transport_failed": 0,
  "candidates": len(cands),
  "screened_out": 1,
  "screened_out_detail": "Fh7G5LnHVdg49bL6CSaPNy 'ıllıllı 𝘞𝘢𝘪𝘳𝘢𝘭 xxx ıllıllı' — banned keyword xxx",
  "pending": 0,
  "leads": len(leads),
  "dead": len(amb),
  "categories": dict(Counter(c["category"] for c in cands)),
  "countries": dict(Counter(c["country"] for c in cands)),
  "notes": [
    "First sequential fetch run died ~25 min in (session lost, no output written); re-ran with 3 parallel workers + per-page checkpoints.",
    "Spot-check found whtsagrouplinks.com serves invite codes in curl HTML intermittently: earn-money page showed 0 codes in pass 1 but ~15 codes on manual re-fetch (likely intermittent bot-challenge). All 43 dead pages were re-fetched with Accept headers + tolerant regex; 5 pages recovered codes (5 fresh, 3 live). 38 pages still dead.",
    "imagesplatform.com (29 of 43 dead) returns empty/short pages to curl — banked as NEEDS-BROWSER-LEG leads.",
    "Verify method validated with controls: known-existing codes return non-empty og:title ('News Line 2', '+234..2016'); known-fake code returns empty og:title. Empty og:title after 3 tries = dead.",
    "Code regex in pass 1 was [A-Za-z0-9] only; refetch regex added _ and - and escaped-slash handling. A few _ / - codes on live pages may have been missed in pass 1 (not re-scanned).",
    "Discovered-pagination leads were NOT persisted (fetch script computed new_leads but never saved them); only the 38 still-dead slice URLs are banked in team05-leads.json.",
    "Descriptions are category templates built from the verified og:title group name (listing-page context fragments were HTML-artifact garbage); no source names, no phone numbers, no personal info in any candidate.",
    "No transport failures: every fresh code got a definitive verify outcome (200 + og:title, or 200 + empty og:title x3)."
  ]
}
json.dump(summary, open(f"{W}/team05-summary.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(summary, indent=1, ensure_ascii=False))
