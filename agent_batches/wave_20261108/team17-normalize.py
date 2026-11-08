import json
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
merged={}
def norm(res):
    # progress.json: (code, status, title); verify2/3: (status, info)
    if len(res)==3:
        return (res[1], res[2])
    return (res[0], res[1])
for f in ['team17-verify-progress.json','team17-verify2-pass1.json','team17-verify3.json']:
    d=json.load(open(WAVE+f))
    for k,v in d.items():
        st,info=norm(v['res'])
        # live wins over dead on overlap; keep first dead otherwise
        if k not in merged or st=='live':
            merged[k]={'cand':cands[k],'res':[st,info]}
from collections import Counter
print('merged unique:',len(merged),Counter(v['res'][0] for v in merged.values()))
print('live:',sum(1 for v in merged.values() if v['res'][0]=='live'))
json.dump(merged, open(WAVE+'team17-merged.json','w'), ensure_ascii=False)
