import re, json, html as htmllib, os, glob

BAD = {"join", "join group", "join now"}
def clean_name(s):
    s = htmllib.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip(' \t-–—|•·')
    return s

def extract(page):
    out = []
    seen = set()
    for m in re.finditer(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', page):
        code = m.group(1)
        if code in seen: continue
        # skip channel links (different host path, already excluded by regex) and whatsapp.com/channel
        window = page[max(0, m.start()-600):m.start()]
        if 'whatsapp.com/channel' in window[-200:]: continue
        nodes = re.findall(r'>([^<>]+)<', window)
        name = ""
        for node in reversed(nodes):
            t = clean_name(node)
            if not t: continue
            low = t.lower()
            if low in BAD: continue
            if 'whatsapp group link' in low: continue
            if len(t) < 2: continue
            name = t
            break
        out.append({"name": name, "code": code})
        seen.add(code)
    return out

if __name__ == "__main__":
    allc = []
    for f in sorted(glob.glob("team24_raw/*.html")):
        page = open(f, encoding='utf-8', errors='replace').read()
        slug = os.path.basename(f)
        items = extract(page)
        print(slug, len(items))
        for it in items:
            it["source_file"] = slug
            allc.append(it)
    print("total items:", len(allc), "unique codes:", len({c['code'] for c in allc}))
    json.dump(allc, open("team24_candidates_v2.json","w"), indent=1, ensure_ascii=False)
    for c in allc[:25]: print(c)
