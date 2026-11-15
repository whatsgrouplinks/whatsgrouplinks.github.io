#!/usr/bin/env python3
"""team03: retry http429-pending codes after cooldown, low concurrency."""
import json, time, sys
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from concurrent.futures import ThreadPoolExecutor, as_completed
from team03_run import verify_one, VER_F

COOLDOWN = 300  # seconds to wait before first retry (429 cooldown)

def retry_one(code):
    for rnd in range(3):
        st, title, err = verify_one(code)
        if st != "pending" or err != "http429":
            return {"code": code, "status": st, "title": title, "err": err}
        time.sleep(60 * (rnd + 1))
    return {"code": code, "status": "pending", "title": "", "err": "http429"}

def main():
    print(f"cooldown {COOLDOWN}s before retrying 429s...", flush=True)
    time.sleep(COOLDOWN)
    ver = json.load(open(VER_F))
    by_code = {v["code"]: v for v in ver}
    pending = [c for c, v in by_code.items() if v["status"] == "pending"]
    print(f"retrying {len(pending)} pending codes, 3 workers", flush=True)
    n = 0
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(retry_one, c): c for c in pending}
        for f in as_completed(futs):
            res = f.result()
            by_code[res["code"]] = res
            n += 1
            if n % 10 == 0:
                json.dump(list(by_code.values()), open(VER_F, "w"), ensure_ascii=False)
                print(f"retry progress {n}/{len(pending)}", flush=True)
    json.dump(list(by_code.values()), open(VER_F, "w"), ensure_ascii=False)
    import collections
    print(collections.Counter(v["status"] for v in by_code.values()), flush=True)
    print("retry done", flush=True)

if __name__ == "__main__":
    main()
