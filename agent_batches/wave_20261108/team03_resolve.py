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
print('resolving', len(ids), 'groupe ids', flush=True)
def resolve(item):
    gid,u,title=item
    out={'gid':gid,'url':u,'title':title,'final_url':'','error':None}
    for attempt in range(2):
        try:
            s=requests.Session(); s.headers.update(UA)
            r=s.get('https://groupchatconnect.info/join.php?id=%d'%gid, timeout=45, allow_redirects=True)
            out['final_url']=r.url
            out['status']=r.status_code
            break
        except Exception as ex:
            out['error']=repr(ex)[:120]
            time.sleep(3)
    print(gid, out.get('status'), out['final_url'][:90], out['error'] or '', flush=True)
    return out
results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(resolve, ids):
        results.append(res)
        time.sleep(0.5)
json.dump(results, open('team03_resolve_raw.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print('DONE', len(results))
print(Counter(('wa' if 'chat.whatsapp.com/' in r['final_url'] else 'tg' if 't.me/' in r['final_url'] else 'other') for r in results))
print('errors:', sum(1 for r in results if r['error'] and not r['final_url']))
