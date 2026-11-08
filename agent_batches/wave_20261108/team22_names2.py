import json, re, html
raw = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw.json"))
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))
pat = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
pat2 = re.compile(r'whatsapp\.com/invite/([A-Za-z0-9]{20,24})')

def clean(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def name_before(h, pos):
    chunk = h[max(0,pos-6000):pos]
    # last <p>...</p> or <li>...</li> with real text
    cands = []
    for m in re.finditer(r'<(?:p|li|h[1-4])[^>]*>(.*?)</(?:p|li|h[1-4])>', chunk, flags=re.S|re.I):
        t = clean(m.group(1))
        if len(t) >= 3 and len(t) <= 200 and t.lower() not in ('join','link','click here'):
            cands.append(t)
    if cands:
        return cands[-1]
    return ""

out = {}
for label, d in raw.items():
    h = d["html"]
    codes = sorted(set(pat.findall(h) + pat2.findall(h)))
    fresh = [c for c in codes if c not in union]
    for code in fresh:
        m = re.search(re.escape(code), h)
        nm = name_before(h, m.start())
        out[code] = {"source": label, "name_ctx": nm}
        print(f"{code} | {label} | {nm[:160]}")
json.dump(out, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_fresh_names.json","w"), indent=1)
print("TOTAL", len(out))
