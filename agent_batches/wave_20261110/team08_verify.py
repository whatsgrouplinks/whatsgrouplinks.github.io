import json, re, subprocess, time, threading, os, html
from concurrent.futures import ThreadPoolExecutor

WD = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

res = json.load(open(os.path.join(WD, 'team08_fetch_raw.json')))
union = set(json.load(open('union_codes.json')))

# code -> occurrences
occ = {}
for r in res:
    for e in r['entries']:
        occ.setdefault(e['code'], []).append({
            'url': r['url'], 'source': r['source'],
            'context': e['context'], 'adult_flag': e['adult_flag']})

SCAM_RE = re.compile(r'b-?love|forsage|shey(i|y)|paypal loader|bitfinex|counterfeit|crypto.?doubling|carding|double (your|the) (money|investment|usdt|trx|btc)|airdrop', re.I)
ADULT_CTX_RE = re.compile(r'🔞|🥵|\bsexy\b|hookup|escort|\bporn\b|xxx|\bpussy\b|seksi|bideos|18\+\s*(hot|adult|sex|video)|hot\s+(girls?|bhabhi|aunty)', re.I)

exclusions = []
candidates = []
for code, lst in sorted(occ.items()):
    if code in union:
        continue
    ctx_all = ' '.join(x['context'] for x in lst)
    if any(x['adult_flag'] for x in lst):
        exclusions.append({'code': code, 'reason': 'groupjoin Adult-category item (tags include Adult/18+/Hot) - never verified'})
        continue
    if SCAM_RE.search(ctx_all):
        exclusions.append({'code': code, 'reason': 'scam pattern in listing context: ' + (SCAM_RE.search(ctx_all).group(0))})
        continue
    if ADULT_CTX_RE.search(ctx_all):
        exclusions.append({'code': code, 'reason': 'adult-sexual signal in listing context: ' + (ADULT_CTX_RE.search(ctx_all).group(0))})
        continue
    candidates.append(code)

print('fresh codes:', sum(1 for c in occ if c not in union))
print('prescreen exclusions:', len(exclusions))
print('to verify:', len(candidates), flush=True)
json.dump(exclusions, open(os.path.join(WD, 'team08_prescreen_exclusions.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({c: occ[c] for c in candidates}, open(os.path.join(WD, 'team08_to_verify_ctx.json'), 'w'), ensure_ascii=False, indent=1)

TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
TITLE_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)
DESC_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
DESC_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:description"', re.I)

lock = threading.Lock()
last_start = [0.0]
def gated_start():
    with lock:
        now = time.time()
        wait = 0.6 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()

def check_once(code):
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

def check(code):
    r = check_once(code)
    attempts = 1
    # empty og:title on HTTP 200 -> 2 spaced retries
    while r.get('http') == 200 and not r.get('title') and attempts < 3:
        time.sleep(5)
        r2 = check_once(code)
        attempts += 1
        r = r2
    r['attempts'] = attempts
    return r

done_file = os.path.join(WD, 'team08_verify_progress.json')
done = {}
if os.path.exists(done_file):
    done = {x['code']: x for x in json.load(open(done_file))}
    print('resuming, already done:', len(done), flush=True)
todo = [c for c in candidates if c not in done]
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
            live = sum(1 for v in done.values() if v.get('http') == 200 and v.get('title'))
            print(f"checked {len(done)}/{len(candidates)} live so far: {live}", flush=True)
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
