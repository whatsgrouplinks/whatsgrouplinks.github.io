#!/usr/bin/env python3
"""team14 P5 verify v2: checks chat.whatsapp.com/<code> with Chrome UA via curl.
LIVE only if HTTP 200 AND non-empty og:title.
Transport failure (timeout/429/5xx/000) -> pending (retry once after 60s).
Genuinely dead (200 + empty og:title, or other non-200) -> dropped.
Concurrency 8 max. Incremental progress JSONL (crash-safe) + retrying final writes.
Usage: verify.py <input.json> <out_live.json> <out_pending.json> <outdir> <progress.jsonl>
"""
import json, re, subprocess, sys, time, os, concurrent.futures

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

def dump_retry(obj, path, tries=15):
    payload = json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")
    for i in range(tries):
        try:
            with open(path, "wb", buffering=0) as f:
                f.write(payload)
            return True
        except PermissionError:
            time.sleep(3 + i)
    # last resort: write to sibling name
    try:
        with open(path + ".alt", "wb", buffering=0) as f:
            f.write(payload)
        print(f"WROTE ALT {path}.alt", flush=True)
        return True
    except Exception as e:
        print(f"WRITE FAILED {path}: {e}", flush=True)
        return False

def check_once(code, outdir):
    url = f"https://chat.whatsapp.com/{code}"
    bodyfile = os.path.join(outdir, f"chk_{code}.html")
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", bodyfile, "-w", "%{http_code}",
             "--max-time", "30", "-A", UA, url],
            capture_output=True, text=True, timeout=40)
    except subprocess.TimeoutExpired:
        return (0, None, True)
    # curl exit code != 0 (e.g. 23 = failed writing body) => transport
    if r.returncode != 0:
        return (0, None, True)
    # body must have actually landed on disk; an empty/tiny file means the
    # write failed (sandbox EPERM waves) => transport, NOT dead
    try:
        if os.path.getsize(bodyfile) < 5000:
            return (0, None, True)
    except OSError:
        return (0, None, True)
    http = r.stdout.strip()
    try:
        http = int(http)
    except ValueError:
        return (0, None, True)
    if http in (429, 500, 502, 503, 504) or http == 0:
        return (http, None, True)
    if http != 200:
        return (http, None, False)
    try:
        body = open(bodyfile, encoding="utf-8", errors="ignore").read()
    except Exception:
        return (http, None, True)
    m = OG_RE.search(body)
    title = m.group(1).strip() if m else ""
    return (http, title if title else "", False)

def main():
    inp, out_live, out_pend, outdir, prog = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    os.makedirs(outdir, exist_ok=True)
    items = json.load(open(inp))
    print(f"checking {len(items)} codes", flush=True)
    live, pending, dead = [], [], []
    transport_first = []
    pf = open(prog, "ab", buffering=0)
    def note(rec):
        line = (json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8")
        for _ in range(10):
            try:
                pf.write(line); return
            except PermissionError:
                time.sleep(3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(check_once, it["code"], outdir): it for it in items}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            it = futs[fut]
            try:
                http, title, transport = fut.result()
            except Exception:
                http, title, transport = 0, None, True
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(items)} live={len(live)} transport={len(transport_first)} dead={len(dead)}", flush=True)
            if transport:
                transport_first.append((it, http))
            elif http == 200 and title:
                d = dict(it); d["og_title"] = title
                live.append(d); note({"verdict": "live", "code": it["code"], "http": http, "og_title": title})
            else:
                dead.append((it, http)); note({"verdict": "dead", "code": it["code"], "http": http})
    print(f"pass1: live={len(live)} transport={len(transport_first)} dead={len(dead)}", flush=True)
    if transport_first:
        print("waiting 60s before transport retry...", flush=True)
        time.sleep(60)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(check_once, it["code"], outdir): (it, h) for it, h in transport_first}
            for fut in concurrent.futures.as_completed(futs):
                it, h0 = futs[fut]
                try:
                    http, title, transport = fut.result()
                except Exception:
                    http, title, transport = 0, None, True
                if transport:
                    pending.append(it); note({"verdict": "pending", "code": it["code"], "http": http})
                elif http == 200 and title:
                    d = dict(it); d["og_title"] = title
                    live.append(d); note({"verdict": "live", "code": it["code"], "http": http, "og_title": title})
                else:
                    dead.append((it, http)); note({"verdict": "dead", "code": it["code"], "http": http})
    pf.close()
    dump_retry(live, out_live)
    dump_retry(pending, out_pend)
    dump_retry([{"code": it["code"], "http": h} for it, h in dead], out_pend + ".dead.json")
    print(f"FINAL live={len(live)} pending={len(pending)} dead={len(dead)}", flush=True)
    print("LIVE_CODES " + " ".join(d["code"] for d in live), flush=True)
    print("PENDING_CODES " + " ".join(d["code"] for d in pending), flush=True)
    print("LIVE_JSON " + json.dumps(live, ensure_ascii=False), flush=True)
    print("PENDING_JSON " + json.dumps(pending, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
