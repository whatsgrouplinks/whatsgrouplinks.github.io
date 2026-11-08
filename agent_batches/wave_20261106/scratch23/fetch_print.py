import requests, re, json, os, time
from concurrent.futures import ThreadPoolExecutor
S=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
CODE_RE=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')
posts=json.load(open(os.path.join(S,"gd_posts.json")))
posts.sort(key=lambda p:(p[2],p[1]))
print("POSTS",len(posts),flush=True)
def fetch(p):
    url,cat,pg=p
    for i in range(3):
        try:
            r=requests.get(url,headers=UA,timeout=60)
            if r.status_code==200:
                t=r.text
                title=re.search(r'<title>(.*?)</title>',t,re.S)
                title=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',title.group(1))).strip() if title else ""
                codes=sorted(set(CODE_RE.findall(t)))
                return {"src":url,"cat":cat,"title":title,"codes":codes}
            if r.status_code in (429,500,502,503,504): time.sleep(10); continue
            return {"src":url,"cat":cat,"title":"","codes":[]}
        except Exception:
            time.sleep(8)
    return {"src":url,"cat":cat,"title":"","codes":[]}
total=0
with ThreadPoolExecutor(max_workers=10) as ex:
    for i,res in enumerate(ex.map(fetch,posts)):
        total+=len(res["codes"])
        print("POSTLINE "+json.dumps(res,ensure_ascii=False),flush=True)
        if (i+1)%20==0: print(f"PROGRESS {i+1}/{len(posts)} codes={total}",flush=True)
print(f"FETCHDONE posts={len(posts)} codes={total}",flush=True)
