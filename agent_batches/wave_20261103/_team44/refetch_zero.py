import sys, json, os, time, re
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
from lib import fetch, extract_li_join, extract_table_join
P=D+'/raw_candidates.json'
cand=json.load(open(P))
changed=0
for url,items in list(cand.items()):
    if items: continue
    slug=url.rstrip('/').split('/')[-1]
    t=fetch(url if url.endswith('/') else url+'/', tries=3)
    if t is None: print('STILL-MISS',slug); continue
    open(D+'/pages_'+slug+'.html','w').write(t)
    its=extract_li_join(t)+extract_table_join(t)
    # dedupe within page
    seen=set(); out=[]
    for n,l in its:
        if l in seen: continue
        seen.add(l); out.append([n,l])
    cand[url]=out; changed+=1
    print('RECOVERED',slug,len(out))
    time.sleep(0.8)
json.dump(cand,open(P,'w'))
print('changed:',changed)
