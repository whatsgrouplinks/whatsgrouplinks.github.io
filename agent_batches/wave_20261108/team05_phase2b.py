import json, re, requests, html
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
CODE_RE=re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")
def sess():
    s=requests.Session(); s.headers.update(UA); return s
S=sess()
cands=[]; seen=set()
def add(code,name,cat,country,listing,desc=""):
    code=(code or "").strip()
    if len(code)!=22 or code in seen: return False
    seen.add(code)
    cands.append({"code":code,"name":(name or "").strip()[:120],"category":cat or "","country":country or "International","listing":listing,"desc":(desc or "")[:300]})
    return True
def clean(t):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",t or ""))).strip()
# phase1
p1=json.load(open(BASE+"team05_phase1.json"))
for c in p1["cands"]: add(c["code"],c.get("name") or "",c.get("category") or "",c.get("country") or "International",c["listing"])
print("phase1:",len(cands), flush=True)
# groupssor
r=S.get("https://groupssor-api.blog-99n.workers.dev/api/groups",timeout=30)
j=json.loads(r.text); items=j if isinstance(j,list) else j.get("groups",[])
n=0
for it in items:
    if not isinstance(it,dict) or it.get("platform")!="whatsapp": continue
    m=CODE_RE.search(it.get("inviteLink") or "")
    if m and add(m.group(1), it.get("name") or "", it.get("category") or "", it.get("country") or "International","https://groupssor-api.blog-99n.workers.dev/api/groups", it.get("description") or ""): n+=1
print("groupssor:",n,"total",len(cands), flush=True)
# linkado
ids=json.load(open(BASE+"team05_linkado_ids.json"))
def fetch_linkado(gid):
    s=sess()
    try:
        r=s.get(f"https://linkado.app/grupo/{gid}",headers={"RSC":"1"},timeout=25)
        txt=r.content.decode("utf-8",errors="ignore")
        m=CODE_RE.search(txt)
        if not m: return None
        dm=re.search(r"Grupo de WhatsApp ([^,]{3,100}), na categoria",txt)
        name=dm.group(1) if dm else ""
        catm=re.search(r"na categoria ([A-Za-zÀ-ÿ &\-]{3,40})",txt)
        return {"code":m.group(1),"name":clean(name),"category":catm.group(1) if catm else "","country":"BR","listing":f"https://linkado.app/grupo/{gid}"}
    except Exception: return None
n=0
with ThreadPoolExecutor(max_workers=4) as ex:
    for fut in as_completed([ex.submit(fetch_linkado,g) for g in ids]):
        res=fut.result()
        if res and add(res["code"],res["name"],res["category"],res["country"],res["listing"]): n+=1
print("linkado:",n,"total",len(cands), flush=True)
# igrupos from saved results
ig_res=json.load(open(BASE+"team05_igrupos_res.json"))
n=0
for res in ig_res:
    if res.get("code") and add(res["code"],res.get("title",""),"","International",f"https://www.igrupos.com/grupo/{res['gid']}"): n+=1
print("igrupos:",n,"total",len(cands), flush=True)
# groupsinvite first 60 detail links
gi_links=json.load(open(BASE+"team05_gi_links.json"))
def fetch_gi(u):
    s=sess()
    try:
        r=s.get(u,timeout=15); txt=r.text
        m=CODE_RE.search(txt)
        t=re.search(r"<title>([^<]{3,150})</title>",txt)
        return {"url":u,"code":m.group(1) if m else None,"title":clean(t.group(1)) if t else ""}
    except Exception: return {"url":u,"code":None,"title":""}
n=0
with ThreadPoolExecutor(max_workers=5) as ex:
    for fut in as_completed([ex.submit(fetch_gi,u) for u in gi_links[:60]]):
        res=fut.result()
        if res.get("code") and add(res["code"],res.get("title",""),"","International",res["url"]): n+=1
print("groupsinvite:",n,"total",len(cands), flush=True)
# linkado category p2 leads: extract slugs from categorias page
leads=[]
try:
    r=S.get("https://linkado.app/categorias",timeout=30)
    slugs=sorted(set(re.findall(r"/categoria/([a-z0-9\-]+)", r.text)))
    for s in slugs:
        leads.append({"url":f"https://linkado.app/categoria/{s}?page=2","source":"linkado-categoria-p2"})
    print("linkado cats:",len(slugs), flush=True)
except Exception as e: print("cats err",e)
for tag in ["negocios","free-fire","musica","futbol"]:
    leads.append({"url":f"https://www.igrupos.com/tag/whatsapp/{tag}/2","source":"igrupos-tag-p2"})
leads.append({"url":"https://groupizo.com/sitemaps/sitemap-groups-1.xml","source":"groupizo-sitemap-browser-leg"})
json.dump(leads, open(BASE+"team05-leads-harvest-e-leads.json","w"), ensure_ascii=False, indent=1)
json.dump(cands, open(BASE+"team05_phase2.json","w"))
print("PHASE2B total cands:",len(cands),"leads:",len(leads))
