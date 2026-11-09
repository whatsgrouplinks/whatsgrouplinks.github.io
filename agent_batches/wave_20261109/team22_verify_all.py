import subprocess, re, json, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor
WD = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
fresh1 = json.load(open(os.path.join(WD,"team22_fresh.json")))
fresh2 = json.load(open(os.path.join(WD,"team22_fresh2.json")))
allfresh = dict(fresh1); allfresh.update(fresh2)
out = os.path.join(WD,"team22_verify_results.json")
results = json.load(open(out)) if os.path.exists(out) else {}
lock = threading.Lock()
def check(code):
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","10","-A",UA,"-w","\n__HTTP__:%{http_code}",f"https://chat.whatsapp.com/{code}"], capture_output=True, text=True, timeout=15)
        m = re.search(r"__HTTP__:(\d+)", r.stdout or "")
        status = int(m.group(1)) if m else 0
        body = r.stdout or ""
    except Exception as e:
        return {"code":code,"status":0,"title":"","desc":"","error":str(e)}
    title=""
    tm = re.search(r'og:title" content="([^"]*)"', body)
    if tm: title = html.unescape(tm.group(1)).strip()
    desc=""
    dm = re.search(r'og:description" content="([^"]*)"', body)
    if dm: desc = html.unescape(dm.group(1)).strip()
    return {"code":code,"status":status,"title":title,"desc":desc}
def work(code):
    with lock:
        if code in results: return
    res = check(code)
    tries=1
    while (res["status"]==0 or (res["status"]==200 and not res["title"])) and tries<3:
        time.sleep(2)
        res=check(code); tries+=1
    res["tries"]=tries
    res["hint"]=allfresh[code].get("name_hint","")
    res["sources"]=allfresh[code].get("sources",[])
    with lock:
        results[code]=res
        json.dump(results, open(out,"w"), indent=1, ensure_ascii=False)
        live = sum(1 for v in results.values() if v.get("title"))
        print(f"{len(results)}/{len(allfresh)} live={live} {code} {res['status']} {res['title'][:50]!r}", flush=True)
    time.sleep(0.7)
allfresh["EqR1KiR6wYg8L1jVAmCrKH"]={"name_hint":"WhatsApp Music Group","sources":["https://www.youtube.com/shorts/rCO8X5pl4EE"]}
# batch2 (slice-specific pages first by insertion order) before batch1 remainder
todo=[c for c in list(fresh2.keys())+list(fresh1.keys())+["EqR1KiR6wYg8L1jVAmCrKH"] if c not in results]
todo=list(dict.fromkeys(todo))
print("total fresh:", len(allfresh), "already verified:", len(results), "todo:", len(todo), flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
print("DONE", len(results), "live:", sum(1 for v in results.values() if v.get("title")))
