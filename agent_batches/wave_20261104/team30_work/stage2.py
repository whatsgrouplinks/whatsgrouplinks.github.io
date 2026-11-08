import re, pickle, requests, json, html, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
s = requests.Session()
s.mount('https://', HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=Retry(total=2, backoff_factor=2)))
union = pickle.load(open('union_set.pkl','rb'))
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
TAG_RE = re.compile(r'<[^>]+>')

def clean(t):
    t = html.unescape(TAG_RE.sub(' ', t))
    return re.sub(r'\s+', ' ', t).strip()

PAGES = [
    ('whatgroups_ca', 'https://whatgroups.com/whatsapp-group-links-canada/'),
    ('whatsgroupslinkspk_ca', 'https://whatsgroupslinkspk.com/canada-whatsapp-group-links/'),
    ('wemakescholars_us', 'https://www.wemakescholars.com/blog/whatsapp-group-for-ms-in-us-fall'),
    ('wabotso_au', 'https://wagroups.wabotso.com/australian-whatsapp-group-links/'),
    ('wahublink_edu', 'https://wahublink.com/education-whatsapp-group-links/'),
]

pairs = {}  # code -> [name, source_page]
for tag, url in PAGES:
    try:
        r = s.get(url, headers=UA, timeout=60)
        h = r.text
        print(f'{tag}: {r.status_code} len={len(h)}', flush=True)
        if r.status_code != 200: continue
        fn = f'html_{tag}.html'
        try:
            open(fn, 'w').write(h)
        except Exception as e:
            print(f'  (write fail {fn}: {e})', flush=True)
        # name-before-link: capture text of enclosing row/item before each link
        for m in re.finditer(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', h):
            code = m.group(1)
            if code in union or code in pairs: continue
            # look back up to 600 chars for a plausible name: nearest >...< text or table cell
            back = h[max(0, m.start()-800):m.start()]
            texts = re.findall(r'>([^<>]{3,120})<', back)
            name = ''
            for t in reversed(texts):
                t = clean(t)
                if not t: continue
                tl = t.lower()
                if any(x in tl for x in ['join', 'click here', 'link', 'whatsapp group links', 'join now', 'join group']):
                    continue
                if len(t) < 3: continue
                name = t
                break
            pairs[code] = [name, tag]
    except Exception as e:
        print(f'{tag} FAIL: {repr(e)[:100]}', flush=True)

import sys
sys.stdout.write(json.dumps(pairs))
sys.stdout.write('\n')
print('TOTAL:', len(pairs), file=sys.stderr, flush=True)
for c,(n,t) in pairs.items():
    print(c, '|', n[:70], '|', t, file=sys.stderr, flush=True)
