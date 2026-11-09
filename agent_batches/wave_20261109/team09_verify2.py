"""Team 09 slow verifier v2 for 704 codes in team08_codes.json.
Partial-head fetch: og:title sits at byte ~2518 on WhatsApp invite pages,
so read only the first 16KB via Popen and terminate curl. Much lighter/faster
than full 223KB downloads and avoids the throttling seen with full fetches.
curl-only (never python requests on chat.whatsapp.com), 3 workers,
0.6s sleep per worker between requests.
Empty og:title -> retry up to 2 more times spaced 3s apart, then dead.
No og:title in head at all / curl error / timeout -> fetch failure; after
3 failed fetches -> pending (transport-failed), NOT dead.
Resumable: appends one JSON line per code to team09_verify_raw2.jsonl.
Reliable v1 results (full-body, title empty) are imported as dead.
"""
import json, re, subprocess, html, time, os

WAVE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
RAW2 = os.path.join(WAVE, "team09_verify_raw2.jsonl")
RAW1 = os.path.join(WAVE, "team09_verify_raw.jsonl")
OG_TITLE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.I)
HEAD_BYTES = 16384

def fetch_head(code):
    """Return (status, title) where status in {'ok','fail'}.
    ok = head received and og:title tag present (title may be '')."""
    url = "https://chat.whatsapp.com/" + code
    try:
        p = subprocess.Popen(
            ["curl", "-sL", "--http2", "--max-time", "20", "-A", UA, url],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            data = p.stdout.read(HEAD_BYTES)
        finally:
            try:
                p.terminate()
            except Exception:
                pass
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
        text = data.decode("utf-8", errors="ignore")
        m = OG_TITLE.search(text)
        if m is None:
            return "fail", ""
        return "ok", html.unescape(m.group(1)).strip()
    except Exception:
        return "fail", ""

def work(code):
    title = ""
    fails = 0
    attempts = 0
    for i in range(3):
        attempts += 1
        status, title = fetch_head(code)
        if status == "ok":
            if title:
                break
            if i < 2:
                time.sleep(3)
        else:
            fails += 1
            if i < 2:
                time.sleep(3)
    if title:
        verdict = "live"
    elif fails == 3:
        verdict = "pending"
    elif fails > 0:
        # got at least one ok-but-empty head; empty og:title seen on a real page
        verdict = "dead"
    else:
        verdict = "dead"
    time.sleep(0.6)
    return {"code": code, "title": title, "verdict": verdict,
            "attempts": attempts, "fails": fails}

def main():
    from concurrent.futures import ThreadPoolExecutor
    codes = json.load(open(os.path.join(WAVE, "team08_codes.json")))
    existing = set(json.load(open(os.path.join(WAVE, "../../.existing_codes.json"))))
    fresh = [c for c in dict.fromkeys(codes) if c not in existing]
    print("total", len(codes), "union-dup", len(codes) - len(fresh),
          "fresh", len(fresh), flush=True)
    done = {}
    # import reliable v1 results
    if os.path.exists(RAW1):
        for line in open(RAW1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("title"):
                done[r["code"]] = {"code": r["code"], "title": r["title"],
                                   "verdict": "live", "attempts": r.get("attempts", 1),
                                   "fails": 0, "src": "v1"}
            elif all(s > 100000 for s in r.get("sizes", [])) and r.get("http") == "200":
                done[r["code"]] = {"code": r["code"], "title": "",
                                   "verdict": "dead", "attempts": r.get("attempts", 3),
                                   "fails": 0, "src": "v1"}
            # else: unreliable (http 000 / zero-size attempts) -> recheck
    if os.path.exists(RAW2):
        for line in open(RAW2):
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    done[r["code"]] = r
                except Exception:
                    pass
    todo = [c for c in fresh if c not in done]
    print("already done", len(done), "todo", len(todo), flush=True)
    n = 0
    with open(RAW2, "a") as out:
        with ThreadPoolExecutor(max_workers=3) as ex:
            for res in ex.map(work, todo):
                out.write(json.dumps(res, ensure_ascii=False) + "\n")
                out.flush()
                n += 1
                if n % 25 == 0:
                    print(f"checked {n}/{len(todo)}", flush=True)
    print("DONE checked", n, flush=True)

if __name__ == "__main__":
    main()
