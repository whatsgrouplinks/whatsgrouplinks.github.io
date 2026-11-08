import requests, re, json, html as htmlmod, time, threading, os
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
cands = json.load(open(os.path.join(BASE, "_t06_candidates.json")))
codes = list(cands.keys())
tls = threading.local(); lock = threading.Lock()

def wretry(path, obj, tries=15):
    data = json.dumps(obj, ensure_ascii=False, indent=1)
    for a in range(tries):
        try:
            with open(path, "w") as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            back = json.load(open(path))
            if isinstance(back, dict) and len(back) == len(obj):
                return True
        except Exception:
            time.sleep(2)
    return False

done = {}
JL = os.path.join(BASE, "_t06_v5.jsonl")
if os.path.exists(JL):
    for line in open(JL):
        line = line.strip()
        if line:
            r = json.loads(line); done[r["code"]] = r
todo = [c for c in codes if c not in done]
print("todo:", len(todo), "have:", len(done), flush=True)

def sess():
    s = getattr(tls, "s", None)
    if s is None:
        s = requests.Session(); tls.s = s
    return s

def verify(code):
    for attempt in range(2):
        try:
            r = sess().get("https://chat.whatsapp.com/" + code, headers=UA, timeout=60)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            t = htmlmod.unescape(m.group(1)).strip() if m else ""
            return {"status": "live" if t else "dead", "title": t}
        except Exception:
            tls.s = None; time.sleep(2)
    return {"status": "transport", "title": ""}

def worker(batch):
    for c in batch:
        rr = verify(c)
        line = json.dumps({"code": c, **rr}, ensure_ascii=False)
        with lock:
            for _ in range(10):
                try:
                    f = open(JL, "a"); f.write(line + "\n"); f.flush(); os.fsync(f.fileno()); f.close(); break
                except Exception:
                    time.sleep(1.5)

batches = [todo[i::20] for i in range(20) if todo[i::20]]
with ThreadPoolExecutor(max_workers=20) as ex:
    list(ex.map(worker, batches))
rows = []
for line in open(JL):
    line = line.strip()
    if line: rows.append(json.loads(line))
print("rows:", len(rows), flush=True)
out = {r["code"]: {"status": r["status"], "title": r["title"]} for r in rows}
ok = wretry(os.path.join(BASE, "_t06_verify5.json"), out)
print("final write:", "OK" if ok else "FAILED", flush=True)
from collections import Counter
print(Counter(r["status"] for r in rows), flush=True)
