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
items=[]
def save(): json.dump(items,open(os.path.join(S,"pk_html_raw.json"),"w"))
def harvest_text(t, cat, cty, src):
    n0=len(items)
    for m in re.finditer(r'<strong>([^<]{3,120})</strong>.*?(?:chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,}))', t, flags=re.S):
        items.append({"code":m.group(2),"name_hint":re.sub(r'\s+',' ',m.group(1)).strip(),"cat_hint":cat,"country_hint":cty,"src":src})
    have={i["code"] for i in items}
    for code in set(CODE_RE.findall(t)):
        if code not in have:
            items.append({"code":code,"name_hint":"","cat_hint":cat,"country_hint":cty,"src":src})
    return len(items)-n0
PAGES=[("https://groupda.pk/","pk-home","PK"),
 ("https://groupda.pk/category/girls-groups/","girls",""),
 ("https://groupda.pk/category/indian-groups/","indian","IN"),
 ("https://groupda.pk/category/pakistani-groups/","pakistani","PK"),
 ("https://groupda.pk/group-whatsapp-link/","pk-list",""),
 ("https://groupda.pk/whatsapp-group-links-india/","pk-india","IN")]
for base,cat,cty in PAGES:
    r=get(base)
    if r is None or r.status_code!=200:
        print("STOP",base,flush=True); continue
    print(base,"+",harvest_text(r.text,cat,cty,base),"total",len(items),flush=True); save()
    for pg in range(2,21):
        url=base.rstrip('/')+f"/page/{pg}/"
        r=get(url)
        if r is None or r.status_code!=200:
            print("no more pages at",url,flush=True); break
        if not CODE_RE.search(r.text):
            print("empty page",url,flush=True); break
        print(url,"+",harvest_text(r.text,cat,cty,url),"total",len(items),flush=True); save()
        time.sleep(2)
print("PK HTML DONE items:",len(items),flush=True)
