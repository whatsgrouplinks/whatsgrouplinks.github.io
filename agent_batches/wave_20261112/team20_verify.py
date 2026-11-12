import json, re, time, html, os, sys, threading
import requests
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
fresh=json.load(open(os.path.join(WD,"team20_fresh_raw.json")))
CK=os.path.join(WD,"team20_verify_ckpt.jsonl")
done={}
if os.path.exists(CK):
    for line in open(CK):
        try:
            r=json.loads(line); done[r["code"]]=r
        except Exception: pass
print("fresh",len(fresh),"already checkpointed",len(done),flush=True)

_local=threading.local()
def sess():
    if not hasattr(_local,"s"): _local.s=requests.Session()
    return _local.s

def fetch_one(code, attempts=3):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    r=None
    for a in range(attempts):
        try:
            resp=sess().get(url, headers=UA, timeout=75)
            body=resp.text
            m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
            title=html.unescape(m.group(1)).strip() if m else ""
            # NOTE: og:description is the generic "WhatsApp Group Invite" on EVERY
            # page (live and dead), so it must NOT be used as a live fallback.
            # A non-empty og:title that equals the generic string is also dead.
            if title == "WhatsApp Group Invite":
                title = ""
            if resp.status_code==200 and title:
                r={"code":code,"status":"live","title":title}; break
            if resp.status_code in (404,410):
                r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
            if resp.status_code==200 and not title:
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
                time.sleep(2); continue
            r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {type(e).__name__}: {e}"}; break
    if r is None:
        r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
    with open(CK,"a") as f:
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
    done[code]=r
    return r

# CONTROLS FIRST
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
live_code=None
for it in g:
    m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: live_code=m.group(1); break
print("control live code:",live_code,flush=True)
rc=fetch_one(live_code)
print("CONTROL live ->",rc,flush=True)
assert rc["status"]=="live" and rc["title"], "CONTROL FAILED: known-live code did not show og:title"
fake="ZZZNotARealCode1234567890"
rf=fetch_one(fake)
print("CONTROL fake ->",rf,flush=True)
assert rf["status"]!="live", "CONTROL FAILED: fabricated code showed live"
# remove controls from checkpoint accounting (they are not in fresh anyway)
print("CONTROLS PASSED",flush=True)

from concurrent.futures import ThreadPoolExecutor
codes=[c for c in fresh if c not in done]
print("to verify:",len(codes),flush=True)
def run(code):
    r=fetch_one(code)
    time.sleep(0.4)
    return r
with ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(run, codes))
print("verify done",flush=True)
live=[c for c,r in done.items() if r["status"]=="live" and c in fresh]
pend=[c for c,r in done.items() if r["status"]=="pending" and c in fresh]
dead=[c for c,r in done.items() if r["status"]=="dead" and c in fresh]
print(f"live={len(live)} pending={len(pend)} dead={len(dead)}",flush=True)
