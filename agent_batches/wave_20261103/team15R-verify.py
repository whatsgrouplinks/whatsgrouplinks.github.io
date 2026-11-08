#!/usr/bin/env python3
"""Team15R stage2: parallel og:title verification of 974 candidates.
Writes _team15work/team15-progress.json checkpoints.
On HTTP 429: stop verifying, bank rest as rate-limited pending.
"""
import json, re, os, time, html as ihtml, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
WORK = os.path.join(WAVE, "_team15work")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"}

PORN_RE = re.compile(
    r'\b(porn|pornhub|xxx|nude|nudist|sex\s?video|escort|call\s?girl|'
    r'fuck|dick|pussy|boobs?|tits|anal|horny|porno|'
    r'sexo\s?(gratis|duro|expl[ií]cito)|chicas\s?(calientes|sexys))\b', re.I)
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B]')

WORKERS = 6

def og_title(code):
    try:
        r = requests.get(f"https://chat.whatsapp.com/{code}",
                         headers=HEADERS, timeout=25)
    except Exception:
        return None
    if r.status_code == 429:
        return "RATELIMIT"
    body = r.text
    if not body:
        return None
    m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', body)
    if not m:
        return None
    return ihtml.unescape(m.group(1)).strip()

def main():
    d = json.load(open(os.path.join(WORK, "team15-candidates.json")))
    results = d["candidates"]
    porn_drops = d.get("porn_drops", 0)
    n = len(results)
    print(f"stage2: {n} candidates, {WORKERS} workers", flush=True)

    verified, pending = [], []
    porn_lock = threading.Lock()
    stop = threading.Event()
    done = [0]
    seen_codes = set()
    codes_lock = threading.Lock()

    def work(i):
        nonlocal porn_drops
        if stop.is_set():
            return ("skip", None)
        r = results[i]
        with codes_lock:
            if r["code"] in seen_codes:
                return ("dup", None)
            seen_codes.add(r["code"])
        og = og_title(r["code"])
        time.sleep(0.6)
        if og == "RATELIMIT":
            stop.set()
            return ("ratelimit", r)
        return ("done", (r, og))

    def flush():
        json.dump({"verified": verified, "pending": pending, "porn_drops": porn_drops},
                  open(os.path.join(WORK, "team15-progress.json"), "w"), ensure_ascii=False)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, (status, payload) in enumerate(ex.map(work, range(n))):
            done[0] += 1
            if status == "ratelimit":
                payload["note"] = "rate-limited"
                pending.append(payload)
                # bank everything not yet attempted
                break
            if status == "done":
                r, og = payload
                if og is None:
                    r["note"] = "transport failure"
                    pending.append(r)
                elif og == "":
                    pass
                else:
                    name = og if og else r["title"]
                    if re.search(r'^\+?\d[\d\s\-]{7,}$', name):
                        continue
                    if PORN_RE.search(name) or EMOJI_RE.search(name):
                        with porn_lock:
                            porn_drops += 1
                        continue
                    verified.append({
                        "name": name, "category": "",
                        "country": r["iso"], "description": "",
                        "invite": f"https://chat.whatsapp.com/{r['code']}", "image": "",
                        "_meta": {"title": r["title"], "tag": r["tag"],
                                  "cityname": r["cityname"], "desc": r["raw_desc"]},
                    })
            if done[0] % 25 == 0:
                flush()
                print(f"verify {done[0]}/{n} verified={len(verified)} pending={len(pending)}", flush=True)

    if stop.is_set():
        print("RATE LIMITED — banking remainder as pending", flush=True)
        attempted = done[0]
        for r in results[attempted:]:
            with codes_lock:
                if r["code"] in seen_codes:
                    continue
            r["note"] = "rate-limited"
            pending.append(r)

    flush()
    print(f"STAGE2 DONE verified={len(verified)} pending={len(pending)} porn_drops={porn_drops}", flush=True)

if __name__ == "__main__":
    main()
