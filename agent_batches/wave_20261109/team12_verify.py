import json, re, subprocess, time, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
fresh = json.load(open('team12_fresh_raw.json'))

def check(code):
    """returns (status, og_title) status in live/ambiguous/dead/transport"""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl","-sL","--max-time","20","-A",UA,"-o","-","-w","\n%{http_code}",url],
                           capture_output=True, text=True, timeout=30)
    except Exception as e:
        return "transport", ""
    out = r.stdout or ""
    lines = out.rsplit("\n", 1)
    http = lines[1].strip() if len(lines) == 2 else ""
    body = lines[0] if len(lines) == 2 else out
    if not body or len(body) < 100:
        return "transport", ""
    if http != "200":
        return "dead", ""
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body, re.I)
    title = (m.group(1).strip() if m else "")
    if title:
        return "live", title
    return "ambiguous", ""

results = {}
# resume if partial file exists
try:
    prev = json.load(open('team12_verify_partial.json'))
    results = {r["code"]: r for r in prev}
    print("resumed", len(results), flush=True)
except Exception:
    pass

for i, e in enumerate(fresh):
    code = e["code"]
    if code in results and results[code]["status"] in ("live","dead"):
        continue
    status, title = check(code)
    if status == "ambiguous":
        # retry up to 2 more times spaced apart
        for attempt in range(2):
            time.sleep(3)
            s2, t2 = check(code)
            if s2 == "live":
                status, title = s2, t2; break
            if s2 == "dead":
                status, title = s2, ""; break
            if s2 == "transport":
                status = "transport"; break
            status, title = s2, t2
    results[code] = {"code": code, "name": e["name"], "section": e["section"],
                     "source": e["source"], "status": status, "og_title": title}
    if (i+1) % 25 == 0:
        json.dump(list(results.values()), open('team12_verify_partial.json','w'), ensure_ascii=False, indent=1)
        live = sum(1 for r in results.values() if r["status"]=="live")
        print(f"{i+1}/{len(fresh)} live={live} checked={len(results)}", flush=True)
    time.sleep(0.7)

json.dump(list(results.values()), open('team12_verify_partial.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r["status"] for r in results.values()))
print("done", len(results))
