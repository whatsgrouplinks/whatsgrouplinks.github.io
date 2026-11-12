#!/usr/bin/env python3
"""TEAM30 extract: reuse extract3 logic on team30 fetch jobs."""
import re, json, html, sys, os

sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team25_scratch")
from extract3 import extract

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SCRATCH = os.path.join(WAVE, "team30_scratch")

def main():
    fj = json.load(open(os.path.join(SCRATCH, "fetch_jobs.json")))
    jobs = fj["jobs"]
    allc = []
    for j in jobs:
        if not os.path.exists(j["file"]) or j.get("size", 0) < 500:
            print("SKIP", j["url"], j.get("status"), j.get("size"), flush=True)
            continue
        items = extract(j["file"], j["url"])
        print(j["url"], "->", len(items), "codes", flush=True)
        allc.extend(items)
    ded = {}
    for it in allc:
        if it["code"] not in ded or (not ded[it["code"]]["name"] and it["name"]):
            ded[it["code"]] = it
    print("unique codes:", len(ded))
    json.dump(sorted(ded.values(), key=lambda x: x["code"]), open(os.path.join(SCRATCH, "raw_all.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
