#!/usr/bin/env python3
"""team03 — groupjoin.link category deep scrape (wave 20261102).
Resumable: state in team03-state.json. Outputs team03-gjl-categories.json (verified),
team03-unverified-pending.json, team03-leads.json in the wave dir.
"""
import json, re, subprocess, time, html, os, sys

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261102')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

STATE_F = WAVE + '/team03-state.json'
VERIFIED_F = WAVE + '/team03-gjl-categories.json'
PENDING_F = WAVE + '/team03-unverified-pending.json'
LEADS_F = WAVE + '/team03-leads.json'

CATMAP = {'gaming': 'Gaming', 'marketing': 'Business', 'online-shopping': 'Buy-Sell',
          'money': 'Finance', 'education': 'Education', 'business': 'Business',
          'entertainment': 'Entertainment', 'sports-and-fitness': 'Sports'}

DESC2 = {
 'Gaming': 'Members discuss games, share tips and team up with fellow gamers.',
 'Business': 'Members network, share business ideas and discuss market opportunities.',
 'Buy-Sell': 'Members post products, compare prices and trade safely with other shoppers.',
 'Finance': 'Members discuss money matters, share finance tips and market updates.',
 'Education': 'Members share study material, notes and exam preparation help.',
 'Entertainment': 'Members share fun posts, videos and entertainment updates.',
 'Sports': 'Members follow sports news, discuss matches and share fitness tips.',
}

PORN_RE = re.compile(r'(porn|pornhub|xxx|xnxx|bokep|nude|naked|sex\s*(video|chat|tape)?|escort|call\s*girl|'
                     r'fuck|dick|pussy|boobs|boob|anal|blowjob|horny|🥵|🍆|🍑|🔞|💦|👅|👄|💋)',
                     re.I)
PERSONAL_RE = re.compile(r'\+\d[\d ()\-]{7,}|[\w.]+@[\w.]+\.\w+')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')

def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return p.stdout

def fetch(url):
    return sh(['curl', '-sL', '--max-time', '30', '-A', UA, url])

def clean(s):
    """Collapse JS escape levels in a captured value."""
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

def get_count(page_html):
    m = re.search(r'currentCount\\*"\s*:\s*\\*(\d+)', page_html)
    return int(m.group(1)) if m else 0

def parse_records(page_html):
    """Return list of dicts: code, title, desc, img, cat_slug, country_name, iso2, is_channel."""
    # Work on a cleaned copy so keys read as plain JSON-ish text
    t = clean(page_html)
    recs = []
    for m in CODE_RE.finditer(t):
        is_channel = bool(m.group(1))
        code = m.group(2)
        before = t[max(0, m.start() - 3500):m.start()]
        after = t[m.end():m.end() + 1500]  # category/country objects come after the link
        def last(pat, win):
            ms = list(re.finditer(pat, win))
            return clean(ms[-1].group(1)) if ms else ''
        title = last(r'"group_title":"((?:\\"|[^"])*)"', before)
        desc = last(r'"group_desc":"((?:\\"|[^"])*)"', before)
        img = last(r'"group_img":"([^"]*)"', before)
        cat = last(r'"category_name":"([^"]*)"', after)
        cm = None
        for c2 in re.finditer(r'"country":\{"id":\d+,"name":"([^"]*)","iso2":"([A-Za-z]{2})"', after):
            cm = c2
            break
        country_name = clean(cm.group(1)) if cm else ''
        iso2 = cm.group(2).upper() if cm else ''
        recs.append({'code': code, 'title': title, 'desc': desc, 'img': img,
                     'cat': cat, 'country_name': country_name, 'iso2': iso2,
                     'is_channel': is_channel})
    return recs

def verify(code):
    """Return (og_title, http_code) — og_title '' means dead; None means transport fail."""
    body_f = '/tmp/t03_body.html'
    out = sh(['curl', '-sL', '--max-time', '25', '-A', UA,
              '-o', body_f, '-w', '%{http_code}', 'https://chat.whatsapp.com/' + code])
    http_code = out.strip().split('\n')[-1] if out.strip() else ''
    if http_code == '429':
        return ('RATE_LIMIT', http_code)
    try:
        body = open(body_f, encoding='utf-8', errors='replace').read()
    except Exception:
        return (None, http_code)
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', body)
    title = html.unescape(m.group(1)).strip() if m else ''
    return (title, http_code)

def load_json(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default

def main():
    union = set(load_json(WAVE + '/dedupe_union.json', []))
    state = load_json(STATE_F, {})
    verified = load_json(VERIFIED_F, [])
    pending = load_json(PENDING_F, [])
    leads = load_json(LEADS_F, [])
    seen = set(state.get('seen_codes', [])) | {re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', i['invite']).group(1) for i in verified if 'chat.whatsapp.com/' in i.get('invite', '')}
    seen |= {p.get('code', '') for p in pending if p.get('code')}
    counts = state.get('counts', {'porn': 0, 'personal': 0, 'channel': 0, 'dupe': 0})

    # (slug, first_page, mode, npages, page_cap)  mode 'asc' or 'desc-from-last'
    # page_cap: max pages to process this wave (None = all)
    plan = [
        ('marketing', 1, 'asc', None, None),
        ('online-shopping', 1, 'asc', None, 15),
        ('sports-and-fitness', 1, 'asc', None, 12),
        ('gaming', 41, 'asc', None, None),
        ('money', None, 'desc', 30, None),
        ('education', None, 'desc', 30, None),
        ('business', None, 'desc', 30, None),
        ('entertainment', None, 'desc', 30, None),
    ]
    VERIFY_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    TIME_BUDGET_MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 75
    t_start = time.time()
    verified_this_run = 0
    rate_limited = False
    time_up = False

    for slug, first, mode, npages, page_cap in plan:
        if rate_limited or time_up:
            break
        key = 'pages_done_' + slug
        done = set(state.get(key, []))
        base = 'https://www.groupjoin.link/category/%s/?page=%%d&limit=20&safeSearch=blur' % slug
        p1 = fetch(base % 1)
        if len(p1) < 5000:
            leads.append({'domain': 'groupjoin.link', 'url': base % 1,
                          'why': 'category %s fetch failed/empty on resume probe' % slug})
            continue
        total = get_count(p1)
        last = max(1, (total + 19) // 20)
        if mode == 'asc':
            pages = list(range(first, last + 1))
        else:
            pages = list(range(last, max(first or 1, last - npages + 1) - 1, -1))
            if first:
                pages = [p for p in pages if p >= first]
        todo = [p for p in pages if p not in done]
        if page_cap:
            todo = todo[:page_cap]
        if not todo:
            continue
        print('CAT %s total=%d last=%d todo=%d' % (slug, total, last, len(todo)), flush=True)
        for pg in todo:
            if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
                break
            if (time.time() - t_start) / 60 > TIME_BUDGET_MIN:
                time_up = True
                break
            html_pg = p1 if pg == 1 else fetch(base % pg)
            if len(html_pg) < 5000:
                continue
            for r in parse_records(html_pg):
                if rate_limited or time_up or verified_this_run >= VERIFY_BUDGET:
                    break
                code = r['code']
                if r['is_channel']:
                    counts['channel'] += 1
                    continue
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
                time.sleep(0.5)
                if og == 'RATE_LIMIT':
                    rate_limited = True
                    pending.append({'code': code, 'title': r['title'], 'category_slug': slug,
                                    'page': pg, 'note': 'rate-limited'})
                    break
                if og is None:
                    pending.append({'code': code, 'title': r['title'], 'category_slug': slug,
                                    'page': pg, 'note': 'transport failure'})
                    continue
                if not og:
                    continue  # dead link
                if PORN_RE.search(og):
                    counts['porn'] += 1
                    continue
                cat = CATMAP.get(slug, 'Other')
                cname = r['country_name'] or 'International'
                iso = r['iso2'] or 'International'
                name = og if len(og) <= 120 and 'http' not in og else r['title'][:120]
                if not name:
                    continue
                d2 = DESC2.get(cat, 'Members connect, share updates and discuss common interests.')
                if cname == 'International' or iso == 'International':
                    desc_txt = ('Join %s, an active %s WhatsApp group with members from around the world. %s'
                                % (name, cat.lower(), d2))
                else:
                    desc_txt = ('Join %s, an active %s WhatsApp group from %s. %s'
                                % (name, cat.lower(), cname, d2))
                img = r['img'] if r['img'].startswith('https://') and 'whatsapp.net' in r['img'] else ''
                verified.append({'name': name, 'category': cat, 'country': iso,
                                 'description': desc_txt,
                                 'invite': 'https://chat.whatsapp.com/' + code,
                                 'image': img})
                verified_this_run += 1
            done.add(pg)
            state[key] = sorted(done)
            state['seen_codes'] = sorted(seen)
            state['counts'] = counts
            json.dump(state, open(STATE_F, 'w'))
            json.dump(verified, open(VERIFIED_F, 'w'), ensure_ascii=False)
            json.dump(pending, open(PENDING_F, 'w'), ensure_ascii=False)
        # resume lead
        remaining = [p for p in pages if p not in done]
        if remaining:
            leads.append({'domain': 'groupjoin.link',
                          'url': 'https://www.groupjoin.link/category/%s/' % slug,
                          'why': 'resume: %d pages left (%s), budget/rate stop' % (len(remaining), slug)})

    json.dump(state, open(STATE_F, 'w'))
    json.dump(verified, open(VERIFIED_F, 'w'), ensure_ascii=False)
    json.dump(pending, open(PENDING_F, 'w'), ensure_ascii=False)
    json.dump(leads, open(LEADS_F, 'w'), ensure_ascii=False)
    print('DONE verified_total=%d verified_this_run=%d pending=%d leads=%d counts=%s rate_limited=%s'
          % (len(verified), verified_this_run, len(pending), len(leads), counts, rate_limited))

if __name__ == '__main__':
    main()
