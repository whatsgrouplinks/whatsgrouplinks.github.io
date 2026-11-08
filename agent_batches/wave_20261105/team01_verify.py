#!/usr/bin/env python3
"""team01 wave 20261105: verify groups1 pool A codes[0:5892] via og:title.
Streaming fetch (head only), 4 workers, 0.5-2s delays, 429 backoff.
Checkpoint: team01_progress.jsonl (one JSON object per code, resumable)."""
import json, re, html, os, random, threading, time
import requests

BASE = '/home/hatch/workspace/whatsapp-groups-site/'
WAVE = BASE + 'agent_batches/wave_20261105/'
POOL = BASE + 'agent_batches/wave_20261104/team14-unverified-pending.json'
CAND = '/home/hatch/workspace/team28_work/candidates.json'
PROG = WAVE + 'team01_progress.jsonl'
LOG = WAVE + 'team01_verify.log'

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

BLOCK_PATTERNS = [
    ('porn', r'porn'), ('xxx', r'xxx'), ('xvideo', r'x ?video'), ('pornhub', r'pornhub'),
    ('onlyfans', r'onlyfans'), ('escort', r'escort'), ('callgirl', r'call\s*girl'),
    ('nude', r'nud[ei]'), ('naked', r'naked'), ('sexvideo', r'sex\s*video'),
    ('sexy', r'sexy'), ('erotic', r'erotic'), ('adult', r'\badult\b'), ('sex', r'\bsex\b'),
    ('hyip', r'hyip'), ('satta', r'satta'), ('matka', r'matka'),
    ('dblmoney', r'(double|doubling).{0,10}money|money.{0,10}(double|doubling)'),
    ('cryptopump', r'crypto.{0,10}pump|pump.{0,10}signal'),
    ('counterfeit', r'counterfeit|fake (currency|note|money)'),
    ('moneymule', r'money\s*mule'),
    ('drugs', r'\b(cocaine|heroin|charas|weed|ganja)\b'),
    ('urlname', r'https?://|www\.|\.com\b'),
    ('phone', r'\+\d[\d\s\-]{7,}\d'),
    ('email', r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'),
]
MINOR_SEX = re.compile(r'(teen|school\s*girl|underage|child|minor|young\s*girl).{0,20}(sex|porn|xxx|nude|hot)|(sex|porn|xxx|nude).{0,20}(teen|school\s*girl|underage|child|minor)', re.I)

def blocked_reason(text):
    low = (text or '').lower()
    for name, pat in BLOCK_PATTERNS:
        if re.search(pat, low):
            return name
    if MINOR_SEX.search(low):
        return 'minor-sex'
    return None

def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

def fetch_ogtitle(code):
    """Returns (ogtitle or None, http_status or None, note). Streams head only."""
    url = f'https://chat.whatsapp.com/{code}'
    for attempt in range(2):
        try:
            with requests.get(url, headers=UA, timeout=20, stream=True, allow_redirects=True) as r:
                if r.status_code == 429:
                    return None, 429, 'http-429'
                if r.status_code != 200:
                    return None, r.status_code, f'http-{r.status_code}'
                buf = ''
                for chunk in r.iter_content(chunk_size=4096, decode_unicode=True):
                    if not chunk:
                        continue
                    buf += chunk
                    m = OG_RE.search(buf)
                    if m:
                        return html.unescape(m.group(1)).strip(), 200, ''
                    if len(buf) > 65536:
                        break
                m = OG_RE.search(buf)
                if m:
                    return html.unescape(m.group(1)).strip(), 200, ''
                return '', 200, 'empty-og-title'
        except requests.exceptions.RequestException as e:
            if attempt == 0:
                time.sleep(2)
                continue
            return None, None, f'error:{type(e).__name__}'
    return None, None, 'error:unknown'

def main():
    pool = json.load(open(POOL))
    slice_codes = pool['codes'][0:5892]
    union = set(json.load(open(WAVE + 'dedupe_union.json')))
    cand = {}
    for e in json.load(open(CAND)):
        cand.setdefault(e['code'], e)
    # dedupe + pre-filter
    done = {}
    if os.path.exists(PROG):
        for line in open(PROG):
            try:
                d = json.loads(line)
                done[d['code']] = d
            except Exception:
                pass
    log(f"resume: {len(done)} already in progress file")
    skipped_union, dropped_pre = [], []
    todo = []
    for c in slice_codes:
        if c in union:
            skipped_union.append(c)
            continue
        title = (cand.get(c, {}).get('post_title') or '')
        reason = blocked_reason(title)
        if reason:
            dropped_pre.append({'code': c, 'name': title, 'reason': reason})
            continue
        if c in done:
            continue
        todo.append(c)
    log(f"slice={len(slice_codes)} union-skip={len(skipped_union)} pre-drop={len(dropped_pre)} todo={len(todo)}")
    with open(WAVE + 'team01_skipped_union.json', 'w') as f:
        json.dump(skipped_union, f)
    with open(WAVE + 'team01_dropped_pre.json', 'w') as f:
        json.dump(dropped_pre, f, indent=1)

    cool_until = [0.0]
    cool_lock = threading.Lock()
    write_lock = threading.Lock()
    counter = [0]
    total = len(todo)

    def worker(codes):
        for code in codes:
            with cool_lock:
                wait = cool_until[0] - time.time()
            if wait > 0:
                time.sleep(wait)
            title, status, note = fetch_ogtitle(code)
            if status == 429:
                with cool_lock:
                    cool_until[0] = time.time() + 180
                log(f"429 on {code}; backing off 180s, retry once")
                time.sleep(180)
                title, status, note = fetch_ogtitle(code)
                if status == 429:
                    with cool_lock:
                        cool_until[0] = time.time() + 240
                    note = 'http-429-persistent'
            rec = {'code': code, 'status': status, 'og_title': title, 'note': note}
            if title:
                reason = blocked_reason(title)
                if reason:
                    rec['blocked'] = reason
            with write_lock:
                with open(PROG, 'a') as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                counter[0] += 1
                if counter[0] % 200 == 0:
                    log(f"progress {counter[0]}/{total}")
            time.sleep(random.uniform(0.5, 2.0))

    threads = []
    chunks = [todo[i::4] for i in range(4)]
    for ch in chunks:
        t = threading.Thread(target=worker, args=(ch,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    log(f"DONE attempted-this-run={counter[0]} total-todo={total}")

if __name__ == '__main__':
    main()
