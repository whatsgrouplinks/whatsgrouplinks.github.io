"""Parallel resume of team20 recheck: 3 workers, 2s sleep. Resumes team20_recheck_ckpt.jsonl."""
import json, re, time, html, os, threading
import requests
from concurrent.futures import ThreadPoolExecutor
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
fresh=json.load(open(os.path.join(WD,"team20_fresh_raw.json")))
rows=[json.loads(l) for l in open(os.path.join(WD,"team20_verify_ckpt.jsonl"))]
prev={r["code"]:r for r in rows if r["code"] in fresh}
todo_codes=[c for c,r in prev.items() if r.get("reason") in ("http 429","empty og:title after retries")]
CK=os.path.join(WD,"team20_recheck_ckpt.jsonl")
done={}
lock=threading.Lock()
if os.path.exists(CK):
    for line in open(CK):
        try:
            r=json.loads(line); done[r["code"]]=r
        except Exception: pass
print(f"todo {len(todo_codes)}, already rechecked {len(done)}", flush=True)
_local=threading.local()
def sess():
    if not hasattr(_local,"s"): _local.s=requests.Session()
    return _local.s
def check(code):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    r=None
    for a in range(2):
        try:
            resp=sess().get(url, headers=UA, timeout=75)
            m=re.search(r'<meta property="og:title" content="([^"]*)"', resp.text)
            title=html.unescape(m.group(1)).strip() if m else ""
            if title=="WhatsApp Group Invite": title=""
            if resp.status_code==200 and title:
                r={"code":code,"status":"live","title":title}; break
            if resp.status_code in (404,410):
                r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
            if resp.status_code==429:
                r={"code":code,"status":"pending","title":"","reason":"http 429"}
                if a<1: time.sleep(20); continue
                break
            if resp.status_code==200 and not title:
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
                if a<1: time.sleep(8); continue
                break
            r={"code":code,"status":"pending","title":"","reason":f"http {resp.status_code}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {type(e).__name__}: {e}"}; break
    with lock:
        with open(CK,"a") as f:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
        done[code]=r
    return r
todo=[c for c in todo_codes if c not in done]
print("to recheck:",len(todo),flush=True)
def run(code):
    r=check(code); time.sleep(2); return r
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(run, todo))
from collections import Counter
print("RECHECK2", Counter(r["status"] for r in done.values()), flush=True)
print("live:", [(c,r["title"]) for c,r in done.items() if r["status"]=="live"], flush=True)
print("pending:", [c for c,r in done.items() if r["status"]=="pending"], flush=True)
