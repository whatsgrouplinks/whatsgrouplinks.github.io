# TEAM 01 — wave 20261114, tglinkhub resume (leaf team, no subagents).
# Slice as assigned: verify ONLY codes not already verified-live/dead/dup in
# wave_20261112/verify2_results_20261112.jsonl; skip any code in the union
# (.existing_codes.json). Derivation (recomputed 2026-11-14, see summary):
#   tg_fresh pool = 13,147 codes; decided across Nov10+Nov11+Nov12 verify2
#   files = 13,147 (live 6,763 / dead 6,322 / pending 62). The Nov12 file
#   itself holds 11,587 decided rows (live 5,967 / dead 5,620), 0 undecided.
#   The only undecided codes in the pool are the 62 pending ones; 3 are
#   union dupes (no fetch), 59 to verify here. Wave_20261113 team04 already
#   re-verified those 59 (58 dead, 1 live-excluded); this run re-verifies
#   them INDEPENDENTLY (fresh evidence, not trusting the prior verdict).
#   PLUS the 6 codes in the wider tglinkhub universe (recs/code2src/fresh)
#   that were never verified AND are not in the union: the 7
#   tg_name_exclusions codes minus the 1 already in the union. Those 6 are
#   the only never-verified, non-union tglinkhub codes that exist.
#   Total fetches: 59 + 6 = 65, plus 2 controls.
#   Parent's "~2,394 unverified" matches NO derivable count (closest:
#   2,144 live-not-in-union; 1,990 f12-live-not-in-union; 2,203 live-not-
#   union + pending-not-union). Reported honestly in the summary.
# Method (per task): one persistent requests.Session per worker thread
# (keep-alive reuse, NOT a fresh session per code), browser UA, 75s timeout.
# LIVE = HTTP 200 + non-empty og:title only (og:description is always the
# generic 'WhatsApp Group Invite'). Empty og:title -> 2 spaced retries
# before dead. HTTP 429 / transport failure -> PENDING, never dead.
import json, re, time, threading, html as H
import requests
from concurrent.futures import ThreadPoolExecutor

W14 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
W12 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
W11 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/'
RAW = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
BASE = '/home/hatch/workspace/whatsapp-groups-site/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

# --- build todo ---
union = set(json.load(open(f'{BASE}.existing_codes.json')))
done = {}
for p in (f'{RAW}verify2_results.jsonl', f'{W11}verify2_results_20261111.jsonl',
          f'{W12}verify2_results_20261112.jsonl'):
    try:
        for line in open(p):
            d = json.loads(line); done[d['code']] = d
    except FileNotFoundError:
        pass
pending = [c for c, v in done.items() if v['status'] == 'pending']
pending_dupes = [c for c in pending if c in union]
pending_todo = sorted(c for c in pending if c not in union)
# never-verified, non-union codes in the wider tglinkhub universe
recs = json.load(open(f'{RAW}tg_code_recs.json'))
c2 = json.load(open(f'{RAW}tg_code2src.json'))
fresh = json.load(open(f'{RAW}tg_fresh_codes.json'))
universe = set(recs) | set(c2) | set(fresh)
never_todo = sorted(c for c in universe if c not in done and c not in union)
todo = pending_todo + [c for c in never_todo if c not in pending_todo]
print(f"pending total={len(pending)} dupes-in-union={len(pending_dupes)} "
      f"pending-to-verify={len(pending_todo)} never-verified-non-union={len(never_todo)} "
      f"todo={len(todo)}", flush=True)
json.dump({'pending_dupes': pending_dupes, 'pending_todo': pending_todo,
           'never_todo': never_todo, 'todo': todo},
          open(f'{W14}team01-todo.json', 'w'), ensure_ascii=False, indent=1)

ogpat = re.compile(r'<meta[^>]*property=[\"\']og:title[\"\'][^>]*content=[\"\']([^\"\']*)', re.I)
ogpat2 = re.compile(r'<meta[^>]*content=[\"\']([^\"\']*)[\"\'][^>]*property=[\"\']og:title[\"\']', re.I)

_tls = threading.local()
def session():
    s = getattr(_tls, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        _tls.s = s
    return s

def fetch(code):
    try:
        r = session().get(f'https://chat.whatsapp.com/{code}', timeout=75)
        return r.status_code, r.text, ''
    except Exception as e:
        return 0, '', f'{type(e).__name__}: {str(e)[:120]}'

def og_title(body):
    m = ogpat.search(body) or ogpat2.search(body)
    return H.unescape(m.group(1)).strip() if m else ''

def check(code):
    """Returns result dict. Empty og:title on a full 200 body: 2 spaced
    retries (3s, 10s) then dead. 429 / transport failure: retries then PENDING."""
    last_err = ''
    for attempt in range(3):
        http, body, err = fetch(code)
        if http == 429:
            last_err = 'http 429 rate-limited'
            if attempt < 2:
                time.sleep(60); continue
            return {'code': code, 'status': 'pending', 'http': 429,
                    'og_title': '', 'reason': last_err}
        if http == 0 or not body.strip():
            last_err = f'transport: http={http} body_len={len(body)} {err}'
            if attempt < 2:
                time.sleep([5, 20][attempt]); continue
            return {'code': code, 'status': 'pending', 'http': http,
                    'og_title': '', 'reason': last_err}
        title = og_title(body)
        if http == 200 and title:
            return {'code': code, 'status': 'live', 'http': http, 'og_title': title}
        if http == 200 and not title:
            last_err = 'empty og:title'
            if attempt < 2:
                time.sleep([3, 10][attempt]); continue
            return {'code': code, 'status': 'dead', 'http': http, 'og_title': '',
                    'reason': 'empty og:title after 3 attempts'}
        if http in (500, 502, 503, 504):
            last_err = f'http {http}'
            if attempt < 2:
                time.sleep([5, 20][attempt]); continue
            return {'code': code, 'status': 'dead', 'http': http, 'og_title': title,
                    'reason': last_err + ' after retries'}
        return {'code': code, 'status': 'dead', 'http': http, 'og_title': title,
                'reason': f'http {http}'}
    return {'code': code, 'status': 'pending', 'http': 0, 'og_title': '',
            'reason': last_err or 'transport failure'}

# --- CONTROLS FIRST, same run ---
print('CONTROL live KrDwdK8EIkB6vgauHg5M7N ...', flush=True)
ctrl_live = check('KrDwdK8EIkB6vgauHg5M7N')
print('CONTROL live ->', ctrl_live, flush=True)
print('CONTROL fabricated ZzZzZzZzZzZzZzZzZzZzZzZz ...', flush=True)
ctrl_fab = check('ZzZzZzZzZzZzZzZzZzZzZzZz')
print('CONTROL fabricated ->', ctrl_fab, flush=True)
controls = {
    'live': {'code': 'KrDwdK8EIkB6vgauHg5M7N', 'expected': 'JAY - PHP & Python Full Stack Developer',
             'got': ctrl_live.get('og_title', ''), 'http': ctrl_live.get('http'),
             'pass': ctrl_live.get('status') == 'live' and ctrl_live.get('og_title') == 'JAY - PHP & Python Full Stack Developer'},
    'fabricated': {'code': 'ZzZzZzZzZzZzZzZzZzZzZzZz', 'expected': '',
                   'got': ctrl_fab.get('og_title', ''), 'http': ctrl_fab.get('http'),
                   'pass': ctrl_fab.get('status') == 'dead' and ctrl_fab.get('og_title') == ''},
}
print('CONTROLS:', json.dumps(controls, ensure_ascii=False), flush=True)
if not (controls['live']['pass'] and controls['fabricated']['pass']):
    json.dump({'controls': controls, 'error': 'CONTROLS FAILED - STOPPED, no verification run'},
              open(f'{W14}team01-controls.json', 'w'), ensure_ascii=False, indent=1)
    raise SystemExit('CONTROLS FAILED - stopping')
json.dump({'controls': controls}, open(f'{W14}team01-controls.json', 'w'),
          ensure_ascii=False, indent=1)

# --- verify todo ---
lock = threading.Lock()
fout = open(f'{W14}team01-verify-results.jsonl', 'w')
n = [0]; t0 = time.time()
def work(code):
    r = check(code)
    with lock:
        fout.write(json.dumps(r, ensure_ascii=False) + '\n'); fout.flush()
        n[0] += 1
        if n[0] % 10 == 0:
            print(f"{n[0]}/{len(todo)} elapsed {time.time()-t0:.0f}s", flush=True)
    time.sleep(0.5)

with ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(work, todo))
fout.close()
print(f"DONE {n[0]} elapsed {time.time()-t0:.0f}s", flush=True)
