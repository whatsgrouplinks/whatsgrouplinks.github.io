import json, re, subprocess, time, threading
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
fresh = json.load(open('team12_fresh_raw.json'))

def check_once(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl","-sL","--max-time","15","-A",UA,"-o","-","-w","\n%{http_code}",url],
                           capture_output=True, text=True, timeout=25)
    except Exception:
        return "transport", ""
    out = r.stdout or ""
    parts = out.rsplit("\n", 1)
    http = parts[1].strip() if len(parts) == 2 else ""
    body = parts[0] if len(parts) == 2 else out
    if not body or len(body) < 100:
        return "transport", ""
    if http != "200":
        return "dead", ""
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body, re.I)
    title = (m.group(1).strip() if m else "")
    return ("live", title) if title else ("ambiguous", "")

def check(code):
    status, title = check_once(code)
    if status == "ambiguous":
        for _ in range(1):
            time.sleep(3)
            s2, t2 = check_once(code)
            if s2 in ("live", "dead", "transport"):
                return s2, t2
            status, title = s2, t2
    return status, title

results = {}
lock = threading.Lock()
done = [0]
try:
    prev = json.load(open('team12_verify_partial.json'))
    results = {r["code"]: r for r in prev}
    print("resumed", len(results), flush=True)
except Exception:
    pass

def work(e):
    code = e["code"]
    if code in results and results[code]["status"] in ("live", "dead"):
        return
    status, title = check(code)
    with lock:
        results[code] = {"code": code, "name": e["name"], "section": e["section"],
                         "source": e["source"], "status": status, "og_title": title}
        done[0] += 1
        if done[0] % 10 == 0:
            json.dump(list(results.values()), open('team12_verify_partial.json','w'), ensure_ascii=False, indent=1)
            live = sum(1 for r in results.values() if r["status"]=="live")
            print(f"done={done[0]} stored={len(results)} live={live}", flush=True)

# stagger dispatch: submit in small waves with 0.6s gaps
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = []
    for e in fresh:
        futs.append(ex.submit(work, e))
        time.sleep(0.2)
    for f in futs:
        f.result()

json.dump(list(results.values()), open('team12_verify_partial.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r["status"] for r in results.values()))
print("ALL DONE", len(results))
