import json, re, subprocess, time, threading, os, html, sys
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
ATTEMPT = sys.argv[1]  # e.g. retry1 / retry2
SRC = sys.argv[2]      # file whose ambiguous codes to retry
OUT = f'team08_verify_{ATTEMPT}.json'

prev = json.load(open(SRC))
codes = sorted(v['code'] for v in prev if v.get('http') == 200 and not v.get('title'))
print(f'{ATTEMPT}: retrying {len(codes)} ambiguous codes from {SRC}', flush=True)

TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
TITLE_RE2 = re.compile(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", re.I)
lock = threading.RLock()
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
    try:
        r = subprocess.run(['curl','-sL','--max-time','15','-A',UA,'-w','\n__HTTP__:%{http_code}',
                            'https://chat.whatsapp.com/' + code],
                           capture_output=True, text=True, timeout=25)
        out = r.stdout or ''
        m = re.search(r'__HTTP__:(\d+)\s*$', out)
        http = int(m.group(1)) if m else 0
        body = out[:m.start()] if m else out
        t = TITLE_RE.search(body) or TITLE_RE2.search(body)
        title = html.unescape(t.group(1)).strip() if t else ''
        return {'code': code, 'http': http, 'title': title, 'attempt': ATTEMPT}
    except Exception as e:
        return {'code': code, 'http': 0, 'title': '', 'attempt': ATTEMPT, 'error': str(e)[:80]}

done = {}
if os.path.exists(OUT):
    done = {x['code']: x for x in json.load(open(OUT))}
todo = [c for c in codes if c not in done]
print('todo:', len(todo), flush=True)

def save():
    with lock:
        json.dump(list(done.values()), open(OUT, 'w'), ensure_ascii=False, indent=0)

count = [0]
def work(code):
    r = check(code)
    with lock:
        done[code] = r
        count[0] += 1
        if count[0] % 25 == 0:
            save()
            live = sum(1 for v in done.values() if v.get('http') == 200 and v.get('title'))
            print(f"checked {len(done)}/{len(codes)} recovered-live so far: {live}", flush=True)

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
save()
live = sum(1 for v in done.values() if v.get('http') == 200 and v.get('title'))
print(f'DONE {ATTEMPT} total={len(done)} recovered_live={live} still_empty={len(done)-live}', flush=True)
