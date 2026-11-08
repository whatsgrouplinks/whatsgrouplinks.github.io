import sys, json, os, time
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
from lib import fetch, extract_li_join, extract_table_join
P=D+'/raw_candidates.json'
cand=json.load(open(P))
urls=[
 'https://thewhatspgrouplinks.com/los-angeles-whatsapp-group-links/',
 'https://wagroupshub.com/usa-whatsapp-group-links/',
 'https://wahublink.com/usa-whatsapp-group-links/',
 'https://pkwhatsgrouplinks.com/usa-whatsapp-group-links/',
 'https://newgrouplinks.pk/usa-whatsapp-group-links/',
 'https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/',
]
for url in urls:
    if url in cand and cand[url]: print('SKIP',url); continue
    t=fetch(url,tries=3)
    if t is None: print('MISS',url,flush=True); cand[url]=None
    else:
        its=extract_li_join(t)+extract_table_join(t)
        seen=set(); out=[]
        for n,l in its:
            if l in seen: continue
            seen.add(l); out.append([n,l])
        print('HIT',url,len(out),flush=True); cand[url]=out
    json.dump(cand,open(P,'w')); time.sleep(0.8)
print('fresh harvest done')
