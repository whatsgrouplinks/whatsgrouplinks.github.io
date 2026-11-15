import json, re, time, html, os, sys
import requests
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
S=requests.Session(); S.headers.update(UA)
CK=os.path.join(WD,"team17_verify_ckpt.jsonl")
done={}
if os.path.exists(CK):
    for line in open(CK):
        try:
            r=json.loads(line); done[r["code"]]=r
        except Exception: pass

def og_title(body):
    m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
    return html.unescape(m.group(1)).strip() if m else ""

def fetch_one(code, attempts=3):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    r=None
    for a in range(attempts):
        try:
            resp=S.get(url, timeout=75)
            title=og_title(resp.text)
            if title=="WhatsApp Group Invite": title=""
            if resp.status_code==200 and title:
                r={"code":code,"status":"live","title":title}; break
            if resp.status_code in (404,410):
                r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
            if resp.status_code==429:
                r={"code":code,"status":"pending","title":"","reason":"http 429"}
                if a < attempts-1:
                    time.sleep(25); continue
                break
            if resp.status_code==200 and not title:
                if a < attempts-1:
                    time.sleep(6); continue
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after 3 spaced retries"}; break
            r={"code":code,"status":"pending","title":"","reason":f"http {resp.status_code}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {type(e).__name__}: {e}"}; break
    with open(CK,"a") as f:
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
    done[code]=r
    return r

# CONTROLS (exact, per task)
rc=fetch_one("KrDwdK8EIkB6vgauHg5M7N")
print("CONTROL live ->",rc,flush=True)
assert rc["status"]=="live" and rc["title"]=="JAY - PHP & Python Full Stack Developer", f"CONTROL FAILED live: {rc}"
rf=fetch_one("ZzZzZzZzZzZzZzZzZzZzZzZz")
print("CONTROL fake ->",rf,flush=True)
assert rf["status"]!="live" and rf["title"]=="", f"CONTROL FAILED fake: {rf}"
print("CONTROLS PASSED",flush=True)

fresh=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113/team20_fresh_77.json"))
# extra codes file (poll results) optional second arg
extra=[]
if len(sys.argv)>1 and os.path.exists(sys.argv[1]):
    extra=json.load(open(sys.argv[1]))
    print("extra codes:",len(extra),flush=True)
codes=[c for c in list(fresh.keys())+extra if c not in done]
print("to verify:",len(codes),"already checkpointed:",len(done),flush=True)
for i,code in enumerate(codes):
    r=fetch_one(code)
    if (i+1)%25==0: print(f"{i+1}/{len(codes)} live={sum(1 for v in done.values() if v['status']=='live')} dead={sum(1 for v in done.values() if v['status']=='dead')} pending={sum(1 for v in done.values() if v['status']=='pending')}",flush=True)
    time.sleep(2.5)
print("VERIFY DONE live=%d dead=%d pending=%d"%(
    sum(1 for v in done.values() if v["status"]=="live"),
    sum(1 for v in done.values() if v["status"]=="dead"),
    sum(1 for v in done.values() if v["status"]=="pending")),flush=True)
