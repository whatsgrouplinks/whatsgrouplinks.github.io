import requests, re, json, html as htmlmod, time
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
v = json.load(open("_t06_verify.json"))
codes = list(v["transport"].keys())
print("retrying", len(codes))
results = {}
def verify(code):
    for attempt in range(3):
        try:
            s = requests.Session()
            r = s.get("https://chat.whatsapp.com/"+code, headers=UA, timeout=55)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            if m:
                t = htmlmod.unescape(m.group(1)).strip()
                return (code, "live" if t else "dead", t)
            return (code, "dead", "")
        except Exception as e:
            time.sleep(4)
    return (code, "transport", "3x fail")
def worker(batch):
    for c in batch:
        code, st, title = verify(c)
        results[code] = {"status": st, "title": title}
        time.sleep(0.15)
batches = [codes[i::15] for i in range(15)]
with ThreadPoolExecutor(max_workers=15) as ex:
    list(ex.map(worker, batches))
for c,r in results.items():
    v["live"][c] = r if False else v["live"]
    if r["status"] == "live": v["live"][c] = r
    elif r["status"] == "dead": v["dead"][c] = r
    else: v["transport"][c] = r
# remove from transport those that resolved
json.dump(v, open("_t06_verify.json","w"), ensure_ascii=False, indent=1)
print("now live:", len(v["live"]), "dead:", len(v["dead"]), "transport:", len(v["transport"]))
