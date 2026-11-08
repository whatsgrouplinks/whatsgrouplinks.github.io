"""TEAM 30R: verify exact-cased chat codes with liveness check."""
import json, re, time, sys, html as htmllib
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
STOP = {'flag': False}  # set on 429

def check(code):
    if STOP['flag']:
        return code, 'stopped', ''
    try:
        time.sleep(0.8)
        r = requests.get(f'https://chat.whatsapp.com/{code}', headers=UA, timeout=25)
        if r.status_code == 429:
            STOP['flag'] = True
            return code, 'rate-limited', ''
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title = htmllib.unescape(m.group(1)).strip() if m else ''
        return code, ('verified' if title else 'dead'), title
    except Exception as e:
        return code, 'transport', type(e).__name__

def main():
    classify = json.load(open('/tmp/team30r/classify.json'))
    union = set(x.lower() for x in json.load(
        open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/dedupe_union.json')))
    # slug -> code for chat kinds, dedupe by code (case-insensitive), exclude union
    code_to_slug = {}
    for slug, v in classify.items():
        if v.get('kind') == 'chat' and re.match(r'^[A-Za-z0-9]{20,24}$', v.get('code', '')):
            key = v['code'].lower()
            if key in union:
                continue
            if key not in code_to_slug:
                code_to_slug[key] = (slug, v['code'])
    codes = list(code_to_slug.values())
    print(f'codes to verify: {len(codes)}', flush=True)

    results = {}
    try:
        results = json.load(open('/tmp/team30r/verify.json'))
        print(f'resuming with {len(results)} done', flush=True)
    except Exception:
        pass
    todo = [(slug, code) for slug, code in codes if code not in results]
    print(f'todo: {len(todo)}', flush=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
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
                json.dump(results, open('/tmp/team30r/verify.json', 'w'))
                vs = sum(1 for r in results.values() if r['status'] == 'verified')
                print(f'{n}/{len(todo)} verified-so-far={vs}', flush=True)
    json.dump(results, open('/tmp/team30r/verify.json', 'w'))
    vs = sum(1 for r in results.values() if r['status'] == 'verified')
    print(f'FINAL: checked={len(results)} verified={vs} stopped={STOP["flag"]}', flush=True)

if __name__ == '__main__':
    main()
