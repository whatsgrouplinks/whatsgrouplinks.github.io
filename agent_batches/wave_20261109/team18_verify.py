import json, re, subprocess, time, threading
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
pool = json.load(open('team18_raw/team18_pool.json'))
try: results = json.load(open('team18_raw/team18_verify.json'))
except Exception: results = {}
print('pool', len(pool), 'already done', len(results), flush=True)
lock = threading.Lock()
last_start = [0.0]
def check(code):
    with lock:
        gap = 0.6 - (time.time() - last_start[0])
        if gap > 0: time.sleep(gap)
        last_start[0] = time.time()
    url = f'https://chat.whatsapp.com/{code}'
    try:
        r = subprocess.run(['curl','-s','-L','--max-time','20','-A',UA,'-w','\n%{http_code}',url],
                           capture_output=True, text=True, timeout=30)
        body = r.stdout or ''
        m = re.search(r'\n(\d{3})\s*$', body)
        http = int(m.group(1)) if m else 0
        body_only = body[:m.start()] if m else body
        og = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', body_only, re.I)
        if not og:
            og = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body_only, re.I)
        title = (og.group(1).strip() if og else '')
        return {'code':code,'http':http,'og_title':title,'curl_rc':r.returncode}
    except Exception as e:
        return {'code':code,'http':0,'og_title':'','curl_rc':-1,'error':str(e)[:100]}

todo = [rec for rec in pool if rec['code'] not in results]
print('todo', len(todo), flush=True)
def work(rec):
    res = check(rec['code'])
    with lock:
        results[rec['code']] = res
        json.dump(results, open('team18_raw/team18_verify.json','w'), indent=1)
    print(rec['code'], res['http'], repr(res['og_title'][:60]), flush=True)
    return res
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
print('DONE first pass:', len(results), flush=True)
