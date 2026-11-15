import requests, re, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
fetched=set()
for line in open('../wave_20261112/team16_scratch/all_pages.jsonl'):
    try: fetched.add(json.loads(line).get('url',''))
    except: pass
cur = re.findall(r'<loc>([^<]+)</loc>', open('team24-whts-sitemap.xml', encoding='utf-8', errors='replace').read())
new = [u for u in dict.fromkeys(cur) if u not in fetched]
print("new pages:", len(new))
s = requests.Session()
out=[]
for i,u in enumerate(new):
    try:
        r = s.get(u, headers=UA, timeout=60)
        html = r.text if r.status_code==200 else ""
    except Exception as e:
        out.append({"url":u,"error":str(e)}); continue
    codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,})', html)
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    name = re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ""
    title = re.search(r'<title>(.*?)</title>', html, re.S)
    t = re.sub(r'\s+',' ',title.group(1)).strip() if title else ""
    out.append({"url":u,"status":r.status_code,"codes":list(dict.fromkeys(codes)),"name_h1":name,"title":t})
    time.sleep(0.2)
json.dump(out, open("team24-whts-mined.json","w"), ensure_ascii=False, indent=1)
for o in out:
    print(o["status"], o.get("codes"), "|", o["name_h1"][:50] or o["title"][:50])
