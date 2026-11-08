import requests, re, json, os, time
from concurrent.futures import ThreadPoolExecutor
S=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
CODE_RE=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')
posts=json.load(open(os.path.join(S,"gd_posts.json")))
print("posts to fetch:",len(posts),flush=True)
out=[]; done=set()
if os.path.exists(os.path.join(S,"gd_post_codes.json")):
    out=json.load(open(os.path.join(S,"gd_post_codes.json"))); done={o["src"] for o in out}
    print("resuming, already have",len(out),flush=True)
def fetch(p):
    url,cat,pg=p
    if url in done: return []
    for i in range(3):
        try:
            r=requests.get(url,headers=UA,timeout=60)
            if r.status_code==200:
                t=r.text
                title=re.search(r'<title>(.*?)</title>',t,re.S)
                title=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',title.group(1))).strip() if title else ""
                codes=set(CODE_RE.findall(t))
                return [{"code":c,"name_hint":title,"cat_hint":cat,"country_hint":"","src":url} for c in codes]
            if r.status_code in (429,500,502,503,504): time.sleep(10); continue
            return []
        except Exception as e:
            time.sleep(8)
    return []
todo=[p for p in posts if p[0] not in done]
todo.sort(key=lambda p:(p[2],p[1]))  # newest first: page 1 of every category before deeper pages
print("todo:",len(todo),flush=True)
with ThreadPoolExecutor(max_workers=6) as ex:
    for i,res in enumerate(ex.map(fetch,todo)):
        out.extend(res)
        if (i+1)%25==0:
            json.dump(out,open(os.path.join(S,"gd_post_codes.json"),"w"))
            print(f"fetched {i+1}/{len(todo)} posts, codes {len(out)}",flush=True)
json.dump(out,open(os.path.join(S,"gd_post_codes.json"),"w"))
print("DONE codes:",len(out),flush=True)
