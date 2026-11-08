import json, re
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json')))
data = json.load(open('/tmp/gs.json'))
print("total", len(data))
from collections import Counter
print("platforms", Counter(d.get('platform') for d in data))
print("created dates", Counter((d.get('createdAt') or '')[:10] for d in data))
wa = [d for d in data if d.get('platform')=='whatsapp']
print("whatsapp", len(wa))
def code(link):
    if not link: return None
    m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{15,30})', link)
    return m.group(1) if m else None
cands=[]
for d in wa:
    c = code(d.get('inviteLink') or '')
    if not c:
        print("NOCODE", d.get('name'), d.get('inviteLink'))
        continue
    cands.append((c,d))
print("with code", len(cands))
print("in union already", sum(1 for c,_ in cands if c in union))
print("fresh", sum(1 for c,_ in cands if c not in union))
print("dup within batch", len(cands)-len(set(c for c,_ in cands)))
print("categories", Counter(d.get('category') for _,d in cands))
print("countries", Counter(d.get('country') for _,d in cands))
fresh=[(c,d) for c,d in cands if c not in union]
# dedupe within batch keep first
seen=set(); uniq=[]
for c,d in fresh:
    if c in seen: continue
    seen.add(c); uniq.append((c,d))
print("fresh unique", len(uniq))
for c,d in uniq:
    print(c, '|', d.get('createdAt','')[:10], '|', d.get('category'), '|', d.get('country'), '|', (d.get('name') or '')[:60])
json.dump([{'code':c,'rec':d} for c,d in uniq], open('/tmp/gs_fresh.json','w'), ensure_ascii=False)
