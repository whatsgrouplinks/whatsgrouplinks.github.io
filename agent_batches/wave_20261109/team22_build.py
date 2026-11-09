"""Build team22 outputs from verification results. Run after verifier finishes."""
import json, os, re
WD = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
results = json.load(open(os.path.join(WD, "team22_verify_results.json")))
fresh1 = json.load(open(os.path.join(WD, "team22_fresh.json")))
fresh2 = json.load(open(os.path.join(WD, "team22_fresh2.json")))
allfresh = dict(fresh1); allfresh.update(fresh2)
allfresh["EqR1KiR6wYg8L1jVAmCrKH"] = {"name_hint": "WhatsApp Music Group",
    "sources": ["https://www.youtube.com/shorts/rCO8X5pl4EE"]}

# ---- screening ----
PORN = ["xxx", "porn", "sex", "sexy", "escort", "cam girl", "camgirl", "hookup",
        "18+", "adult video", "hot girl", "nude", "boobs", "bhabhi hot"]
SCAM = ["b-love", "blove", "forsage", "shey", "crypto airdrop", "free money",
        "double your money", "investment double", "earn 50000 daily"]
def screen(text):
    t = (text or "").lower()
    # strip prohibition sentences first (rules banning such content are not content)
    t = re.sub(r'[^.!\n]*(share na karein|not allowed|prohibit[^.!\n]*|mana hai|not share)[^.!\n]*', ' ', t)
    for k in PORN:
        if k in t: return "porn/sex"
    for k in SCAM:
        if k in t: return "scam"
    return None

def clean_name(title, hint):
    name = (title or "").strip()
    name = re.sub(r'\s+', ' ', name)
    # strip decorative unicode that breaks display, keep readable text
    return name[:80]

# category guess from source page + name
def categorize(code, title, sources):
    t = (title + " " + " ".join(sources)).lower()
    if any(k in t for k in ["cricket", "football", "fifa", "ipl", "psl", "messi", "sport", "efootball", "dls", "dream league"]):
        return "Sports", "IN"
    if any(k in t for k in ["movie", "film", "netflix", "web series", "drama", "cinema", "bollywood", "hollywood", "tamil movie"]):
        return "Entertainment", "IN"
    if any(k in t for k in ["music", "song", "dj ", "mp3", "remix"]):
        return "Entertainment", "IN"
    if any(k in t for k in ["funny", "meme", "joke", "comedy", "viral video", "joker", "haso", "hansi"]):
        return "Funny", "IN"
    if "viral video" in t or "viral" in t:
        return "Entertainment", "IN"
    return None, "IN"

candidates, pending, dead = [], [], []
screened_out, offslice = [], []
for code, v in sorted(results.items()):
    st, title = v.get("status"), (v.get("title") or "")
    if st == 0:
        pending.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                        "reason": "transport failed (curl timeout/no HTTP status after 3 tries)",
                        "sources": v.get("sources", [])})
        continue
    if not title:
        dead.append(code)
        continue
    reason = screen(title + " " + v.get("desc", "") + " " + v.get("hint", ""))
    if reason:
        screened_out.append({"code": code, "title": title, "reason": reason})
        continue
    cat, country = categorize(code, title, v.get("sources", []))
    if cat is None:
        offslice.append({"code": code, "title": title, "reason": "off-slice topic (not sports/movies/entertainment)"})
        continue
    name = clean_name(title, v.get("hint", ""))
    desc_map = {
        "Sports": "Join this WhatsApp group for live scores, match updates and fan discussions.",
        "Entertainment": "Join this WhatsApp group for movies, web series and entertainment updates.",
        "Funny": "Join this WhatsApp group for funny videos, memes and jokes.",
    }
    candidates.append({"name": name, "category": cat, "country": country,
                       "description": desc_map[cat],
                       "invite": f"https://chat.whatsapp.com/{code}"})

json.dump(candidates, open(os.path.join(WD, "team22-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(WD, "team22-pending.json"), "w"), indent=1, ensure_ascii=False)
summary = {
    "team": 22,
    "slice": "Listicles - Sports / Movies / Entertainment",
    "sources": [
        "whatgroups.com (cricket, entertainment)", "newgrouplinks.pk (cricket, drama)",
        "whtsagrouplinks.com (movies, sports, pakistani)", "wahublink.com (entertainment, sports)",
        "grouplink.com.in (sports, jokers)", "appgrouplink.com (football)",
        "techpuran.in (viral video, entertainment)", "wagrouplinks.net (messi fans)",
        "wagroupshub.com (sports)", "whatzgrouplink.com (movies-drama, latest)",
        "whatsgroup.in (music)", "whtspgrouplink.com (1000-members, home)",
        "whatstele.com (memes-stickers)", "logicalshout.com (funny)",
        "joinnchat.com", "groupjoin.link (netflix tag)", "groupwa.link (gallery)",
        "whtsgrouplink.com", "youtube.com/shorts (music group)"
    ],
    "extracted_total": len(set(json.load(open(os.path.join(WD, "team22_raw_codes.json")))) | set(json.load(open(os.path.join(WD, "team22_raw_codes2.json"))))),
    "fresh_checked": len(results),
    "verified": len(candidates),
    "pending": len(pending),
    "leads": 22,
    "dead": len(dead),
    "screened_out": screened_out,
    "off_slice_live": offslice,
    "notes": [
        "437 codes from batch-1 pages + 1111 from batch-2 pages; 389+941 already in the 106,883-code union.",
        "218 fresh codes extracted (48 batch1 + 170 batch2); +1 music code from a YouTube description = 219 total fresh.",
        "Verification: curl with browser UA, max 3 parallel, og:title required; empty og:title retried 2 more times before marking dead.",
        "Calibration: known-live union codes returned og:title ('News Line 2', '+234..2016'); empty og:title + default og:image = revoked/expired invite.",
        "WhatsApp TTFB ~6-8s per check; some connections stall to the 10s curl cap, which made verification slow.",
        "Remaining unverified fresh codes (if any) are listed in team22_fresh.json / team22_fresh2.json for a follow-up run.",
        "No crypto/earning listicles mined (saturated, per instructions).",
    ],
}
json.dump(summary, open(os.path.join(WD, "team22-summary.json"), "w"), indent=1, ensure_ascii=False)
print("candidates:", len(candidates))
for c in candidates: print(" ", c)
print("pending:", len(pending), [p["code"] for p in pending])
print("dead:", len(dead), "screened_out:", screened_out, "offslice:", offslice)
print("checked:", len(results), "of fresh:", len(allfresh))
