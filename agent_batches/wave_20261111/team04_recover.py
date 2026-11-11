#!/usr/bin/env python3
"""TEAM 04 recovery — verifies codes mined in team04-mined.jsonl that have no
record in team04-verify.jsonl (the miner died mid-verification of batch 3).
Appends results incrementally to team04-verify.jsonl, then exits. Run before
relaunching team04_mine.py. Reuses team04_mine's verify/screen/category code.
"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
sys.path.insert(0, WAVE)
import team04_mine as tm

def load_jl(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    return out

def main():
    existing = set(json.load(open(tm.EXISTING)))
    mined = load_jl(tm.MINED_JL)
    ver = load_jl(tm.VERIFY_JL)
    vcodes = {r["code"] for r in ver}
    seen = set(vcodes)
    cands = []
    for r in mined:
        if r.get("stage") != "mined":
            continue
        code = r["code"]
        if code in existing or code in seen:
            continue
        seen.add(code)
        cands.append(r)
    print(f"recovery candidates: {len(cands)}", flush=True)
    if not cands:
        return
    def verify_one(r):
        code = r["code"]
        cat = tm.map_category(r.get("pt_category", ""), r.get("name", ""), r.get("description", ""))
        name = r.get("name", "") or "WhatsApp Group"
        desc = r.get("description", "")
        status, ogt = tm.verify_code(code)
        rec = {"code": code, "name": name, "category": cat, "country": "BR",
               "description": desc, "invite": f"https://chat.whatsapp.com/{code}",
               "og_title": ogt or "", "status": status,
               "pt_category": r.get("pt_category", ""), "source_url": r["url"]}
        if status == "live":
            reason = tm.screen(name, desc, ogt)
            if reason:
                rec["status"] = "excluded"
                rec["reason"] = reason
            else:
                if not desc:
                    rec["description"] = f"Join {name}, a WhatsApp group listed under {cat}."
                elif len(desc) > 300:
                    rec["description"] = desc[:297].rstrip() + "..."
        return rec
    done = 0
    with ThreadPoolExecutor(max_workers=tm.WORKERS) as ex:
        futs = {ex.submit(verify_one, r): r for r in cands}
        for fut in as_completed(futs):
            rec = fut.result()
            tm.append_jl(tm.VERIFY_JL, rec)
            done += 1
            if done % 10 == 0:
                print(f"recovered {done}/{len(cands)}", flush=True)
    print(f"RECOVERY DONE {done} codes verified", flush=True)

if __name__ == "__main__":
    main()
