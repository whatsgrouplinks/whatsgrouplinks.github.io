import json, re, time, requests, html
from urllib.parse import urljoin
BASE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
S=requests.Session(); S.headers.update(UA)
def get(url,timeout=25):
    try:
        r=S.get(url,timeout=timeout); return r.status_code, r.text
    except Exception as e:
        return None, str(e)
leads=json.load(open(BASE+"leads_slice_05.json"))
print("leads",len(leads))
cands=[]  # dict code,name,cat,country,listing
seen=set()
def add(code,name,cat,country,listing):
    code=code.strip()
    if len(code)!=22: return
    if code in seen: return
    seen.add(code)
    cands.append({"code":code,"name":(name or "").strip()[:120],"category":cat or "","country":country or "International","listing":listing})
CODE_RE=re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{22})")
INV_RE=re.compile(r"chat\.whatsapp\.com/invite/([A-Za-z0-9]{22})")

attempted=[]
# --- groupizo sitemaps ---
groupizo_oct=[]
for i in range(1,12):
    u=f"https://groupizo.com/sitemaps/sitemap-groups-{i}.xml"
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0))
    print("groupizo sitemap",i,st,len(txt) if txt else 0, flush=True)
    if st==200:
        for m in re.finditer(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>",txt):
            loc,lm=m.groups()
            if lm.startswith("2026-10"):
                groupizo_oct.append((loc,lm))
print("groupizo Oct entries:",len(groupizo_oct), flush=True)
json.dump(groupizo_oct, open(BASE+"team05_groupizo_oct.json","w"))
# --- groupssor API ---
st,txt=get("https://groupssor-api.blog-99n.workers.dev/api/groups")
attempted.append(("groupssor-api",st,len(txt) if txt else 0)); print("groupssor",st,len(txt) if txt else 0, flush=True)
if st==200:
    try:
        j=json.loads(txt)
        items=j if isinstance(j,list) else j.get("groups",j.get("data",[]))
        print(" groupssor items",len(items))
        for it in items if isinstance(items,list) else []:
            if not isinstance(it,dict): continue
            inv=it.get("invite") or it.get("link") or it.get("url") or ""
            m=CODE_RE.search(inv) or INV_RE.search(inv)
            if m: add(m.group(1), it.get("name") or it.get("title") or "", it.get("category") or "", it.get("country") or "International","https://groupssor-api.blog-99n.workers.dev/api/groups")
    except Exception as e: print(" groupssor parse err",e)
# --- grupbul ---
grupbul_cats=[("https://grupbul.com/en/category/whatsapp/49/earning-money","Online Earning"),("https://grupbul.com/en/category/whatsapp/27/other","Community & Social"),("https://grupbul.com/en/category/whatsapp/5/game","Gaming"),("https://grupbul.com/en/category/whatsapp/1/x","Community & Social")]
for u,cat in grupbul_cats:
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0)); print("grupbul",u,st,len(txt) if txt else 0, flush=True)
    if st==200:
        for m in CODE_RE.finditer(txt): add(m.group(1),"",cat,"International",u)
        for m in INV_RE.finditer(txt): add(m.group(1),"",cat,"International",u)
# --- linkado listings ---
linkado_ids=[]
for u in ["https://linkado.app/?page=4","https://linkado.app/?page=5","https://linkado.app/?page=6","https://linkado.app/categoria/amizade?page=2","https://linkado.app/categorias"]:
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0)); print("linkado",u,st,len(txt) if txt else 0, flush=True)
    if st==200:
        for m in re.finditer(r"/grupo/([0-9a-f]{24})",txt):
            if m.group(1) not in linkado_ids: linkado_ids.append(m.group(1))
print("linkado grupo ids:",len(linkado_ids), flush=True)
json.dump(linkado_ids, open(BASE+"team05_linkado_ids.json","w"))
# --- whatsappkanali ---
for u in ["https://whatsappkanali.com/?page=4","https://whatsappkanali.com/kategori/sohbet?page=2","https://whatsappkanali.com/kategori/is-ilanlari?page=2","https://whatsappkanali.com/kategori/egitim?page=2","https://whatsappkanali.com/kategori/oyun?page=3"]:
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0)); print("wk",u,st,len(txt) if txt else 0, flush=True)
    if st==200:
        for m in CODE_RE.finditer(txt): add(m.group(1),"","Community & Social","TR",u)
# --- igrupos tags ---
for u in ["https://www.igrupos.com/tag/whatsapp/amistad","https://www.igrupos.com/tag/whatsapp/negocios","https://www.igrupos.com/tag/whatsapp/free-fire","https://www.igrupos.com/tag/whatsapp/musica","https://www.igrupos.com/tag/whatsapp/futbol"]:
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0)); print("igrupos",u,st,len(txt) if txt else 0, flush=True)
    if st==200:
        gids=sorted(set(int(x) for x in re.findall(r"/grupo/(\d+)",txt)))
        print("  gids",len(gids),"max",max(gids) if gids else None, gids[-5:] if gids else [])
        for m in CODE_RE.finditer(txt): add(m.group(1),"","","International",u)
# --- appgrouplink / whtsagrouplinks / wagrouplink / groupchatconnect ---
for u,cat in [("https://appgrouplink.com/scholarship-whatsapp-group-links/","Scholarship"),("https://appgrouplink.com/medical-whatsapp-group-links/","Health"),
 ("https://www.whtsagrouplinks.com/news-whatsapp-group-links/","News"),("https://www.whtsagrouplinks.com/students-whatsapp-group-links/","Education"),("https://www.whtsagrouplinks.com/study/","Education"),("https://www.whtsagrouplinks.com/travel-whatsapp-group-links/","Travel"),("https://www.whtsagrouplinks.com/shayari-whatsapp-group-links/","Poetry"),("https://www.whtsagrouplinks.com/urdu-poetry-whatsapp-group-links/","Poetry"),("https://www.whtsagrouplinks.com/love-and-romance-whatsapp-group-links/","Friendship"),
 ("https://wagrouplink.com/indian/","Community & Social"),("https://wagrouplink.com/ipl/","Sports"),("https://wagrouplink.com/business/","Business"),("https://whatsgroupslinkspk.com/poetry-whatsapp-group-links/","Poetry"),
 ("https://groupchatconnect.info/groupe/2959","Community & Social"),("https://groupchatconnect.info/groupe/3028","Community & Social"),("https://groupchatconnect.info/groupe/3060","Community & Social"),("https://groupchatconnect.info/groupe/3067","Community & Social"),
 ("https://groupsinvite.link/group/category/education-study-learning/","Education"),("https://groupsinvite.link/group/country/pakistan/","Community & Social")]:
    st,txt=get(u); attempted.append((u,st,len(txt) if txt else 0)); print("misc",u,st,len(txt) if txt else 0, flush=True)
    if st==200 and txt:
        # extract codes with nearby name context: look for title tags
        for m in CODE_RE.finditer(txt): add(m.group(1),"",cat,"International",u)
        for m in INV_RE.finditer(txt): add(m.group(1),"",cat,"International",u)
# --- groupjoin API (known stale, one quick check) ---
for tag in ["dubbed-movies","hindi-movies"]:
    u=f"https://api.groupjoin.link/groups?tag={tag}&page=1&limit=20&safeSearch=blur"
    st,txt=get(u,timeout=15); attempted.append((u,st,len(txt) if txt else 0)); print("groupjoin",tag,st,len(txt) if txt else 0, flush=True)
json.dump({"attempted":attempted,"cands":cands}, open(BASE+"team05_phase1.json","w"))
print("PHASE1 cands:",len(cands))
