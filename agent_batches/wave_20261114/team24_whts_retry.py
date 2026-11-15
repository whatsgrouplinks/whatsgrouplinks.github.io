import requests, re, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
out = json.load(open("team24-whts-mined.json"))
failed = [o for o in out if o.get("error")]
print("retrying:", len(failed))
s = requests.Session()
for o in failed:
    ok = False
    for attempt in range(3):
        try:
            r = s.get(o["url"], headers=UA, timeout=60)
            if r.status_code == 200:
                html = r.text
                codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,})', html)
                m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
                name = re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ""
                t = re.search(r'<title>(.*?)</title>', html, re.S)
                o.update({"status":200,"codes":list(dict.fromkeys(codes)),"name_h1":name,
                          "title": re.sub(r'\s+',' ',t.group(1)).strip() if t else ""})
                o.pop("error", None); ok=True; break
        except Exception as e:
            last = str(e)
        time.sleep(15)
    if not ok:
        o["error"] = "retry failed: " + last
    print(o["url"].split("/")[-1], o.get("codes"), o.get("error",""))
    time.sleep(2)
json.dump(out, open("team24-whts-mined.json","w"), ensure_ascii=False, indent=1)
print("done. errors left:", sum(1 for o in out if o.get("error")))
