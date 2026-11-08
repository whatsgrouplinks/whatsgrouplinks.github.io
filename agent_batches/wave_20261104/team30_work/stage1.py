import re, pickle, requests, json, html, time, sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
s = requests.Session()
s.mount('https://', HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=Retry(total=2, backoff_factor=2)))
union = pickle.load(open('union_set.pkl','rb'))
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

def fetch(url):
    t = time.time()
    r = s.get(url, headers=UA, timeout=60)
    print(f'FETCH {url} -> {r.status_code} {round(time.time()-t,1)}s len={len(r.text)}', flush=True)
    return r.text if r.status_code == 200 else ''

PAGES = [
    'https://whatgroups.com/whatsapp-group-links-canada/',
    'https://whatsgroupslinkspk.com/canada-whatsapp-group-links/',
    'https://wagroupshub.com/usa-whatsapp-group-links/',
    'https://groupchatlink.com/college-whatsapp-group-links/',
    'https://www.wemakescholars.com/blog/whatsapp-group-for-ms-in-us-fall',
]
allc = {}
for u in PAGES:
    try:
        h = fetch(u)
        codes = CODE_RE.findall(h)
        new = [c for c in codes if c not in union and c not in allc]
        for c in new:
            allc[c] = u
        print(f'  codes={len(codes)} fresh_new={len(new)}', flush=True)
    except Exception as e:
        print(f'  FAIL {u}: {repr(e)[:100]}', flush=True)
json.dump(allc, open('candidates_stage1.json','w'))
print('TOTAL fresh candidates:', len(allc), flush=True)
