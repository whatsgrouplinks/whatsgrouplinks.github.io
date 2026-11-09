import json, re, subprocess, time, html, os
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
st = json.load(open(f"{W}/team05-extracted.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
fresh = [c for c in st["codes"] if c not in existing]
OUT = f"{W}/team05-verify.json"
res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT))
def check(code):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25","-A",UA,f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=35)
        body = r.stdout or ""
    except Exception:
        return {"status": 0, "title": "", "size": 0}
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body, re.I)
    title = html.unescape(m.group(1)).strip() if m else ""
    md = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', body, re.I)
    desc = html.unescape(md.group(1)).strip() if md else ""
    return {"status": 200 if body else 0, "title": title, "desc": desc, "size": len(body)}
todo = [c for c in fresh if c not in res]
print("to verify:", len(todo), "already:", len(res), flush=True)
for i, c in enumerate(todo):
    r1 = check(c)
    tries = 1
    while r1["status"] == 200 and not r1["title"] and tries < 3:
        time.sleep(8)
        r1 = check(c)
        tries += 1
    r1["tries"] = tries
    res[c] = r1
    print(i+1, c, r1["status"], repr(r1["title"][:60]), "tries", tries, flush=True)
    json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
    time.sleep(0.6)
live = [c for c,v in res.items() if v["status"]==200 and v["title"]]
amb = [c for c,v in res.items() if v["status"]==200 and not v["title"]]
dead = [c for c,v in res.items() if v["status"]!=200]
print("LIVE:", len(live), "AMBIG(still empty after retries):", len(amb), "DEAD/non200:", len(dead))
