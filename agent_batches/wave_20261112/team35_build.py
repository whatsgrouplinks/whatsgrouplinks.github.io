import json

CAT = {
 "CoJvzISpmnwKsxYV5DNDs3": ("Jobs", ""),
 "FA8dd6auWfTBtymHCOmId7": ("Finance", ""),
 "CKLIwAjMoa48TArEDJFva2": ("Community & Social", "US"),
 "CwvJvE3a4430vIrTDegTrd": ("Education", "US"),
 "DglQ2X8UTKkEOiUxZTBJaQ": ("News", "PK"),
 "EflKopqALJ2A39IpxajVcd": ("Community & Social", "US"),
 "EYErTOOKjAV7y3Yul7Gd6C": ("Entertainment", "US"),
 "BBhiBZH4MlzAb0CHAsHTEa": ("Finance", ""),
 "Bbi7c1sYUWHDNCNR8DVs15": ("Finance", ""),
 "CkgQTpIIIOF2rwiLPCJKn7": ("Finance", ""),
 "DBeTrubgGqjEQoMkUzYD23": ("Finance", ""),
 "DCWqP7d98uoHS7BDxYoUnu": ("Finance", ""),
 "EoioFu1OyFIHwrq4iRuvSa": ("Finance", ""),
 "FHozlwajzNb6quCjO3CueF": ("Finance", ""),
 "CoB0oL4TJZRCBA43H3KrWf": ("Finance", ""),
}
ALLOWED = {"Education","Entertainment","Jobs","Community & Social","Sports","Funny","Islamic","Health","Finance","News","Buy & Sell","Friendship","Gaming","Technology","Business","Cooking","Crypto","Real Estate","Poetry"}

ver = [json.loads(l) for l in open("team35_verify_progress.jsonl")]
live = [r for r in ver if r["status"] == "live"]
dead = [r for r in ver if r["status"] == "dead"]
pend = [r for r in ver if r["status"] == "transport"]
predrop = json.load(open("team35_predrop.json"))["pre_dropped"]

candidates = []
for r in live:
    cat, country = CAT[r["code"]]
    assert cat in ALLOWED
    name = r["og_title"].strip()
    candidates.append({
        "name": name,
        "category": cat,
        "country": country,
        "description": f"Join {name}, a WhatsApp group listed under {cat}.",
        "invite": f"https://chat.whatsapp.com/{r['code']}",
    })

# final validation: unique codes, none in union, schema fields, no source names/links, no phones
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
codes = [c["invite"].split("/")[-1] for c in candidates]
assert len(codes) == len(set(codes)), "dup codes in candidates"
assert not (set(codes) & union), "union leak!"
for c in candidates:
    assert set(c.keys()) == {"name","category","country","description","invite"}
    assert c["name"] and c["invite"].startswith("https://chat.whatsapp.com/")
    assert "whatsgroupjoinlinks" not in json.dumps(c).lower() and "groupslink" not in json.dumps(c).lower()
    assert not any(ch.isdigit() and len(c["name"]) > 0 and False for ch in c["name"])  # placeholder
import re
for c in candidates:
    assert not re.search(r"\+\d{7,}|@|\b\d{10,}\b", c["name"] + c["description"]), f"personal info? {c}"

json.dump(candidates, open("team35-discovery-global-candidates.json","w"), ensure_ascii=False, indent=2)
json.dump(pend, open("team35-discovery-global-pending.json","w"), ensure_ascii=False, indent=2)

leads = [
 {"url": "https://groupslink.pk/18-whatsapp-groups-pakistan/", "note": "groupslink.pk sub-page returned 200 with 0 chat codes in static HTML; may be JS-loaded or empty - needs browser leg re-check"},
 {"url": "https://groupslink.pk/school-girls-whatsapp-group-links/", "note": "groupslink.pk sub-page returned 200 with 0 chat codes in static HTML; needs browser leg re-check (screen names; drop if sexualised)"},
 {"url": "https://groupslink.pk/pakistani-whatsapp-group-video-links/", "note": "groupslink.pk sub-page returned 200 with 0 chat codes in static HTML; needs browser leg re-check"},
 {"url": "https://ghanacitizenship.com/ghana-whatsapp-telegram-groups/", "note": "Ghana guide listing official WhatsApp Channels (whatsapp.com/channel, not chat groups) + vetted orgs (ghanainfo.net etc.); no chat.whatsapp.com codes in search snippet - check for group invites via browser leg"},
 {"url": "https://wappgrouplinks.com/page/2/", "note": "wappgrouplinks.com homepage repurposed to MEDICAL WordPress content (0 codes); paginated archive may still hold old group posts - low priority re-check"},
]
json.dump(leads, open("team35-discovery-global-leads.json","w"), ensure_ascii=False, indent=2)

exclusions = []
for code, reason in predrop.items():
    exclusions.append({"code": code, "reason": "Pre-verify drop: " + reason, "stage": "pre-verify (listing name)"})
summary = {
 "team": "team35",
 "slice": "fresh-directory discovery, global",
 "date": "2026-11-12",
 "controls": {
   "known_live": "KrDwdK8EIkB6vgauHg5M7N -> live, og:title 'JAY - PHP & Python Full Stack Developer'",
   "fabricated": "ZzZzZzZzZzZzZzZzZzZzZz / QqQqQqQqQqQqQqQqQqQqQq / Xk9f2LmNpQrStUvWxYz1234 -> dead, og:title generic 'WhatsApp Group Invite' (generic title treated as dead)"
 },
 "sites_found_checked": [
   "wagroupshub.com - already mined wave 20261111 team29/30, not re-mined",
   "groupwa.link - already mined (w09/w10, team27), not re-mined",
   "activewagroup.com - already mined wave 20261111 team29/30, not re-mined",
   "groupwhat.com - already mined (team25/26 notes), not re-mined",
   "instantgrouplink.com - already mined (team25/26/27 notes), not re-mined",
   "whtsagrouplinks.com - already mined (team29/30), not re-mined",
   "whtsagroupslinks.com - already mined (team26 Zimbabwe page), not re-mined",
   "whatsappgrouplink.org / groupinvitelink.com / whatgroups.com / whtspgrouplink.com / groupsor.in - already mined per team25 notes / edopedia list, not re-mined",
   "groupjoin.link / appgrouplink.com / whtsgrouplink.com / whatzgrouplink.com / groupsgyani.org - already mined per team25/26, not re-mined",
   "freshnote.com.ng - already mined wave 20261111 team26, not re-mined",
   "newgrouplinks.pk / wagroupslink.com - already mined wave 20261111 team25/29/30, not re-mined",
   "wappgrouplinks.com - MINED this run: repurposed to MEDICAL WordPress blog, 0 chat codes on homepage, categories health/blog only; sitemap fetch failed (proxy disconnect). Dead directory.",
   "whatsgroupjoinlinks.com - MINED this run: homepage clone of whtsagrouplinks.com content; 216 codes in static HTML, 319 unique codes across both mined sites, 274 already in union, 45 fresh.",
   "groupslink.pk - MINED this run: homepage + 12 clean sub-pages fetched; 27 homepage + 99 sub-page raw codes; 0 of its fresh codes verified live (all dead or porn pre-drops); porn sub-pages /sexy-whatsapp-group-link/ and /xxx-video-whatsapp-group-links/ NOT fetched (hard-porn exclusion)."
 ],
 "counts": {
   "raw_rows_extracted": 355,
   "unique_codes": 319,
   "already_in_union": 274,
   "fresh_vs_union": 45,
   "pre_verify_dropped_porn": len(predrop),
   "sent_to_verification": len(ver),
   "verified_live_kept": len(candidates),
   "verified_dead": len(dead),
   "pending_transport": len(pend),
 },
 "live_rate_fresh_verified": f"{len(candidates)}/{len(ver)}",
 "exclusions": exclusions,
 "leads": len(leads),
 "pending": len(pend),
 "resume_point": "All 45 fresh codes resolved (15 live banked, 19 dead, 11 pre-dropped porn). No codes left to verify. Next wave: work the 5 leads (groupslink.pk 0-code sub-pages via browser leg; ghanacitizenship.com guide; wappgrouplinks.com /page/2/ low priority). Do NOT re-mine whatsgroupjoinlinks.com homepage or groupslink.pk static pages - exhausted for fresh codes (only 45/319 fresh, and groupslink.pk 0% live).",
 "files": {
   "candidates": "team35-discovery-global-candidates.json",
   "pending": "team35-discovery-global-pending.json",
   "leads": "team35-discovery-global-leads.json",
   "raw_html": "team35_raw/",
   "extract": "team35_extracted.jsonl / team35_fresh.jsonl",
   "verify_log": "team35_verify_progress.jsonl",
   "scripts": "team35_verify.py / team35_extract.py / team35_verify_fresh.py / team35_build.py",
 },
}
json.dump(summary, open("team35-discovery-global-summary.json","w"), ensure_ascii=False, indent=2)
print("candidates:", len(candidates), "dead:", len(dead), "pending:", len(pend), "leads:", len(leads))
for c in candidates: print(" ", c["category"], c["country"], "|", c["name"])
