import json, re, time, html, requests
W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
codes = ["L8lS7DjrCr9627LLIInvsl", "IGhtsGtrH3n3k5TS0Tn2PQ", "EkeiobkWygVIVJP9DmrB58"]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
def check(code):
    for attempt in (1,2):
        try:
            s = requests.Session()
            r = s.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=20)
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ""
            if title or attempt == 2:
                return {"code": code, "status": r.status_code, "title": title, "attempt": attempt, "error": ""}
            print(code, "empty on attempt 1, pausing before retry", flush=True)
            time.sleep(30)
        except Exception as e:
            if attempt == 1:
                time.sleep(10)
                continue
            return {"code": code, "status": 0, "title": "", "attempt": attempt, "error": str(e)[:150]}
    return {"code": code, "status": 0, "title": "", "attempt": 2, "error": "?"}
out = []
for c in codes:
    r = check(c)
    out.append(r)
    print(c, r["status"], repr(r["title"][:80]), r["error"][:80], flush=True)
    time.sleep(2)
json.dump(out, open(W+"team22_extra_verify.json","w"), indent=1)
print("done", flush=True)
