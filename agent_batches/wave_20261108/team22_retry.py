import json, re, time, html, requests
res = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_verify_raw.json"))
empties = [r["code"] for r in res if r["status"]==200 and not r["title"]]
print("retrying", len(empties), "empties after pause", flush=True)
time.sleep(180)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
out = []
for i, code in enumerate(empties):
    try:
        s = requests.Session()
        r = s.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=20)
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
        title = html.unescape(m.group(1)).strip() if m else ""
        out.append({"code": code, "status": r.status_code, "title": title, "attempt": "retry", "error": ""})
        print(i+1, code, r.status_code, repr(title[:80]), flush=True)
    except Exception as e:
        out.append({"code": code, "status": 0, "title": "", "attempt": "retry", "error": str(e)[:120]})
        print(i+1, code, "ERR", str(e)[:80], flush=True)
    time.sleep(1.5)
json.dump(out, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_retry_raw.json","w"), indent=1)
live = [r for r in out if r["status"]==200 and r["title"] and r["title"] not in ("WhatsApp Group","Join this group on WhatsApp")]
print("RETRY LIVE:", len(live), flush=True)
