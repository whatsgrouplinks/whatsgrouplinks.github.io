import json, re, time, requests, html
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
CODE_RE=re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")
def sess():
    s=requests.Session(); s.headers.update(UA); return s
S=sess()
cands=[]
seen=set()
def add(code,name,cat,country,listing,desc=""):
    code=(code or "").strip()
    if len(code)!=22 or code in seen: return False
    seen.add(code)
    cands.append({"code":code,"name":(name or "").strip()[:120],"category":cat or "","country":country or "International","listing":listing,"desc":(desc or "")[:300]})
    return True
def clean(t):
    t=html.unescape(re.sub(r"<[^>]+>"," ",t or ""))
    t=re.sub(r"\s+"," ",t).strip()
    return t
# ---- groupssor (inviteLink field) ----
try:
    r=S.get("https://groupssor-api.blog-99n.workers.dev/api/groups",timeout=30)
    j=json.loads(r.text); items=j if isinstance(j,list) else j.get("groups",[])
    n=0
    for it in items:
        if not isinstance(it,dict) or it.get("platform")!="whatsapp": continue
        m=CODE_RE.search(it.get("inviteLink") or "")
        if m and add(m.group(1), it.get("name") or "", it.get("category") or "", it.get("country") or "International","https://groupssor-api.blog-99n.workers.dev/api/groups", it.get("description") or ""): n+=1
    print("groupssor added",n, flush=True)
except Exception as e: print("groupssor err",e, flush=True)
# ---- name-context re-parse for phase1 code pages ----
p1=json.load(open(BASE+"team05_phase1.json"))
by_listing={}
for c in p1["cands"]: by_listing.setdefault(c["listing"],[]).append(c["code"])
for url, codes in by_listing.items():
    if "whatsgroupslinkspk" not in url and "appgrouplink" not in url and "whatsappkanali" not in url: continue
    try:
        r=S.get(url,timeout=30)
        if r.status_code!=200: continue
        txt=r.text
        for code in codes:
            idx=txt.find(code)
            if idx<0: continue
            window=clean(txt[max(0,idx-1500):idx])
            # name = last 2-4 words-ish chunk; take tail after last '>'-ish separator
            tail=window[-160:]
            # try h-tag titles in window
            names=re.findall(r"(?:Join|WhatsApp Group|Group Link)[^|<\n]{0,80}", window)
            nm = names[-1] if names else tail
            nm=re.sub(r"^(Join|WhatsApp Group Link|Group Link)\s*","",nm).strip(" -|")
            for c in p1["cands"]:
                if c["code"]==code and c["listing"]==url and not c["name"]:
                    c["name"]=nm[:120]
        print("name-context",url,"ok", flush=True)
    except Exception as e: print("name-context err",url,e, flush=True)
# merge phase1 cands (with names filled) into cands
for c in p1["cands"]:
    add(c["code"],c.get("name") or "",c.get("category") or "",c.get("country") or "International",c["listing"])
print("after phase1 merge:",len(cands), flush=True)
# ---- linkado grupo pages ----
ids=json.load(open(BASE+"team05_linkado_ids.json"))
def fetch_linkado(gid):
    s=sess()
    try:
        r=s.get(f"https://linkado.app/grupo/{gid}",headers={"RSC":"1"},timeout=25)
        txt=r.content.decode("utf-8",errors="ignore")
        m=CODE_RE.search(txt)
        if not m: return None
        # og:description 'Grupo de WhatsApp <NAME>, na categoria <PT>'
        dm=re.search(r"Grupo de WhatsApp ([^,]{3,100}), na categoria",txt)
        name=dm.group(1) if dm else ""
        if not name:
            t=re.search(r"<title>([^<]{3,120})</title>",txt); name=t.group(1) if t else ""
        catm=re.search(r"na categoria ([A-Za-zÀ-ÿ &\-]{3,40})",txt)
        return {"code":m.group(1),"name":clean(name),"category":catm.group(1) if catm else "","country":"BR","listing":f"https://linkado.app/grupo/{gid}"}
    except Exception: return None
n=0
with ThreadPoolExecutor(max_workers=4) as ex:
    for fut in as_completed([ex.submit(fetch_linkado,g) for g in ids]):
        res=fut.result()
        if res and add(res["code"],res["name"],res["category"],res["country"],res["listing"]): n+=1
print("linkado added",n,"total",len(cands), flush=True)
# ---- igrupos tag pages -> grupo ids -> grupo pages ----
ig_ids=[]
for u in ["https://www.igrupos.com/tag/whatsapp/amistad","https://www.igrupos.com/tag/whatsapp/negocios","https://www.igrupos.com/tag/whatsapp/free-fire","https://www.igrupos.com/tag/whatsapp/musica","https://www.igrupos.com/tag/whatsapp/futbol"]:
    try:
        r=S.get(u,timeout=30)
        for g in re.findall(r"grupo/(\d{6})",r.text):
            if g not in ig_ids: ig_ids.append(g)
    except Exception as e: print("igrupos tag err",u,e)
print("igrupos ids:",len(ig_ids), ig_ids, flush=True)
json.dump(ig_ids, open(BASE+"team05_igrupos_ids.json","w"))
def fetch_igrupos(gid):
    s=sess()
    try:
        r=s.get(f"https://www.igrupos.com/grupo/{gid}",timeout=25)
        txt=r.text
        m=CODE_RE.search(txt)
        t=re.search(r"<title>([^<]{3,150})</title>",txt)
        return {"gid":gid,"code":m.group(1) if m else None,"title":clean(t.group(1)) if t else "","has_chat": "chat.whatsapp.com" in txt}
    except Exception as e: return {"gid":gid,"code":None,"title":"","err":str(e)}
ig_res=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for fut in as_completed([ex.submit(fetch_igrupos,g) for g in ig_ids]):
        ig_res.append(fut.result())
json.dump(ig_res, open(BASE+"team05_igrupos_res.json","w"))
n=0
for res in ig_res:
    if res.get("code") and add(res["code"],res.get("title",""),"","International",f"https://www.igrupos.com/grupo/{res['gid']}"): n+=1
print("igrupos added",n,"with chat link:",sum(1 for r in ig_res if r.get("has_chat")),"total",len(cands), flush=True)
# ---- groupsinvite detail pages ----
gi_links=[]
for u in ["https://groupsinvite.link/group/category/education-study-learning/","https://groupsinvite.link/group/country/pakistan/"]:
    try:
        r=S.get(u,timeout=30)
        for slug in re.findall(r'href="(https://groupsinvite\.link/group/[^"]+/)"',r.text):
            if slug not in gi_links: gi_links.append(slug)
    except Exception as e: print("gi err",e)
print("groupsinvite detail links:",len(gi_links), flush=True)
json.dump(gi_links, open(BASE+"team05_gi_links.json","w"))
def fetch_gi(u):
    s=sess()
    try:
        r=s.get(u,timeout=25); txt=r.text
        m=CODE_RE.search(txt)
        t=re.search(r"<title>([^<]{3,150})</title>",txt)
        return {"url":u,"code":m.group(1) if m else None,"title":clean(t.group(1)) if t else ""}
    except Exception: return {"url":u,"code":None,"title":""}
n=0
with ThreadPoolExecutor(max_workers=3) as ex:
    for fut in as_completed([ex.submit(fetch_gi,u) for u in gi_links[:60]]):
        res=fut.result()
        if res.get("code") and add(res["code"],res.get("title",""),"","International",res["url"]): n+=1
print("groupsinvite added",n,"total",len(cands), flush=True)
# ---- groupizo Oct pages ----
oct_entries=json.load(open(BASE+"team05_groupizo_oct.json"))
print("groupizo Oct to fetch:",len(oct_entries), flush=True)
def fetch_gz(entry):
    url,lm=entry
    s=sess()
    try:
        r=s.get(url,timeout=20)
        if r.status_code!=200: return None
        txt=r.text
        m=CODE_RE.search(txt)
        if not m: return None
        og=re.search(r'property="og:title" content="([^"]{3,150})"',txt)
        name=og.group(1) if og else ""
        if not name:
            t=re.search(r"<title>([^<]{3,150})</title>",txt); name=t.group(1) if t else ""
        return {"code":m.group(1),"name":clean(name),"category":"","country":"International","listing":url}
    except Exception: return None
gz_n=0; gz_done=0
with ThreadPoolExecutor(max_workers=5) as ex:
    futs={ex.submit(fetch_gz,e):e for e in oct_entries}
    for fut in as_completed(futs):
        gz_done+=1
        res=fut.result()
        if res and add(res["code"],res["name"],res["category"],res["country"],res["listing"]): gz_n+=1
        if gz_done%200==0:
            print(f"groupizo progress {gz_done}/{len(oct_entries)} added {gz_n} total {len(cands)}", flush=True)
            json.dump(cands, open(BASE+"team05_phase2_partial.json","w"))
print("groupizo added",gz_n,"total",len(cands), flush=True)
json.dump(cands, open(BASE+"team05_phase2.json","w"))
print("PHASE2 total cands:",len(cands))
