#!/usr/bin/env python3
"""team11 worker A — groupjoin.link category sports-and-fitness pages 101-191 (wave 20261103).
Resumable: state in team11b-state.json. Outputs team11b-gjl-sportsfitness.json (verified),
team11b-unverified-pending.json, team11b-leads.json in the wave dir.

NOTE: assignment said /tag/sports-and-fitness but that route is EMPTY on the site
(currentCount=0 on every page, 0 codes). The real route is /category/sports-and-fitness/
(currentCount=3819 = 191 pages). Yesterday's team03 covered category pages 1-14.
(worker B)
"""
import json, re, time, html, os, sys
import requests
import fcntl

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261103')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

STATE_F = WAVE + '/team11b-state.json'
VERIFIED_F = WAVE + '/team11b-gjl-sportsfitness.json'
PENDING_F = WAVE + '/team11b-unverified-pending.json'
LEADS_F = WAVE + '/team11b-leads.json'
PAGE_START, PAGE_END = 101, 191

CAT = 'Sports'
CATMAP_DESC = ('Members follow sports news, discuss matches and share fitness tips.')

PORN_RE = re.compile(r'(porn|pornhub|xxx|xnxx|bokep|nude|naked|sex\s*(video|chat|tape)?|escort|call\s*girl|'
                     r'fuck|dick|pussy|boobs|boob|anal|blowjob|horny|\U0001f975|\U0001f346|\U0001f351|\U0001f51e|\U0001f4a6|\U0001f445|\U0001f444|\U0001f48b)',
                     re.I)
PERSONAL_RE = re.compile(r'\+\d[\d ()\-]{7,}|[\w.]+@[\w.]+\.\w+')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')

def fetch(url):
    last_exc = None
    for _ in range(2):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
            return r.text
        except Exception as e:
            last_exc = e
    raise last_exc

def clean(s):
    for _ in range(2):
        out = []
        i = 0
        while i < len(s):
            c = s[i]
            if c == '\\' and i + 1 < len(s):
                n = s[i + 1]
                if n == 'n':
                    out.append(' '); i += 2
                elif n in '"\\/':
                    out.append(n); i += 2
                elif n == 'u' and i + 5 < len(s) and all(x in '0123456789abcdefABCDEF' for x in s[i+2:i+6]):
                    out.append(chr(int(s[i+2:i+6], 16))); i += 6
                else:
                    out.append(n); i += 2
            else:
                out.append(c); i += 1
        s = ''.join(out)
    return s.strip()

def parse_records(page_html):
    t = clean(page_html)
    recs = []
    for m in CODE_RE.finditer(t):
        is_channel = bool(m.group(1))
        code = m.group(2)
        before = t[max(0, m.start() - 3500):m.start()]
        after = t[m.end():m.end() + 1500]
        def last(pat, win):
            ms = list(re.finditer(pat, win))
            return clean(ms[-1].group(1)) if ms else ''
        title = last(r'"group_title":"((?:\\"|[^"])*)"', before)
        desc = last(r'"group_desc":"((?:\\"|[^"])*)"', before)
        img = last(r'"group_img":"([^"]*)"', before)
        cm = None
        for c2 in re.finditer(r'"country":\{"id":\d+,"name":"([^"]*)","iso2":"([A-Za-z]{2})"', after):
            cm = c2
            break
        country_name = clean(cm.group(1)) if cm else ''
        iso2 = cm.group(2).upper() if cm else ''
        recs.append({'code': code, 'title': title, 'desc': desc, 'img': img,
                     'country_name': country_name, 'iso2': iso2,
                     'is_channel': is_channel})
    return recs

def verify(code):
    """Return (og_title, http_code) — og_title '' means dead; None means transport fail;
    'RATE_LIMIT' sentinel on 429."""
    try:
        with requests.Session() as s:
            r = s.get('https://chat.whatsapp.com/' + code,
                      headers={"User-Agent": UA}, timeout=25, allow_redirects=True)
            hc = str(r.status_code)
            if r.status_code == 429:
                return ('RATE_LIMIT', hc)
            body = r.text
    except requests.exceptions.Timeout:
        return (None, 'timeout')
    except requests.exceptions.RequestException:
        return (None, 'conn')
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', body)
    title = html.unescape(m.group(1)).strip() if m else ''
    return (title, hc)

def load_json(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default

def make_desc(name, country_name):
    base = CATMAP_DESC
    if country_name and country_name.lower() != 'international':
        return ('Join %s, an active sports WhatsApp group from %s. %s'
                % (name, country_name, base))
    return ('Join %s, an active sports WhatsApp group with members from around the world. %s'
            % (name, base))

def main():
    union = set(load_json(WAVE + '/dedupe_union.json', []))
    state = load_json(STATE_F, {})
    verified = load_json(VERIFIED_F, [])
    pending = load_json(PENDING_F, [])
    leads = load_json(LEADS_F, [])
    seen = set(state.get('seen_codes', [])) | {
        re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', i['invite']).group(1)
        for i in verified if 'chat.whatsapp.com/' in i.get('invite', '')}
    seen |= {p.get('code', '') for p in pending if p.get('code')}
    counts = state.get('counts', {'porn': 0, 'personal': 0, 'channel': 0, 'dupe': 0})
    done = set(state.get('pages_done', []))

    VERIFY_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    TIME_BUDGET_MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 300
    t_start = time.time()
    verified_this_run = 0
    rate_limited = False
    time_up = False

    todo = [p for p in range(PAGE_START, PAGE_END + 1) if p not in done]
    print('pages todo=%d verify_budget=%d time_budget=%dmin' % (len(todo), VERIFY_BUDGET, TIME_BUDGET_MIN), flush=True)

    def save():
        state['pages_done'] = sorted(done)
        state['seen_codes'] = sorted(seen)
        state['counts'] = counts
        json.dump(state, open(STATE_F, 'w'))
        json.dump(verified, open(VERIFIED_F, 'w'), ensure_ascii=False)
        json.dump(pending, open(PENDING_F, 'w'), ensure_ascii=False)
        json.dump(leads, open(LEADS_F, 'w'), ensure_ascii=False)

    for pg in todo:
        if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
            break
        if (time.time() - t_start) / 60 > TIME_BUDGET_MIN:
            time_up = True
            break
        try:
            html_pg = fetch('https://www.groupjoin.link/category/sports-and-fitness/?page=%d&limit=20&safeSearch=blur' % pg)
        except Exception as e:
            print('page %d fetch ERR %s' % (pg, e), flush=True)
            continue
        if len(html_pg) < 5000:
            print('page %d short (%d bytes) - skipping' % (pg, len(html_pg)), flush=True)
            continue
        recs = parse_records(html_pg)
        if not recs:
            # flaky empty page — retry on next run, do NOT mark done
            print('page %d: 0 records (likely flaky) - not marking done' % pg, flush=True)
            continue
        for r in recs:
            if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
                break
            code = r['code']
            # /invite/ codes are tested in PLAIN form per Nov-2 policy (valid groups sometimes)
            if code in union or code in seen:
                counts['dupe'] += 1
                continue
            seen.add(code)
            blob = (r['title'] + ' ' + r['desc'])
            if PORN_RE.search(blob):
                counts['porn'] += 1
                continue
            if PERSONAL_RE.search(r['title']):
                counts['personal'] += 1
                continue
            og, hc = verify(code)
            time.sleep(0.6)
            if og == 'RATE_LIMIT':
                rate_limited = True
                pending.append({'code': code, 'title': r['title'], 'category_slug': 'sports-and-fitness',
                                'page': pg, 'note': 'rate-limited'})
                break
            if og is None:
                pending.append({'code': code, 'title': r['title'], 'category_slug': 'sports-and-fitness',
                                'page': pg, 'note': 'transport failure'})
                continue
            if not og:
                continue  # dead link
            if PORN_RE.search(og):
                counts['porn'] += 1
                continue
            iso = r['iso2'] or 'International'
            cname = r['country_name'] or 'International'
            name = og if len(og) <= 120 and 'http' not in og else r['title'][:120]
            if not name:
                continue
            if PERSONAL_RE.search(name):
                counts['personal'] += 1
                continue
            img = r['img'] if r['img'].startswith('https://pps.whatsapp.net/') else ''
            verified.append({'name': name, 'category': CAT,
                             'country': iso,
                             'description': make_desc(name, cname),
                             'invite': 'https://chat.whatsapp.com/' + code,
                             'image': img})
            verified_this_run += 1
        done.add(pg)
        save()
        print('page %d done: verified_this_run=%d pending=%d counts=%s' % (pg, verified_this_run, len(pending), counts), flush=True)

    remaining = [p for p in range(PAGE_START, PAGE_END + 1) if p not in done]
    if remaining:
        leads.append({'domain': 'groupjoin.link',
                      'url': 'https://www.groupjoin.link/category/sports-and-fitness/?page=%d&limit=20&safeSearch=blur' % remaining[0],
                      'why': 'RESUME POINT (team11 worker B, pages 101-191): %d pages left (%d..%d), budget/rate stop' % (len(remaining), remaining[0], remaining[-1])})
    save()
    print('DONE verified_total=%d verified_this_run=%d pending=%d leads=%d counts=%s rate_limited=%s time_up=%s pages_done=%d'
          % (len(verified), verified_this_run, len(pending), len(leads), counts, rate_limited, time_up, len(done)))

if __name__ == '__main__':
    # exclusive lock: a second instance of this worker exits immediately
    _lockf = open(STATE_F, 'a+')
    try:
        fcntl.flock(_lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('LOCK HELD by another instance — exiting', flush=True)
        sys.exit(3)
    main()
