#!/usr/bin/env python3
"""TEAM24 finalize: build the three deliverable files from raw round outputs."""
import json, re

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030"
WORK = WAVE + "/team24_work"

CAT_NOUN = {
    "Education": "study group", "Jobs": "jobs group", "Entertainment": "entertainment group",
    "Islamic": "Islamic group", "News": "news group", "Sports": "sports group",
    "Technology": "tech group", "Health": "health group", "Business": "business group",
    "Gaming": "gaming group", "Friendship": "friendship group", "Community & Social": "community group",
    "Online Earning": "online earning group", "Crypto": "crypto group", "Cooking": "cooking group",
    "Poetry": "poetry group", "Travel": "travel group", "Scholarship": "scholarship group",
    "Freelance": "freelance group", "Real Estate": "real estate group", "Buy & Sell": "buy-and-sell group",
}
DEMONYM = {"QA": "Qatari", "PK": "Pakistani", "IN": "Indian", "US": "American", "GB": "British",
           "AE": "Emirati", "SA": "Saudi", "BD": "Bangladeshi", "NP": "Nepali", "LK": "Sri Lankan",
           "PH": "Filipino", "ID": "Indonesian", "MY": "Malaysian", "CA": "Canadian", "AU": "Australian",
           "NG": "Nigerian", "KE": "Kenyan", "GH": "Ghanaian", "MT": "Maltese", "LT": "Lithuanian",
           "RU": "Russian", "DE": "German", "FR": "French", "IT": "Italian", "ES": "Spanish",
           "XX": ""}

BUYSELL_FIX = re.compile(r"boutique|saree|salwar|kurti|lehenga|wear|clothes|apparel|fashion|jewel|vogue|shopping|deal|offer|product|sale", re.I)
AIRDROP_FIX = re.compile(r"airdrop", re.I)
CODE22 = re.compile(r"^[A-Za-z0-9_-]{22}$")
# adult-content exclusion (verified live but sexual framing; excluded per content rules)
ADULT_EXCLUDE = {"DjADR6HD9MKKuLPVDcoifw"}

def clean_name(n):
    n = re.sub(r"\s+", " ", n).strip()
    n = re.sub(r"[\-–—|:>»]+$", "", n).strip()
    if len(n) > 80:
        n = n[:80].rstrip()
    return n

def main():
    items = []
    for rnd in ("r1", "r2", "r3", "r4"):
        try:
            items += json.load(open(f"{WORK}/{rnd}_verified_raw.json"))
        except FileNotFoundError:
            pass
    seen, fresh = set(), []
    for x in items:
        code = x["invite"].rsplit("/", 1)[1]
        if not CODE22.match(code):
            continue
        if code in ADULT_EXCLUDE:
            continue
        if code in seen:
            continue
        seen.add(code)
        name = clean_name(x["name"])
        cat = x["category"]
        if cat == "Community & Social" and BUYSELL_FIX.search(name):
            cat = "Buy & Sell"
        if AIRDROP_FIX.search(name):
            cat = "Crypto"
        ctry = x["country"]
        dem = DEMONYM.get(ctry, "")
        noun = CAT_NOUN.get(cat, "community group")
        geo = f"{dem} " if dem else ""
        desc = f"Join '{name}' \u2014 an active {geo}{noun} on WhatsApp."
        fresh.append({"name": name, "category": cat, "country": ctry,
                      "description": desc, "image": "",
                      "invite": "https://chat.whatsapp.com/" + code})
    json.dump(fresh, open(WAVE + "/team24-fresh-newdirs-deep.json", "w"), ensure_ascii=False, indent=1)
    print("fresh:", len(fresh))

    pending = [
        {"code": "CQoUM2XVasj", "source_page": "https://www.youtube.com/watch?v=6iBKqlGuoek",
         "note": "truncated code from video description snippet (Qatar Religious Institute Scholarship group)"},
    ]
    json.dump(pending, open(WAVE + "/team24-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print("pending:", len(pending))

    leads = [
        {"name": "wagroupslink.com", "code_or_invite": "https://wagroupslink.com/",
         "source_page": "https://wagroupslink.com/", "note": "domain discovery: new directory, 617KB homepage, direct chat.whatsapp.com codes, country pages (USA/PK/IN/RU)"},
        {"name": "groupinvitelink.com", "code_or_invite": "https://groupinvitelink.com/",
         "source_page": "https://groupinvitelink.com/", "note": "domain discovery: new directory, 175 direct codes on homepage, category pages (jobs/study/friendship/gk/upsc/state pages)"},
        {"name": "whatsgroupjoinlinks.com", "code_or_invite": "https://www.whatsgroupjoinlinks.com/",
         "source_page": "https://www.whatsgroupjoinlinks.com/", "note": "domain discovery: new directory, 6,799+ links claimed, 206 direct codes on homepage, category pages (job/educational/friendship/crypto/bgmi)"},
        {"name": "whtspgrouplink.com", "code_or_invite": "https://whtspgrouplink.com/",
         "source_page": "https://whtspgrouplink.com/qatar-whatsapp-group-links/",
         "note": "domain discovery: new directory, 503 posts in sitemap, country + niche pages; NOTE most links verified DEAD this wave (see team24_work dead lists)"},
        {"name": "appgrouplink.com", "code_or_invite": "https://appgrouplink.com/teachers-whatsapp-group-links/",
         "source_page": "https://appgrouplink.com/teachers-whatsapp-group-links/",
         "note": "domain discovery: new directory, teacher/education niche pages; links mostly dead this wave"},
        {"name": "wtgrouplinks.com", "code_or_invite": "https://wtgrouplinks.com/education-news-whatsapp-group-link/",
         "source_page": "https://wtgrouplinks.com/education-news-whatsapp-group-link/",
         "note": "domain discovery: new directory, India state-wise education-news pages"},
        {"name": "whatsonly.com", "code_or_invite": "https://whatsonly.com/",
         "source_page": "https://whatsonly.com/",
         "note": "domain discovery: new directory homepage, jobs/dubai/BGMI sections; yielded live links this wave"},
        {"name": "whtsagrouplinks.com", "code_or_invite": "https://www.whtsagrouplinks.com/international-whatsapp-groups-links/",
         "source_page": "https://www.whtsagrouplinks.com/international-whatsapp-groups-links/",
         "note": "domain discovery: new directory, international/country sections; yielded live links this wave"},
        {"name": "groupsinvite.link", "code_or_invite": "https://groupsinvite.link/business-whatsapp-group/",
         "source_page": "https://groupsinvite.link/business-whatsapp-group/",
         "note": "domain discovery: new directory, business category pages; yielded live links this wave"},
        {"name": "groupwhat.com", "code_or_invite": "https://groupwhat.com/",
         "source_page": "https://www.edopedia.com/blog/groupsor-alternatives/",
         "note": "domain discovery: JS-rendered directory (10,000+ links claimed), no server-side codes; needs JS-capable harvester"},
        {"name": "whatgroups.com", "code_or_invite": "https://whatgroups.com/",
         "source_page": "https://www.edopedia.com/blog/groupsor-alternatives/",
         "note": "domain discovery: JS-rendered directory (22,000+ links claimed), no server-side codes; needs JS-capable harvester"},
        {"name": "whatsappgrouplink.org", "code_or_invite": "https://whatsappgrouplink.org/",
         "source_page": "https://www.edopedia.com/blog/groupsor-alternatives/",
         "note": "domain discovery: JS-rendered directory, no server-side codes on homepage; needs JS-capable harvester"},
        {"name": "groupor.link", "code_or_invite": "https://www.groupor.link/",
         "source_page": "browser_search results 2026-10-30",
         "note": "domain discovery: JS app directory (28 categories, 180+ countries), binary/compressed homepage; needs JS-capable harvester"},
    ]
    json.dump(leads, open(WAVE + "/team24-leads.json", "w"), ensure_ascii=False, indent=1)
    print("leads:", len(leads))

if __name__ == "__main__":
    main()
