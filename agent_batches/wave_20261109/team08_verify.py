import json, re, subprocess, time, threading, os, html
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
res = json.load(open('team08_fetch_raw.json'))
existing = set(json.load(open('../../.existing_codes.json')))
pre = set(json.load(open('team08_codes.json')))
allcodes = set()
for r in res: allcodes.update(r['codes'])
codes = sorted((allcodes | pre) - existing)
print('to verify:', len(codes), flush=True)

TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
TITLE_RE2 = re.compile(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", re.I)
DESC_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
DESC_RE2 = re.compile(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:description\"", re.I)

lock = threading.Lock()
last_start = [0.0]
def gated_start():
    with lock:
        now = time.time()
        wait = 0.6 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()

def check(code):
    gated_start()
    url = 'https://chat.whatsapp.com/' + code
    try:
        r = subprocess.run(['curl','-sL','--max-time','15','-A',UA,'-w','\n__HTTP__:%{http_code}',url],
                           capture_output=True, text=True, timeout=25)
        out = r.stdout or ''
        m = re.search(r'__HTTP__:(\d+)\s*$', out)
        http = int(m.group(1)) if m else 0
        body = out[:m.start()] if m else out
        t = TITLE_RE.search(body) or TITLE_RE2.search(body)
        d = DESC_RE.search(body) or DESC_RE2.search(body)
        title = html.unescape(t.group(1)).strip() if t else ''
        desc = html.unescape(d.group(1)).strip() if d else ''
        return {'code': code, 'http': http, 'title': title, 'desc': desc}
    except Exception as e:
        return {'code': code, 'http': 0, 'title': '', 'desc': '', 'error': str(e)[:80]}

done_file = 'team08_verify_progress.json'
done = {}
if os.path.exists(done_file):
    done = {x['code']: x for x in json.load(open(done_file))}
    print('resuming, already done:', len(done), flush=True)
todo = [c for c in codes if c not in done]
print('todo:', len(todo), flush=True)

def save():
    with lock:
        json.dump(list(done.values()), open(done_file, 'w'), ensure_ascii=False, indent=0)

count = [0]
def work(code):
    r = check(code)
    with lock:
        done[code] = r
        count[0] += 1
        if count[0] % 50 == 0:
            save()
            live = sum(1 for v in done.values() if v.get('http')==200 and v.get('title'))
            print(f"{count[0]+len([c for c in codes if c in done])-count[0]}/{len(codes)} checked, live so far: {live}", flush=True)
    return r

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
save()
live = sum(1 for v in done.values() if v.get('http')==200 and v.get('title'))
amb = sum(1 for v in done.values() if v.get('http')==200 and not v.get('title'))
dead = sum(1 for v in done.values() if v.get('http') not in (200,0))
err = sum(1 for v in done.values() if v.get('http')==0)
print(f'DONE total={len(done)} live={live} ambiguous200={amb} non200={dead} transport0={err}', flush=True)
