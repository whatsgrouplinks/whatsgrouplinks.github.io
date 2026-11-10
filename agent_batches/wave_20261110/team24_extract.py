import re, json, html as htmllib, os, glob, sys
def extract(page):
    out=[]
    for li in re.findall(r"<li[^>]*>(.*?)</li>", page, flags=re.S|re.I):
        if 'whatsapp.com/channel' in li: continue
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', li)
        if not m: continue
        code=m.group(1)
        name = re.sub(r'<[^>]+>', '', li[:m.start()])
        name = htmllib.unescape(name)
        name = re.sub(r'\s+', ' ', name).strip(' \t-–—|')
        out.append((name, code))
    return out
allc=[]
for f in sorted(glob.glob("team24_raw/*.html")):
    page=open(f, encoding='utf-8', errors='replace').read()
    slug=os.path.basename(f)
    items=extract(page)
    print(slug, len(items))
    for name,code in items:
        allc.append({"name":name,"code":code,"source_file":slug})
print("total raw items:", len(allc))
print("unique codes:", len({c['code'] for c in allc}))
json.dump(allc, open("team24_candidates_partial.json","w"), indent=1, ensure_ascii=False)
for c in allc[:15]: print(c)
