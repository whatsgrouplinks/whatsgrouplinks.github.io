import json
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
OLD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
union=json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"))
union=set(union if isinstance(union,list) else union.keys())
print("union size:", len(union))
today=json.load(open(f"{WD}/team20_77_all_extracted.json"))
yest=json.load(open(f"{OLD}/team20_all_extracted.json"))
print("today codes:", len(today), "yesterday codes:", len(yest))
new_vs_yest={c:v for c,v in today.items() if c not in yest}
print("new vs yesterday extraction:", len(new_vs_yest))
from collections import Counter
print("new by page:", Counter(v['page'] for v in new_vs_yest.values()))
fresh={c:v for c,v in new_vs_yest.items() if c not in union}
print("fresh (new + not in union):", len(fresh))
print("fresh by page:", Counter(v['page'] for v in fresh.values()))
dupes_new=sum(1 for c in new_vs_yest if c in union)
print("new-but-in-union dupes:", dupes_new)
# old codes still in union?
print("today codes already in union:", sum(1 for c in today if c in union))
# yesterday pending
pend=json.load(open(f"{OLD}/team20-77links-pending.json"))
print("yesterday pending:", len(pend))
pend_codes=[p['invite'].split('/')[-1] for p in pend]
print("pending still not in union:", sum(1 for c in pend_codes if c not in union))
print("pending now in union:", sum(1 for c in pend_codes if c in union))
# LTG fresh code
ltg=json.load(open(f"{WD}/ltg_new_resolved.json"))
for r in ltg:
    if 'chat.whatsapp.com/' in r['destination']:
        code=r['destination'].split('/')[-1]
        print("LTG code", code, "in union?", code in union, "name:", r['name'])
json.dump(fresh, open(f"{WD}/team20_fresh_77.json",'w'), ensure_ascii=False, indent=1)
json.dump(new_vs_yest, open(f"{WD}/team20_new_vs_yest.json",'w'), ensure_ascii=False, indent=1)
print("DONE")
