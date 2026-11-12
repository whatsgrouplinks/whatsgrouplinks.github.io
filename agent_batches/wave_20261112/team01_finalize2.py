#!/usr/bin/env python3
"""TEAM 01 wave 20261112 — finalize2: fold stream-verifier results from BOTH
passes (merged candidates + deep candidates) into the final wave outputs.
Reads (wave_20261112): team01-leads-slice1.json/.pending/.leads/.summary (base),
team01-stream-verified.json / -pending.json / -stats.json / -dead.json,
team01-merged-candidates.json, team01-deep-candidates.json,
team01-deep-progress.json.
Writes: team01-leads-slice1.json (verified), team01-leads-slice1-pending.json,
team01-leads-slice1-leads.json (base leads + deep failed/nocode listing URLs),
team01-leads-slice1-summary.json, team01-merged-candidates.json (leftovers:
still-unverified candidates from both pools).
Safe to re-run (idempotent folds).
"""
import json, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def main():
    verified = load_json(os.path.join(WAVE, "team01-leads-slice1.json"), [])
    pending = load_json(os.path.join(WAVE, "team01-leads-slice1-pending.json"), [])
    leads = load_json(os.path.join(WAVE, "team01-leads-slice1-leads.json"), [])
    summary_old = load_json(os.path.join(WAVE, "team01-leads-slice1-summary.json"), {})
    stream_ver = load_json(os.path.join(WAVE, "team01-stream-verified.json"), [])
    stream_pend = load_json(os.path.join(WAVE, "team01-stream-pending.json"), [])
    stream_stats = load_json(os.path.join(WAVE, "team01-stream-stats.json"), {})
    dead_codes = set(load_json(os.path.join(WAVE, "team01-stream-dead.json"), []))

    _seen = {v["invite"] for v in verified}
    n_new = 0
    for v in stream_ver:
        if v["invite"] not in _seen:
            verified.append(v); _seen.add(v["invite"]); n_new += 1
    _seenp = {p["invite"] for p in pending}
    for p in stream_pend:
        if p["invite"] not in _seenp and p["invite"] not in _seen:
            pending.append(p); _seenp.add(p["invite"])
    _ver_inv = {v["invite"] for v in verified}
    pending = [p for p in pending if p["invite"] not in _ver_inv]
    save_json(os.path.join(WAVE, "team01-leads-slice1.json"), verified)
    save_json(os.path.join(WAVE, "team01-leads-slice1-pending.json"), pending)
    verified_codes = {v["invite"].split("/")[-1] for v in verified}

    # exclusions: union of old summary + stream stats + deep progress
    excl = {}
    for e in summary_old.get("exclusions", []):
        excl[e["code"]] = e
    for e in stream_stats.get("exclusions", []):
        excl[e["code"]] = e
    deep_prog = load_json(os.path.join(WAVE, "team01-deep-progress.json"), {})
    for e in deep_prog.get("exclusions", []):
        excl[e["code"]] = e
    excl_codes = set(excl)

    # leftovers: merged + deep candidates minus verified/dead/excluded
    leftovers = {}
    for path in ["team01-merged-candidates.json", "team01-deep-candidates.json"]:
        for code, rec in load_json(os.path.join(WAVE, path), {}).items():
            if code in verified_codes or code in dead_codes or code in excl_codes:
                continue
            leftovers.setdefault(code, rec)
    save_json(os.path.join(WAVE, "team01-merged-candidates.json"), leftovers)

    # leads: base leads + deep failed/nocode listing URLs (unresolvable as codes)
    deep_leads = set()
    for f in deep_prog.get("failed", []):
        if f["kind"] == "gi":
            deep_leads.add(f"https://groupsinvite.link/group/rules/{f['item']}/")
        else:
            deep_leads.add(f"https://linkado.app/grupo/{f['item']}")
    for n in deep_prog.get("nocode", []):
        if n["kind"] == "gi":
            deep_leads.add(f"https://groupsinvite.link/group/rules/{n['item']}/")
        else:
            deep_leads.add(f"https://linkado.app/grupo/{n['item']}")
    leads_out = sorted(set(leads) | deep_leads)
    save_json(os.path.join(WAVE, "team01-leads-slice1-leads.json"), leads_out)

    dead_total = stream_stats.get("dead", len(dead_codes))
    resume_parts = []
    if leftovers:
        resume_parts.append(f"verify {len(leftovers)} leftover candidates in team01-merged-candidates.json (merged+deep pools, team01_verify_stream.py)")
    if deep_prog.get("failed"):
        resume_parts.append(f"retry {len(deep_prog['failed'])} failed deep fetches (team01_deep.py — failed items not marked done)")
    summary = dict(summary_old)
    summary.update({
        "team": "team01",
        "slice": "leads slice 1",
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads_out),
        "dead": dead_total,
        "exclusions": list(excl.values()),
        "resume": "; ".join(resume_parts) if resume_parts else "slice complete",
        "notes": (summary_old.get("notes", "") +
            f" FINALIZE2: folded {n_new} new stream-verified (merged+deep passes) for {len(verified)} total verified. "
            f"Deep-fetch resolved 1738 candidates (163 groupsinvite + 1575 linkado); "
            f"{len(deep_prog.get('failed', []))} deep fetches failed transport (in leads for retry); "
            f"{len(deep_prog.get('nocode', []))} deep slugs/ids had no invite code (in leads). "
            f"Leftover unverified candidates: {len(leftovers)}. "
            f"Deep exclusions: {len(deep_prog.get('exclusions', []))}."),
    })
    save_json(os.path.join(WAVE, "team01-leads-slice1-summary.json"), summary)
    print(f"FINALIZE2: verified={len(verified)} (+{n_new}) pending={len(pending)} leads={len(leads_out)} "
          f"dead={dead_total} excl={len(excl)} leftovers={len(leftovers)}")
    print("resume:", summary["resume"])

if __name__ == "__main__":
    main()
