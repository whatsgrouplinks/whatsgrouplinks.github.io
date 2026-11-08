#!/usr/bin/env python3
"""team05 wave 20261105: re-verify gjl-newtags + linkado pending codes.
Control test passed: curl -sL on KrDwdK8EIkB6vgauHg5M7N returned
og:title 'JAY - PHP & Python Full Stack Developer' (matches groups.json).
Streaming fetch (urllib, first 32KB, same URL + UA, same og:title regex)
verified identical on the control + 3 test codes, ~5s/req vs ~15s curl.
4 workers, 0.5-2s random delay per worker between requests.
Non-empty og:title = verified, EXCEPT placeholders 'Group Closed' /
'WhatsApp Group Invite' (not a group name) -> pending.
Blocked og:title/name (porn/xxx/scam/etc.) -> dropped, never verified.
Checkpoint every 100 completions; resumable from checkpoint file.
"""
import json, re, time, random, threading, html, os, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))  # agent_batches/wave_20261105
SITE = os.path.dirname(os.path.dirname(BASE))
PEND = os.path.join(SITE, 'agent_batches/wave_20261104/team33-unverified-pending.json')
UNION = os.path.join(BASE, 'dedupe_union.json')
CKPT = os.path.join(BASE, 'team05-checkpoint.json')
OUT_VER = os.path.join(BASE, 'team05-gjl-linkado.json')
OUT_PEND = os.path.join(BASE, 'team05-unverified-pending.json')
OUT_LEADS = os.path.join(BASE, 'team05-leads.json')
OUT_DROPS = os.path.join(BASE, 'team05-drops.json')
LOG = os.path.join(BASE, 'team05-verify.log')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
TITLE_RE = re.compile(rb'<meta property="og:title" content="([^"]*)"')
BLOCK_RE = re.compile(
    r'(?i)\b(xxx|porn|porno|onlyfans|hentai|nudes?|escorts?|call\s*girls?)\b'
    r'|\bsex\s+(videos?|chat|dating|xxx|stories|clips)\b|\b(desi|hindi|tamil|mallu)\s*sex\b'
    r'|\badult\s+(videos?|sex|chat|xxx|dating|content|18\+?)\b'
    r'|crypto\s*pump|pump\s*signals?|hyip|money\s*mule|counterfeit|\bsatta\b|\bmatka\b'
    r'|\b(cocaine|heroin)\b|drugs?\s+for\s+sale'
    r'|child\s*sex|teen\s*sex|minor\s*sex|sex\s+with\s+(a\s+)?(child|minors?)',
    re.I)
PLACEHOLDER = {'group closed', 'whatsapp group invite', 'whatsapp'}

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

def code_of(rec):
    u = rec.get('invite', '')
    return u.replace('https://chat.whatsapp.com/', '').replace('invite/', '').strip('/').split('?')[0].split('#')[0]

def blocked(text):
    return bool(text and BLOCK_RE.search(text))

# ---- load + dedupe + pre-screen ----
pend = json.load(open(PEND))
union = set(json.load(open(UNION)))
work, skipped_union, pre_drops = [], [], []
seen = set()
for r in pend:
    c = code_of(r)
    if c in union:
        skipped_union.append({'code': c, 'name': r.get('name', ''), 'note': 'in dedupe_union.json — skipped before verifying'})
        continue
    if c in seen:
        continue
    seen.add(c)
    if blocked(r.get('name', '')):
        pre_drops.append({'code': c, 'name': r.get('name', ''), 'note': 'dropped pre-verify: blocked name pattern (crypto-pump/scam/porn rule)'})
        continue
    work.append(r)
log(f"slice={len(pend)} union-skipped={len(skipped_union)} pre-drops={len(pre_drops)} to-verify={len(work)}")

# ---- resume from checkpoint ----
done = {}   # code -> result dict
if os.path.exists(CKPT):
    ck = json.load(open(CKPT))
    done = ck.get('results', {})
    skipped_union = ck.get('skipped_union', skipped_union)
    pre_drops = ck.get('pre_drops', pre_drops)
    log(f"resumed from checkpoint: {len(done)} already done")
todo = [r for r in work if code_of(r) not in done]
log(f"todo this run: {len(todo)}")

backoff_until = [0.0]
backoff_lock = threading.Lock()
rate429 = [0]
stop_flag = threading.Event()
ckpt_lock = threading.Lock()
counter = [len(done)]

def fetch_title(code):
    req = Request('https://chat.whatsapp.com/' + code, headers={'User-Agent': UA})
    with urlopen(req, timeout=25) as resp:
        if resp.status == 429:
            raise HTTPError(resp.url, 429, 'Too Many Requests', resp.headers, None)
        data = resp.read(32768)
    m = TITLE_RE.search(data)
    if not m:
        return ''
    return html.unescape(m.group(1).decode('utf-8', 'ignore')).strip()

def save_checkpoint():
    with ckpt_lock:
        json.dump({'results': done, 'skipped_union': skipped_union,
                   'pre_drops': pre_drops, 'at': time.strftime('%Y-%m-%d %H:%M:%S')},
                  open(CKPT, 'w'))

def process(rec):
    code = code_of(rec)
    if stop_flag.is_set():
        return code, {'status': 'pending', 'note': 'not attempted: repeated-429 stop'}
    time.sleep(random.uniform(0.5, 2.0))
    # respect global backoff
    while True:
        with backoff_lock:
            wait = backoff_until[0] - time.time()
        if wait <= 0:
            break
        time.sleep(min(wait, 10))
    for attempt in (1, 2):
        try:
            title = fetch_title(code)
            break
        except HTTPError as e:
            if e.code == 429:
                with backoff_lock:
                    rate429[0] += 1
                    backoff_until[0] = time.time() + 180
                log(f"429 on {code} (count {rate429[0]}); backing off 180s")
                if rate429[0] >= 8:
                    stop_flag.set()
                    return code, {'status': 'pending', 'note': 'http-429: backoff exhausted / repeated-429 stop'}
                if attempt == 1:
                    time.sleep(180)
                    continue
                return code, {'status': 'pending', 'note': 'http-429 after backoff retry'}
            return code, {'status': 'pending', 'note': f'http-{e.code}'}
        except Exception as e:
            return code, {'status': 'pending', 'note': f'{type(e).__name__}: {str(e)[:80]}'}
    else:
        return code, {'status': 'pending', 'note': 'http-429 after backoff retry'}
    if not title:
        return code, {'status': 'pending', 'note': 'empty og:title'}
    if title.lower() in PLACEHOLDER:
        return code, {'status': 'pending', 'note': f'og:title placeholder: {title!r} (invite closed/revoked or no group name)'}
    if blocked(title):
        return code, {'status': 'dropped', 'note': f'dropped: blocked og:title {title!r}'}
    if title.lower().startswith(('http', 'www.')):
        return code, {'status': 'dropped', 'note': f'dropped: og:title is a URL {title!r}'}
    name = rec.get('name') or title
    out = {'name': name, 'category': rec.get('category', 'Other'), 'country': rec.get('country', 'International'),
           'description': rec.get('description', ''), 'invite': 'https://chat.whatsapp.com/' + code,
           'image': rec.get('image', '') or ''}
    return code, {'status': 'verified', 'record': out, 'og_title': title}

def main():
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        for code, res in ex.map(process, todo):
            done[code] = res
            counter[0] += 1
            if counter[0] % 100 == 0:
                v = sum(1 for r in done.values() if r['status'] == 'verified')
                p = sum(1 for r in done.values() if r['status'] == 'pending')
                d = sum(1 for r in done.values() if r['status'] == 'dropped')
                log(f"progress {counter[0]}/{len(work)} verified={v} pending={p} dropped={d} elapsed={int(time.time()-t0)}s")
                save_checkpoint()
    save_checkpoint()
    # ---- final outputs ----
    by_code = {code_of(r): r for r in pend}
    verified, pending, drops = [], [], list(pre_drops)
    for code, res in done.items():
        src = by_code.get(code, {})
        if res['status'] == 'verified':
            verified.append(res['record'])
        elif res['status'] == 'dropped':
            drops.append({'code': code, 'name': src.get('name', ''), 'note': res['note']})
        else:
            pending.append({'code': code, 'name': src.get('name', ''), 'note': res['note']})
    # union-skipped codes stay OUT of pending (already in union = already handled upstream)
    verified.sort(key=lambda r: r['invite'])
    pending.sort(key=lambda r: r['code'])
    json.dump(verified, open(OUT_VER, 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(OUT_PEND, 'w'), ensure_ascii=False, indent=1)
    json.dump([], open(OUT_LEADS, 'w'))
    json.dump(drops, open(OUT_DROPS, 'w'), ensure_ascii=False, indent=1)
    v = len(verified); p = len(pending); d = len(drops)
    log(f"DONE slice={len(pend)} union-skipped={len(skipped_union)} verified={v} pending={p} drops={d} elapsed={int(time.time()-t0)}s")
    print(f"FINAL verified={v} pending={p} drops={d} union_skipped={len(skipped_union)}")

if __name__ == '__main__':
    main()
