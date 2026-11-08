import requests, re, time, json
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
raw=json.load(open('team03_crawl_raw.json'))
ids=[]
for rec in raw:
    u=rec['url']
    m=re.search(r'/groupe/(\d+)', u)
    if m: ids.append((int(m.group(1)), u, rec.get('title','')))
ids.sort()
print('resolving', len(ids), 'groupe ids via /join manual chain', flush=True)
def resolve(item):
    gid,u,title=item
    out={'gid':gid,'url':u,'title':title,'dest':'','error':None}
    for attempt in range(2):
        try:
            s=requests.Session(); s.headers.update(UA)
            r=s.get('https://groupchatconnect.info/join?id=%d'%gid, timeout=40, allow_redirects=False)
            loc=r.headers.get('Location','')
            out['status']=r.status_code
            out['dest']=loc
            if loc: break
            # if no Location (e.g. 200 interstitial), note it
            out['error']='no-location status=%s' % r.status_code
            break
        except Exception as ex:
            out['error']=repr(ex)[:120]
            time.sleep(3)
    print(gid, out.get('status'), out['dest'][:90], out['error'] or '', flush=True)
    return out
results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(resolve, ids):
        results.append(res)
        time.sleep(0.3)
json.dump(results, open('team03_resolve2_raw.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
def kind(d):
    if 'chat.whatsapp.com/' in d: return 'wa-direct'
    if 'groupsor.link/group/join/' in d: return 'wa-via-groupsor'
    if 't.me/' in d: return 'telegram'
    return 'other:'+d[:40]
print('DONE', len(results))
print(Counter(kind(r['dest']) for r in results))
print('errors/no-dest:', sum(1 for r in results if not r['dest']))
