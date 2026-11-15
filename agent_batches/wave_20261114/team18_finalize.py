import json
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
OLD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"

controls = json.load(open(f"{WD}/team18-controls.json"))
fetch_log = json.load(open(f"{WD}/team18_ltg_fetch_log.json"))
resolved = json.load(open(f"{WD}/team18_ltg_new_resolved_all.json"))
verify = json.load(open(f"{WD}/team18_verify_results.json"))
first_new = json.load(open(f"{WD}/team18_ltg_new_ids.json"))
extra_new = json.load(open(f"{WD}/team18_ltg_new_ids_extra.json"))
pages = json.load(open(f"{WD}/team18_ltg_listing_pages.json"))

print("first batch new:", len(first_new), "extra countries new:", len(extra_new),
      "resolved total:", len(resolved), "known ids now:", len(pages))

def code_of(r):
    return r["destination"].rstrip("/").split("/")[-1]

wa_chat = [r for r in resolved if r["destination"].startswith("https://chat.whatsapp.com/")]
telegram = [r for r in resolved if r["destination"].startswith("https://t.me/")]
channel = [r for r in resolved if "whatsapp.com/channel" in r["destination"]]
wame = [r for r in resolved if r["destination"].startswith("https://wa.me")]
print("wa-chat:", len(wa_chat), "telegram:", len(telegram),
      "channel:", len(channel), "wa.me:", len(wame))

# dead / dupe detail for wa-chat (verify results cover all 9)
excluded = []
for r in wa_chat:
    c = code_of(r)
    v = verify.get(c, {})
    st = v.get("status", "?")
    if c == "CccUUZdjC6xA4NIk7ppoem":
        excluded.append({"code": c, "ltg_id": r["id"], "name": r["name"],
                         "reason": "LIVE (og:title 'THE TRADING ZONE') but DUPE - code already in 119,266-code union; not banked"})
    else:
        excluded.append({"code": c, "ltg_id": r["id"], "name": r["name"],
                         "reason": f"DEAD - empty og:title on 3 spaced verification passes (HTTP 200 each time)"})
for r in channel + wame:
    excluded.append({"code": "", "ltg_id": r["id"], "name": r["name"],
                     "reason": f"not a WhatsApp group invite - destination is {r['destination']} (banked as lead)"})

leads = []
for r in channel + wame + [x for x in resolved if x["id"] == "4024"]:
    leads.append({"ltg_id": r["id"], "name": r["name"], "pages": r["pages"],
                  "destination": r["destination"],
                  "reason": ("WhatsApp Channel, not a chat-group invite" if "channel" in r["destination"]
                             else "wa.me message link, not a group invite" if r["destination"].startswith("https://wa.me")
                             else "resolves to a Telegram bot (t.me), not WhatsApp")})

candidates = []
pending = []

json.dump(candidates, open(f"{WD}/team18-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WD}/team18-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WD}/team18-pending.json", "w"), ensure_ascii=False, indent=1)

summary = {
    "team": "team18",
    "slice": "linktogroups (ltg) continuation - wave_20261114",
    "sources": [
        "https://linktogroups.com/en/whatsapp-groups (+?page=2..5)",
        "https://linktogroups.com/en/ghana",
        "https://linktogroups.com/en/kenya",
        "https://linktogroups.com/en/nigeria (+?page=2..6)",
        "https://linktogroups.com/en/saudi-arabia",
        "https://linktogroups.com/en (home - retry ok, relative hrefs, no new country links beyond known set)",
        "EXTRA country pages first fetched by this slice (Nov13 never fetched them): pakistan, india, australia, canada, ethiopia, malaysia, philippines, russia, singapore, iran"
    ],
    "controls": {
        "live": "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (PASS)",
        "fabricated": "ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title (PASS, dead)",
        "method": "one requests.Session, browser User-Agent, 60-90s timeouts; og:description ignored (generic on live and dead)"
    },
    "counts": {
        "raw_new_listing_ids_vs_nov13": len(resolved),
        "raw_first_batch_original_pages": len(first_new),
        "raw_extra_country_pages": len(extra_new),
        "resolved_via_click_api": len([r for r in resolved if r["status"] == 200]),
        "unresolved_ids": 0,
        "whatsapp_chat_destinations": len(wa_chat),
        "verified_live": 1,
        "verified_dead_3_passes": 8,
        "dupes_vs_union": 1,
        "candidates_banked": 0,
        "dead": 8,
        "excluded": len(excluded) + len(telegram),
        "pending_429_transport": 0,
        "leads": len(leads)
    },
    "verified": {"live": 1, "dead": 8, "http429": 0, "transport": 0},
    "dupes": [
        {"code": "CccUUZdjC6xA4NIk7ppoem", "ltg_id": "4023",
         "name": "MR Rajib FX | GOLD Signals (live og:title 'THE TRADING ZONE')",
         "reason": "live but already in 119,266-code union; NOT banked; not in any wave_20261113/14 candidate file"}
    ],
    "dead": [
        {"code": code_of(r), "ltg_id": r["id"], "name": r["name"]}
        for r in wa_chat if verify.get(code_of(r), {}).get("status") == "dead"
    ],
    "excluded": excluded + [
        {"code": "", "ltg_id": r["id"], "name": r["name"],
         "reason": f"Telegram destination, not WhatsApp: {r['destination']}"}
        for r in telegram
    ],
    "pending": [],
    "leads": leads,
    "notes": [
        "Nov13 carryover checked: all 6 Nov13 new IDs were already resolved by team20 (119-122 = Telegram, 4003 = WhatsApp Channel, 4020 DVoice Media -> LvkywXnuMqP16t35FhH4gZ). 4020 was already banked as a candidate by team19 in wave_20261113 (Dvoice Media General Chat, Business, NG) - NOT re-banked here.",
        "Every one of the 14 original listing pages returned HTTP 200 (several needed a retry after a proxy RemoteDisconnected on first attempt; same flakiness as Nov13). Home page failed on first attempt, succeeded on retry (411KB saved as team18_ltg_home.html); its country links are relative hrefs, which is why the absolute-URL regex found none.",
        "Extra country pages were fetched because the Nov13 slice had never covered them; their 121 'new' IDs are old listings (IDs 131-1897) unseen by this slice, NOT fresh Nov14 listings. 120 of the 131 resolved destinations are Telegram - linktogroups is overwhelmingly a Telegram directory for those country pages.",
        "The 8 dead WhatsApp codes (4027-4034, all crypto/trading names on whatsapp-groups-p4) returned HTTP 200 with empty og:title on all 3 spaced passes - dead, not pending. No 429s, no transport failures anywhere in this run.",
        "Content screening: only 1 code went live and it was a dupe, so no content decision was needed on a bankable item. FLAG for coordinator: the live dupe (4023, 'THE TRADING ZONE' / MR Rajib FX gold/forex 'Free Trading Signals') is a forex-signals group; if it ever reappears under a fresh code, treat free-signals/forex-signal groups as borderline under the free-money-signal exclusion.",
        "No porn/scam/casino screening hits among bankable items (nothing bankable). Girls/friendship restoration rules not triggered.",
        "Known listing IDs now total %d (was 176 after Nov13)." % len(pages),
        "Unfetched linktogroups surface for future waves: category pages /en/crypto, /en/betting, /en/jobs, /en/dating, /en/education, /en/ai, /en/programming, /en/news-politics, /en/religion, /en/sports, /en/gaming, /en/comedy, /en/movies-tv, /en/music, /en/health, /en/business, /en/deals, /en/fashion-beauty, /en/telegram-groups, /en/telegram-channels, /en/telegram-bots, and /en/countries index."
    ],
    "resume": "Next run: compare against team18_ltg_listing_pages.json (now %d IDs) in wave_20261114; re-fetch the same 24 listing pages + home; resolve new IDs via POST /api/v1/listings/{id}/click; verify WhatsApp chat codes only. Unfetched category pages listed in notes are the next expansion surface. No pending codes to retry (0 pending, 0 unresolved)." % len(pages),
    "files": {
        "fetch_script": "team18_ltg_fetch.py",
        "fetch_extra_script": "team18_ltg_fetch_extra.py",
        "resolve_scripts": ["team18_ltg_resolve.py", "team18_ltg_resolve_extra.py"],
        "verify_script": "team18_ltg_verify.py",
        "html": "team18_ltg_<tag>.html (24 pages + home)",
        "fetch_log": "team18_ltg_fetch_log.json",
        "listing_pages": "team18_ltg_listing_pages.json",
        "listing_names": "team18_ltg_listing_names.json",
        "new_ids": ["team18_ltg_new_ids.json", "team18_ltg_new_ids_extra.json"],
        "resolved": "team18_ltg_new_resolved_all.json (131 records)",
        "verify_results": "team18_verify_results.json",
        "verify_ckpt": "team18_verify_ckpt.jsonl",
        "controls": "team18-controls.json"
    }
}
json.dump(summary, open(f"{WD}/team18-summary.json", "w"), ensure_ascii=False, indent=1)
print("counts:", json.dumps(summary["counts"], indent=1))
print("DONE FINALIZE")
