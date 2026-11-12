#!/usr/bin/env python3
"""TEAM05 repair — verify the 45 batch-18 orphans: codes mined (stage=mined,
not dup-existing) but never verified because the VM rebooted ~08:18 PKT
mid-verify of batch 18. Reuses team05_mine.verify_code/screen/map_category.
Appends results to team05-verify.jsonl. Idempotent: skips codes already in
verify file or in the existing-codes union."""
import json, os, sys, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import team05_mine as M
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
MINED_JL = os.path.join(WAVE, "team05-mined.jsonl")
VERIFY_JL = os.path.join(WAVE, "team05-verify.jsonl")

def main():
    mined = M.load_jl(MINED_JL)
    verify = M.load_jl(VERIFY_JL)
    vcodes = {r["code"] for r in verify}
    dup = {r["code"] for r in mined if r.get("stage") == "dup-existing"}
    existing = set(json.load(open(M.EXISTING)))
    seen = set()
    orphans = []
    for r in mined:
        if r.get("stage") == "mined" and r.get("code"):
            c = r["code"]
            if c in seen:
                continue
            seen.add(c)
            if c not in vcodes and c not in dup and c not in existing:
                orphans.append(r)
    print(f"orphans to verify: {len(orphans)}", flush=True)

    def verify_one(r):
        code = r["code"]
        cat = M.map_category(r.get("pt_category", ""), r.get("name", ""), r.get("description", ""))
        name = r.get("name", "") or "WhatsApp Group"
        desc = r.get("description", "")
        status, ogt = M.verify_code(code)
        rec = {"code": code, "name": name, "category": cat, "country": "BR",
               "description": desc, "invite": f"https://chat.whatsapp.com/{code}",
               "og_title": ogt or "", "status": status,
               "pt_category": r.get("pt_category", ""), "source_url": r["url"]}
        if status == "live":
            reason = M.screen(name, desc, ogt)
            if reason:
                rec["status"] = "excluded"
                rec["reason"] = reason
            else:
                if not desc:
                    rec["description"] = f"Join {name}, a WhatsApp group listed under {cat}."
                elif len(desc) > 300:
                    rec["description"] = desc[:297].rstrip() + "..."
        return rec

    done = {"live": 0, "dead": 0, "pending": 0, "excluded": 0}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(verify_one, r): r for r in orphans}
        for fut in as_completed(futs):
            rec = fut.result()
            M.append_jl(VERIFY_JL, rec)
            done[rec["status"]] = done.get(rec["status"], 0) + 1
            print(f"  {rec['status']}: {rec['code']} {rec['name'][:50]}", flush=True)
    print(f"REPAIR DONE {done}", flush=True)

if __name__ == "__main__":
    main()
