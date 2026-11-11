"""Fix names for fresh candidates using tight patterns:
- <li>NAME &ndash; <a href="...CODE">  (name within 250 chars before link, no tags/JSON)
- <td>NAME</td><td>...<a href="...CODE"> (table rows)
"""
import json, re, glob, os, html

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip(' \t–-—|•·\xa0')
    return s.strip()

LI = re.compile(r'<li[^>]*>([^<]{1,200}?)\s*(?:&#8211;|&ndash;|–|-|:)\s*(?:<[^>]+>)*<a\s[^>]*href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', re.DOTALL | re.IGNORECASE)
TD = re.compile(r'<td[^>]*>([^<]{1,200}?)</td>\s*<td[^>]*>(?:<[^>]+>)*<a\s[^>]*href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', re.DOTALL | re.IGNORECASE)

fresh = json.load(open(W + "team24_fresh.json"))
cands = json.load(open(W + "team24_candidates.json"))
names = {}
for f in sorted(glob.glob(W + "team24_raw/*.html")):
    h = open(f).read()
    for m in LI.finditer(h):
        nm = clean(m.group(1))
        if nm and 'schema' not in nm.lower() and '{' not in nm and 'http' not in nm.lower():
            names.setdefault(m.group(2), nm)
    for m in TD.finditer(h):
        nm = clean(m.group(1))
        if nm and 'schema' not in nm.lower() and '{' not in nm:
            names.setdefault(m.group(2), nm)

fixed = 0
for code, v in fresh.items():
    if code in names and v.get("name") != names[code]:
        v["name"] = names[code]
        fixed += 1
    if code in names and code in cands:
        cands[code]["name"] = names[code]
json.dump(fresh, open(W + "team24_fresh.json", "w"), indent=1, ensure_ascii=False)
json.dump(cands, open(W + "team24_candidates.json", "w"), indent=1, ensure_ascii=False)
print("fixed names:", fixed)
for c, v in fresh.items():
    print(c, '|', repr(v.get("name", "")[:70]))
