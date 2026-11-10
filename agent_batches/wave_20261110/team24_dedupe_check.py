import json, re
exist = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
gj = json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
gset = set()
if isinstance(gj, list):
    for it in gj:
        inv = it.get('invite','') if isinstance(it, dict) else ''
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)', inv)
        if m: gset.add(m.group(1))
print("existing:", len(exist), "groups.json codes:", len(gset), "union:", len(exist|gset))
cands = json.load(open("team24_candidates_partial.json"))
# fix names: cut at <a
import html as h
fixed={}
for c in cands:
    name = c['name'].split('<a')[0].strip(' \t-–—|')
    name = re.sub(r'\s+',' ',name)
    if c['code'] not in fixed: fixed[c['code']]=name
print("unique codes in partial:", len(fixed))
fresh = {k:v for k,v in fixed.items() if k not in (exist|gset)}
print("fresh (not in union):", len(fresh))
for k,v in list(fresh.items())[:20]: print(v, k)
json.dump({"union_size":len(exist|gset)}, open("team24_union_meta.json","w"))
