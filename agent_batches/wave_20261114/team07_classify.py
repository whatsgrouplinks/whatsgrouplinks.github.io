#!/usr/bin/env python3
"""team07 classify: build candidates/leads/pending/summary from banked verification."""
import json, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
PROG = os.path.join(WAVE, "team07-progress.json")
p = json.load(open(PROG))
results = sorted(p["results"], key=lambda r: r["idx"])
controls = p["controls"]

CANON = {"Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell",
         "Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto",
         "Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"}

# Content screen on LIVE og:title only.
def screen(title):
    t = title.lower()
    # hard porn / xxx voyeur — Roman + Devanagari keywords (og:title may be in Devanagari script)
    porn_markers = ["xxx", "porn", "sex video", "xvideo", "pornhub",
                    "susu", "nahati", "nangi", "susu ", " पोर्न", "सेक्स",
                    "सुसु", "नहाती", "नहाते", "नंगी", "नंगा", "पोर्न", "सेक्स", "xxx"]
    if any(k in t for k in porn_markers):
        return "porn/xxx voyeur content in live og:title"
    # casino / slots / betting signals
    if "mines" in t or "tigrinho" in t or "fortune tiger" in t or "roleta" in t or "cassino" in t or "casino" in t:
        return "casino/slots/betting content in live og:title"
    if "palpite" in t or "sinais" in t or "resultado e palpite" in t or "apostado" in t or "aposta" in t:
        return "betting-signal content in live og:title"
    if "airdrop" in t or "binary option" in t or "opções binárias" in t or "free money" in t:
        return "crypto-airdrop/binary-option/free-money scam in live og:title"
    return None

live = [r for r in results if r["status"] == "live"]
dead = [r for r in results if r["status"] == "empty"]
still_pending = [r for r in results if r["status"] in ("ratelimit", "transport")]

candidates, excluded = [], []
for r in live:
    reason = screen(r["og_title"])
    if reason:
        excluded.append({"code": r["code"], "og_title": r["og_title"],
                         "pending_name": r["pending_name"], "reason": reason})
        continue
    # clean live item -> schema (not reached this run, kept for completeness)
    name = r["og_title"] if r["og_title"] else r["pending_name"]
    cat = r["pending_category"] if r["pending_category"] in CANON else "Community & Social"
    country = r["pending_country"] or ""
    candidates.append({"name": name, "category": cat, "country": country,
                       "description": f"Join {name}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and stay in touch.",
                       "invite": r["invite"]})

json.dump(candidates, open(os.path.join(WAVE, "team07-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(candidates, open(os.path.join(WAVE, "team07-leads.json"), "w"), indent=1, ensure_ascii=False)
json.dump([{"code": r["code"], "invite": r["invite"], "reason": r["note"],
            "prev_reason": r["prev_reason"]} for r in still_pending],
          open(os.path.join(WAVE, "team07-pending.json"), "w"), indent=1, ensure_ascii=False)

summary = {
    "team": "team07",
    "wave": "wave_20261114",
    "slice": "pending 0-141 (first half of wave_20261112_pending_all.json, 285 codes; team08 owns 142-284)",
    "sources": ["wave_20261112_pending_all.json (items 0-141)",
                ".existing_codes.json (119,266 codes, union dedupe)",
                "live og:title from https://chat.whatsapp.com/<CODE> (requests.Session, browser UA, 60s timeout, max 2 parallel, batches of 12, 6s pause between batches)"],
    "controls": controls,
    "counts": {"raw": 142, "verified": 142, "live": len(live), "dead": len(dead),
               "dupes_union": len(p["dupes_union"]), "dupes_within_team": len(p["dupes_within"]),
               "excluded": len(excluded), "pending": len(still_pending),
               "candidates": len(candidates), "leads": len(candidates)},
    "excluded": excluded,
    "dead_codes": [r["code"] for r in dead],
    "dead_note": "Each dead code returned HTTP 200 with EMPTY og:title on 3 spaced attempts (delays 8s then 30s). Per task rule, empty og:title after retries = dead, not pending.",
    "pending": [],
    "notes": [
        "No clean candidates this run: all 3 live groups failed the content screen on their LIVE og:title (not on directory names).",
        "Names: no output items, so no names were published. Pending-file names were never used as output names; live og:title was the name authority for the 3 live items.",
        "Girls/friendship groups in the slice were NOT excluded on directory name alone; they were decided by live og:title. All such codes in this slice returned empty og:title (dead), so none reached the content screen.",
        "First verifier run was SIGTERM-killed by the runtime at 120/142 (banked progress survived); resume script team07_resume.py completed idx 120-141 and the run finished EXIT=0 with 142/142 verified.",
        "No 429 or transport failures in the final pass: 0 still-pending. No union dupes and no within-team dupes in this slice.",
        "team07-progress.json holds the per-code verification record (idx, code, status, og_title, http, attempts, pending name/category/country)."
    ],
    "resume_point": "COMPLETE - all 142 slice items verified; nothing left to resume. Next wave should start from a fresh pending file, not this slice."
}
json.dump(summary, open(os.path.join(WAVE, "team07-summary.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(summary["counts"], indent=1))
print("excluded:", json.dumps(excluded, ensure_ascii=False, indent=1))
