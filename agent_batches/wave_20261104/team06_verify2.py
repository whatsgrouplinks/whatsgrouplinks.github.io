import requests, re, json, html as htmlmod, time, threading
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
cands = json.load(open("_t06_candidates.json"))
codes = list(cands.keys())
tls = threading.local()
results = {}
lock = threading.Lock()
def get_session():
    s = getattr(tls, "s", None)
    if s is None:
        s = requests.Session(); tls.s = s
    return s
def verify(code):
    for attempt in range(4):
        try:
            r = get_session().get("https://chat.whatsapp.com/"+code, headers=UA, timeout=55)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            t = htmlmod.unescape(m.group(1)).strip() if m else ""
            return {"status": "live" if t else "dead", "title": t}
        except Exception as e:
            tls.s = None
            time.sleep(3 + attempt*3)
    return {"status": "transport", "title": ""}
def worker(batch):
    for c in batch:
        r = verify(c)
        with lock:
            results[c] = r
            open("_t06_v2_partial.json","w").write(json.dumps(results))
        time.sleep(0.05)
batches = [codes[i::20] for i in range(20)]
with ThreadPoolExecutor(max_workers=20) as ex:
    list(ex.map(worker, batches))
json.dump(results, open("_t06_verify2.json","w"), ensure_ascii=False, indent=1)
live=sum(1 for r in results.values() if r["status"]=="live")
print("live:",live,"dead:",sum(1 for r in results.values() if r["status"]=="dead"),"transport:",sum(1 for r in results.values() if r["status"]=="transport"))
