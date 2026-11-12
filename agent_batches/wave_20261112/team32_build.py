#!/usr/bin/env python3
"""TEAM32 step 7: build candidates/pending/leads/summary + validate."""
import json, re, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"

CAT = {"virenial_yt": "Entertainment", "tls_shopee_tanam": "Buy & Sell"}
CAT_ART = {"Entertainment": "an entertainment", "Buy & Sell": "a buy & sell"}

pool = {p["code"]: p for p in json.load(open(WAVE + "team32_pool_final.json"))}
verify = {}
for line in open(WAVE + "team32_verify.tsv"):
    parts = line.rstrip("\n").split("\t")
    verify[parts[0]] = {"verdict": parts[1], "og_title": parts[2] if len(parts) > 2 else "", "source": parts[3] if len(parts) > 3 else ""}

assert len(verify) == 131, f"verify rows {len(verify)} != 131"
live = [(c, v) for c, v in verify.items() if v["verdict"] == "live"]
dead = [(c, v) for c, v in verify.items() if v["verdict"] == "dead"]
pending = [(c, v) for c, v in verify.items() if v["verdict"] == "pending"]
print(f"live={len(live)} dead={len(dead)} pending={len(pending)}")

# --- content screen on live titles + source names ---
BLOCK = [r"xnxx", r"xvideos", r"pornhub", r"brazzers", r"hentai", r"call.?girl", r"escort",
         r"18\+.*(sex|porn|xxx|sticker)", r"desi bhabhi", r"sexual home", r"hookup",
         r"crypto.?airdrop", r"airdrop.*crypto", r"binary.?option", r"paid.?hack",
         r"venda de xit", r"betting", r"ai.?trading.*profit", r"daily.?profit"]
exclusions = []
candidates = []
for code, v in sorted(live, key=lambda x: (x[1]["source"], x[0])):
    name = html.unescape(v["og_title"]).strip()
    src = v["source"]
    cat = CAT.get(src, "Community & Social")
    low = name.lower()
    hit = [p for p in BLOCK if re.search(p, low)]
    if hit:
        exclusions.append({"code": code, "name": name, "source": src,
                           "reason": f"LIVE og:title matched block pattern(s): {hit}"})
        continue
    desc = f"Join {name} — {CAT_ART[cat]} WhatsApp group in Indonesia for members to connect, chat and share updates."
    candidates.append({"name": name, "category": cat, "country": "ID",
                       "description": desc,
                       "invite": f"https://chat.whatsapp.com/{code}"})

# --- validation ---
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
codes = [c["invite"].split("/")[-1] for c in candidates]
assert len(codes) == len(set(codes)), "duplicate codes in candidates"
assert not (set(codes) & union), "union leak in candidates"
VALID_CATS = {"Education","Entertainment","Jobs","Community & Social","Sports","Funny","Islamic",
              "Health","Finance","News","Buy & Sell","Friendship","Gaming","Technology","Business",
              "Cooking","Crypto","Real Estate","Poetry"}
for c in candidates:
    assert c["category"] in VALID_CATS, c
    assert re.fullmatch(r"[A-Z]{2}", c["country"]), c
    assert c["description"].startswith("Join "), c
    assert "thelastsurvivors" not in json.dumps(c).lower() and "virenial" not in json.dumps(c).lower() \
        and "grouplinksforyou" not in json.dumps(c).lower(), c
    assert not re.search(r"\+?\d[\d\s\-]{7,}\d", c["name"] + c["description"]), c  # no phones
print(f"candidates={len(candidates)} exclusions={len(exclusions)}")

json.dump(candidates, open(WAVE + "team32-newdirs-seasia-candidates.json", "w"), indent=1, ensure_ascii=False)

# --- pending: transport failures (none this run; Ramadhan 2 now dead) ---
pending_out = []
for code, v in pending:
    p = pool[code]
    pending_out.append({"name": p.get("name", "") or v["og_title"], "category": CAT.get(v["source"], "Community & Social"),
                        "country": "ID",
                        "description": f"Join {p.get('name','')} — a WhatsApp group in Indonesia for members to connect, chat and share updates.",
                        "invite": f"https://chat.whatsapp.com/{code}",
                        "reason": "transport failure on verify (curl timeout/connection)"})
json.dump(pending_out, open(WAVE + "team32-newdirs-seasia-pending.json", "w"), indent=1, ensure_ascii=False)

# --- leads: disposition of all 16 team27 leads + sub-leads ---
leads = [
 "https://www.thelastsurvivors.org/grup-wa-shopee-tanam/ (MINED: 24 bit.ly links, 23 resolved to codes, 16 live — see candidates; bit.ly/ShopeeKeEmpatbi did not redirect, dead short link)",
 "https://www.thelastsurvivors.org/category/grup/ (MINED: index lists only 5 grup articles — ff, sahur, shopee-tanam, youtubers, editor — all already mined by team27 except shopee-tanam; no new articles)",
 "https://aussiesin.com/ (STILL BLOCKED: requests fail + curl rc=52 empty reply on retry; needs browser leg; SE Asia country pages unmined)",
 "https://joinnchat.com/philippines-girl-whatsapp-group-link/ (JS-HIDDEN: static HTML + wp-json post 581 contain ZERO invite links; follow-on page https://joinnchat.com/girl-whatsapp-group-join/ also 0 codes; needs browser leg)",
 "https://virenial.com/teknologi/vr-11228/100-grup-wa-subscribe-youtube-yang-bisa-anda-ikuti (MINED via handler?url= encoded links: 89 codes, 71 fresh, 11 live — see candidates)",
 "https://helloworldawaits.com/digital-nomad-travel/trusted-travel-whatsapp-channel/ (NO LINKS: 'Join Asia Travel WhatsApp Group' page contains zero whatsapp.com links in static HTML; invite likely JS-gated; needs browser leg)",
 "https://whtsgrouplink.com/travel-whatsapp-group-links/ (CLOUDFLARE: 'One moment, please...' challenge page, 12KB; needs browser leg)",
 "https://grouplink.com.in/1300-international-whatsapp-group-link/ (MINED: 34 codes, ALL 34 already in union — 0 fresh)",
 "https://www.scribd.com/document/578911793/11-Ribu-Link-Grup-WA-Dengan-Nama-Grup (JS/LOGIN-WALLED: 1.3MB shell, 0 codes in static HTML; needs browser leg)",
 "https://www.scribd.com/document/423556831/11rb-Link-Group-WA-Dengan-Nama-Group (JS/LOGIN-WALLED: 1.5MB shell, 0 codes in static HTML; needs browser leg)",
 "https://www.grouplinksforyou.com/feeds/posts/default?alt=json&max-results=50 (MINED feed: 33 posts, only 1 in-slice — #19 'Link Grup WA Bisnis Indonesia' 97 codes, 37 fresh, 0 live; other 32 posts are Pakistan/India/Gulf/crypto/forex — out of slice, not banked)",
 "https://techsslash.com/philippines-whatsapp-group-links/ (MINED: 11 codes, ALL 11 already in union — 0 fresh)",
 "https://www.whtsagrouplinks.com/international-whatsapp-groups-links/ (CLOUDFLARE: HTTP 403 on retry; needs browser leg)",
 "https://groupwa.link/jobs/ https://groupwa.link/education/ https://groupwa.link/gaming/ (PAGE 1 MINED EARLIER by team27: 10 cards each, all in union or team27 pool — 0 fresh. PAGES 2+ via wagd_more ajax: POST https://groupwa.link/wp-admin/admin-ajax.php {action:'wagd_more', p:2, c:'Jobs'|'Education'|'Gaming', o:'', l:'', n:'10'} — Cloudflare 'Checking your browser' challenge on retry; needs browser leg. Same ajax pattern serves all groupwa categories: news/islamic/sports/health/movies/cricket/online-earning.)",
 "https://joinnchat.com/girl-whatsapp-group-join/ (SUB-LEAD from joinnchat PH page: 0 invite codes in static HTML; JS Join buttons; needs browser leg)",
 "https://bit.ly/ShopeeKeEmpatbi (UNRESOLVED short link from shopee-tanam table row 'Shopee Tanam' — curl follows to itself, no chat.whatsapp.com target; dead short link, not verifiable)",
]
json.dump(leads, open(WAVE + "team32-newdirs-seasia-leads.json", "w"), indent=1, ensure_ascii=False)

from collections import Counter
summary = {
 "team": "team32",
 "slice": "NEW directory discovery - SE Asia (Indonesia, Malaysia, Philippines, Thailand, Vietnam, Singapore) — team27 leads",
 "verified": len(live),
 "dead": len(dead),
 "pending": len(pending),
 "leads": len(leads),
 "exclusions": exclusions,
 "ramadhan_recheck": {
   "HKGPWAcXHgV9GS3A3j6wZg": "dead (session + curl confirm, empty og:title, HTTP 200)",
   "JuxbmdqiwAnJPUCIpP32XT": "dead (session + curl confirm, empty og:title, HTTP 200)",
   "note": "Both pending codes from team27 are now resolved dead; nothing remains pending from team27."
 },
 "counts_by_source": {
   "virenial_yt": {"extracted": 89, "fresh_vs_union_and_team27": 71, "live": 11, "dead": 60},
   "grouplinksforyou_feed_post19_bisnis_indonesia": {"extracted": 97, "fresh_vs_union_and_team27": 37, "live": 0, "dead": 37},
   "tls_shopee_tanam_bitly": {"extracted": 24, "resolved_to_codes": 23, "unresolved": 1, "fresh_vs_union_and_team27": 23, "live": 16, "dead": 7},
   "grouplink_intl": {"extracted": 34, "fresh": 0, "note": "all 34 already in union"},
   "techsslash_ph": {"extracted": 11, "fresh": 0, "note": "all 11 already in union"},
   "groupwa_jobs_education_gaming_page1": {"extracted": 30, "fresh": 0, "note": "all in union or team27 pool (mined by team27)"},
   "grouplinksforyou_feed_other_32_posts": {"extracted": 1854, "fresh": 0, "note": "out of slice (Pakistan/India/Gulf/crypto/forex); dropped, not verified"}
 },
 "dedupe": "Fresh pool 131 = 71 virenial + 37 feed#19 + 23 shopee; checked against 112,070-code union + team27's 346 pool codes. Dropped pre-verify: 146 in union, 7 in team27 pool, 1,854 out-of-slice feed codes. 0 union leaks in candidates, 0 duplicate codes.",
 "verification": "Controls first: known-live KrDwdK8EIkB6vgauHg5M7N (og:title 'JAY - PHP & Python Full Stack Developer') passed; fabricated ZZZZZZZZZZZZZZZZZZZZZZZZ empty og:title passed. Method: curl browser UA, --max-time 90, 4 parallel workers; LIVE = non-empty og:title (og:description fallback); empty og:title confirmed with a second spaced curl before dead; transport failures retried 3x spaced 45s then pending (0 pending). Evidence: team32_raw/verify_<code>.html for live codes; team32_verify.tsv + team32_verify.jsonl.",
 "notes": [
   "Virenial codes were URL-encoded behind /handler?url=https%3A%2F%2Fchat.whatsapp.com%2FCODE links; names concatenated across split anchor tags (e.g. 'Youtube SEO Indon'+'e'+'sia' = 'Youtube SEO Indonesia'). Final names use live og:title.",
   "Grouplinksforyou feed post #19 names are 'Join Now' buttons only ('Grup Bisnis WA' label); names use live og:title — but 0/37 live, so no names banked from it.",
   "Shopee bit.ly links were bare text (no scheme) in the table; 23/24 resolved via curl -L to chat.whatsapp.com codes (3 carried ?fbclid= suffixes, stripped). 16/23 live — freshest source this run.",
   "Grouplink intl + techsslash PH yielded 0 fresh — both pages' codes are already in groups.json.",
   "Feed #19 (Indonesia business) 0/37 live — Nov 3 post, already stale or invite-rotated.",
   "No live title triggered the porn/scam screen; 0 exclusions among the 27 kept. Girls/friendship groups: none in this pool."
 ],
 "resume": "Pool fully verified (131/131 resolved: 27 live, 104 dead, 0 pending). Ramadhan pendings resolved dead. Next wave: browser leg for the still-blocked leads — aussiesin.com SE Asia country pages; joinnchat.com PH girl page + /girl-whatsapp-group-join/ (JS Join buttons, 0 links in HTML/wp-json); groupwa.link wagd_more pages 2+ (POST admin-ajax.php action=wag_more, p=2, c=<Category>, o='', l='', n='10', CF-challenged); whtsgrouplink.com travel page + whtsagrouplinks.com intl page (Cloudflare); helloworldawaits Asia travel channel page (no links in HTML); scribd 11rb compilations x2 (JS/login-walled). New directory discovery for SE Asia beyond these leads is open — thelastsurvivors category/grup index is exhausted (5 articles, all mined).",
 "files": ["team32-newdirs-seasia-candidates.json", "team32-newdirs-seasia-pending.json",
           "team32-newdirs-seasia-leads.json", "team32-newdirs-seasia-summary.json",
           "team32_pool_final.json", "team32_verify.tsv", "team32_verify.jsonl",
           "team32_fetch.json", "team32_shopee_resolved.json", "team32_ramadhan_recheck.json",
           "team32_run.py", "team32_fetch.py", "team32_extract.py", "team32_filter.py",
           "team32_step5.py", "team32_verify.py", "team32_build.py", "team32_raw/"]
}
json.dump(summary, open(WAVE + "team32-newdirs-seasia-summary.json", "w"), indent=1, ensure_ascii=False)
print("WROTE all 4 output files")
print("candidates by category:", Counter(c["category"] for c in candidates))
for c in candidates:
    print(f"  {c['category'][:12]:12s} {c['name'][:55]}")
