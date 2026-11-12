# TEAM 03 — wave 20261112, tglinkhub verify2 resume
# Adapted from wave_20261111/verify2_team31.py (same inputs, same sort order,
# same results schema, same retry/dead logic) with ONE change: curl subprocess
# replaced by a per-thread persistent requests.Session (task-prescribed method;
# curl was ~5.8s/code at 6 workers, warm session requests are ~0.5s/code).
# Controls verified 2026-11-12: known-live KrDwdK8EIkB6vgauHg5M7N -> og:title
# present; fabricated ZZZZZZZZZZZZZZZZZZZZZZ -> og:title empty; og:description
# is the constant string 'WhatsApp Group Invite' on live AND dead pages, so it
# is NOT a valid fallback — live = non-empty og:title only.
import json, re, time, threading, html as H
import requests
from concurrent.futures import ThreadPoolExecutor

RAW = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
OUT = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
W11 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

fresh = json.load(open(f'{RAW}tg_fresh_codes.json'))
recs = json.load(open(f'{RAW}tg_code_recs.json'))
excl = json.load(open(f'{RAW}tg_name_exclusions.json'))
keep = [c for c in fresh if c not in excl]
MINED_NOV9 = {'whatsapp-group-links', 'kerala-group', 'malayalam-whatsapp'}
def sortkey(c):
    r = recs.get(c, {})
    slug = r.get('slug', '') if r else ''
    mined = 1 if slug in MINED_NOV9 else 0
    return (mined, slug)
keep.sort(key=sortkey)
print("to verify:", len(keep), flush=True)

done = {}
for path in (f'{RAW}verify2_results.jsonl',
             f'{W11}verify2_results_20261111.jsonl',
             f'{OUT}verify2_results_20261112.jsonl'):
    try:
        for line in open(path):
            d = json.loads(line); done[d['code']] = d
    except FileNotFoundError:
        pass
todo = [c for c in keep if c not in done]
print("already done (Nov10 + Nov11 + this run):", len(done), "todo:", len(todo), flush=True)

ogpat = re.compile(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', re.I)
ogpat2 = re.compile(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', re.I)

# Fresh Session per request: WhatsApp 429-throttles LONG-LIVED keep-alive
# sessions (persistent-session runs decayed to 0.11/s with 429 storms);
# fresh sessions measured 0.71/s sustained, 0 x 429 over probes.
def fetch(code):
    s = requests.Session()
    s.headers.update({'User-Agent': UA})
    try:
        r = s.get(f'https://chat.whatsapp.com/{code}', timeout=60)
        return r.status_code, r.text, 0, ''
    except Exception as e:
        return 0, '', -1, f'{type(e).__name__}: {str(e)[:100]}'
    finally:
        s.close()

def check(code):
    last_err = ''
    for attempt in range(3):
        http, body, rc, err = fetch(code)
        if http == 0 or not body.strip():
            last_err = f'transport: http={http} body_len={len(body)} rc={rc} {err}'
            if attempt < 2:
                # HTTP 429 = WhatsApp rate-limit (shared egress IP, whole wave
                # verifying at once): back off LONG so the run self-paces
                # through the storm instead of burning attempts.
                time.sleep([60, 120][attempt] if http == 429 else [3, 10][attempt]); continue
            return {'code': code, 'status': 'pending', 'http': http, 'og_title': '', 'reason': last_err}
        og = ogpat.search(body) or ogpat2.search(body)
        ogtitle = H.unescape(og.group(1)).strip() if og else ''
        if http == 200 and ogtitle:
            return {'code': code, 'status': 'live', 'http': http, 'og_title': ogtitle}
        if http == 200 and not ogtitle:
            # Full 200 body with empty og:title is a deterministic dead page
            # (verified: dead pages return full ~220KB bodies with no og:title);
            # retries only help transport failures, not this case.
            return {'code': code, 'status': 'dead', 'http': http, 'og_title': '', 'reason': 'empty og:title on full 200 body'}
        return {'code': code, 'status': 'dead', 'http': http, 'og_title': ogtitle, 'reason': f'http {http}'}
    return {'code': code, 'status': 'pending', 'http': 0, 'og_title': '', 'reason': last_err or 'transport failure'}

lock = threading.Lock()
fout = open(f'{OUT}verify2_results_20261112.jsonl', 'a')
n = [0]; t0 = time.time()
def work(code):
    r = check(code)
    with lock:
        fout.write(json.dumps(r, ensure_ascii=False) + '\n'); fout.flush()
        n[0] += 1
        if n[0] % 200 == 0:
            print(f"{n[0]}/{len(todo)} elapsed {time.time()-t0:.0f}s", flush=True)
    time.sleep(0.5)

with ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(work, todo))
fout.close()
print("DONE", n[0], "elapsed", time.time() - t0, flush=True)
