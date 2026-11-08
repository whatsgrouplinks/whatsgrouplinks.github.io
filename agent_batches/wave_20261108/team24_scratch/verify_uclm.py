import json, sys, time, html
sys.path.insert(0,'.')
from curlutil import verify
pairs=json.load(open('uclm_final.json'))
results={}
for code,name in pairs.items():
    st, title = verify(code)
    results[code]={'name':name,'verify':st,'ogtitle':html.unescape(title)}
    print(code, st, '|', html.unescape(title)[:80], '|', name, flush=True)
    time.sleep(0.7)
json.dump(results, open('verified_uclm.json','w'), ensure_ascii=False, indent=1)
live=[c for c,r in results.items() if r['verify']=='live']
trans=[c for c,r in results.items() if r['verify']=='transport']
print('LIVE:',len(live),'TRANSPORT:',len(trans),'DEAD:',len(results)-len(live)-len(trans), flush=True)
