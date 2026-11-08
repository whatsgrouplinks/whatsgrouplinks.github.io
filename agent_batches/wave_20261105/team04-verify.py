#!/usr/bin/env python3
"""team04: re-verify 2,917 ongrupos codes (wave 20261104 team34 pending) against
chat.whatsapp.com. Control passed (live code -> non-empty og:title; bogus -> empty).
4 workers, 0.5-2s per-worker delay, curl --max-time 20. Checkpoints to
team04-progress.jsonl (one JSON line per code, resumable)."""
import json, re, subprocess, threading, time, random, html, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
PENDING = os.path.join(BASE, '..', 'wave_20261104', 'team34-unverified-pending.json')
UNION = os.path.join(BASE, 'dedupe_union.json')
PROG = os.path.join(BASE, 'team04-progress.jsonl')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
OG_RE = re.compile(r'og:title"\s+content="([^"]*)"', re.I)

def code_of(rec):
    return rec['invite'].split('chat.whatsapp.com/')[-1].replace('invite/', '').strip('/')

backoff_until = [0.0]
backoff_lock = threading.Lock()

def check(code):
    url = 'https://chat.whatsapp.com/' + code
    try:
        r = subprocess.run(['curl', '-sL', '-A', UA, '--max-time', '20',
                            '-w', '\nHTTP:%{http_code}', url],
                           capture_output=True, text=True, timeout=30)
        out = r.stdout
        m = out.rsplit('HTTP:', 1)
        http = m[1].strip() if len(m) > 1 else '?'
        body = m[0] if len(m) > 1 else out
        if http == '429':
            with backoff_lock:
                backoff_until[0] = time.time() + 180
            return None, 'http-429'
        mm = OG_RE.search(body)
        title = html.unescape(mm.group(1)).strip() if mm else ''
        if title:
            return title, 'verified'
        if http not in ('200',):
            return '', 'http-' + http
        return '', 'empty-og-title'
    except subprocess.TimeoutExpired:
        return '', 'timeout'
    except Exception as e:
        return '', 'error:' + type(e).__name__

def main():
    pending = json.load(open(PENDING))
    union = set(json.load(open(UNION)))
    done = {}
    if os.path.exists(PROG):
        for line in open(PROG):
            line = line.strip()
            if line:
                d = json.loads(line)
                done[d['code']] = d
    todo = [r for r in pending if code_of(r) not in union and code_of(r) not in done]
    print(f'total={len(pending)} in-union-dropped={sum(1 for r in pending if code_of(r) in union)} already-done={len(done)} todo={len(todo)}', flush=True)
    lock = threading.Lock()
    counter = [0]
    fout = open(PROG, 'a')

    def worker(recs):
        for rec in recs:
            # respect global 429 backoff
            while True:
                with backoff_lock:
                    wait = backoff_until[0] - time.time()
                if wait > 0:
                    time.sleep(min(wait, 30))
                else:
                    break
            time.sleep(random.uniform(0.5, 2.0))
            c = code_of(rec)
            title, status = check(c)
            d = {'code': c, 'name': rec.get('name', ''), 'category': rec.get('category', ''),
                 'country': rec.get('country', 'BR'), 'description': rec.get('description', ''),
                 'invite': rec['invite'], 'image': rec.get('image', ''),
                 'og_title': title, 'status': status}
            with lock:
                fout.write(json.dumps(d, ensure_ascii=False) + '\n')
                fout.flush()
                counter[0] += 1
                if counter[0] % 100 == 0:
                    v = sum(1 for x in done.values() if x['status'] == 'verified')
                    print(f'progress {counter[0]}/{len(todo)} elapsed {time.time()-t0:.0f}s', flush=True)

    t0 = time.time()
    chunks = [todo[i::4] for i in range(4)]
    threads = [threading.Thread(target=worker, args=(ch,)) for ch in chunks]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    fout.close()
    print(f'DONE elapsed {time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    main()
