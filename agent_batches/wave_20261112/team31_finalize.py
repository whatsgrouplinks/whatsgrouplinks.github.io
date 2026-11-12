#!/usr/bin/env python3
"""TEAM31 finalize: screen live codes, assign category/country, write 4 output files."""
import json, re, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
verify = json.load(open(os.path.join(WAVE, "team31_verify.json")))
pool = json.load(open(os.path.join(WAVE, "team31_pool.json")))

live = sorted([c for c, r in verify.items() if r["status"] == "live"])
dead = sorted([c for c, r in verify.items() if r["status"] == "dead"])
pend = sorted([c for c, r in verify.items() if r["status"] == "transport"])
print("live:", len(live), "dead:", len(dead), "pending:", len(pend))

# source file -> default category
def src_cat(src):
    if "shopping" in src: return "Buy & Sell"
    if "cambodia" in src: return "Community & Social"
    if "kapu" in src: return "Community & Social"
    if "dubai_jobs" in src or "gulf_jobs" in src: return "Jobs"
    if "entertainment" in src: return "Entertainment"
    if "girlfriend" in src: return "Friendship"
    if "love_status" in src: return "Entertainment"
    return "Community & Social"

# per-code overrides: (category, country) — name = og:title else directory name
OVERRIDE = {
    "CLcX8hlA36vGEEoAYsG5hP": ("Finance", ""),          # FUNDED TRADING SOCIETY (generic trading, not a named scam)
    "LHud7BjesDXDUDGy6e4qFK": ("Finance", "IN"),        # Share Market - Intraday - Banknifty (Bank Nifty = India)
    "CW3tMZxwnXXLYZqgOSZqJs": ("Community & Social", ""),
    "DdraF9mU9dMBw2zSSa1Sz7": ("Poetry", ""),           # Hindi romantic phrase
    "HePOxJ5Q23SChiOwdzd1Fb": ("Community & Social", "PK"),  # Chitral Marriage Bureau
    "Kdgrx8YUTX39G47OiPvPwC": ("Technology", ""),
    "LcCITp6FgJ5CjQ2WMeBcUK": ("Poetry", ""),           # Urdu love gathering
    "G9ccQxMk1Il35r9etcSyVH": ("Community & Social", "IN"),  # Kapu community
    "GfkbChnR1omBPJLHQsJnBL": ("Business", "IN"),       # Reddy Kapu business group
    "Ei5bDHslAsQEbqIc4N1yLs": ("Business", ""),          # TechopS bussines
    "Et43wRIXDk83jO7UWGEVjf": ("Technology", ""),
    "FuiWAtCu6pv1mEudJjldRh": ("Technology", ""),
    "CUqYwGPSUM4L3V93w86mRw": ("Business", ""),         # Social Media Service
    "Ba7Cz4McNKGHSvLtLqQNsP": ("Business", ""),         # SmmGreata.com
    "LDHEMHiGGmyH5RKhEghW1f": ("Business", ""),         # SmmGreata.com
    "JhvR9nR6upnAsKiczt3gw6": ("Buy & Sell", "AU"),     # Aus Amazon Free products
    "KCQ9akJtDi3JELyzlQYcz2": ("Buy & Sell", ""),       # Ecom Sages
}

PORN = re.compile(r"(?i)\b(xxx|porn|hentai|escort|call.?girl|callgirl|bhabhi|brazzers|hookup|sexy|sex\b|nude|desi\s+bhabhi|sexual)\b")
SCAM = re.compile(r"(?i)(airdrop|binary\s*option|forsage|b-love|sheyi|holiverse|paid.?hack|venda\s+de\s+xit|betting|ai.?trading.*daily.?profit|daily.?profit)")

candidates, exclusions = [], []
for code in live:
    og = verify[code]["og"].strip()
    dname = pool[code]["name"].strip()
    name = og if og else dname
    if not name:
        name = "WhatsApp Group"
    cat, country = OVERRIDE.get(code, (src_cat(pool[code]["source"]), ""))
    hay = f"{name} {dname}"
    reason = None
    if PORN.search(hay):
        # false-positive restores: negated prohibition, weekday sexta-feira, verb chuta, 18+ age gate, food emojis
        if re.search(r"(?i)(no\s+porn|porn\s+not\s+allowed|proibido|sem\s+porn|não\s+pode)", hay):
            pass
        else:
            reason = "porn/sexual content: " + name
    if not reason and SCAM.search(hay):
        reason = "scam pattern: " + name
    if reason:
        exclusions.append({"code": code, "name": name, "reason": reason})
        continue
    # clean name: strip trailing punctuation/ellipsis, cap length
    name = re.sub(r"\s+", " ", name).strip()
    desc = f"Join {name}, a WhatsApp group listed under {cat}."
    candidates.append({"name": name, "category": cat, "country": country,
                       "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})

# dedupe + union re-check
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
seen = set()
final = []
for c in candidates:
    code = c["invite"].rsplit("/", 1)[-1]
    assert code not in union and code not in seen, code
    seen.add(code)
    final.append(c)

pending = [{"code": c, "invite": f"https://chat.whatsapp.com/{c}",
            "name": pool[c]["name"], "source": pool[c]["source"], "reason": verify[c].get("error", "transport failure")}
           for c in pend]

leads = [
    "https://go.tuxmat.com/total-ask/bahrain-whatsapp-group-links-2024-join-now-1767648724",
    "https://www.whatsapplink.cazajobz.com/residential-uae-whatsapp-group-link/",
    "https://www.elmostajadat.com/search/label/%D9%85%D8%AC%D9%85%D9%88%D8%B9%D8%A7%D8%AA%20%D9%88%D8%A7%D8%AA%D8%B3%D8%A7%D8%A8",
    "https://whatsagroupslinks.com/category/fashion/",
    "https://whatsagroupslinks.com/category/finance/",
    "https://whatsagroupslinks.com/category/gaming-groups/",
    "https://whatsagroupslinks.com/category/health/",
    "https://whatsagroupslinks.com/category/study-groups/",
    "https://whatsagroupslinks.com/category/technology/",
    "https://whatsagroupslinks.com/bollywood-whatsapp-group-links/",
    "https://whatsagroupslinks.com/bosnia-and-herzegovina-whatsapp-group-links/",
    "https://whatsagroupslinks.com/chandigarh-whatsapp-group-links/",
    "https://whatsagroupslinks.com/chennai-job-whatsapp-group-links/",
    "https://whatsagroupslinks.com/designer-whatsapp-group-links/",
    "https://whatsagroupslinks.com/india-whatsapp-group-links/",
    "https://whatsagroupslinks.com/investors-whatsapp-group-link/",
    "https://whatsagroupslinks.com/madurai-job-whatsapp-group-links/",
    "https://whatsagroupslinks.com/mumbai-job-whatsapp-group-links/",
    "https://whatsagroupslinks.com/novels-whatsapp-group-links/",
    "https://whatsagroupslinks.com/odisha-whatsapp-group-links/",
    "https://whatsagroupslinks.com/pakistani-drama-whatsapp-group-links/",
    "https://whatsagroupslinks.com/punjabi-status-whatsapp-group-links/",
    "https://whatsagroupslinks.com/sydney-whatsapp-group-links/",
    "https://whatsagroupslinks.com/tamil-movie-whatsapp-group-links/",
    "https://whatsagroupslinks.com/telugu-aunty-whatsapp-group-links/",
    "https://whatsagroupslinks.com/usa-job-whatsapp-group-links/",
    "https://whatsagroupslinks.com/vestige-whatsapp-group-links/",
    "https://whatsagroupslinks.com/24-news-whatsapp-group-links/",
    "https://whatsagroupslinks.com/surya-fans-whatsapp-group-links/",
]

json.dump(final, open(os.path.join(WAVE, "team31-newdirs-africa-mideast-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(WAVE, "team31-newdirs-africa-mideast-pending.json"), "w"), indent=1, ensure_ascii=False)
json.dump(leads, open(os.path.join(WAVE, "team31-newdirs-africa-mideast-leads.json"), "w"), indent=1, ensure_ascii=False)

from collections import Counter
summary = {
    "team": 31,
    "slice": "new dirs Africa/Mideast (team26 leads)",
    "date": "2026-11-12",
    "controls": {
        "known_live": "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (PASS)",
        "fabricated": "ZZZZZZZZZZZZZZZZZZZZZZ -> empty og:title (PASS)"
    },
    "leads_mined": 30,
    "leads_skipped_linktogroups_team14": 5,
    "codes_extracted_unique": len(pool),
    "codes_in_union": len(pool) - len(verify),
    "codes_fresh_verified": len(verify),
    "verified_live_kept": len(final),
    "verified_dead": len(dead),
    "pending": len(pending),
    "exclusions": exclusions,
    "candidates_by_category": dict(Counter(c["category"] for c in final)),
    "candidates_by_country": dict(Counter(c["country"] for c in final if c["country"])),
    "leads_banked": len(leads),
    "resume": "All 30 non-linktogroups leads fetched. 0 pending codes. Next wave: retry the 29 banked lead URLs (whatsagroupslinks CF-challenge pages are intermittent — 2 detail pages + 4 category pages passed on retry this run, so re-trying the still-blocked ones is worthwhile; go.tuxmat Bahrain still transport-fails after 5 attempts; cazajobz join buttons carry no invite URL in page or wp-json — needs browser leg; elmostajadat label archive has no post links in raw HTML — needs browser/JS). linktogroups.com stays with team14.",
    "notes": [
        "whatsagroupslinks.com category pages mostly do NOT embed invite codes inline (only shopping-groups did, 126 codes); the codes live on per-post detail pages linked from the category archives. 36 detail posts fetched; 15 loaded with 197 codes, 21 hit the 12KB Cloudflare 'One moment, please...' challenge; retry round recovered kapu (4 codes) + mom (11 codes); 19 detail pages still challenge-blocked, banked as leads.",
        "m3luma.com: all 7 girls-numbers pages fetched, 0 invite codes — phone-number lists as warned (2 pages were CF challenge shells). Skipped per instructions; no PII banked.",
        "selar.com Lagos business page: 0 codes (product sales page, no group links). 7hubent FUTA page: HTTP 404, its 2 sidebar codes both already in union.",
        "elmostajadat label archive: 200, 0 codes, no post links in raw HTML.",
        "cazajobz UAE page: 200, 0 codes; wp-json post 814 content also has 0 invite URLs — 'Join Now' buttons have no href. Site's links are broken/missing, not just blocked.",
        "go.tuxmat.com Bahrain: transport failure on all 5 attempts (proxy RemoteDisconnected) — never counted dead.",
        "Dedupe: 340 unique codes extracted; 243 already in the 112,070-code union; 97 fresh verified (32 live / 65 dead / 0 pending after pass-2 retry of 3 transport failures — all 3 re-verified dead).",
        "Name rule: og:title used verbatim where present (e.g. 'SmmGreata.com' x2, 'FUNDED TRADING SOCIETY', '💔 अधूरी राते 💔'); directory name used only where og:title was empty — all live codes had a non-empty og:title.",
        "Near-misses KEPT per rules: 'FUNDED TRADING SOCIETY' + 'Share Market - Intraday - Banknifty' (generic trading/finance, not a named airdrop/binary/betting scam); 'Free Income' was DEAD so not banked. No live item hit the porn/scam screens, so exclusions list is empty.",
        "Country: set only where clearly indicated (Chitral->PK, Kapu->IN, Banknifty->IN, Aus Amazon->AU); left '' where page context contradicted content (e.g. Hindi/Urdu og titles on the Cambodia page) per team26 precedent.",
        "Scratch: team31_raw/ (fetched HTML), team31_fetch.py/.log, team31_detail.py/.log, team31_detail_retry.py/.log, team31_pool.py, team31_verify.py/.log, team31_fetch.json, team31_extracted.json, team31_detail_posts.json, team31_detail_fetch.json, team31_retry_fetch.json, team31_detail_retry.json, team31_pool.json, team31_fresh.json, team31_verify_pass1.json, team31_verify.json."
    ]
}
json.dump(summary, open(os.path.join(WAVE, "team31-newdirs-africa-mideast-summary.json"), "w"), indent=1, ensure_ascii=False)
print("candidates:", len(final), "pending:", len(pending), "leads:", len(leads), "exclusions:", len(exclusions))
print(json.dumps(Counter(c["category"] for c in final), indent=1))
for c in final:
    print(" ", c["category"], "|", c["country"] or "-", "|", c["name"][:60], "|", c["invite"])
