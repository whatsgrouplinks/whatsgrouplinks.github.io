import re, sys, json, html
def clean(t): return html.unescape(re.sub(r'\s+',' ',t or '')).strip()
for path in sys.argv[1:]:
    h = open(path, encoding='utf-8', errors='ignore').read()
    out = {}
    # list items
    for m in re.finditer(r'<li[^>]*>(.*?)</li>', h, re.S):
        li = m.group(1)
        code = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', li)
        if code:
            txt = clean(re.sub(r'<[^>]+>',' ',li))
            txt = re.sub(r'\s*(Join|Join Group|Join Now)\s*$','',txt).strip(' :–-')
            out[code.group(1)] = txt
    # table rows fallback
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', h, re.S):
        tr = m.group(1)
        code = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', tr)
        if code and code.group(1) not in out:
            cells = [clean(re.sub(r'<[^>]+>',' ',c)) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
            cells = [c for c in cells if c and c.lower() not in ('join','join group','join now','click here','link')]
            if cells: out[code.group(1)] = cells[0]
    print(f"{path}: {len(out)}")
    for c,n in list(out.items())[:60]:
        print(f"  {c} | {n[:90]}")
    json.dump(out, open('team25_raw/li_'+re.sub(r'[^A-Za-z0-9]+','_',path)+'.json','w'), indent=1, ensure_ascii=False)
