"""Team 13 repair: re-fetch rules pages for slugs saved with no code (and not flagged
channel), using the fixed regex that also matches chat.whatsapp.com/invite/CODE.
Some groups show 'Link Unavailable' (genuinely codeless) — those stay empty.
Updates team13_state/gi_rules.json in place.
"""
import requests, re, time, json, os, threading
from concurrent.futures import ThreadPoolExecutor

WORK = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WORK, "gi_rules.json")
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
lock = threading.Lock()
_tls = threading.local()

def get_session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*",
                          "Accept-Language": "en-US,en;q=0.9"})
        _tls.s = s
    return s

state = json.load(open(OUT))
todo = [k for k, v in state.items()
        if not v.get("code") and not v.get("channel") and not k.lower().startswith("0029v")]
print("repair targets:", len(todo), flush=True)

def fetch_one(slug):
    s = get_session()
    url = "https://groupsinvite.link/group/rules/%s/" % slug
    for attempt in range(2):
        try:
            r = s.get(url, timeout=45)
            if r.status_code == 200 and len(r.text) > 5000:
                codes = CODE_RE.findall(r.text)
                is_channel = "whatsapp.com/channel/" in r.text
                unavailable = "Link Unavailable" in r.text
                code = "" if is_channel else (codes[0] if codes else "")
                with lock:
                    state[slug]["code"] = code
                    state[slug]["all_codes"] = codes
                    state[slug]["channel"] = is_channel
                    state[slug]["unavailable"] = unavailable
                    json.dump(state, open(OUT, "w"))
                return "ok %s -> %s" % (slug, "CHANNEL" if is_channel else ("UNAVAIL" if unavailable else (code or "NO-CODE")))
            time.sleep(3)
        except Exception:
            time.sleep(4)
    return "fail %s" % slug

if __name__ == "__main__":
    n = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_one, s): s for s in todo}
        for f in futs:
            try:
                res = f.result()
            except Exception as e:
                res = "ERR %s" % e
            n += 1
            if n % 20 == 0 or res.startswith("fail"):
                print(n, res, flush=True)
    have = sum(1 for v in state.values() if v.get("code"))
    print("DONE with_code=%d total=%d" % (have, len(state)), flush=True)
