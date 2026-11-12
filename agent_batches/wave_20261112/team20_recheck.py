"""Recheck team20: 119 codes mislabelled dead on HTTP 429 (must be pending per rules),
plus one spaced re-check of the 68 empty-og codes. Single worker, slow pace."""
import json, re, time, html, os
import requests
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
fresh=json.load(open(os.path.join(WD,"team20_fresh_raw.json")))
rows=[json.loads(l) for l in open(os.path.join(WD,"team20_verify_ckpt.jsonl"))]
prev={r["code"]:r for r in rows if r["code"] in fresh}
r429=[c for c,r in prev.items() if r.get("reason")=="http 429"]
empty=[c for c,r in prev.items() if r.get("reason")=="empty og:title after retries"]
print(f"429-codes: {len(r429)}, empty-og codes: {len(empty)}", flush=True)
CK=os.path.join(WD,"team20_recheck_ckpt.jsonl")
done={}
if os.path.exists(CK):
    for line in open(CK):
        try:
            r=json.loads(line); done[r["code"]]=r
        except Exception: pass
print("already rechecked:",len(done),flush=True)
s=requests.Session()
def check(code, attempts=2):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    r=None
    for a in range(attempts):
        try:
            resp=s.get(url, headers=UA, timeout=75)
            m=re.search(r'<meta property="og:title" content="([^"]*)"', resp.text)
            title=html.unescape(m.group(1)).strip() if m else ""
            if title=="WhatsApp Group Invite": title=""
            if resp.status_code==200 and title:
                r={"code":code,"status":"live","title":title}; break
            if resp.status_code in (404,410):
                r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
            if resp.status_code==429:
                r={"code":code,"status":"pending","title":"","reason":"http 429"}
                if a<attempts-1: time.sleep(30); continue
                break
            if resp.status_code==200 and not title:
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
                if a<attempts-1: time.sleep(10); continue
                break
            r={"code":code,"status":"pending","title":"","reason":f"http {resp.status_code}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {type(e).__name__}: {e}"}; break
    with open(CK,"a") as f:
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
    done[code]=r
    return r
# cooldown first
print("cooldown 60s...", flush=True); time.sleep(60)
todo=[c for c in r429 if c not in done]
print("rechecking 429 codes:",len(todo),flush=True)
for i,c in enumerate(todo):
    r=check(c)
    if i%10==0: print(i, r["status"], r.get("reason",""), r.get("title",""), flush=True)
    time.sleep(3)
todo2=[c for c in empty if c not in done]
print("spaced re-check of empty-og codes:",len(todo2),flush=True)
for i,c in enumerate(todo2):
    r=check(c, attempts=1)
    if i%10==0: print(i, r["status"], r.get("reason",""), r.get("title",""), flush=True)
    time.sleep(3)
from collections import Counter
print("RECHECK", Counter(r["status"] for r in done.values()), flush=True)
print("live titles:", [(c,r["title"]) for c,r in done.items() if r["status"]=="live"], flush=True)
