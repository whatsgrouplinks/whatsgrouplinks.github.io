#!/usr/bin/env python3
"""team17: verify candidate codes via chat.whatsapp.com og:title.
Control (2026-11-05): live code KrDwdK8EIkB6vgauHg5M7N -> og:title non-empty
('JAY - PHP & Python Full Stack Developer'); fake code -> og:title ''.
Non-empty og:title = VERIFIED, else PENDING. 4 workers, 0.5-2s delays,
one retry pass for empties/errors after a 60s pause.
"""
import json, subprocess, re, random, time, os
from concurrent.futures import ThreadPoolExecutor

UA = 'Mozilla/5.0'
OUT = '/tmp/t17_verify.json'

def check(code):
    time.sleep(random.uniform(0.5, 2.0))
    try:
        r = subprocess.run(['curl', '-sL', '-A', UA, '--max-time', '20',
                            f'https://chat.whatsapp.com/{code}'],
                           capture_output=True, text=True, timeout=30)
        body = r.stdout or ''
        m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        og = m.group(1) if m else None
        t = re.search(r'<title>([^<]*)</title>', body)
        return {'code': code, 'og_title': og, 'title_tag': t.group(1) if t else None,
                'bytes': len(body), 'rc': r.returncode, 'error': None}
    except Exception as e:
        return {'code': code, 'og_title': None, 'title_tag': None,
                'bytes': 0, 'rc': -1, 'error': str(e)}

def save(results):
    tmp = OUT + '.tmp'
    json.dump(results, open(tmp, 'w'), ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)

def run_pass(codes, results):
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(check, codes):
            results[res['code']] = res
            save(results)
            print(f"{res['code']} og={res['og_title']!r} bytes={res['bytes']}", flush=True)

def main():
    items = json.load(open('/tmp/t17_verify_list.json'))
    codes = [it['code'] for it in items]
    results = {}
    if os.path.exists(OUT):
        results = json.load(open(OUT))
    todo = [c for c in codes if c not in results]
    print(f'verify list {len(codes)}; pass1 todo {len(todo)}', flush=True)
    run_pass(todo, results)
    empties = [c for c in codes
               if not (results.get(c, {}).get('og_title') or '').strip()]
    print(f'pass1 done; empties/errors to retry: {len(empties)}', flush=True)
    if empties:
        print('pausing 60s before retry pass...', flush=True)
        time.sleep(60)
        run_pass(empties, results)
    verified = [c for c in codes if (results.get(c, {}).get('og_title') or '').strip()]
    print(f'DONE verified={len(verified)} pending={len(codes)-len(verified)}', flush=True)
    print('verified codes:', verified, flush=True)

if __name__ == '__main__':
    main()
