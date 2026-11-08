import json, subprocess, time, urllib.parse, concurrent.futures, os
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OUT="team14_tag_probe.json"
res={}
if os.path.exists(OUT):
    try: res=json.load(open(OUT))
    except: res={}
def total(tag):
    url="https://api.groupjoin.link/groups?tag="+urllib.parse.quote(tag)+"&page=1&limit=1&safeSearch=blur"
    t0=time.time()
    try:
        r=subprocess.run(["curl","-s","--max-time","45","-A",UA,url],capture_output=True,text=True,timeout=50)
        d=json.loads(r.stdout)
        return tag, d.get("total"), d.get("totalPages"), round(time.time()-t0,1)
    except Exception as e:
        return tag, "ERR", None, round(time.time()-t0,1)
cands=["music","movies","cricket","football","study","quran","poetry","shayari","recipes","cooking",
"travel","photography","books","crypto","forex","freelancing","pubg","free-fire","ludo","love","status",
"quotes","motivation","fitness","beauty","makeup","mobile","cars","property","lahore","karachi",
"islamabad","dubai","malaysia","nepal","kenya","exams","ielts","scholarships","online-earning",
"punjabi","sindhi","pashto","sad-poetry","romantic","css","nursing","students","university","food",
"wedding","rishta","islamic","ramadan","english","hindi","tamil",
"funny","health","entertainment","videos","bangladesh","science","indonesia","girls","earning","pakistan"]
todo=[c for c in cands if c not in res]
print("todo:",len(todo),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    futs={ex.submit(total,t):t for t in todo}
    for fut in concurrent.futures.as_completed(futs):
        tag,tot,pages,dt=fut.result()
        res[tag]=[tot,pages]
        print(f"{tag:20} total={tot} pages={pages} ({dt}s)",flush=True)
        json.dump(res,open(OUT,"w"),indent=1)
print("DONE",len(res),flush=True)
