import json, subprocess, re, time, html as htmllib, sys
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
passfile = sys.argv[1]; outfile = sys.argv[2]
prev = json.load(open(passfile))
codes = [c for c,v in prev.items() if v["status"]==200 and not v["title"]]
print("retrying:", len(codes), flush=True)
def check(code):
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","30","-A",UA,"-o","/dev/stdout","-w","\n%{http_code}",f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=40)
        body, _, status = r.stdout.rpartition("\n")
        status = int(status.strip()) if status.strip().isdigit() else 0
    except Exception as e:
        return {"code":code,"status":0,"title":"","desc":"","error":str(e)}
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body, re.I)
    title = htmllib.unescape(m.group(1)).strip() if m else ""
    m2 = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', body, re.I)
    desc = htmllib.unescape(m2.group(1)).strip() if m2 else ""
    return {"code":code,"status":status,"title":title,"desc":desc}
def worker(i, code):
    time.sleep(0.5 * (i % 3))
    return check(code)
results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(worker, i, c): c for i, c in enumerate(codes)}
    for j, f in enumerate(futs):
        r = f.result(); results[r["code"]] = r
        if (j+1) % 20 == 0: print(j+1, "done", flush=True)
json.dump(results, open(outfile,"w"), indent=1, ensure_ascii=False)
live = [r for r in results.values() if r["status"]==200 and r["title"]]
print("retry live:", len(live), [ (r["code"], r["title"]) for r in live ], flush=True)
