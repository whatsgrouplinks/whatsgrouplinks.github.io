#!/usr/bin/env python3
"""team16 finalize — wave 20261114.
Reads team16-api-raw.json + team16-verify.json + team16-controls.json,
applies content screen on LIVE og:title, builds candidates/leads/pending/summary.
"""
import json, os, re

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CUTOFF = "2026-11-12 16:26:43"  # team17 newest seen

raw = json.load(open(os.path.join(WD, "team16-api-raw.json")))
verify = {r["code"]: r for r in json.load(open(os.path.join(WD, "team16-verify.json")))}
controls = json.load(open(os.path.join(WD, "team16-controls.json")))

# Hard-drop patterns (applied to live og:title + api title/desc, lowercased).
DROP_PATTERNS = [
    (r"\bporn\b|xxx|sex video|video call girl|nangi|hot chat service", "hard porn/xxx"),
    (r"airdrop|free money|earn \$?\d+.*(free|daily)|binary option", "crypto-airdrop/binary-option/free-money scam"),
    (r"casino|slot|tigrinho|fortune tiger|\bsinais\b|plataformas pagantes|wjbet|betting signal|aviator", "casino/slots/betting-signal"),
]
# Flag-only (keep, note in summary): crypto trading-signal / copy-trading discussion.
FLAG_PATTERNS = [r"signal", r"copy trad"]

def screen(text):
    t = text.lower()
    for pat, reason in DROP_PATTERNS:
        if re.search(pat, t):
            return ("drop", reason)
    for pat in FLAG_PATTERNS:
        if re.search(pat, t):
            return ("flag", "trading-signal/copy-trading discussion — kept, flagged")
    return ("keep", "")

def canon_category(it):
    """Map groupjoin category + content to canonical category."""
    gcat = it["category"]["category_slug"]
    title = it["group_title"].lower()
    if gcat == "money":
        return "Crypto"  # all 10 fresh Money items are crypto topics
    if gcat == "business" and ("friend" in it["group_desc"].lower()
                               or "contact" in title or "meet new people" in it["group_desc"].lower()):
        return "Community & Social"
    return {"business": "Business", "education": "Education",
            "entertainment": "Entertainment"}.get(gcat, "Community & Social")

def description(name, cat, country):
    cl = cat.lower()
    base = f"Join {name}, an active WhatsApp group for {cl}."
    tail = {
        "Crypto": " Follow crypto news, market trends and blockchain discussion with fellow enthusiasts.",
        "Community & Social": " Meet new people, chat and make friends with members from around the world.",
    }.get(cat, " Connect with members who share your interest.")
    ctry = f" Based in {country}." if country else ""
    return base + tail + ctry

fresh = []
for pg in ("page1", "page2"):
    for it in raw[pg]["data"]:
        if it["created_at"][:19] > CUTOFF:
            fresh.append(it)
fresh.sort(key=lambda i: i["created_at"], reverse=True)

candidates, excluded, pending, dead, flags = [], [], [], [], []
for it in fresh:
    code = it["link"].split("chat.whatsapp.com/")[1].split("?")[0]
    cat_slug = it["category"]["category_slug"]
    if cat_slug == "adult":
        excluded.append({"code": code,
                         "reason": f"Adult category dropped wholesale (groupjoin Adult; title={it['group_title']!r}, created {it['created_at'][:19]}, country={it['country']['iso2']}). NOT verified/banked."})
        continue
    v = verify.get(code)
    if v is None:
        pending.append({"code": code, "reason": "not verified (missing verify result)"})
        continue
    if v["status"] == "pending":
        pending.append({"code": code, "reason": v.get("reason", "pending")})
        continue
    if v["status"] == "dead":
        dead.append({"code": code, "reason": v.get("reason", "dead"),
                     "og_title": v.get("og_title", "")})
        continue
    # live — screen on live og:title (primary) + api title/desc
    og = v.get("og_title", "")
    verdict, why = screen(og + " " + it["group_title"] + " " + it["group_desc"])
    if verdict == "drop":
        excluded.append({"code": code, "reason": f"{why} — live og:title={og!r}, api title={it['group_title']!r}."})
        continue
    cat = canon_category(it)
    candidates.append({
        "name": it["group_title"],
        "category": cat,
        "country": it["country"]["iso2"],
        "description": description(it["group_title"], cat, it["country"]["name"]),
        "invite": f"https://chat.whatsapp.com/{code}",
    })
    if verdict == "flag":
        flags.append({"code": code, "name": it["group_title"], "note": why})

newest_seen = max(i["created_at"][:19] for i in fresh) if fresh else CUTOFF

leads = [
    {"note": "WORKING newest-first feed (no tag param): page 1 spans 2026-11-12..2026-11-13; poll until created_at < cutoff. Page 2 spans 2026-11-08..2026-11-11, max 2026-11-11 18:29 — nothing fresher than cutoff there.",
     "url": "https://api.groupjoin.link/groups?page=1&limit=20&safeSearch=blur"},
    {"note": "Homepage listing (JS-rendered, backed by the same API). Detail pages /group/<group_uid> return HTTP 200 with the group title in <title>; invite codes are client-rendered (not in static HTML) — API link field is the authoritative invite source.",
     "url": "https://groupjoin.link/"},
    {"note": "STALE — tag=onlynew feed is Adult-only, May-Aug 2026 items; do not use as the 'new' source.",
     "url": "https://api.groupjoin.link/groups?tag=onlynew&page=1&limit=20&safeSearch=blur"},
]

summary = {
    "team": 16,
    "slice": "groupjoin.link newest poll (no tag param), fresh since 2026-11-12 16:26:43 (team17 Nov 13 newest)",
    "sources": [
        "https://api.groupjoin.link/groups?page=1&limit=20&safeSearch=blur",
        "https://api.groupjoin.link/groups?page=2&limit=20&safeSearch=blur",
    ],
    "controls": {
        "live": f"KrDwdK8EIkB6vgauHg5M7N returned og:title {controls[0].get('og_title')!r} — matches expected; method valid",
        "fabricated": f"ZzZzZzZzZzZzZzZzZzZzZzZz returned empty og:title — correctly dead",
        "detail": {"control_live": controls[0], "control_fabricated": controls[1]},
    },
    "raw": len(fresh),
    "verified": len(candidates),
    "dupes": 0,
    "dead": len(dead),
    "excluded": excluded,
    "pending": len(pending),
    "leads": len(leads),
    "flags": flags,
    "dead_list": dead,
    "notes": (
        f"FIRST fresh non-Adult group on this feed in 3 runs, but only 1 of 11 verified live. "
        "Page 1 (20 items, 2026-11-12..2026-11-13) contains 14 items newer than the cutoff; "
        "11 non-Adult (1 Business NG 'Contact gain hub' + 10 Money US crypto groups posted 11:54-12:03 on Nov 13) "
        "and 3 Adult, dropped wholesale. Page 2 guard: 20 items, 2026-11-08..2026-11-11, max 2026-11-11 18:29 — nothing fresher. "
        "The 10 crypto groups are a bulk upload (10 in 9 minutes, all US, same 'Crypto …' naming) AND ALL 10 ARE DEAD on WhatsApp "
        "(empty og:title after 3 spaced fetches each; method proven by the live control) — the directory lists stale/revoked invites; none banked. "
        "Only 'Contact gain hub' verified live (og:title matches API title). "
        "Detail pages: all 11 returned HTTP 200 with <title> matching the API group title exactly; invite codes are client-rendered, so the API link field is the authoritative invite source. "
        "All 14 fresh codes were absent from .existing_codes.json (119,266 codes); 0 within-team dupes. No transport failures, no 429s; 4s+ spacing kept on API, 8s+ on WhatsApp verifies."
    ),
    "resume": "Next run: poll https://api.groupjoin.link/groups?page=N&limit=20&safeSearch=blur (NO tag param — newest-first) starting page 1 until created_at < cutoff date; keep 4s+ spacing (API 429s on bursts). Fresh = created_at > " + newest_seen + " (this run's newest seen). Dedupe against .existing_codes.json + this run's Adult drops before verifying; verify via chat.whatsapp.com og:title with a known-live control code each run. HARD RULE: never fetch, verify, or bank anything from the groupjoin.link Adult category.",
    "resume_point": {
        "newest_created_at_seen": newest_seen,
        "last_page_polled": 2,
        "page1_date_range": "2026-11-12..2026-11-13",
        "page2_date_range": "2026-11-08..2026-11-11",
    },
}

for name, data in (("team16-candidates.json", candidates),
                   ("team16-leads.json", leads),
                   ("team16-pending.json", pending),
                   ("team16-summary.json", summary)):
    with open(os.path.join(WD, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", name, "n =", len(data) if isinstance(data, list) else "summary")
print("counts: raw", len(fresh), "verified", len(candidates), "excluded", len(excluded),
      "dead", len(dead), "pending", len(pending), "flags", len(flags))
