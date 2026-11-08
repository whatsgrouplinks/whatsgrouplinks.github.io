import requests, re, json, html as htmlmod, time, threading
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
cands = json.load(open("_t06_candidates.json"))
codes = list(cands.keys())
tls = threading.local(); lock = threading.Lock()
done = set()
try:
    for line in open("_t06_v4.jsonl"):
        done.add(json.loads(line)["code"])
except FileNotFoundError:
    pass
todo = [c for c in codes if c not in done]
print("todo:", len(todo), "already:", len(done), flush=True)
def sess():
    s = getattr(tls, "s", None)
    if s is None:
        s = requests.Session(); tls.s = s
    return s
def verify(code):
    for attempt in range(2):
        try:
            r = sess().get("https://chat.whatsapp.com/"+code, headers=UA, timeout=60)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            t = htmlmod.unescape(m.group(1)).strip() if m else ""
            return {"status": "live" if t else "dead", "title": t}
        except Exception as e:
            tls.s = None
            time.sleep(2)
    return {"status": "transport", "title": ""}
def worker(batch):
    for c in batch:
        rr = verify(c)
        line = json.dumps({"code": c, **rr}, ensure_ascii=False)
        with lock:
            for _ in range(5):
                try:
                    open("_t06_v4.jsonl","a").write(line+"\n"); break
                except Exception:
                    time.sleep(1)
batches = [todo[i::20] for i in range(20)]
with ThreadPoolExecutor(max_workers=20) as ex:
    list(ex.map(worker, batches))
n = sum(1 for _ in open("_t06_v4.jsonl"))
print("wrote total:", n, flush=True)
