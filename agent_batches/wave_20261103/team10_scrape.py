#!/usr/bin/env python3
"""team10 — groupjoin.link online-shopping pages 40-114 (wave 20261103).
TEAM 10 slice of the 50-team wave. Uses the /category/online-shopping/ route,
which server-renders the same pool team03 covered (pages 1-39) — /tag/ is
client-rendered and embeds no records. Resumable via team10-state.json.
"""
import json, re, time, html, os, sys, subprocess, requests
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261103')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
WORKERS = 8  # moderate parallelism; 0.3s stagger keeps effective rate gentle

STATE_F = WAVE + '/team10-state.json'
VERIFIED_F = WAVE + '/team10-gjl-onlineshopping.json'
PENDING_F = WAVE + '/team10-unverified-pending.json'
LEADS_F = WAVE + '/team10-leads.json'

SLUG = 'online-shopping'
CAT = 'Buy-Sell'
FIRST_PAGE = 40

PORN_RE = re.compile(r'(porn|pornhub|xnxx|bokep|nude|naked|sex\s*(video|chat|tape)?|escort|'
                     r'call\s*girl|fuck|dick|pussy|boobs|boob|anal|blowjob|horny|'
                     r'\U0001f975|\U0001f346|\U0001f351|\U0001f51e|\U0001f4a6|\U0001f445|\U0001f444|\U0001f48b)',
                     re.I)
PERSONAL_RE = re.compile(r'\+\d[\d ()\-]{7,}|[\w.]+@[\w.]+\.\w+')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')

# light country detection when the record carries no iso2
COUNTRY_KW = [
    ('ID', re.compile(r'indonesia|jakarta|bandung|surabaya|jual\s*beli|\bJB\b', re.I)),
    ('PK', re.compile(r'pakistan|karachi|lahore|islamabad|faisalabad|peshawar', re.I)),
    ('IN', re.compile(r'\bindia\b|mumbai|delhi|bangalore|kolkata|chennai|hyderabad|kerala|punjab|gujarat', re.I)),
    ('NG', re.compile(r'nigeria|lagos|abuja', re.I)),
    ('LK', re.compile(r'sri\s*lanka|colombo', re.I)),
    ('BD', re.compile(r'bangladesh|dhaka|chittagong', re.I)),
    ('PH', re.compile(r'philippines|manila|cebu', re.I)),
    ('MY', re.compile(r'malaysia|kuala\s*lumpur', re.I)),
    ('EG', re.compile(r'egypt|cairo', re.I)),
    ('ZA', re.compile(r'south\s*africa|johannesburg|cape\s*town|durban', re.I)),
    ('KE', re.compile(r'kenya|nairobi', re.I)),
    ('GH', re.compile(r'ghana|accra', re.I)),
    ('BR', re.compile(r'brasil|brazil|s[aã]o\s*paulo', re.I)),
    ('US', re.compile(r'\busa\b|united\s*states|new\s*york|california|texas', re.I)),
    ('UK', re.compile(r'\buk\b|united\s*kingdom|london', re.I)),
    ('AE', re.compile(r'\buae\b|dubai|abu\s*dhabi|sharjah', re.I)),
    ('SA', re.compile(r'saudi|riyadh|jeddah', re.I)),
    ('QA', re.compile(r'qatar|doha', re.I)),
    ('NP', re.compile(r'nepal|kathmandu', re.I)),
]
COUNTRY_NAME = {'ID': 'Indonesia', 'PK': 'Pakistan', 'IN': 'India', 'NG': 'Nigeria',
                'LK': 'Sri Lanka', 'BD': 'Bangladesh', 'PH': 'the Philippines',
                'MY': 'Malaysia', 'EG': 'Egypt', 'ZA': 'South Africa', 'KE': 'Kenya',
                'GH': 'Ghana', 'BR': 'Brazil', 'US': 'the USA', 'UK': 'the UK',
                'AE': 'the UAE', 'SA': 'Saudi Arabia', 'QA': 'Qatar', 'NP': 'Nepal'}

def load_json(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default

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

def fetch_page(pg):
    """Fetch listing pages via curl (proven path through the egress proxy)."""
    url = ('https://www.groupjoin.link/category/%s/?page=%d&limit=20&safeSearch=blur'
           % (SLUG, pg))
    for attempt in range(3):
        try:
            p = subprocess.run(['curl', '-sL', '--max-time', '45', '-A', UA, url],
                               capture_output=True, text=True, timeout=60)
            if p.stdout and len(p.stdout) > 5000:
                return p.stdout
        except Exception:
            pass
        time.sleep(2)
    return ''

def parse_records(page_html):
    t = clean(page_html)
    by_code = {}
    for m in CODE_RE.finditer(t):
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
        cname = clean(cm.group(1)) if cm else ''
        iso = cm.group(2).upper() if cm else ''
        rec = {'code': code, 'title': title, 'desc': desc, 'img': img,
               'country_name': cname, 'iso2': iso}
        # keep the record with the most info for each code
        if code not in by_code or len(title) > len(by_code[code]['title']):
            by_code[code] = rec
    return list(by_code.values())

def verify(code):
    """Return og:title ('' = dead), None = transport failure, 'RATE_LIMIT'."""
    try:
        # fresh connection per request (no session reuse through proxy)
        r = requests.get('https://chat.whatsapp.com/' + code,
                         headers={'User-Agent': UA}, timeout=25)
    except Exception:
        return None
    if r.status_code == 429:
        return 'RATE_LIMIT'
    body = r.text
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', body)
    return html.unescape(m.group(1)).strip() if m else ''

def verify_batch(codes):
    """Verify a list of codes in parallel with staggered starts."""
    results = {}
    def one(c):
        time.sleep(0.3)  # stagger to keep effective rate gentle
        return c, verify(c)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for c, og in ex.map(lambda c: one(c), codes):
            results[c] = og
            if og == 'RATE_LIMIT':
                break
    return results

def detect_country(blob, rec):
    if rec['iso2']:
        return rec['iso2'], rec['country_name'] or COUNTRY_NAME.get(rec['iso2'], '')
    for iso, pat in COUNTRY_KW:
        if pat.search(blob):
            return iso, COUNTRY_NAME[iso]
    return 'International', ''

def save(state, verified, pending, leads, counts):
    json.dump(state, open(STATE_F, 'w'))
    json.dump(verified, open(VERIFIED_F, 'w'), ensure_ascii=False)
    json.dump(pending, open(PENDING_F, 'w'), ensure_ascii=False)
    json.dump(leads, open(LEADS_F, 'w'), ensure_ascii=False)

def main():
    union = set(load_json(WAVE + '/dedupe_union.json', []))
    state = load_json(STATE_F, {})
    verified = load_json(VERIFIED_F, [])
    pending = load_json(PENDING_F, [])
    leads = load_json(LEADS_F, [])
    seen = set(state.get('seen_codes', []))
    for i in verified:
        m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', i.get('invite', ''))
        if m:
            seen.add(m.group(1))
    for p in pending:
        if p.get('code'):
            seen.add(p['code'])
    counts = state.get('counts', {'porn': 0, 'personal': 0, 'channel': 0, 'dupe': 0,
                                  'dead': 0, 'bad_name': 0})
    done = set(state.get('pages_done', []))
    rate_limited = False
    time_up = False

    VERIFY_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    TIME_BUDGET_MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 55
    t_start = time.time()
    verified_this_run = 0
    last_page_seen = state.get('last_page_seen', None)

    # discover bounds: total count from a probe of page 40
    probe = fetch_page(FIRST_PAGE)
    m = re.search(r'currentCount\\*"\s*:\s*\\*(\d+)', clean(probe))
    total = int(m.group(1)) if m else 0
    last = max(FIRST_PAGE, (total + 19) // 20) if total else FIRST_PAGE + 74
    print('total records=%d -> last page=%d' % (total, last), flush=True)
    state['total_records'] = total
    state['last_page'] = last

    pages = [p for p in range(FIRST_PAGE, last + 1) if p not in done]
    last_page_seen = None  # recompute; a previous run may have stopped early on a flaky page
    state['last_page_seen'] = None
    empty_streak = 0
    skipped_pages = []
    for pg in pages:
        if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
            break
        if (time.time() - t_start) / 60 > TIME_BUDGET_MIN:
            time_up = True
            break
        page_html = probe if pg == FIRST_PAGE else fetch_page(pg)
        if len(page_html) < 5000:
            print('page %d: fetch failed, skipping (will retry on resume)' % pg, flush=True)
            skipped_pages.append(pg)
            continue
        recs = parse_records(page_html)
        if len(recs) == 0:
            # SSR can flake: retry the fetch once before calling it empty
            time.sleep(2)
            page_html = fetch_page(pg)
            if len(page_html) >= 5000:
                recs = parse_records(page_html)
            if len(recs) == 0:
                empty_streak += 1
                print('page %d: 0 records (streak %d), skipping for now' % (pg, empty_streak), flush=True)
                skipped_pages.append(pg)
                # only stop past-the-end when the actual last page is ALSO empty
                if empty_streak >= 2:
                    last_probe = fetch_page(last)
                    last_recs = parse_records(last_probe) if len(last_probe) >= 5000 else []
                    if len(last_recs) == 0:
                        print('last page %d also empty -> stopping (past end)' % last, flush=True)
                        last_page_seen = pg
                        state['last_page_seen'] = last_page_seen
                        break
                    else:
                        print('last page %d has %d records -> NOT past end, continuing' % (last, len(last_recs)), flush=True)
                continue
        empty_streak = 0
        new_this_page = 0
        # filter to fresh candidates first
        cands = []
        for r in recs:
            code = r['code']
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
            cands.append(r)
        # verify the page's candidates in one parallel batch
        processed = set()
        if cands and not rate_limited and not time_up and verified_this_run < VERIFY_BUDGET:
            results = verify_batch([r['code'] for r in cands])
        else:
            results = {}
        for r in cands:
            if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
                break
            code = r['code']
            processed.add(code)
            og = results.get(code)
            if og == 'RATE_LIMIT':
                rate_limited = True
                pending.append({'code': code, 'title': r['title'], 'category_slug': SLUG,
                                'page': pg, 'note': 'rate-limited'})
                break
            if og is None:
                pending.append({'code': code, 'title': r['title'], 'category_slug': SLUG,
                                'page': pg, 'note': 'transport failure'})
                continue
            if not og:
                counts['dead'] += 1
                continue
            if PORN_RE.search(og):
                counts['porn'] += 1
                continue
            name = og if (len(og) <= 120 and 'http' not in og) else r['title'][:120]
            name = name.strip()
            if not name or 'whatsapp.com' in name.lower():
                counts['bad_name'] += 1
                continue
            iso, cname = detect_country(blob + ' ' + og, r)
            cword = COUNTRY_NAME.get(iso, '')
            if cword:
                desc_txt = ('Join %s, an active Buy-Sell WhatsApp group from %s. '
                            'Members post products, compare prices and trade safely with other shoppers.'
                            % (name, cword))
            else:
                desc_txt = ('Join %s, an active Buy-Sell WhatsApp group with members from around the world. '
                            'Members post products, compare prices and trade safely with other shoppers.'
                            % name)
            img = r['img'] if (r['img'].startswith('https://') and 'whatsapp.net' in r['img']) else ''
            verified.append({'name': name, 'category': CAT, 'country': iso,
                             'description': desc_txt,
                             'invite': 'https://chat.whatsapp.com/' + code,
                             'image': img})
            verified_this_run += 1
            new_this_page += 1
        # on rate limit or time budget: bank every candidate of this page we
        # didn't finish, so the next wave can retry them
        if rate_limited or time_up:
            note = 'rate-limited' if rate_limited else 'time budget'
            for r in cands:
                if r['code'] not in processed:
                    pending.append({'code': r['code'], 'title': r['title'],
                                    'category_slug': SLUG, 'page': pg, 'note': note})
                    processed.add(r['code'])
        done.add(pg)
        state['pages_done'] = sorted(done)
        state['seen_codes'] = sorted(seen)
        state['counts'] = counts
        save(state, verified, pending, leads, counts)
        print('page %d done: +%d verified_this_run=%d counts=%s' % (pg, new_this_page, verified_this_run, counts), flush=True)

    remaining = [p for p in range(FIRST_PAGE, last + 1) if p not in done]
    if remaining and not last_page_seen:
        leads.append({'domain': 'groupjoin.link',
                      'url': 'https://www.groupjoin.link/category/%s/' % SLUG,
                      'why': 'TEAM10 resume: pages left %s (budget/rate stop)' % remaining[:10]})
    state['last_page_seen'] = last_page_seen
    state['counts'] = counts
    save(state, verified, pending, leads, counts)
    print('DONE verified_total=%d verified_this_run=%d pending=%d leads=%d counts=%s '
          'rate_limited=%s time_up=%s done_pages=%d last_page_seen=%s'
          % (len(verified), verified_this_run, len(pending), len(leads), counts,
             rate_limited, time_up, len(done), last_page_seen), flush=True)

if __name__ == '__main__':
    main()
