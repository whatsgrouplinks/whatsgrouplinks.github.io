#!/usr/bin/env python3
"""TEAM30 finalize: build candidates/pending/leads/summary."""
import json, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SCRATCH = os.path.join(WAVE, "team30_scratch")

def og_title(code):
    for line in open(os.path.join(SCRATCH, "verify_results.jsonl")):
        d = json.loads(line)
        if d["code"] == code:
            return d["title"]
    return ""

CANDIDATES = [
    {
        "name": og_title("DWyo0QkhFZFBNWbpPRKg91"),
        "category": "Entertainment",
        "country": "PK",
        "description": "Join the VIP HD Songs WhatsApp group \u2014 Entertainment community in Pakistan. Active invite link, join to chat and share updates with members.",
        "invite": "https://chat.whatsapp.com/DWyo0QkhFZFBNWbpPRKg91",
    },
    {
        "name": "Pakistan Mall",
        "category": "Buy & Sell",
        "country": "PK",
        "description": "Join Pakistan Mall, a Buy & Sell WhatsApp group in Pakistan. Active invite link, join to chat and share updates with members.",
        "invite": "https://chat.whatsapp.com/KzJBW7FX9Ng44olQ6Ibz6D",
    },
]

OG_EXCLUSIONS = [
    {"code": "GHLxojd0v1NFdJnUSEwDNV", "reason": "og:title 'SO PIR4NHAS' — Brazilian Portuguese adult/sexual group (piranhas = promiscuous-girl slang, leetspeak evasion)"},
    {"code": "IHmVLO71w570SGtLhVJcTK", "reason": "og:title 'NINF4TAS' — 'ninfetas' (nymphets), sexual/underage connotation"},
    {"code": "JOtzGPaRwhj3pjQjibv3rL", "reason": "og:title 'NINFET4AS LOIRAS 🔞' — nymphets + 18+ sexual"},
    {"code": "JQ9tHcI1LpP2iuMitlpE2C", "reason": "og:title 'SO SAF4DINHAS' — 'safadinhas' (naughty girls), sexual content group"},
    {"code": "K3Hhbys6v3mBYFAIzIDzbj", "reason": "og:title 'NOVINHAS +18' — 'novinhas' (young girls) + 18 sexual"},
    {"code": "KbslFnSwUSELRtWJie6MZJ", "reason": "og:title 'VAZ4DINHOS' — 'vazadinhos' (leaked nudes) group"},
    {"code": "LEjKaTk0dSh1YbNHKkbeGT", "reason": "og:title 'SO PUT4RIA' — 'putaria' (pornographic content)"},
    {"code": "LNhEGyjFCcoKjrNReXYhwL", "reason": "og:title 'SO NOVINHAS 🔞' — 'novinhas' (young girls) + 18 sexual"},
    {"code": "J9WBIR7Hh1KHwfNyL2Bv3X", "reason": "og:title 'Famous Tiktoker Leak Data' — leaked personal data/content group"},
    {"code": "GKeNQz9jXIC80FoHF410CM", "reason": "og:title 'Zambia investment' — out of slice (ZM, not South Asia) + investment-promo group"},
]

def main():
    fj = json.load(open(os.path.join(SCRATCH, "fetch_jobs.json")))
    prescreen = json.load(open(os.path.join(SCRATCH, "prescreen_dropped.json")))
    vsum = json.load(open(os.path.join(SCRATCH, "verify_summary.json")))

    # Leads: real (non-#anchor) fetch ERR pages + ~12KB bot-challenge pages
    leads = []
    for j in fj["jobs"]:
        u = j["url"]
        if "#" in u:
            continue  # anchor duplicates of the whtsgrouplink homepage, already mined
        if isinstance(j["status"], str) and j["status"].startswith("ERR"):
            leads.append({"url": u, "why": "Fetch failed (proxy/transport error, ProxyError RemoteDisconnected) — page never retrieved; needs retry / live-browser pass."})
        elif j.get("size") and 10000 < j["size"] < 13000:
            leads.append({"url": u, "why": "Returned ~12KB 'One moment, please...' bot-challenge page, 0 invite codes — needs live-browser pass."})
    # dedupe leads by url, keep order
    seen = set()
    ded = []
    for l in leads:
        if l["url"] not in seen:
            seen.add(l["url"])
            ded.append(l)
    leads = ded

    json.dump(CANDIDATES, open(os.path.join(WAVE, "team30-newdirs-southasia-candidates.json"), "w"), ensure_ascii=False, indent=1)
    json.dump([], open(os.path.join(WAVE, "team30-newdirs-southasia-pending.json"), "w"), indent=1)
    json.dump(leads, open(os.path.join(WAVE, "team30-newdirs-southasia-leads.json"), "w"), ensure_ascii=False, indent=1)

    summary = {
        "team": 30,
        "slice": "new dirs South Asia (team25 leads)",
        "sources": [
            "wave 20261111 team25 leads (13 URLs): imagesplatform add page; wagroupslink whatsapp-group-links + private; wagroupzone girls; wahublink boys/youtube/visa-travel/desi-girls; newgrouplinks college-girls/pakistani-girls/school-girls/all-groups; whtsgrouplink homepage + category sub-pages (discovered 74 links)",
            "wave 20261110 team25 leads: whatslinky.com 29 sub-pages/category archives; pkwhatsgrouplinks.com 7 sub-pages/category archives",
        ],
        "pages_fetched": len(fj["jobs"]),
        "raw_unique_codes": 783,
        "in_union": 683,
        "fresh": 100,
        "prescreen_dropped": len(prescreen),
        "verified_pool": 95,
        "verified": len(CANDIDATES),
        "dead": len(vsum["dead"]),
        "pending": 0,
        "leads": len(leads),
        "exclusions": [{"code": d["code"], "reason": d["reason"]} for d in prescreen] + OG_EXCLUSIONS,
        "resume": "Mine the leads in team30-newdirs-southasia-leads.json (48 transport-failed pages + 33 bot-challenge pages). The whtsgrouplink.com category sub-pages that DID return full HTML and were mined: educational, girls, international, lahore, option-trading, shayari, status + homepage; the rest need a live-browser pass. whatslinky.com girls/online-work/shayari pages mined; its bollywood/college-girls/friendship-girls/indian/kerala/music/pubg/tamil/youtube-subscribers pages are bot-challenged.",
        "notes": [
            "Controls: live control 00CHZw0BFnP6ZLQVROVo0Y returned og:title '+234..2016'; fabricated control ZZZZZZZZZZZZZZZZZZZZZZ returned HTTP 200 + EMPTY og:title but generic og:description 'WhatsApp Group Invite'. So og:description is NOT a liveness fallback (it is generic on dead invites) — LIVE = non-empty og:title only, per team25 precedent. The verify script was fixed accordingly before the pool ran.",
            "Verification: python requests Session, browser UA, 4 workers, 90s timeout; empty og:title retried once after 20s, transport errors retried once. All 95 pool codes resolved: 12 live, 83 dead, 0 pending.",
            "Fresh-code yield concentrated in pkwhatsgrouplinks.com (71 of 100 fresh: pakistani 42, entertainment 25, movies 4) and imagesplatform (10). whatslinky/whtsgrouplink/wahublink/newgrouplinks pools were almost entirely union (only 19 fresh combined).",
            "imagesplatform 'Recent Added' finding: its recent-added feed is polluted with a Brazilian Portuguese adult cluster using leetspeak evasion (4 for A): SO PIR4NHAS / NINF4TAS / NINFET4AS / SO SAF4DINHAS / NOVINHAS +18 / VAZ4DINHOS / SO PUT4RIA / SO NOVINHAS — all dropped on og:title. 'novinhas'/'ninfetas' = young-girl/nymphet sexual slang, 'vazadinhos' = leaked nudes, 'putaria' = porn. Its 'funny' labels are untrusted; future teams should screen imagesplatform titles before banking.",
            "Name rule: banked name = og:title (HTML-unescaped), the group's actual current name. For DWyo0QkhFZFBNWbpPRKg91 the directory name was 'KING OF ROMANCE' but og:title is the VIP-songs stylized name, which is banked verbatim.",
            "Categories/countries of the 2 kept: Entertainment/PK (VIP HD songs), Buy & Sell/PK (Pakistan Mall).",
            "Scratch/evidence in team30_scratch/ (fetched HTML, fetch_jobs.json, raw_all.json, fresh_all.json, prescreen_dropped.json, verify_results.jsonl, verify_summary.json, controls.json).",
        ],
    }
    json.dump(summary, open(os.path.join(WAVE, "team30-newdirs-southasia-summary.json"), "w"), ensure_ascii=False, indent=1)
    print("candidates:", len(CANDIDATES), "pending: 0", "leads:", len(leads), "exclusions:", len(summary["exclusions"]))

if __name__ == "__main__":
    main()
