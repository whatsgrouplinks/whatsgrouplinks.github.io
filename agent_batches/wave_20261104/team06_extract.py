import re, json, html as htmlmod
union = set(json.load(open("_team06_dedupe_set.json")))
files = {"crypto":"_t06_crypto.html", "earning":"_t06_earning.html", "dubai":"_t06_dubai.html"}
cands = {}  # code -> (name, page)
for key, fn in files.items():
    h = open(fn).read()
    for m in re.finditer(r'href="(https://chat\.whatsapp\.com/[A-Za-z0-9]{20,24})"', h):
        code = m.group(1).split("/")[-1]
        if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code): continue
        tail = h[m.end():m.end()+600]
        nm = re.search(r'<div style="text-align: center;">\s*([^<]+?)\s*</div>', tail)
        name = htmlmod.unescape(nm.group(1).strip()) if nm else ""
        if code in cands: continue
        cands[code] = (name, key)
print("total candidates:", len(cands))
fresh = {c:v for c,v in cands.items() if c not in union}
print("fresh (not in union):", len(fresh), "dup-in-union:", len(cands)-len(fresh))
json.dump({c:{"name":n,"page":p} for c,(n,p) in fresh.items()}, open("_t06_candidates.json","w"), ensure_ascii=False, indent=1)
# sample
for c,(n,p) in list(fresh.items())[:10]:
    print(c, "|", n, "|", p)
