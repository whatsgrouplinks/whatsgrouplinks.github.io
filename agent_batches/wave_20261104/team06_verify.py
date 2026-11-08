import requests, re, json, html as htmlmod, time
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
cands = json.load(open("_t06_candidates.json"))
codes = list(cands.keys())
def verify(code):
    try:
        s = requests.Session()
        r = s.get("https://chat.whatsapp.com/"+code, headers=UA, timeout=55)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        if m:
            t = htmlmod.unescape(m.group(1)).strip()
            return (code, "live" if t else "dead", t)
        return (code, "dead", "")
    except Exception as e:
        return (code, "transport", repr(e)[:80])
results = {}
def worker(batch):
    for c in batch:
        code, st, title = verify(c)
        results[code] = {"status": st, "title": title}
        time.sleep(0.1)
batches = [codes[i::30] for i in range(30)]
with ThreadPoolExecutor(max_workers=30) as ex:
    list(ex.map(worker, batches))
live = {c:r for c,r in results.items() if r["status"]=="live"}
dead = {c:r for c,r in results.items() if r["status"]=="dead"}
tr = {c:r for c,r in results.items() if r["status"]=="transport"}
print("live:", len(live), "dead:", len(dead), "transport:", len(tr))
json.dump({"live":live,"dead":dead,"transport":tr}, open("_t06_verify.json","w"), ensure_ascii=False, indent=1)
