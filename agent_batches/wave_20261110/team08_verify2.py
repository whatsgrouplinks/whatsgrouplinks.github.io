"""Keep-alive verifier for team08 slice 8 (wave 20261110).
Priority order: never-seen codes first, then prior-live, then prior-dead re-checks.
3 workers, >=0.6s between request starts, 15s timeout, 2 spaced retries on empty og:title.
Saves progress every 5 results so a killed run resumes cleanly.
"""
import json, re, time, threading, os, html
from concurrent.futures import ThreadPoolExecutor
import requests

WD = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

new_codes = json.load(open(os.path.join(WD, 'team08_new_codes.json')))
seen_codes = json.load(open(os.path.join(WD, 'team08_seen_codes.json')))
prior_v = {x['code']: x for x in json.load(open('../wave_20261109/team08_verify_final.json'))}
prior_live = [c for c in seen_codes if prior_v.get(c, {}).get('http') == 200 and prior_v.get(c, {}).get('title')]
prior_dead = [c for c in seen_codes if c not in prior_live]
order = sorted(new_codes) + sorted(prior_live) + sorted(prior_dead)
print('order: new=%d prior_live=%d prior_dead=%d total=%d' % (len(new_codes), len(prior_live), len(prior_dead), len(order)), flush=True)

TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
TITLE_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)
DESC_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
DESC_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:description"', re.I)

lock = threading.RLock()
last_start = [0.0]
def gated_start():
    with lock:
        now = time.time()
        wait = 0.6 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()

local = threading.local()
def get_session():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                          'Accept-Language': 'en-US,en;q=0.9', 'Accept-Encoding': 'gzip, deflate'})
        local.s = s
    return s

def parse(body):
    t = TITLE_RE.search(body) or TITLE_RE2.search(body)
    d = DESC_RE.search(body) or DESC_RE2.search(body)
    title = html.unescape(t.group(1)).strip() if t else ''
    desc = html.unescape(d.group(1)).strip() if d else ''
    return title, desc

def check_once(code):
    gated_start()
    url = 'https://chat.whatsapp.com/' + code
    for attempt in range(2):  # one reconnect retry on transport exception only
        try:
            s = get_session()
            r = s.get(url, timeout=15)
            title, desc = parse(r.text)
            return {'code': code, 'http': r.status_code, 'title': title, 'desc': desc}
        except requests.exceptions.RequestException as e:
            # drop dead session, retry once
            try:
                local.s.close()
            except Exception:
                pass
            local.s = None
            if attempt == 1:
                return {'code': code, 'http': 0, 'title': '', 'desc': '', 'error': type(e).__name__ + ': ' + str(e)[:100]}
            time.sleep(1)
    return {'code': code, 'http': 0, 'title': '', 'desc': '', 'error': 'unreachable'}

def check(code):
    r = check_once(code)
    attempts = 1
    while r.get('http') == 200 and not r.get('title') and attempts < 3:
        time.sleep(5)
        r = check_once(code)
        attempts += 1
    r['attempts'] = attempts
    return r

done_file = os.path.join(WD, 'team08_verify_progress.json')
done = {}
if os.path.exists(done_file):
    done = {x['code']: x for x in json.load(open(done_file))}
    print('resuming, already done:', len(done), flush=True)
todo = [c for c in order if c not in done]
print('todo:', len(todo), flush=True)

def save():
    with lock:
        tmp = done_file + '.tmp'
        json.dump(list(done.values()), open(tmp, 'w'), ensure_ascii=False, indent=0)
        os.replace(tmp, done_file)

count = [0]
def work(code):
    r = check(code)
    with lock:
        done[code] = r
        count[0] += 1
        if count[0] % 5 == 0:
            save()
            live = sum(1 for v in done.values() if v.get('http') == 200 and v.get('title'))
            print(f"checked {len(done)}/{len(order)} live: {live} elapsed-checks: {count[0]}", flush=True)
    return r

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
save()
live = sum(1 for v in done.values() if v.get('http') == 200 and v.get('title'))
amb = sum(1 for v in done.values() if v.get('http') == 200 and not v.get('title'))
dead = sum(1 for v in done.values() if v.get('http') not in (200, 0))
err = sum(1 for v in done.values() if v.get('http') == 0)
print(f'DONE total={len(done)} live={live} empty-title-200={amb} non200={dead} transport0={err}', flush=True)
json.dump(list(done.values()), open(os.path.join(WD, 'team08_verify.json'), 'w'), ensure_ascii=False, indent=1)
