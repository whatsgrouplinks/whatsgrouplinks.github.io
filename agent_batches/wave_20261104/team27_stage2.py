import re, json, html as htmlmod, os, sys, time, threading
import requests
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(line_buffering=True)
WD = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

cands = json.load(open(os.path.join(WD, "team27_candidates.json")))
codes = [c["code"] for c in cands]
print("to verify:", len(codes), flush=True)

tls = threading.local()
def sess():
    if not hasattr(tls, "s"):
        tls.s = requests.Session()
        tls.s.headers.update(UA)
    return tls.s

def verify(code):
    for i in range(2):
        try:
            r = sess().get("https://chat.whatsapp.com/" + code, timeout=60)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            if m:
                t = htmlmod.unescape(m.group(1)).strip()
                return (code, "live" if t else "dead", t)
            return (code, "dead", "")
        except Exception as e:
            err = repr(e)[:80]
            time.sleep(4)
    return (code, "transport", err)

results = {}
def worker(batch):
    for c in batch:
        code, st, title = verify(c)
        results[code] = {"status": st, "title": title}

batches = [codes[i::24] for i in range(24)]
with ThreadPoolExecutor(max_workers=24) as ex:
    list(ex.map(worker, batches))

live = {c: r for c, r in results.items() if r["status"] == "live"}
dead = {c: r for c, r in results.items() if r["status"] == "dead"}
tr = {c: r for c, r in results.items() if r["status"] == "transport"}
print("live:", len(live), "dead:", len(dead), "transport:", len(tr), flush=True)
json.dump({"live": live, "dead": dead, "transport": tr},
          open(os.path.join(WD, "team27_verify_results.json"), "w"), ensure_ascii=False, indent=1)
