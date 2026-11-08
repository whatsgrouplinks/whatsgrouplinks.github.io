import json, subprocess
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def get(url):
    r=subprocess.run(["curl","-s","--max-time","60","-A",UA,url],capture_output=True,text=True,timeout=70)
    try:
        d=json.loads(r.stdout); return d
    except Exception as e:
        print(url,"parse fail",r.stdout[:200]); return None
for url in [
 "https://api.groupjoin.link/tags?limit=500",
 "https://api.groupjoin.link/tags?page=2&limit=20",
 "https://api.groupjoin.link/tags?limit=100&page=1",
]:
    d=get(url)
    if d:
        print(url,"-> keys",list(d.keys()),"n=",len(d.get("data",[])))
        for t in d.get("data",[])[:5]: print("   ",t)
        if len(d.get("data",[]))>5: print("   ... last:", d["data"][-1])
