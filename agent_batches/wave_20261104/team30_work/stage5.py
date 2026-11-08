import re, requests, json, html, sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
OG_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.I)

pairs = json.load(open('candidates_r2.json'))
# out-of-slice India state groups: skip verification, leave for other teams
OUT = {'EVFvInDmgTGDFy17cHaApk','IWnTNrFjVHkG6LBbEzWoVi','CfUZi4Sa5NXEIwzbiiXHVh',
       'HNyt1X6H6DhG3FYf5mN3yq','D7RuSp3nA2O4L841kF0gpV','Fi1eGoDOn7x0JIo5YHVmFT',
       'JoIssDNNJDrK6LxVXtms6D','BoICxmHuVFh9j3X583wqgI','JCN03YlRcj2HN4fSUZr1Jw',
       'Eohj8fX5yiKFUSyGYVYCem'}

def check(item):
    code, (name, tag) = item
    s = requests.Session()
    s.mount('https://', HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=Retry(total=1, backoff_factor=1)))
    try:
        r = s.get(f'https://chat.whatsapp.com/{code}', headers=UA, timeout=55)
        m = OG_RE.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return (code, 'ok' if title else 'dead', title)
    except Exception as e:
        return (code, 'transport', repr(e)[:80])

todo = [(c, v) for c, v in pairs.items() if c not in OUT]
results = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    for code, status, title in ex.map(check, todo):
        results[code] = {'status': status, 'og_title': title, 'src_name': pairs[code][0], 'src': pairs[code][1]}
        print(code, status, '|', title[:60], '|', pairs[code][0][:45], file=sys.stderr, flush=True)

print(json.dumps(results))
ok = sum(1 for v in results.values() if v['status']=='ok')
print(f'VERIFIED={ok} DEAD={sum(1 for v in results.values() if v["status"]=="dead")} TRANSPORT={sum(1 for v in results.values() if v["status"]=="transport")} SKIPPED_OUT_OF_SLICE={len(OUT)}', file=sys.stderr, flush=True)
