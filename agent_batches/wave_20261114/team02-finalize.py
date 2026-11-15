#!/usr/bin/env python3
"""team02 finalize — run AFTER team02-mine.py completes.
1. Re-screens ALL banked candidates with the CURRENT screen() from
   team02-mine.py (covers chunks banked before screen fixes) + fixes
   divulgação categories.
2. Resolves team02-pending.json codes (HTTP 429 / transport): one shared
   session, 60s timeout, 75s alarm; live -> screen/bank; empty -> 2 spaced
   retries -> dead; still-429 -> stays pending.
3. Rewrites candidates/pending/state/summary with final honest counts.
"""
import json, re, time, html, os, sys, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'team02_mine', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'team02-mine.py'))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
screen, categorize, describe, norm, fold = _mod.screen, _mod.categorize, _mod.describe, _mod.norm, _mod.fold

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114'
UNION = '/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}

class VerifyTimeout(Exception):
    pass
def _alarm_handler(signum, frame):
    raise VerifyTimeout()
signal.signal(signal.SIGALRM, _alarm_handler)

def og_title(text):
    if not text:
        return ''
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)', text)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', text)
    return html.unescape(m.group(1)).strip() if m else ''

def main():
    st = json.load(open(os.path.join(WAVE, 'team02-state.json')))
    candidates = json.load(open(os.path.join(WAVE, 'team02-candidates.json')))
    pending = json.load(open(os.path.join(WAVE, 'team02-pending.json')))
    excluded = st['excluded']
    counts = st['counts']
    union = set(json.load(open(UNION)))
    seen = set(st['seen_codes'])

    # --- 1. re-screen candidates with current screen ---
    kept = []
    for c in candidates:
        code = c['invite'].split('/')[-1]
        if code in union:
            counts['dupes'] += 1
            excluded.append({'code': code, 'reason': 'dupe vs union (final audit)', 'title': c['name']})
            continue
        reason, flag = screen(c['name'])
        if reason:
            counts['excluded_n'] += 1
            excluded.append({'code': code, 'reason': reason + ' (final audit)', 'title': c['name']})
            continue
        # category fix: generic divulgacao groups are advertising, not Finance
        t = norm(c['name'])
        if 'divulgacao' in t and c['category'] == 'Finance' and not any(
                k in t for k in ['dinheiro', 'renda', 'ganhar', 'lucro', 'investimento', 'pix']):
            c['category'] = 'Business'
            c['description'] = describe(c['name'], 'Business')
        kept.append(c)
        if flag:
            excluded.append({'code': code, 'reason': f"KEPT-FLAG: {flag} (final audit)", 'title': c['name']})
    dropped = len(candidates) - len(kept)
    candidates = kept
    print(f"re-screen: dropped {dropped}, kept {len(candidates)}", flush=True)

    # --- 2. resolve pending codes ---
    if pending:
        print(f"resolving {len(pending)} pending codes (300s cool-down first)...", flush=True)
        time.sleep(300)
        sess = requests.Session()
        sess.headers.update(UA)

        def verify_once(code):
            t0 = time.time()
            try:
                signal.setitimer(signal.ITIMER_REAL, 75)
                try:
                    r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=60)
                    if r.status_code == 429:
                        return 'rate_limited', ''
                    title = og_title(r.text)
                    return ('live', title) if title else ('empty', '')
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
            except VerifyTimeout:
                return 'pending', 'verify wall-time 75s (hung read)'
            except Exception as e:
                try:
                    signal.setitimer(signal.ITIMER_REAL, 75)
                    try:
                        r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=60)
                        if r.status_code == 429:
                            return 'rate_limited', ''
                        title = og_title(r.text)
                        return ('live', title) if title else ('empty', '')
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                except VerifyTimeout:
                    return 'pending', 'verify wall-time 75s (hung read)'
                except Exception as e2:
                    return 'pending', f'{type(e2).__name__}: {e2}'

        def bank(code, title, listing):
            reason, flag = screen(title)
            if reason:
                counts['excluded_n'] += 1
                excluded.append({'code': code, 'reason': reason + ' (pending resolution)', 'title': title})
                return
            cat = categorize(title, None)
            candidates.append({'name': title, 'category': cat, 'country': 'BR',
                               'description': describe(title, cat),
                               'invite': f'https://chat.whatsapp.com/{code}'})
            if flag:
                excluded.append({'code': code, 'reason': f"KEPT-FLAG: {flag} (pending resolution)", 'title': title})

        still_pending = []
        empties = []
        for item in pending:
            code = item['code']
            status, info = verify_once(code)
            time.sleep(1)  # gentle pace: the 429 storm came from aggregate load
            if status == 'live':
                bank(code, info, item.get('listing', ''))
            elif status == 'empty':
                empties.append(item)
            else:
                still_pending.append({'code': code,
                                      'reason': info or 'HTTP 429',
                                      'listing': item.get('listing', '')})
        print(f"pending pass 1: {len(still_pending)} still pending, {len(empties)} empty", flush=True)
        # second full pass over still-pending after another cool-down
        if still_pending:
            print(f"pending pass 2: {len(still_pending)} codes, 120s cool-down first...", flush=True)
            time.sleep(120)
            retry_pending = still_pending
            still_pending = []
            for item in retry_pending:
                code = item['code']
                status, info = verify_once(code)
                time.sleep(1)
                if status == 'live':
                    bank(code, info, item.get('listing', ''))
                elif status == 'empty':
                    empties.append(item)
                else:
                    still_pending.append({'code': code,
                                          'reason': info or 'HTTP 429',
                                          'listing': item.get('listing', '')})
            print(f"pending pass 2: {len(still_pending)} still pending, {len(empties)} empty total", flush=True)
        for pass_no, pause in ((1, 10), (2, 20)):
            if not empties:
                break
            time.sleep(pause)
            still = []
            for item in empties:
                code = item['code']
                status, info = verify_once(code)
                time.sleep(1)
                if status == 'live':
                    bank(code, info, item.get('listing', ''))
                elif status in ('pending', 'rate_limited'):
                    still_pending.append({'code': code, 'reason': info or 'HTTP 429',
                                          'listing': item.get('listing', '')})
                else:
                    still.append(item)
            empties = still
            print(f"pending retry pass {pass_no}: {len(empties)} still empty, "
                  f"{len(still_pending)} pending", flush=True)
        counts['dead'] += len(empties)
        counts['pending_n'] = len(still_pending)
        pending = still_pending

    # --- 3. rewrite outputs ---
    json.dump(candidates, open(os.path.join(WAVE, 'team02-candidates.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, 'team02-pending.json'), 'w'), ensure_ascii=False, indent=1)
    st['excluded'] = excluded
    st['counts'] = counts
    json.dump(st, open(os.path.join(WAVE, 'team02-state.json'), 'w'), ensure_ascii=False, indent=1)
    leads = json.load(open(os.path.join(WAVE, 'team02-leads.json')))
    summary = {
        'team': 'team02',
        'slice': ("linkado.app grupo sitemap indices 6000-8499 (grupo-only, 0-based; 2500 URLs; "
                  "first=https://linkado.app/grupo/67db20d3916daeae13772619 "
                  "last=https://linkado.app/grupo/66b2c97430349688bd900fcf)"),
        'sources': ['linkado.app grupo pages (sitemap copy wave_20261110/linkado_sitemap.xml, 19731 grupo URLs; index mapping confirmed vs team05 last idx5999 and team34 first idx8500)'],
        'controls': {
            'live': "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (LIVE, as expected)",
            'fabricated': "ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title (dead, as expected)"},
        'raw': counts['raw'], 'verified': len(candidates), 'dupes': counts['dupes'],
        'dead': counts['dead'],
        'excluded': [e for e in excluded if not e['reason'].startswith('KEPT-FLAG')],
        'kept_flags': [e for e in excluded if e['reason'].startswith('KEPT-FLAG')],
        'pending': len(pending), 'leads': len(leads),
        'listings_attempted': len(st['done_offsets']),
        'listings_no_invite': counts['no_invite'],
        'listings_fetch_fail': counts['fetch_fail'],
        'resume_point': f"done_offsets={len(st['done_offsets'])}/2500; unmined indices banked in team02-leads.json",
        'notes': [
            'Slice yield is very low: ~95% of verifiable codes dead (old listings), ~40% dupes vs union.',
            'WhatsApp returned HTTP 429 heavily from chunk 5 on (many sibling teams verifying concurrently); 429 codes were deferred to a cool-down sweep, never marked dead. Unresolved 429s remain in team02-pending.json for a later run.',
            'Verification used ONE shared requests.Session per process; empty og:title got 2 spaced retries before dead.',
            'Screen applied to live og:title with NFKD fold (stylized Unicode), word-boundary matching, negated-prohibition restore, and PT betting vocabulary (bet/bets, tigrinho, sinais+context, plataforma+bonus/link/lancamento/pagando, slots, 🎰).',
        ],
    }
    json.dump(summary, open(os.path.join(WAVE, 'team02-summary.json'), 'w'), ensure_ascii=False, indent=1)
    print('FINAL:', json.dumps({k: summary[k] for k in ('raw', 'verified', 'dupes', 'dead', 'pending', 'leads')}), flush=True)

if __name__ == '__main__':
    main()
