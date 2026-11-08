import requests, re, time, json, html as htmllib
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
raw=json.load(open('team03_crawl_raw.json'))
out=[]
for rec in raw:
    u=rec['url']
    if '/groupe/' not in u:
        continue
    r2={'url':u,'title':rec.get('title',''),'go_tokens':[],'status':None,'error':None}
    for attempt in range(2):
        try:
            r=requests.get(u, headers=UA, timeout=60)
            r2['status']=r.status_code
            r2['go_tokens']=sorted(set(re.findall(r'href="/go/([A-Za-z0-9_-]+)"', r.text)))
            # also join.php id links
            r2['join_ids']=sorted(set(re.findall(r'/join\.php\?id=(\d+)', r.text)))
            break
        except Exception as ex:
            r2['error']=repr(ex)
            time.sleep(3)
    out.append(r2)
    print(u, r2['status'], r2['go_tokens'], flush=True)
    time.sleep(1.0)
json.dump(out, open('team03_go_raw.json','w'), ensure_ascii=False, indent=1)
print('DONE', len(out))
from collections import Counter
print(Counter(t for r in out for t in r['go_tokens']).most_common(10))
print('pages with go tokens:', sum(1 for r in out if r['go_tokens']))
print('errors:', sum(1 for r in out if r['error'] and r['status'] is None))
