"""Team 13: fetch groupsinvite.link /group/link/<slug>/ pages, extract the REAL invite
code (embedded in the group description as chat.whatsapp.com/CODE...).
NOTE: /group/rules/<slug>/ shows chat.whatsapp.com/<GROUP-ID> which is NOT the invite
code (verified Nov 8: rules page lacks the real code). Link pages are authoritative.
Bounded to first LIMIT slugs in enumeration order (site order = newest first).
Saves incrementally to team13_state/gi_codes.json : {slug: {code, ...meta}}.
"""
import requests, re, time, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

WORK = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WORK, "gi_codes.json")
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
lock = threading.Lock()

enum = json.load(open(os.path.join(WORK, "gi_enum.json")))
slugs = list(enum.keys())[:LIMIT]
state = {}
if os.path.exists(OUT):
    state = json.load(open(OUT))
print("target slugs: %d already have codes: %d" % (len(slugs), len(state)), flush=True)

def fetch_one(slug):
    with lock:
        if slug in state:
            return "cached"
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*",
                      "Accept-Language": "en-US,en;q=0.9"})
    url = "https://groupsinvite.link/group/link/%s/" % slug
    for attempt in range(2):
        try:
            r = s.get(url, timeout=45)
            if r.status_code == 200 and len(r.text) > 5000:
                codes = CODE_RE.findall(r.text)
                # drop the group-id lookalike (slug re-cased)
                real = [c for c in codes if c.lower() != slug.lower()]
                code = real[0] if real else (codes[0] if codes else "")
                with lock:
                    rec = dict(enum[slug])
                    rec["code"] = code
                    rec["all_codes"] = codes
                    state[slug] = rec
                    json.dump(state, open(OUT, "w"))
                return "ok %s -> %s" % (slug, code if code else "NO-CODE")
            time.sleep(3)
        except Exception:
            time.sleep(4)
    with lock:
        rec = dict(enum[slug])
        rec["code"] = ""
        rec["fetch_failed"] = True
        state[slug] = rec
        json.dump(state, open(OUT, "w"))
    return "fail %s" % slug

if __name__ == "__main__":
    todo = [s for s in slugs if s not in state]
    print("to fetch: %d" % len(todo), flush=True)
    n = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_one, s): s for s in todo}
        for f in futs:
            try:
                res = f.result()
            except Exception as e:
                res = "ERR %s %s" % (futs[f], e)
            n += 1
            if n % 50 == 0 or res.startswith("fail"):
                print(n, res, flush=True)
            time.sleep(0.15)
    have = sum(1 for v in state.values() if v.get("code"))
    print("DONE fetched=%d with_code=%d no_code=%d" % (
        len(state), have, len(state) - have), flush=True)
