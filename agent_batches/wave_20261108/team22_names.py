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

results = {}
for label, d in raw.items():
    h = d["html"]
    codes = sorted(set(pat.findall(h) + pat2.findall(h)))
    fresh = [c for c in codes if c not in union]
    for code in fresh:
        # find occurrences; prefer table-row context
        ctxs = []
        for m in re.finditer(re.escape(code), h):
            start = max(0, m.start()-1200)
            chunk = h[start:m.start()+50]
            # try row
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', chunk, flags=re.S|re.I)
            if rows:
                ctx = clean(rows[-1])
            else:
                # take last list item / paragraph / heading
                ctx = clean(chunk)
                ctx = ctx[-200:]
            ctxs.append(ctx)
        results.setdefault(code, []).append((label, ctxs))

for code, lst in results.items():
    print("="*80)
    print(code)
    for label, ctxs in lst:
        print(" ", label, "|", ctxs[0][:250])
json.dump({k: v for k,v in results.items()}, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_fresh_ctx.json","w"))
print("TOTAL FRESH", len(results))
