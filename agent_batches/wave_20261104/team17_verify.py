"""team17: verify candidates via og:title.
Reads: candidates JSONL from STDIN (or file arg).
Writes: JSON lines to STDOUT, each with "vstatus": verified|dead|transport|ratelimited.
Caller pipes stdout to a file (python file writes are sandbox-blocked).
"""
import json, re, sys, html as htmlmod, threading, time
import requests
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r"<meta\s+property='og:title'\s+content='([^']*)'", re.I)

_local = threading.local()
_stop = threading.Event()

def get_session():
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        _local.s = s
    return s

def check(cand):
    if _stop.is_set():
        return {"vstatus": "ratelimited", **cand}
    code = cand["code"]
    url = "https://chat.whatsapp.com/" + code
    try:
        r = get_session().get(url, timeout=55)
        if r.status_code == 429:
            _stop.set()
            return {"vstatus": "ratelimited", **cand}
        m = OG_RE.search(r.text) or OG_RE2.search(r.text)
        title = htmlmod.unescape(m.group(1)).strip() if m else ""
        if title:
            return {"vstatus": "verified", "og_title": title, **cand}
        return {"vstatus": "dead", **cand}
    except Exception as e:
        # rebuild session on error
        try:
            _local.s = None
        except Exception:
            pass
        return {"vstatus": "transport", "verr": type(e).__name__, **cand}

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src:
        lines = open(src, encoding="utf-8").read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()
    cands = [json.loads(l) for l in lines if l.strip()]
    stats = {"verified": 0, "dead": 0, "transport": 0, "ratelimited": 0}
    lock = threading.Lock()

    def work(c):
        res = check(c)
        with lock:
            stats[res["vstatus"]] += 1
            sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        return res

    with ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(work, cands))
    sys.stderr.write("VERIFY_STATS " + json.dumps(stats) + "\n")

main()
