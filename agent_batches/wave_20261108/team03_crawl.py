import requests, re, time, json, html as htmllib
from collections import Counter

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
leads=json.load(open('leads_slice_03.json'))
out=[]
for i,e in enumerate(leads):
    u=e['url']
    rec={'idx':i,'url':u,'status':None,'wa_codes':[],'title':'','similar':[],'error':None}
    for attempt in range(2):
        try:
            r=requests.get(u, headers=UA, timeout=60)
            rec['status']=r.status_code
            html=r.text
            rec['wa_codes']=sorted(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', html)))
            rec['invite_codes']=sorted(set(re.findall(r'whatsapp\.com/invite/([A-Za-z0-9_-]{15,30})', html)))
            t=re.search(r'<title>(.*?)</title>', html, re.S)
            rec['title']=htmllib.unescape(t.group(1).strip()) if t else ''
            # similar groupe/channel links
            sims=sorted(set(re.findall(r'href="(/groupe/\d+|/channel/\d+)"', html)))
            rec['similar']=['https://groupchatconnect.info'+s for s in sims]
            # meta description
            m=re.search(r'<meta name="description" content="([^"]*)"', html)
            rec['meta_desc']=htmllib.unescape(m.group(1)) if m else ''
            break
        except Exception as ex:
            rec['error']=repr(ex)
            time.sleep(3)
    out.append(rec)
    print(i, u, rec['status'], 'wa=', rec['wa_codes'], 'title=', rec['title'][:80], flush=True)
    time.sleep(1.2)
json.dump(out, open('team03_crawl_raw.json','w'), ensure_ascii=False, indent=1)
print('DONE', len(out))
print('pages with wa codes:', sum(1 for r in out if r['wa_codes']))
print('code counter:', Counter(c for r in out for c in r['wa_codes']))
print('errors:', sum(1 for r in out if r['error'] and r['status'] is None))
