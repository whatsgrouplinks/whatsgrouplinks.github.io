import requests, re, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
urls = json.load(open("team24-linkado-sitemap-urls.json"))
new = [(u, lm) for u, lm in urls if lm > "2026-11-10"]
print("to fetch:", len(new))
s = requests.Session()
out = []
for i, (u, lm) in enumerate(new):
    try:
        r = s.get(u, headers=UA, timeout=60)
        html = r.text if r.status_code == 200 else ""
    except Exception as e:
        print(i, u, "ERR", e); out.append({"url": u, "lastmod": lm, "error": str(e)}); continue
    codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,})', html)
    # name: <h1 ...> or og:title
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    name = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ""
    og = re.search(r'property="og:title" content="([^"]*)"', html)
    ogt = og.group(1) if og else ""
    cat = re.search(r'/categoria/([a-z0-9-]+)', html)
    # category label near "Categoria"
    cm = re.search(r'[Cc]ategoria[^<]{0,80}', html)
    out.append({"url": u, "lastmod": lm, "status": r.status_code, "codes": codes,
                "name_h1": name, "og_title": ogt, "cat_slug": cat.group(1) if cat else "",
                "cat_ctx": cm.group(0) if cm else ""})
    if i % 10 == 0: print(i, "done")
    time.sleep(0.3)
json.dump(out, open("team24-linkado-mined.json","w"), ensure_ascii=False, indent=1)
ncode = sum(1 for o in out if o.get("codes"))
print("pages with codes:", ncode, "of", len(out))
for o in out:
    if o.get("codes"): print(o["lastmod"][:10], o["codes"], "|", o["name_h1"][:60], "|", o["cat_slug"])
