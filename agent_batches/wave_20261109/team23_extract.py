import re, os, glob, json, html as htmllib
existing = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
def clean(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = htmllib.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t
out = {}
for f in sorted(glob.glob("team23_raw/*.html")):
    src = os.path.basename(f).replace('.html','')
    raw = open(f, encoding="utf-8", errors="ignore").read()
    # find all invite links with position
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})', raw):
        code = m.group(1)
        if code == 'invite': continue
        # look back 800 chars for nearest text
        window = raw[max(0,m.start()-900):m.start()]
        # prefer last <td>...</td> or heading text
        cells = re.findall(r'<td[^>]*>(.*?)</td>', window, re.S|re.I)
        name = clean(cells[-1]) if cells else ''
        if not name or len(name) > 80:
            # fallback: last heading / strong text
            heads = re.findall(r'<(?:h[1-4]|strong|b)[^>]*>(.*?)</(?:h[1-4]|strong|b)>', window, re.S|re.I)
            name = clean(heads[-1]) if heads else ''
        name = name[:80]
        if code not in out:
            out[code] = {"code": code, "name_hint": name, "source": src}
        else:
            if not out[code]["name_hint"] and name:
                out[code]["name_hint"] = name
print("total unique codes:", len(out))
fresh = {c:v for c,v in out.items() if c not in existing}
print("fresh (not in existing):", len(fresh), " already known:", len(out)-len(fresh))
json.dump(out, open("team23_raw/all_extracted.json","w"), indent=1, ensure_ascii=False)
json.dump(fresh, open("team23_raw/fresh_extracted.json","w"), indent=1, ensure_ascii=False)
for c,v in list(fresh.items())[:40]:
    print(c, "|", v["name_hint"], "|", v["source"])
