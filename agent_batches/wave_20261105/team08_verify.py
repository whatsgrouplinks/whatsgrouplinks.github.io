#!/usr/bin/env python3
"""team08: re-verify groupchatconnect pending codes via og:title.
Control test passed 2026-11-05 ~11:55 PKT: known-live codes return non-empty
og:title matching their real group names; synthetic dead codes return empty
og:title. Verification possible via this egress.
"""
import json, re, html, os, random, subprocess, time, threading
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261105')
SRC = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team04-unverified-pending.json')
UNION = os.path.join(BASE, 'dedupe_union.json')
PROGRESS = '/tmp/team08_progress.jsonl'
TMPDIR = '/tmp/team08_verify'
os.makedirs(TMPDIR, exist_ok=True)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
OG_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.I)
BLOCK_RE = re.compile(
    r'\b(xxx|porn|pornhub|xvideos|xnxx|sex video|sexvideos|nude|naked|onlyfans|escort|call girl|desi sex)\b'
    r'|hyip|double (your )?money|money (doubler|mule)|crypto pump|pump (signal|group)|satta|matka'
    r'|fixed match|counterfeit|fake (currency|notes|passport)|\b(child|teen|minor|girl(s)? (under|age))\b.*\b(sex|nude|xxx)\b',
    re.I)
URL_NAME_RE = re.compile(r'^(https?://|www\.)', re.I)

def code_of(invite):
    c = invite.replace('https://chat.whatsapp.com/', '').replace('invite/', '')
    return c.strip('/').split('?')[0].split('#')[0]

def fetch_og(code, tid):
    """Returns (http_code, og_title_or_None, error_str)."""
    path = os.path.join(TMPDIR, f'{tid}.html')
    for attempt in range(2):
        try:
            r = subprocess.run(
                ['curl', '-sL', '-A', UA, '--max-time', '20',
                 '-o', path, '-w', '%{http_code}',
                 f'https://chat.whatsapp.com/{code}'],
                capture_output=True, text=True, timeout=40)
            http = r.stdout.strip()
            if http == '429':
                time.sleep(180)
                continue
            if http != '200':
                return http, None, f'http-{http}'
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read()
            m = OG_RE.search(data)
            if not m:
                return http, None, 'no-og-title-tag'
            title = html.unescape(m.group(1)).strip()
            return http, title, None
        except subprocess.TimeoutExpired:
            return 'timeout', None, 'timeout'
        except Exception as e:
            return 'error', None, f'error:{e}'
    return '429', None, 'http-429-after-retry'

def main():
    union = set(json.load(open(UNION)))
    pending = json.load(open(SRC))
    done = {}
    if os.path.exists(PROGRESS):
        with open(PROGRESS) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done[rec['code']] = rec
                except Exception:
                    pass
    todo = []
    skipped_union = 0
    for r in pending:
        c = code_of(r['invite'])
        if c in union:
            skipped_union += 1
            continue
        if c in done:
            continue
        todo.append((c, r))
    print(f'total={len(pending)} in_union_skipped={skipped_union} already_done={len(done)} todo={len(todo)}', flush=True)
    lock = threading.Lock()

    def work(item):
        c, r = item
        tid = threading.current_thread().name.replace(' ', '_')
        time.sleep(random.uniform(0.5, 2.0))
        http, title, err = fetch_og(c, tid)
        if title:
            blocked = bool(BLOCK_RE.search(title))
            urlname = bool(URL_NAME_RE.match(title))
            name = (r.get('name') or '').strip()
            name_is_url = bool(URL_NAME_RE.match(name))
            if blocked or urlname:
                status, note = 'drop', f"og:title blocked ({'blocked-pattern' if blocked else 'url-name'}): {title[:80]}"
            elif name_is_url:
                status, note = 'verified', f'og:title used as name (listing name was URL); og:{title[:80]}'
            else:
                status, note = 'verified', f'og:{title[:80]}'
        elif err and '429' in str(err):
            status, note = 'pending', 'http-429'
        else:
            status, note = 'pending', f'empty-og-title ({err or "http "+str(http)})'
        rec = {'code': c, 'name': r.get('name', ''), 'invite': r['invite'],
               'status': status, 'note': note, 'og_title': title or '',
               'category': r.get('category', ''), 'country': r.get('country', ''),
               'description': r.get('description', ''), 'image': r.get('image', '')}
        with lock:
            with open(PROGRESS, 'a') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        return rec

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(work, todo))
    counts = {}
    for rec in list(done.values()) + results:
        counts[rec['status']] = counts.get(rec['status'], 0) + 1
    print('COUNTS:', counts, 'in_union_skipped:', skipped_union, flush=True)

if __name__ == '__main__':
    main()
