import json, subprocess, re, time, html as htmllib
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
fresh = json.load(open("team23_raw/fresh_extracted.json"))
codes = sorted(fresh.keys())
print("to verify:", len(codes))

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","30","-A",UA,"-o","/dev/stdout","-w","\n%{http_code}",url],
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
    if not m2:
        m2 = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:description["\']', body, re.I)
    desc = htmllib.unescape(m2.group(1)).strip() if m2 else ""
    return {"code":code,"status":status,"title":title,"desc":desc}

results = {}
def worker(i, code):
    time.sleep(0.5 * (i % 3))
    return check(code)
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(worker, i, c): c for i, c in enumerate(codes)}
    for j, f in enumerate(futs):
        r = f.result()
        results[r["code"]] = r
        if (j+1) % 20 == 0: print(j+1, "done")
json.dump(results, open("team23_raw/verify_pass1.json","w"), indent=1, ensure_ascii=False)
live = [r for r in results.values() if r["status"]==200 and r["title"]]
print("pass1: status200+title:", len(live), " status200 empty title:", sum(1 for r in results.values() if r["status"]==200 and not r["title"]), " non200:", sum(1 for r in results.values() if r["status"]!=200))
titles = {}
for r in live: titles[r["title"]] = titles.get(r["title"],0)+1
print("title distribution:", titles)
