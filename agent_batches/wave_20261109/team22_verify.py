import subprocess, re, json, os, time, html
WD = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
fresh = json.load(open(os.path.join(WD,"team22_fresh.json")))
codes = list(fresh.keys())
out = os.path.join(WD,"team22_verify_results.json")
results = {}
if os.path.exists(out):
    results = json.load(open(out))
def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","25","-A",UA,"-w","\n__HTTP__:%{http_code}","-o","/tmp/t22_body.html",url], capture_output=True, text=True, timeout=40)
        m = re.search(r"__HTTP__:(\d+)", r.stdout or "")
        status = int(m.group(1)) if m else 0
        body = open("/tmp/t22_body.html", encoding="utf-8", errors="ignore").read() if os.path.exists("/tmp/t22_body.html") else ""
    except Exception as e:
        return {"code":code,"status":0,"title":"","desc":"","error":str(e)}
    title = ""
    tm = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', body, re.I)
    if not tm:
        tm = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', body, re.I)
    if tm: title = html.unescape(tm.group(1)).strip()
    desc = ""
    dm = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)', body, re.I)
    if not dm:
        dm = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:description["\']', body, re.I)
    if dm: desc = html.unescape(dm.group(1)).strip()
    return {"code":code,"status":status,"title":title,"desc":desc}
todo = [c for c in codes if c not in results]
print("to check:", len(todo), "already:", len(results))
for i, code in enumerate(todo):
    res = check(code)
    # retry ambiguous: 200 + empty title, up to 2 more times spaced apart
    tries = 1
    while res["status"]==200 and not res["title"] and tries < 3:
        time.sleep(3)
        res = check(code)
        tries += 1
    res["tries"]=tries
    res["hint"]=fresh[code].get("name_hint","")
    res["sources"]=fresh[code].get("sources",[])
    results[code]=res
    print(i+1, code, res["status"], repr(res["title"][:60]), "tries", tries, flush=True)
    json.dump(results, open(out,"w"), indent=1, ensure_ascii=False)
    time.sleep(0.7)
print("done", len(results))
