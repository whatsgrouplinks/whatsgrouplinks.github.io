#!/usr/bin/env python3
"""team30 recheck: re-verify the 728 HTTP-429 pending codes after cool-off.
Gentle pace: 2 workers, small batches, 4s between batches. Updates
team30-verify-progress.json in place and regenerates all outputs + summary.
"""
import json, time, sys
from concurrent.futures import ThreadPoolExecutor
import requests

sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team30_verify import fetch, write_outputs, UA

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/"

def main():
    prog_path = WAVE + "team30-verify-progress.json"
    results = json.load(open(prog_path))
    by_code = {r["code"]: r for r in results}
    pend = [r for r in results if r["status"] == "pending"]
    print("pending to recheck:", len(pend), flush=True)
    session = requests.Session()
    # controls first on the fresh session
    st, title, err = fetch(session, "KrDwdK8EIkB6vgauHg5M7N")
    print("CONTROL live:", st, repr(title), "PASS" if st == "live" and title == "JAY - PHP & Python Full Stack Developer" else "FAIL", flush=True)
    st2, title2, err2 = fetch(session, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    print("CONTROL fabricated:", st2, repr(title2), "PASS" if st2 == "dead" and title2 == "" else "FAIL", flush=True)
    if not ((st == "live" and title == "JAY - PHP & Python Full Stack Developer") and (st2 == "dead" and title2 == "")):
        print("CONTROLS FAILED — STOPPING", flush=True)
        sys.exit(1)
    BATCH = 6
    counts_extra = (434, 14407, 106, 3446, 2567, 879)
    for i in range(0, len(pend), BATCH):
        batch = pend[i:i + BATCH]
        with ThreadPoolExecutor(max_workers=2) as ex:
            outs = list(ex.map(lambda r: fetch(session, r["code"]), batch))
        for r, (s, t, e) in zip(batch, outs):
            r["status"] = s
            r["title"] = t
            r["reason"] = e
        json.dump(results, open(prog_path, "w"), indent=1, ensure_ascii=False)
        nl = sum(1 for r in results if r["status"] == "live")
        np = sum(1 for r in results if r["status"] == "pending")
        print(f"{i+len(batch)}/{len(pend)} live={nl} still-pending={np}", flush=True)
        if (i + BATCH) % 120 == 0 or i + BATCH >= len(pend):
            write_outputs(results, None, counts_extra)
            print("checkpoint outputs written", flush=True)
        if i + BATCH < len(pend):
            time.sleep(4)
    candidates, pending, excluded, n_dead, n_dup = write_outputs(results, None, counts_extra)
    summary = json.load(open(WAVE + "team30-summary.json"))
    summary["counts"].update({"verified_live": len(candidates), "dead": n_dead,
                              "excluded": len(excluded), "pending": len(pending),
                              "leads": len(candidates)})
    summary["excluded"] = excluded
    summary["pending_detail"] = pending
    summary["resume_point"] = ("verify progress banked in team30-verify-progress.json (%d codes checked). "
        "Recheck pass re-verified the 728 HTTP-429 pending codes at gentle pace after cool-off; %d still pending. "
        "groupda codes not in union: 3446 (non-adult 2567, adult 879); 2246 deferred unverified this run "
        "(adult cat_path + non-adult beyond the 1200 freshest-first cap); all listed in "
        "team30-groupda-mined.json with in_union flags — rerun team30_verify.py with TEAM30_GD_CAP=<n> to continue. "
        "groupizo fresh set fully mined in team30-mined-raw.json." % (len(results), len(pending)))
    summary["notes"] += (" Recheck: pending codes were HTTP 429 from the 5-worker verify run; after a cool-off they were "
        "re-fetched sequentially at 2 workers with the same 3-attempt rule.")
    json.dump(summary, open(WAVE + "team30-summary.json", "w"), indent=2, ensure_ascii=False)
    print("DONE recheck:", summary["counts"], flush=True)

if __name__ == "__main__":
    main()
