import requests, re, json, os, time
from concurrent.futures import ThreadPoolExecutor
S=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
CODE_RE=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')
OUT=os.path.join(S,"gd_post_codes_v2.json")
def safe_write(path, data):
    txt=json.dumps(data)
    for i in range(30):
        tmp=path+f".tmp{i%5}"
        try:
            with open(tmp,"w") as f: f.write(txt)
            os.replace(tmp,path)
            return True
        except Exception as e:
            time.sleep(2)
    print("SAFE_WRITE FAILED",path,flush=True)
    return False
posts=json.load(open(os.path.join(S,"gd_posts.json")))
print("posts to fetch:",len(posts),flush=True)
out=[]
if os.path.exists(OUT) and os.path.getsize(OUT)>10:
    try:
        out=json.load(open(OUT)); print("resuming, already have",len(out),flush=True)
    except Exception: out=[]
done={o["src"] for o in out}
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
print("todo:",len(todo),flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for i,res in enumerate(ex.map(fetch,todo)):
        out.extend(res)
        if (i+1)%10==0:
            safe_write(OUT,out)
            print(f"fetched {i+1}/{len(todo)} posts, codes {len(out)}",flush=True)
safe_write(OUT,out)
print("DONE codes:",len(out),flush=True)
