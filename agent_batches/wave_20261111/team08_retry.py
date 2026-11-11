#!/usr/bin/env python3
"""TEAM 08 — retry pass for listing pages that failed in the main fetch (status 0/403/5xx).
Slower (6 workers, 45s timeout, 2 attempts) to give slow hosts a fair chance.
Updates team08_fetch_log.json and appends to team08_raw_candidates.json."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team08_fetch import fetch_one, WAVE
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# patch timeout: monkeypatch requests.get default via wrapper is complex; instead
# re-run fetch_one but with longer timeout by editing module-level? fetch_one uses timeout=25 hardcoded.
# So implement retry fetch here reusing its helpers.
import re
from team08_fetch import CODE_RE, TITLE_RE, clean_text, guess_name, UA

def fetch_retry(url):
    for attempt in range(2):
        try:
            r = requests.get(url, headers=UA, timeout=45, allow_redirects=True)
            if r.status_code != 200 or not r.text:
                if attempt == 0:
                    time.sleep(5); continue
                return url, r.status_code, [], "", 0
            h = r.text
            title = clean_text(TITLE_RE.search(h).group(1)) if TITLE_RE.search(h) else ""
            cands, seen = [], set()
            for m in CODE_RE.finditer(h):
                code = m.group(1)
                if code in seen:
                    continue
                seen.add(code)
                cands.append({"code": code, "name": guess_name(h, m.start()),
                              "listing": url, "page_title": title[:160]})
            return url, r.status_code, cands, title[:160], len(h)
        except Exception as e:
            if attempt == 0:
                time.sleep(5); continue
            return url, 0, [], str(e)[:120], 0
    return url, 0, [], "retry exhausted", 0

def main():
    log = {d["url"]: d for d in json.load(open(os.path.join(WAVE, "team08_fetch_log.json")))}
    cands = json.load(open(os.path.join(WAVE, "team08_raw_candidates.json")))
    failed = [u for u, d in log.items() if d["status"] in (0, 403, 429, 500, 502, 503)]
    print(f"failed to retry: {len(failed)}", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_retry, u): u for u in failed}
        for i, f in enumerate(as_completed(futs)):
            url, status, cs, title, size = f.result()
            log[url] = {"url": url, "status": status, "codes": len(cs), "title": title, "size": size}
            cands.extend(cs)
            if (i+1) % 100 == 0:
                json.dump(list(log.values()), open(os.path.join(WAVE, "team08_fetch_log.json"), "w"), ensure_ascii=False)
                json.dump(cands, open(os.path.join(WAVE, "team08_raw_candidates.json"), "w"), ensure_ascii=False)
                print(f"{i+1}/{len(failed)} codes-so-far {len(cands)} elapsed {time.time()-t0:.0f}s", flush=True)
    json.dump(list(log.values()), open(os.path.join(WAVE, "team08_fetch_log.json"), "w"), ensure_ascii=False)
    json.dump(cands, open(os.path.join(WAVE, "team08_raw_candidates.json"), "w"), ensure_ascii=False)
    still = [u for u, d in log.items() if d["status"] in (0, 403, 429, 500, 502, 503)]
    print(f"RETRY DONE still-failed {len(still)} total-candidates {len(cands)} elapsed {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
