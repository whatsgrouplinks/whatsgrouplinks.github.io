import json, re, html

def norm(code):
    return code.split("?")[0].split("#")[0].rstrip("/")

def clean(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

def parse_html(body, source_url):
    # split by h2 headings to capture section context
    entries = []
    # find sections: heading text then following content until next heading
    parts = re.split(r'(<h2[^>]*>.*?</h2>)', body, flags=re.S|re.I)
    section = ""
    for p in parts:
        if p.lower().startswith('<h2'):
            section = clean(p)
            continue
        for m in re.finditer(r'<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/([A-Za-z0-9_-]+)', p, flags=re.S|re.I):
            name = clean(m.group(1))
            code = norm(m.group(2))
            entries.append({"code": code, "name": name, "section": section, "source": source_url})
    # fallback: any codes not in rows
    have = {e["code"] for e in entries}
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', body):
        c = norm(m.group(1))
        if c not in have:
            entries.append({"code": c, "name": "", "section": section, "source": source_url})
            have.add(c)
    return entries

mega = open('team12_mega.html', encoding='utf-8', errors='ignore').read()
entries = parse_html(mega, "https://tglinkhub.com/whatsapp-group-links/")
print("mega entries:", len(entries), "unique:", len({e['code'] for e in entries}))
print("mega with names:", sum(1 for e in entries if e['name']))

mal = json.load(open('team12_mal_api.json'))
malbody = mal['content']['rendered']
mentries = parse_html(malbody, "https://tglinkhub.com/malayalam-whatsapp/")
print("malayalam entries:", len(mentries), "unique:", len({e['code'] for e in mentries}))

# merge, mega first
allmap = {}
for e in entries + mentries:
    if e["code"] not in allmap:
        allmap[e["code"]] = e
print("total unique codes:", len(allmap))

existing = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
fresh = [e for c, e in allmap.items() if c not in existing]
dup = len(allmap) - len(fresh)
print("fresh:", len(fresh), "dup vs union:", dup)
json.dump(fresh, open('team12_fresh_raw.json','w'), ensure_ascii=False, indent=1)
json.dump({"total_unique": len(allmap), "fresh": len(fresh), "dup": dup,
           "mega_unique": len({e['code'] for e in entries}),
           "malayalam_unique": len({e['code'] for e in mentries})},
          open('team12_extract_stats.json','w'), indent=1)
# section distribution of fresh
from collections import Counter
print(Counter(e['section'][:40] for e in fresh).most_common(15))
print("sample fresh:", fresh[:5])
