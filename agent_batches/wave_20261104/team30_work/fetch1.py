import re, pickle, requests, json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
s = requests.Session()
s.mount('https://', HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=Retry(total=2, backoff_factor=1)))
union = pickle.load(open('union_set.pkl','rb'))
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
HREF_RE = re.compile(r'<a[^>]+href="([^"]+chat\.whatsapp\.com[^"]*)"', re.I)

urls = [
 'https://wagroupshub.com/usa-whatsapp-group-links/',
 'https://whatgroups.com/whatsapp-group-links-canada/',
 'https://whatsgroupslinkspk.com/canada-whatsapp-group-links/',
 'https://groupchatlink.com/college-whatsapp-group-links/',
 'https://www.wemakescholars.com/blog/whatsapp-group-for-ms-in-us-fall',
]
out = {}
for u in urls:
    try:
        r = s.get(u, headers=UA, timeout=55)
        html = r.text
        codes = [c for c in CODE_RE.findall(html)]
        new = [c for c in codes if c not in union]
        print(u, 'status', r.status_code, 'len', len(html), 'codes', len(codes), 'new', len(new))
        out[u] = {'status': r.status_code, 'codes': new}
        open('raw_'+re.sub(r'\W+','_',u)+'.html','w').write(html)
    except Exception as e:
        print(u, 'FAIL', repr(e)[:120])
        out[u] = {'error': repr(e)[:120], 'codes': []}
json.dump(out, open('fetch1_summary.json','w'))
