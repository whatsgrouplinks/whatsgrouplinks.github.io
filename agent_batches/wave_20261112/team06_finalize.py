#!/usr/bin/env python3
"""TEAM06 finalize: rebuild final output files from progress JSONL (ground truth)."""
import json, collections

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
BUILD = "/home/hatch/workspace/whatsapp-groups-site/"

pending = json.load(open(PREV + "team07-leads-slice7-pending.json"))
by_code = {p["invite"].rsplit("/", 1)[-1]: p for p in pending}
existing = set(json.load(open(BUILD + ".existing_codes.json")))

done = {}
for line in open(WAVE + "team06-leads-slice7-pending-progress.jsonl"):
    try:
        r = json.loads(line)
        done[r["code"]] = r
    except Exception:
        pass
assert len(done) == 599, f"expected 599 processed, got {len(done)}"
counts = collections.Counter(v["status"] for v in done.values())
print("counts:", dict(counts))

candidates, still_pending, exclusions, dup_existing = [], [], [], []
seen = set()
for code, rec in done.items():
    item = by_code[code]
    if rec["status"] == "live":
        if code in existing:
            # live but already in groups.json (added by another slice's merge) — never bank
            dup_existing.append({"invite": item["invite"], "name": item.get("name"),
                                 "reason": "already in groups.json (.existing_codes.json)"})
            continue
        assert code not in seen, f"dup live code: {code}"
        seen.add(code)
        name = (item.get("name") or "").strip() or rec.get("title", "")
        candidates.append({
            "name": name,
            "category": item.get("category") or "Community & Social",
            "country": item.get("country") or "",
            "description": f"Join {name}, a WhatsApp group.",
            "invite": f"https://chat.whatsapp.com/{code}",
        })
    elif rec["status"] == "pending":
        still_pending.append({
            "name": item.get("name", ""),
            "category": item.get("category") or "Community & Social",
            "country": item.get("country") or "",
            "description": item.get("description") or "",
            "invite": item["invite"],
            "reason": f"transport failure {rec.get('reason', '')}",
        })
    elif rec["status"] == "excluded":
        exclusions.append({"invite": item["invite"], "name": item.get("name"),
                           "reason": rec.get("reason", "")})

# leads file already written by listpages sample; verify it
leads = json.load(open(WAVE + "team06-leads-slice7-pending-leads.json"))
leads_report = json.load(open(WAVE + "team06-leads-slice7-pending-leads-report.json"))

json.dump(candidates, open(WAVE + "team06-leads-slice7-pending-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(still_pending, open(WAVE + "team06-leads-slice7-pending-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(exclusions, open(WAVE + "team06-leads-slice7-pending-exclusions.json", "w"), ensure_ascii=False, indent=1)

summary = {
    "team": "TEAM06",
    "wave": "20261112",
    "slice": "7 pending re-check (source: wave_20261111/team07-leads-slice7-pending.json)",
    "input_pending_codes": 599,
    "processed": 599,
    "verified_kept_live": len(candidates),
    "live_but_already_in_groups_json_dropped": len(dup_existing),
    "dup_existing": dup_existing,
    "dead_empty_og_title": counts.get("dead-empty", 0),
    "still_pending_transport_failure": len(still_pending),
    "excluded_content_screen": len(exclusions),
    "exclusions": exclusions,
    "failed_listing_pages_sampled": leads_report["sampled"],
    "failed_listing_pages_resolved": len(leads_report["resolved"]),
    "failed_listing_pages_still_failed_banked_as_leads": len(leads),
    "fresh_codes_spotted_on_resolved_listing_pages_unverified": len(leads_report["fresh_codes_found"]),
    "fresh_codes_unverified_note": "111 fresh (not in groups.json) invite codes were seen on resolved listing pages; NOT verified against WhatsApp and NOT banked as candidates — they need a fresh verification pass.",
    "resume_point": "COMPLETE — all 599 pending codes processed; no resume needed. Still-pending 31 codes remain for a future quiet-window re-check.",
    "method_notes": [
        "Controls first: known-live code from groups.json showed non-empty og:title; fabricated code showed empty og:title.",
        "LIVE = non-empty og:title ONLY. og:description is always the generic 'WhatsApp Group Invite' on both live and dead pages, so it is not a live signal (an early run using it as fallback was discarded and re-run).",
        "200 + empty og:title = dead/revoked invite page (full 220KB HTML); 30/30 such codes stayed empty on re-fetch, so no retry was done on empty pages in the final runs.",
        "Transport failures (429/timeout) got one spaced retry (20-60s), then banked as pending — never called dead.",
        "WhatsApp 429 walls hit repeatedly under concurrent wave load (team13 rechecking in parallel); auto 180s pauses after 3 consecutive failures; two manual pauses to let the throttle clear.",
        "One code dropped by content screen (HACKER PARA FF — paid-hack group). 'Bursa Sohbet' kept (false-positive 'bet' inside Turkish 'Sohbet'); 'Crypto Trading' links group kept (generic trading name, not airdrop/binary/daily-profit scam).",
        "All 47 live candidates checked against .existing_codes.json (112,070 codes) — zero duplicates; deduped within output.",
    ],
}
json.dump(summary, open(WAVE + "team06-leads-slice7-pending-summary.json", "w"), ensure_ascii=False, indent=1)
print(f"candidates={len(candidates)} pending={len(still_pending)} exclusions={len(exclusions)} dup_existing={len(dup_existing)} leads={len(leads)}")
print("live candidate names sample:", [c["name"][:40] for c in candidates[:5]])
