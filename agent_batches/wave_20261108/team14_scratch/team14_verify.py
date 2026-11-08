#!/usr/bin/env python3
"""Team14: verify kept candidates live via chat.whatsapp.com og:title.
Max 3 parallel, >=0.5s between check starts. Retry-once for 200-empty;
transport errors -> retry once after 60s -> pending. Incremental JSONL log."""
import json, re, subprocess, time, concurrent.futures, threading, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
GENERIC = {"whatsapp group", "join this group on whatsapp", "whatsapp"}
LOG = os.path.join(WAVE, "team14_verify_log.jsonl")
_last_start = [0.0]
_lock = threading.Lock()

def check_once(code):
    with _lock:
        wait = 0.5 - (time.time() - _last_start[0])
        if wait > 0:
            time.sleep(wait)
        _last_start[0] = time.time()
    try:
        r = subprocess.run(["curl", "-s", "-w", "\n%{http_code}", "--max-time", "25", "-A", UA,
                            f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=35)
    except subprocess.TimeoutExpired:
        return (0, "", True)
    if r.returncode != 0:
        return (0, "", True)
    out = r.stdout
    nl = out.rfind("\n")
    try:
        http = int(out[nl + 1:].strip())
    except ValueError:
        return (0, "", True)
    if http in (429, 500, 502, 503, 504) or http == 0:
        return (http, "", True)
    if http != 200:
        return (http, "", False)
    body = out[:nl]
    if len(body) < 5000:
        return (http, "", True)
    m = OG_RE.search(body)
    title = m.group(1).strip() if m else ""
    return (http, title, False)

def decide(it):
    http, title, tr = check_once(it["code"])
    if tr:
        return ("transport", it, title)
    if http == 200 and title and title.lower() not in GENERIC and "channel" not in title.lower():
        return ("live", it, title)
    if http == 200 and title and "channel" in title.lower():
        return ("channel", it, title)
    if http == 200 and not title:
        return ("empty200", it, title)
    return ("dead", it, title)

def main():
    kept = json.load(open(f"{WAVE}/team14_kept.json"))
    decided = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            line = line.strip()
            if line:
                o = json.loads(line)
                decided[o["code"]] = o["status"]
    todo = [k for k in kept if k["code"] not in decided]
    print(f"kept={len(kept)} already_decided={len(decided)} todo={len(todo)}", flush=True)
    logf = open(LOG, "a")
    def log(code, status, title=""):
        logf.write(json.dumps({"code": code, "status": status, "title": title}, ensure_ascii=False) + "\n")
        logf.flush()
    results = {"live": [], "pending": [], "dead": 0, "channel": 0}
    for k in kept:
        if k["code"] in decided and decided[k["code"]] == "live":
            results["live"].append(k)
        elif k["code"] in decided and decided[k["code"]] == "pending":
            results["pending"].append(k)
    # pass 1
    retry_empty, retry_transport = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(decide, it): it for it in todo}
        n = 0
        for fut in concurrent.futures.as_completed(futs):
            status, it, title = fut.result()
            n += 1
            if n % 100 == 0:
                print(f"  pass1 {n}/{len(todo)} live={len(results['live'])} dead={results['dead']} transport-retry={len(retry_transport)} empty-retry={len(retry_empty)}", flush=True)
            if status == "live":
                results["live"].append(it); log(it["code"], "live", title)
            elif status == "transport":
                retry_transport.append(it)
            elif status == "empty200":
                retry_empty.append(it)
            elif status == "channel":
                results["channel"] += 1; log(it["code"], "channel", title)
            else:
                results["dead"] += 1; log(it["code"], "dead", title)
    print(f"PASS1 live={len(results['live'])} dead={results['dead']} channel={results['channel']} transport-retry={len(retry_transport)} empty-retry={len(retry_empty)}", flush=True)
    # retry pass: transport after 60s, empty after 30s (fresh session each = new curl call)
    if retry_transport:
        print("waiting 60s before transport retry...", flush=True)
        time.sleep(60)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futs = {ex.submit(decide, it): it for it in retry_transport}
            for fut in concurrent.futures.as_completed(futs):
                status, it, title = fut.result()
                if status == "live":
                    results["live"].append(it); log(it["code"], "live", title)
                elif status in ("transport", "empty200"):
                    results["pending"].append(it); log(it["code"], "pending", title)
                elif status == "channel":
                    results["channel"] += 1; log(it["code"], "channel", title)
                else:
                    results["dead"] += 1; log(it["code"], "dead", title)
    if retry_empty:
        print(f"waiting 30s before empty-200 retry ({len(retry_empty)})...", flush=True)
        time.sleep(30)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futs = {ex.submit(decide, it): it for it in retry_empty}
            for fut in concurrent.futures.as_completed(futs):
                status, it, title = fut.result()
                if status == "live":
                    results["live"].append(it); log(it["code"], "live", title)
                elif status in ("transport",):
                    results["pending"].append(it); log(it["code"], "pending", title)
                elif status == "empty200":
                    results["dead"] += 1; log(it["code"], "dead", title)
                elif status == "channel":
                    results["channel"] += 1; log(it["code"], "channel", title)
                else:
                    results["dead"] += 1; log(it["code"], "dead", title)
    print(f"FINAL live={len(results['live'])} pending={len(results['pending'])} dead={results['dead']} channel={results['channel']}", flush=True)
    live_out = [{k: v for k, v in it.items() if not k.startswith("_")} for it in results["live"]]
    pend_out = [{**{k: v for k, v in it.items() if not k.startswith("_")}, "reason": "transport"} for it in results["pending"]]
    # dedupe defensively + sort for stability
    seen = set(); lv = []
    for it in live_out:
        if it["invite"] not in seen:
            seen.add(it["invite"]); lv.append(it)
    seen = set(); pv = []
    for it in pend_out:
        if it["invite"] not in seen:
            seen.add(it["invite"]); pv.append(it)
    for obj, path in [(lv, f"{WAVE}/team14-groupjoin.json"), (pv, f"{WAVE}/team14-groupjoin-pending.json")]:
        for i in range(30):
            try:
                with open(path, "wb", buffering=0) as f:
                    f.write(json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8"))
                print(f"wrote {path} n={len(obj)}", flush=True)
                break
            except PermissionError:
                print(f"write EPERM {path} retry {i}", flush=True)
                time.sleep(5)
    print("VERIFY_DONE", flush=True)

if __name__ == "__main__":
    main()
