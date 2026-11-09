#!/usr/bin/env python3
"""Team14 slow verifier: curl chat.whatsapp.com/<code>, 3 workers, >=0.6s spacing.
LIVE = HTTP 200 AND non-empty, non-generic og:title. 200 + empty/generic title
is AMBIGUOUS -> retry up to 2 more times spaced apart, then dead.
State saved incrementally so the run can resume.
"""
import json, re, subprocess, time, html, os
from concurrent.futures import ThreadPoolExecutor

IN = 'team14_to_verify.json'
STATE = 'team14_verify_state.json'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def code_of(r):
    m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', r.get('inviteLink', '') or '')
    return m.group(1) if m else None

def check(code):
    url = f'https://chat.whatsapp.com/{code}'
    try:
        p = subprocess.run(
            ['curl', '-sS', '-L', '--max-time', '25', '-A', UA,
             '-w', '\n__HTTP__%{http_code}', url],
            capture_output=True, text=True, timeout=40)
        out = p.stdout
        m = re.search(r'__HTTP__(\d+)\s*$', out)
        http = int(m.group(1)) if m else 0
        body = out[:m.start()] if m else out
        t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
        if not t:
            t = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", body)
        title = html.unescape(t.group(1)).strip() if t else ''
        d = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)
        desc = html.unescape(d.group(1)).strip() if d else ''
        return {'http': http, 'title': title, 'og_desc': desc,
                'err': (p.stderr or '').strip()[:200]}
    except Exception as e:
        return {'http': 0, 'title': '', 'og_desc': '', 'err': str(e)[:200]}

def main():
    rows = json.load(open(IN))
    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE))
    todo = [r for r in rows if code_of(r) not in state]
    print(f'total={len(rows)} already_done={len(state)} todo={len(todo)}', flush=True)

    def work(r):
        c = code_of(r)
        attempts = []
        for i in range(3):
            res = check(c)
            attempts.append(res)
            title = res['title']
            if res['http'] == 200 and title and title != 'WhatsApp Group Invite':
                break
            if res['http'] == 200 and (not title or title == 'WhatsApp Group Invite'):
                # ambiguous: retry spaced apart (unless last attempt)
                if i < 2:
                    time.sleep(8)
                    continue
            break
        time.sleep(0.6)
        return c, {'code': c, 'listing': r, 'attempts': attempts}

    with ThreadPoolExecutor(max_workers=3) as ex:
        for c, rec in ex.map(work, todo):
            state[c] = rec
            if len(state) % 10 == 0:
                json.dump(state, open(STATE, 'w'), indent=1, ensure_ascii=False)
                print(f'... {len(state)}/{len(rows)} done', flush=True)
    json.dump(state, open(STATE, 'w'), indent=1, ensure_ascii=False)
    live = sum(1 for v in state.values()
               if v['attempts'][-1]['http'] == 200 and v['attempts'][-1]['title']
               and v['attempts'][-1]['title'] != 'WhatsApp Group Invite')
    print(f'DONE total={len(state)} live-ish={live}', flush=True)

if __name__ == '__main__':
    main()
