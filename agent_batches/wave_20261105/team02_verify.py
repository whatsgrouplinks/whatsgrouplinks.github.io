import json, re, subprocess, time, random, threading, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
RESULTS = WAVE + '/team02-progress.jsonl'
PROGRESS = WAVE + '/team02-verify.log'

with open(WAVE + '/team02_slice.json') as f:
    todo_all = json.load(f)
preblocked = set(json.load(open(WAVE + '/team02_preblocked.json')))
todo = [c for c in todo_all if c not in preblocked]

done = {}
if os.path.exists(RESULTS):
    with open(RESULTS) as f:
        for line in f:
            try:
                r = json.loads(line)
                done[r['code']] = r
            except Exception:
                pass
remaining = [c for c in todo if c not in done]
print(f'total={len(todo)} done={len(done)} remaining={len(remaining)} preblocked={len(preblocked)}', flush=True)

TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"')
lock = threading.RLock()  # RLock: log() is called while holding lock at progress milestones
f_out = open(RESULTS, 'a')
backoff_until = [0.0]
count = [len(done)]

def log(msg):
    with lock:
        with open(PROGRESS, 'a') as pf:
            pf.write(f'{time.time():.0f} {msg}\n')

def fetch_once(code):
    try:
        r = subprocess.run(
            ['curl','-sL','-A','Mozilla/5.0','--max-time','30','--max-filesize','32768',
             '-w','\n%{http_code}','https://chat.whatsapp.com/'+code],
            capture_output=True, text=True, timeout=40)
        out = r.stdout
        if '\n' in out:
            body, status = out.rsplit('\n', 1)
        else:
            body, status = out, '000'
        status = status.strip()
        m = TITLE_RE.search(body)
        title = html.unescape(m.group(1)).strip() if m else ''
        return status, title
    except Exception:
        return '000', ''

def verify(code):
    while True:
        with lock:
            wait = backoff_until[0] - time.time()
        if wait > 0:
            time.sleep(wait)
        else:
            break
    status, title = fetch_once(code)
    if status == '429':
        with lock:
            backoff_until[0] = time.time() + 180
        log(f'429 hit on {code}, backing off 180s')
        time.sleep(180)
        status, title = fetch_once(code)
    if status == '000' or status == '':
        time.sleep(random.uniform(2, 5))
        status, title = fetch_once(code)
    if status == '200' and title:
        verdict, note = 'verified', 'og:title ok'
    elif status == '429':
        verdict, note = 'pending', 'http-429'
    elif status == '200':
        verdict, note = 'pending', 'http-200-empty-title'
    else:
        verdict, note = 'pending', f'http-{status}'
    rec = {'code': code, 'status': status, 'title': title, 'verdict': verdict, 'note': note}
    with lock:
        f_out.write(json.dumps(rec, ensure_ascii=False) + '\n')
        f_out.flush()
        os.fsync(f_out.fileno())
        count[0] += 1
        if count[0] % 50 == 0:
            log(f"progress {count[0]}/{len(todo)}")
            print(f"progress {count[0]}/{len(todo)}", flush=True)
    time.sleep(0.5)
    return rec

t0 = time.time()
with ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(verify, remaining))
f_out.close()
log(f'DONE total={len(todo)} elapsed={time.time()-t0:.0f}s')
print(f'DONE total={len(todo)} elapsed={time.time()-t0:.0f}s', flush=True)
