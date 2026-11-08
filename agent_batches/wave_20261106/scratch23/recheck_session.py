import requests, re, json, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor
WAVE=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106")
S=os.path.join(WAVE,"scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
# --- rebuild candidate sets exactly as in the original runs ---
union=set(json.load(open(os.path.join(WAVE,"dedupe_union.json"))))
# PK candidates
pk={}
for f in ["pk_api_raw.json","pk_html_raw.json"]:
    p=os.path.join(S,f)
    if os.path.exists(p):
        for it in json.load(open(p)):
            pk.setdefault(it["code"],it)
pk_fresh={c:v for c,v in pk.items() if c not in union}
# GD candidates (saved fetch_print stdout page, lines 0-69)
saved=json.load(open(os.path.expanduser("~/workspace/agents/af97b50f-bc6d-4054-8c64-e35a60ecc6f5/tool-output/process.log-call_01a1afeb4af0706eb3ac2c6a15670668.json")))
gd={}
for line in saved["lines"]:
    if not line.startswith("POSTLINE "): continue
    try: d=json.loads(line[len("POSTLINE "):])
    except Exception: continue
    for code in d.get("codes",[]):
        gd.setdefault(code,{"code":code,"name_hint":d.get("title",""),"cat_hint":d.get("cat",""),"country_hint":"","src":d.get("src","")})
gd_fresh={c:v for c,v in gd.items() if c not in union and c not in pk}
print("PKFRESH",len(pk_fresh),"GDFRESH",len(gd_fresh),flush=True)
# --- original verdicts from my delivered files ---
verified=json.load(open(os.path.join(WAVE,"team23-p11-groupda.json")))
live_codes={x["invite"].split("/")[-1]:x for x in verified}
print("ORIGLIVE",len(live_codes),flush=True)
# candidates to re-check: every fresh code (live + dead), Session keep-alive
cands={}
for c,v in pk_fresh.items(): cands[c]=v
for c,v in gd_fresh.items(): cands[c]=v
print("RECHECK_TOTAL",len(cands),flush=True)
local=threading.local()
def get_session():
    if not hasattr(local,"s"):
        local.s=requests.Session()
        local.s.headers.update(UA)
    return local.s
def check(code):
    url=f"https://chat.whatsapp.com/{code}"
    s=get_session()
    t0=time.time()
    try:
        r=s.get(url,timeout=30)
        dt=time.time()-t0
        if r.status_code==200:
            m=re.search(r'<meta property="og:title" content="([^"]*)"',r.text)
            title=html.unescape(m.group(1)).strip() if m else ""
            return (code,"live" if title else "dead",title,round(dt,2))
        return (code,f"http{r.status_code}","",round(dt,2))
    except Exception as e:
        return (code,"transport",repr(e)[:80],round(time.time()-t0,2))
# warmup: one check first (sequential) to open the pool
w=check(next(iter(cands)))
print("WARMUP",w,flush=True)
results={}
with ThreadPoolExecutor(max_workers=8) as ex:
    for i,res in enumerate(ex.map(check,list(cands.keys()))):
        results[res[0]]=res
        if (i+1)%100==0: print(f"RECHECKED {i+1}/{len(cands)}",flush=True)
mismatch_live=[]  # orig dead, session live
mismatch_dead=[]  # orig live, session dead
transport=[]
for code,(c,st,title,dt) in results.items():
    orig="live" if code in live_codes else "dead"
    if st=="transport": transport.append(code)
    elif st=="live" and orig=="dead": mismatch_live.append((code,title))
    elif st=="dead" and orig=="live": mismatch_dead.append(code)
print(f"SESSION_SUMMARY live={sum(1 for r in results.values() if r[1]=='live')} dead={sum(1 for r in results.values() if r[1]=='dead')} transport={len(transport)}",flush=True)
for code,title in mismatch_live:
    print("MISMATCH_DEAD_TO_LIVE "+json.dumps({"code":code,"title":title,"invite":f"https://chat.whatsapp.com/{code}"},ensure_ascii=False),flush=True)
for code in mismatch_dead:
    print("MISMATCH_LIVE_TO_DEAD "+json.dumps({"code":code,"invite":f"https://chat.whatsapp.com/{code}"},ensure_ascii=False),flush=True)
for code in transport:
    print("TRANSPORT_FAIL "+code,flush=True)
# timing sample
dts=[r[3] for r in results.values()]
dts.sort()
print("TIMING median_s=",dts[len(dts)//2],"p90_s=",dts[int(len(dts)*0.9)],"max_s=",dts[-1],flush=True)
print("RECHECK_DONE",flush=True)
