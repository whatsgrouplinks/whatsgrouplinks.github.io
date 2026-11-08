import requests, re, json, os, time
S=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
def get(url, timeout=60, tries=4):
    for i in range(tries):
        try:
            r=requests.get(url,headers=UA,timeout=timeout)
            if r.status_code==200: return r
            print("  HTTP",r.status_code,url,flush=True)
            if r.status_code in (429,500,502,503,504): time.sleep(15); continue
            return r
        except Exception as e:
            print("  ERR",repr(e)[:100],url,flush=True); time.sleep(10)
    return None
CODE_RE=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')
# Phase A: groupda.com category pages 1-3 only (newest posts; full WP-API crawl was already exhausted by prior team)
CATS=["business","buysell","dating","education","games","matrimonial","study"]
posts=[]; seen=set()
for cat in CATS:
    for page in (1,2,3):
        url=f"https://groupda.com/category/{cat}/" if page==1 else f"https://groupda.com/category/{cat}/page/{page}/"
        r=get(url)
        if r is None or r.status_code!=200:
            print(f"STOP cat {cat} page {page}",flush=True); break
        links=sorted(set(re.findall(r'href="(https://groupda\.com/'+re.escape(cat)+r'/[^"]+/)"',r.text)))
        pl=[l for l in links if not l.endswith('/feed/') and '/page/' not in l and l!=f"https://groupda.com/category/{cat}/"]
        new=[l for l in pl if l not in seen]
        print(f"cat {cat} page {page}: {len(pl)} posts ({len(new)} new)",flush=True)
        for l in new: seen.add(l); posts.append((l,cat,page))
        json.dump(posts,open(os.path.join(S,"gd_posts.json"),"w"))
        time.sleep(2)
print("TOTAL groupda.com posts (p1-3):",len(posts),flush=True)
# Phase B: groupda.pk WP-API
pk_items=[]
def add_code(code, name_hint="", cat_hint="", country_hint="", src=""):
    pk_items.append({"code":code,"name_hint":name_hint,"cat_hint":cat_hint,"country_hint":country_hint,"src":src})
r=get("https://groupda.pk/wp-json/wp/v2/categories?per_page=100")
pk_cats={}
if r is not None and r.status_code==200:
    for c in r.json(): pk_cats[c["id"]]=c["slug"]
    print("pk cats:",pk_cats,flush=True)
json.dump(pk_cats,open(os.path.join(S,"pk_cats.json"),"w"))
page=1; total_pages=None
while True:
    r=get(f"https://groupda.pk/wp-json/wp/v2/posts?per_page=100&page={page}&orderby=modified&order=desc")
    if r is None or r.status_code!=200:
        print("pk posts stop page",page,flush=True); break
    if total_pages is None:
        total_pages=int(r.headers.get("X-WP-TotalPages","1")); print("pk total posts:",r.headers.get("X-WP-Total"),"pages:",total_pages,flush=True)
    data=r.json()
    if not data: break
    for p in data:
        title=re.sub(r'<[^>]+>','',p.get("title",{}).get("rendered","")).strip()
        content=p.get("content",{}).get("rendered","")
        cats=[pk_cats.get(i,"") for i in p.get("categories",[])]
        for code in set(CODE_RE.findall(content)):
            add_code(code, title, ",".join(cats), "", p.get("link",""))
    print(f"pk posts page {page}/{total_pages}: cumulative codes {len(pk_items)}",flush=True)
    json.dump(pk_items,open(os.path.join(S,"pk_api_raw.json"),"w"))
    if page>=total_pages: break
    page+=1; time.sleep(1)
print("pk api codes:",len(pk_items),flush=True)
print("HARVEST DONE",flush=True)
