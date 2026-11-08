import json, sys, time, html
sys.path.insert(0,'.')
from curlutil import verify
fresh=json.load(open('tugrupo_fresh.json'))
recs=json.load(open('tugrupo_raw.json'))
code2rec={}
for u,r in recs.items():
    if r.get('code'): code2rec.setdefault(r['code'],[]).append((u,r))
results={}
for code in sorted(fresh):
    st, title = verify(code)
    results[code]={'verify':st,'ogtitle':html.unescape(title)}
    print(code, st, '|', html.unescape(title)[:70], flush=True)
    time.sleep(0.7)
json.dump(results, open('verified_tugrupo.json','w'), ensure_ascii=False, indent=1)
live=[c for c,r in results.items() if r['verify']=='live']
trans=[c for c,r in results.items() if r['verify']=='transport']
print('LIVE:',len(live),'TRANSPORT:',len(trans),'DEAD:',len(results)-len(live)-len(trans), flush=True)
