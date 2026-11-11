"""Re-extract ALL invite codes (direct + /invite/ formats) with list-item names
from already-fetched raw HTML. Merges into team24_candidates.json."""
import json, re, glob, os, html

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
LI_RE = re.compile(
    r'<li[^>]*>(.*?)<a\s[^>]*href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"',
    re.DOTALL | re.IGNORECASE)
ANY_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

cands = json.load(open(W + "team24_candidates.json")) if os.path.exists(W + "team24_candidates.json") else {}
named = 0
unnamed = 0
for f in sorted(glob.glob(W + "team24_raw/*.html")):
    h = open(f).read()
    url = "https://whtspgrouplink.com/" + os.path.basename(f)[:-5] + "/"
    seen_here = set()
    for m in LI_RE.finditer(h):
        raw_name, code = m.group(1), m.group(2)
        name = re.sub(r'<[^>]+>', ' ', raw_name)
        name = html.unescape(name)
        name = re.sub(r'\s+', ' ', name).strip(' –-—|•·')
        name = name.strip()
        if code in seen_here:
            continue
        seen_here.add(code)
        if code not in cands or not cands[code].get("name"):
            cands[code] = {"code": code, "page": url, "name": name, "context": cands.get(code, {}).get("context", "")}
            named += 1
    # any code not inside an <li> (fallback, name empty)
    for m in ANY_RE.finditer(h):
        code = m.group(1)
        if code not in cands:
            cands[code] = {"code": code, "page": url, "name": "", "context": ""}
            unnamed += 1
json.dump(cands, open(W + "team24_candidates.json", "w"), indent=1, ensure_ascii=False)
print(f"total candidates now: {len(cands)} (named adds {named}, unnamed adds {unnamed})")
named_total = sum(1 for c in cands.values() if c.get("name"))
print(f"with name: {named_total}, without name: {len(cands)-named_total}")
