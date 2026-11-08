"""TEAM15: verify exact-cased chat codes with keep-alive sessions (resume 200 done)."""
import json, re, sys, threading, time, random, html as htmllib
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

T = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team15'
UNION = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/dedupe_union.json'
T30R_OUT = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/team30R-groupsinvite.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
STOP = {'flag': False}

_local = threading.local()
def sess():
    s = getattr(_local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _local.s = s
    return s

def check(code):
    if STOP['flag']:
        return code, 'stopped', ''
    try:
        time.sleep(0.3 + random.random() * 0.6)
        r = sess().get(f'https://chat.whatsapp.com/{code}', timeout=60, allow_redirects=True)
        if r.status_code == 429:
            STOP['flag'] = True
            return code, 'rate-limited', ''
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title = htmllib.unescape(m.group(1)).strip() if m else ''
        # WhatsApp serves group pages at this URL; empty og:title = dead link (HTTP 200 proves nothing)
        return code, ('verified' if title else 'dead'), title
    except Exception as e:
        # rebuild session on transport error (keep-alive failure)
        try:
            s = sess(); s.close()
        except Exception:
            pass
        _local.s = None
        return code, 'transport', type(e).__name__

def main():
    classify = json.load(open(f'{T}/classify.json'))
    union = set(x.lower() for x in json.load(open(UNION)))
    # also exclude Nov-3 team30R banked codes (they were finalized after the Nov-4 union was built)
    try:
        t30 = json.load(open(T30R_OUT))
        union |= set(re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', i['invite']).group(1).lower() for i in t30)
    except Exception as e:
        print('team30R exclusion unavailable:', e, flush=True)

    code_to_slug = {}
    for slug, v in classify.items():
        if v.get('kind') == 'chat' and re.match(r'^[A-Za-z0-9]{20,24}$', v.get('code', '')):
            key = v['code'].lower()
            if key in union:
                continue
            if key not in code_to_slug:
                code_to_slug[key] = (slug, v['code'])
    codes = list(code_to_slug.values())
    print(f'codes to verify (union-excluded): {len(codes)}', flush=True)

    results = {}
    try:
        results = json.load(open(f'{T}/verify.json'))
    except Exception:
        pass
    todo = [(slug, code) for slug, code in codes if code not in results]
    print(f'resuming with {len(results)} done, todo={len(todo)}', flush=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(check, code): (slug, code) for slug, code in todo}
        n = 0
        for f in as_completed(futs):
            slug, code = futs[f]
            code, status, title = f.result()
            results[code] = {'status': status, 'title': title, 'slug': slug}
            n += 1
            if STOP['flag']:
                print('RATE LIMITED - stopping', flush=True)
                break
            if n % 50 == 0:
                json.dump(results, open(f'{T}/verify.json', 'w'))
                vs = sum(1 for r in results.values() if r['status'] == 'verified')
                print(f'{n}/{len(todo)} verified-so-far={vs}', flush=True)
    json.dump(results, open(f'{T}/verify.json', 'w'))
    vs = sum(1 for r in results.values() if r['status'] == 'verified')
    print(f'FINAL: checked={len(results)} verified={vs} stopped={STOP["flag"]}', flush=True)

if __name__ == '__main__':
    main()
