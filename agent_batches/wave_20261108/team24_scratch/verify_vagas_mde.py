import json, sys, time
sys.path.insert(0,'.')
from curlutil import verify
fresh=json.load(open('fresh_vagas_mde.json'))
results={}
for src, d in fresh.items():
    for code, name in d.items():
        st, title = verify(code)
        results[code]={'source':src,'name':name,'verify':st,'ogtitle':title}
        print(code, st, '|', title, '|', name, flush=True)
        time.sleep(0.7)
json.dump(results, open('verified_vagas_mde.json','w'), ensure_ascii=False, indent=1)
live=[c for c,r in results.items() if r['verify']=='live']
trans=[c for c,r in results.items() if r['verify']=='transport']
print('LIVE:',len(live),'TRANSPORT:',len(trans),'DEAD:',len(results)-len(live)-len(trans), flush=True)
