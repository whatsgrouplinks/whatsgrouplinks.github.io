#!/usr/bin/env python3
"""TEAM 01 wave 20261112 — finalize: fold wave_20261111 stream-verifier results
into the wave_20261112 outputs and rebuild the merged unverified pool.
Reads: wave_20261111 candidate pools + progress, yesterday's verified/pending,
stream-verifier outputs, leads_slice1.json, .existing_codes.json.
Writes (wave_20261112): team01-leads-slice1.json (verified),
team01-leads-slice1-pending.json, team01-leads-slice1-leads.json,
team01-leads-slice1-summary.json, team01-merged-candidates.json (resume artifact).
Does NOT verify (verification is a separate pass). Safe to re-run.
"""
import json, os, urllib.parse

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
LEADS_FILE = os.path.join(SRC, "leads_slice1.json")
EXISTING_FILE = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
OUT_VER = os.path.join(WAVE, "team01-leads-slice1.json")
OUT_PEND = os.path.join(WAVE, "team01-leads-slice1-pending.json")
OUT_LEADS = os.path.join(WAVE, "team01-leads-slice1-leads.json")
OUT_SUM = os.path.join(WAVE, "team01-leads-slice1-summary.json")
MERGED = os.path.join(WAVE, "team01-merged-candidates.json")

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
    leads = load_json(LEADS_FILE, [])
    existing = set(load_json(EXISTING_FILE, []))
    # base verified/pending = yesterday's finalized outputs (wave_20261111)
    verified = load_json(os.path.join(SRC, "team01-leads-slice1.json"), [])
    pending = load_json(os.path.join(SRC, "team01-leads-slice1-pending.json"), [])
    # merge stream-verifier outputs (separate files, no race with the requests verifier)
    stream_ver = load_json(os.path.join(SRC, "team01-stream-verified.json"), [])
    stream_pend = load_json(os.path.join(SRC, "team01-stream-pending.json"), [])
    stream_stats = load_json(os.path.join(SRC, "team01-stream-stats.json"), {})
    _seen = {v["invite"] for v in verified}
    for v in stream_ver:
        if v["invite"] not in _seen:
            verified.append(v); _seen.add(v["invite"])
    _seenp = {p["invite"] for p in pending}
    for p in stream_pend:
        if p["invite"] not in _seenp and p["invite"] not in {v["invite"] for v in verified}:
            pending.append(p); _seenp.add(p["invite"])
    # a code verified by the stream pass must not stay in pending
    _ver_inv = {v["invite"] for v in verified}
    pending = [p for p in pending if p["invite"] not in _ver_inv]
    # persist the merged verified/pending as the final output files
    save_json(OUT_VER, verified)
    save_json(OUT_PEND, pending)
    verified_codes = {v["invite"].split("/")[-1] for v in verified}
    pending_codes = {p["invite"].split("/")[-1] for p in pending}

    # merge candidate pools (from wave_20261111)
    merged = {}
    for path in ["team01-leads-slice1-candidates.json", "team01-rescue-candidates.json",
                 "team01-remine-candidates.json", "team01-remine0-candidates.json"]:
        for code, rec in load_json(os.path.join(SRC, path), {}).items():
            if code not in existing and code not in verified_codes:
                merged.setdefault(code, rec)
    # the 263 pre-reboot candidates survive in OUT_VER/OUT_PEND records
    for p in pending:
        code = p["invite"].split("/")[-1]
        if code not in merged and code not in verified_codes:
            merged[code] = {"name": p["name"], "category": p["category"], "country": p["country"],
                            "description": p["description"], "invite": p["invite"], "source": ""}
    for v in verified:
        code = v["invite"].split("/")[-1]
        merged.pop(code, None)
    # excluded codes (porn/scam found on verify passes) must never re-enter merged
    _excl_codes = {e["code"] for e in load_json(os.path.join(SRC, "team01-leads-slice1-summary.json"), {}).get("exclusions", [])}
    _excl_codes |= {e["code"] for e in stream_stats.get("exclusions", [])}
    for c in list(merged):
        if c in _excl_codes:
            merged.pop(c)
    # pending codes stay in merged (they are unverified) — keep them marked via pending file
    save_json(MERGED, merged)

    # progress aggregation (from wave_20261111)
    prog_main = load_json(os.path.join(SRC, "team01-leads-slice1-progress.json"), {})
    prog_rescue = load_json(os.path.join(SRC, "team01-rescue-progress.json"), {})
    prog_remine = load_json(os.path.join(SRC, "team01-remine-progress.json"), {})
    prog_remine0 = load_json(os.path.join(SRC, "team01-remine0-progress.json"), {})
    mined = set(prog_main.get("mined_idx", [])) | set(prog_rescue.get("mined_idx", [])) | set(prog_remine.get("mined_idx", [])) | set(prog_remine0.get("mined_idx", []))
    failed = []
    for pg in (prog_main, prog_rescue, prog_remine, prog_remine0):
        failed.extend(pg.get("failed", []))
    failed_urls = sorted({f["url"] for f in failed})
    gi_slugs = sorted(set(prog_main.get("sub_groupsinvite", [])) | set(prog_rescue.get("sub_groupsinvite", [])))
    gi_done = set(prog_main.get("deep_gi_done", [])) | set(prog_rescue.get("deep_gi_done", []))
    linkado_ids = sorted(set(prog_main.get("sub_linkado", [])) | set(prog_rescue.get("sub_linkado", [])))
    linkado_done = set(prog_main.get("deep_linkado_done", [])) | set(prog_rescue.get("deep_linkado_done", []))
    groupizo_done = set(prog_main.get("deep_groupizo_done", []))

    # leads = unmined listing URLs + failed-fetch URLs + all grupodewhatsapp listing URLs
    # (their pages render client-side / time out via curl; none yielded codes)
    unmined = [leads[i] for i in range(len(leads)) if i not in mined]
    gdws = [u for u in leads if "grupodewhatsapp.com" in u]
    junk_hosts = ("api.whatsapp.com", "adult.grouplinks.app")
    leads_out = sorted(set(unmined) | set(failed_urls) | set(gdws))
    leads_out = [u for u in leads_out if not any(j in u for j in junk_hosts)]
    save_json(OUT_LEADS, leads_out)

    dead = prog_main.get("verify_dead", 0) + stream_stats.get("dead", 0)
    exclusions = prog_main.get("verify_exclusions", []) + stream_stats.get("exclusions", [])
    # dedupe exclusions by code
    seen = set(); excl = []
    for e in exclusions:
        if e["code"] not in seen:
            seen.add(e["code"]); excl.append(e)

    resume_parts = []
    if unmined:
        resume_parts.append(f"re-mine {len(unmined)} listing URLs in team01-leads-slice1-leads.json (indices not yet mined)")
    if merged:
        resume_parts.append(f"verify {len(merged)} unverified candidates in team01-merged-candidates.json (team01_verify_stream.py)")
    if len(gi_slugs) > len(gi_done):
        resume_parts.append(f"deep-fetch {len(gi_slugs)-len(gi_done)} unresolved groupsinvite slugs (team01_mine.py deep gi) — slugs in team01-leads-slice1-progress.json sub_groupsinvite")
    if len(linkado_ids) > len(linkado_done):
        resume_parts.append(f"deep-fetch {len(linkado_ids)-len(linkado_done)} unresolved linkado grupo ids (team01_mine.py deep linkado)")
    summary = {
        "team": "team01",
        "slice": "leads slice 1",
        "sources": ["77links.com", "grouplink.com.in", "groupsnest.com", "groupsinvite.link",
                    "linkado.app", "groupizo.com", "groupchatconnect.info", "groupda.com",
                    "freewagroup.com", "englishan.com", "assengaonline.com", "grupbul.com",
                    "groupslink.pk", "groupsor.in", "joingram.in", "hubrecipes.com", "groupwa.link",
                    "app.grupodewhatsapp.com (unmineable via curl — JS/timeouts, all in leads)"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads_out),
        "dead": dead,
        "exclusions": excl,
        "resume": "; ".join(resume_parts) if resume_parts else "slice complete",
        "notes": (
            f"Wave 20261112 resume of wave 20261111 slice 1. Mined {len(mined)}/{len(leads)} listing pages (main+rescue+remine+remine0). "
            f"Failed-fetch listing URLs: {len(failed_urls)} (in leads for retry). "
            f"groupsinvite slugs collected: {len(gi_slugs)} (deep-resolved: {len(gi_done)}); "
            f"linkado grupo ids collected: {len(linkado_ids)} (deep-resolved: {len(linkado_done)}). "
            "Wave 20261111 VM rebooted twice mid-run (~08:00 UTC and ~10:00 UTC); the first reboot truncated the "
            "candidates file — the 263 pre-reboot candidates were re-mined by the remine0 job (idx 0-300) "
            "and grouplink candidates from idx 700-1040 by the remine job. "
            "The wave_20261111 stream verifier (team01_verify_stream.py run2) checked 525/1184, "
            "found 61 new live (138 total stream-verified incl. run1's 77), 462 dead, 1 pending, 1 exclusion, "
            "then died (VM reboot ~11:00 UTC); its dead-code list was never persisted (counts only), so the "
            "wave_20261112 stream pass re-checks the merged file and persists dead codes this time. "
            "Verification is sequential (1 worker): parallel chat.whatsapp.com fetches time out "
            "through the shared egress proxy (verified empirically: 3 concurrent curls all hit 30s; "
            "sequential requests succeed in ~8s). Live = HTTP 200 + non-empty og:title, retried once. "
            "Counts are from the output files at finalize time, not estimates. "
            "Name repair: 610 'Entrar no Grupo' linkado names fixed from grupo page titles; "
            "7 junk-named verified records renamed from og:title; 1 porn-named group "
            "(I1liZQ993ZDJyM9bdA6Ypc, og:title 'Porno xxx') removed from verified and excluded."),
    }
    save_json(OUT_SUM, summary)
    print(f"FINALIZE: verified={len(verified)} pending={len(pending)} leads={len(leads_out)} "
          f"dead={dead} excl={len(excl)} merged_unverified={len(merged)} mined={len(mined)}/{len(leads)}")
    print("resume:", summary["resume"])

if __name__ == "__main__":
    main()
