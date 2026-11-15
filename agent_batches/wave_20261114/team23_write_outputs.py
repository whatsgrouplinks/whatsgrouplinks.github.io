#!/usr/bin/env python3
import json
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
leads = [
 {"site": "groupsor.in", "urls": ["https://groupsor.in/sitemap/groups"],
  "note": "3,804 group detail pages; only 7 SA categories mined (301 pages, 150 fresh). Remaining categories (dating-flirting, love-romance, movies-tv-series, shayari-status-quotes, sports, travel-tourism, health-fitness, fashion-clothing, fan-club-celebrities, social-media-promotion, digital-marketing, make-money-earning, others; adult-18-hot DO NOT MINE) unmined. Codes hide in /golink/wagroups-<CODE> href on detail pages. Homepage JS-loaded via /loadmoredata (403)."},
 {"site": "groupssor.com", "urls": ["https://groupssor-api.blog-99n.workers.dev/api/groups"],
  "note": "Public JSON API, 500-entry cap, no working pagination/filter. User-submitted, spam-heavy: 212 fresh, 123 pre-screened out (38 porn, 6 betting, 2 scam by name; 77 non-SA). Re-poll next run for newer submissions."},
 {"site": "whatsgroupjoinlinks.com", "urls": ["https://whatsgroupjoinlinks.com/"],
  "note": "Cloudflare challenge to requests; needs browser leg."},
 {"site": "whtsagrouplinks.com", "urls": ["https://www.whtsagrouplinks.com/"],
  "note": "Cloudflare challenge (team25 also blocked); needs browser leg. Snippets show 330+ Indian / 690+ Pakistani groups."},
 {"site": "tglinkhub.com", "urls": ["https://tglinkhub.com/whatsapp-group-links/"],
  "note": "Cloudflare challenge; needs browser leg. Snippets show BD/PK/IN sections."},
 {"site": "whtsagroupslinks.com", "urls": ["https://www.whtsagroupslinks.com/"],
  "note": "HTTP 403 to requests; retry later or browser leg."},
 {"site": "wagroup.in", "urls": ["https://wagroup.in/tag/lanka-whatsapp-groups/feed/"],
  "note": "Unreachable from this VM (proxy error on http+https, Nov 14); retry later. Sri Lanka Tamil news groups."},
 {"site": "whatgroups.com", "urls": ["https://whatgroups.com/whatsapp-group-links-pakistan/"],
  "note": "BD page mined Nov 14 (49 codes, 0 fresh). Pakistan page unmined; retry (Cloudflare cleared for BD page)."},
]
leads += [
 {"site": "groupwa.link", "urls": ["https://groupwa.link/"],
  "note": "Homepage mined (230 codes, 0 fresh). Category/country sub-pages unmined; same pool likely, low yield."},
 {"site": "groupinvitelink.com", "urls": ["https://groupinvitelink.com/"],
  "note": "Homepage mined (175 codes, 0 fresh). Sub-pages unmined."},
 {"site": "whtspgrouplink.com", "urls": ["https://whtspgrouplink.com/"],
  "note": "Homepage mined (180 codes, 0 fresh). Sub-pages unmined."},
 {"site": "whatsappgrouplink.org", "urls": ["https://whatsappgrouplink.org/"],
  "note": "DO NOT MINE as a directory: domain now serves Yono Games gambling APK content."},
 {"site": "wappgrouplinks.com", "urls": ["https://wappgrouplinks.com/"],
  "note": "DO NOT MINE as a directory: domain now a medical blog, no WhatsApp groups."},
 {"site": "hubrecipes.com", "urls": ["https://hubrecipes.com/join-active-nepali-girls-whatsapp-group-links/"],
  "note": "DO NOT MINE (carried from team25): sexualized listings + personal phone numbers."},
 {"site": "groupslink.pk", "urls": ["https://groupslink.pk/sexy-whatsapp-group-link/", "https://groupslink.pk/xxx-video-whatsapp-group-links/", "https://groupslink.pk/night-girls-whatsapp-group-links/", "https://groupslink.pk/school-girls-whatsapp-group-links/", "https://groupslink.pk/18-whatsapp-group-links/", "https://groupslink.pk/whatsapp-sex-group-links/"],
  "note": "DO NOT MINE these posts: porn/sex/xxx, night-girls, school-girls, 18+ content."},
]
json.dump(leads, open(f"{WD}/team23-leads.json", "w"), ensure_ascii=False, indent=1)
gs_ex = json.load(open(f"{WD}/team23_groupssor_excluded.json"))
dead_ex = json.load(open(f"{WD}/team23_dead_excluded.json"))
excluded = [{"code": e["code"], "name": e.get("name", ""), "reason": e["reason"], "source": e.get("source", "")} for e in gs_ex]
excluded += [{"code": e["code"], "name": e.get("name", ""), "reason": e["reason"], "source": e.get("source", "")} for e in dead_ex["excluded_live_title"]]
pend = json.load(open(f"{WD}/team23-pending.json"))
cands = json.load(open(f"{WD}/team23-candidates.json"))
SRC = [
 {"site": "groupslink.pk", "urls": ["https://groupslink.pk/"], "pages_mined": 11, "yielded_codes": True, "fresh": 17, "note": "Homepage 27 codes/1 fresh; 10 clean posts mined, 82 codes/16 fresh. Category archives 0 codes. Porn posts NOT mined."},
 {"site": "grouplink.com.in", "urls": ["https://grouplink.com.in/explore-the-active-pakistani-whatsapp-group-links-right-here/"], "pages_mined": 1, "yielded_codes": True, "fresh": 22, "note": "All 22 fresh verified DEAD (stale directory)."},
 {"site": "groupssor.com", "urls": ["https://www.groupssor.com/"], "pages_mined": 2, "yielded_codes": True, "fresh": 212, "note": "Homepage JS-rendered (0 codes); public JSON API gave 500 entries (327 WhatsApp, 212 fresh). 89 SA kept; 123 pre-screen excluded."},
 {"site": "groupwa.link", "urls": ["https://groupwa.link/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "230 codes, all in union."},
 {"site": "whatsappgrouplink.org", "urls": ["https://whatsappgrouplink.org/"], "pages_mined": 1, "yielded_codes": False, "fresh": 0, "note": "Now a Yono Games gambling APK site. DO NOT MINE."},
 {"site": "groupinvitelink.com", "urls": ["https://groupinvitelink.com/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "175 codes, all in union."},
 {"site": "whtspgrouplink.com", "urls": ["https://whtspgrouplink.com/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "180 codes, all in union."},
 {"site": "groupsor.in", "urls": ["https://groupsor.in/", "https://groupsor.in/sitemap/groups"], "pages_mined": 301, "yielded_codes": True, "fresh": 150, "note": "Codes from /golink/wagroups-<CODE> href on detail pages in 7 SA category sitemaps (301 pages). 3,804 group pages total; only 7 SA categories mined."},
 {"site": "wappgrouplinks.com", "urls": ["https://wappgrouplinks.com/"], "pages_mined": 1, "yielded_codes": False, "fresh": 0, "note": "Now a medical blog. DO NOT MINE."},
 {"site": "whatsgroupjoinlinks.com", "urls": ["https://whatsgroupjoinlinks.com/"], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "Cloudflare challenge, unmined; see leads."},
 {"site": "whtsagroupslinks.com", "urls": ["https://www.whtsagroupslinks.com/"], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "HTTP 403, unmined; see leads."},
 {"site": "activesocilalinks.com", "urls": ["https://activesocilalinks.com/"], "pages_mined": 1, "yielded_codes": True, "fresh": 3, "note": "390 codes, 3 fresh; 2 verified LIVE."},
 {"site": "wagroup.in", "urls": ["https://wagroup.in/tag/lanka-whatsapp-groups/feed/"], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "Unreachable (proxy/connection failure); see leads."},
 {"site": "whatstele.com", "urls": ["https://whatstele.com/whatsapp/group-links/tamil/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "206 codes, all in union."},
 {"site": "whtsagrouplinks.com", "urls": ["https://www.whtsagrouplinks.com/"], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "Cloudflare challenge on homepage + IN + PK pages, unmined; see leads."},
 {"site": "whatgroups.com", "urls": ["https://whatgroups.com/bangladesh-whatsapp-group-links/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "49 codes, all in union. Pakistan page unmined, see leads."},
 {"site": "tglinkhub.com", "urls": ["https://tglinkhub.com/whatsapp-group-links/"], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "Cloudflare challenge, unmined; see leads."},
 {"site": "whatzgrouplink.com", "urls": ["https://whatzgrouplink.com/bangladesh-whatsapp-group-link/"], "pages_mined": 1, "yielded_codes": True, "fresh": 0, "note": "16 codes, all in union."},
 {"site": "web search (Nepal)", "urls": [], "pages_mined": 0, "yielded_codes": False, "fresh": 0, "note": "No Nepal directory found (only hubrecipes.com, DO-NOT-MINE). Two Nepal codes in snippets (Nomads in Nepal; Live Guru NEB class) - both already in union."},
]
summary = {
 "team": "team23",
 "slice": "South Asia fresh-directory discovery (Pakistan / India / Bangladesh / Sri Lanka / Nepal)",
 "sources": SRC,
 "controls": {
  "live": "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (PASS)",
  "fabricated": "ZzZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title after retries (PASS, dead)"
 },
 "verification": "One requests.Session per run, browser UA, 60-75s timeout. Live = non-empty, non-generic og:title (og:description ignored, always generic). Empty og:title retried 3x spaced before dead. HTTP 429 -> pending, never dead. NOTE: verify2 run was killed by a service restart at 120/239 and resumed from saved results; WhatsApp began rate-limiting (HTTP 429) partway through the groupsor.in batch - 65 went pending, a retry pass after a 7-min cooldown resolved 21 (16 to dead/live, 5 still 429) then stopped after 5 consecutive 429s. 44 never re-attempted + 5 re-429 = 49 pending.",
 "raw": 1843, "verified": 281, "dupes": 1440, "dead": 199,
 "excluded": len(excluded),
 "excluded_breakdown": {"groupssor_api_prescreen": 123, "of_which_porn_xxx_by_directory_name": 38, "of_which_betting_casino_by_directory_name": 6, "of_which_crypto_airdrop_free_money_scam_by_directory_name": 2, "of_which_non_sa_country": 77, "live_title_screen": 1},
 "pending": len(pend), "candidates": len(cands), "leads": len(leads),
 "excluded_list": excluded,
 "pending_codes": [p["code"] for p in pend],
 "resume_point": "49 pending groupsor.in codes (all HTTP 429) in team23-pending.json - retry in a later run after a longer cooldown, fresh session, slower pace. groupsor.in still has ~3,500 unmined group pages (remaining categories in sitemap/groups). groupssor API re-poll for new submissions (500-entry cap). Cloudflare sites (whatsgroupjoinlinks.com, whtsagrouplinks.com, tglinkhub.com) need a browser leg.",
 "flags": [
  "Live og:title 'Inactive' (Gi8BfXNCsNi9RZOlop0J8U) kept as Education - group is literally named 'Inactive'; category from its groupsor.in education listing.",
  "Country '' on 19 candidates: live title + directory gave no reliable country signal (groupsor.in education/jobs/friendship/entertainment categories are not country-specific).",
  "Tamil newcomers group (G2NrbLdUhQxID1fAiiga86) country '' - Tamil could be IN or LK; left blank rather than guessed.",
  "1 groupssor pre-screen-excluded code overlapped a code verified via another source (403 fresh = 281 verified + 122 never attempted; pre-screen list has 123 entries).",
 ]
}
json.dump(summary, open(f"{WD}/team23-summary.json", "w"), ensure_ascii=False, indent=1)
print("leads:", len(leads), "excluded:", len(excluded), "pending:", len(pend), "candidates:", len(cands))
print("summary written")
