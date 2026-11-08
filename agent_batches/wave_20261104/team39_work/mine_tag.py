#!/usr/bin/env python3
"""Team39 groupjoin.link tag-page miner: fetch page N, parse flight-data groups,
filter porn/adult/channels, dedupe vs union, verify via og:title, append verified."""
import requests, re, html, time, json, pickle, os, sys, concurrent.futures

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team39_work')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}

PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx|nude|sexy\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|bokep|satta|matka|realmeet|leak|vairal|viral\s*video|desi\s*video|hot\s*(boy|girl)|bhabhi|randi|randiya)\b|مزا\s*دینے|مزہ\s*دینے|رنڈی')
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B\U0001F60D\U0001F618\U0001F60B\U0001FAE6]')
VULGAR_RE = re.compile(r'(?i)(bakchod|launday|chut|lund|gandu|madarchod|bhosdi)')

# my slice categories from groupjoin category names
CATMAP = {'Comedy': 'Funny', 'Entertainment': 'Entertainment', 'Friendship': 'Friendship',
          'Love & Relationship': 'Friendship', 'Community': 'Community', 'Health & Fitness': 'Health',
          'Quotes': 'Entertainment', 'Other': 'Other', 'Family': 'Community'}
OUT_OF_SLICE = {'Gaming', 'Business', 'Music', 'Sports', 'Jobs', 'Education', 'News', 'Technology',
                'Crypto', 'Islamic', 'Movies', 'Food', 'Pets', 'Travel', 'Finance', 'Buy-Sell', 'Regional'}

def fetch_page(tag, page):
    for attempt in range(4):
        s = requests.Session(); s.headers.update(UA)
        try:
            r = s.get(f'https://www.groupjoin.link/tag/%23{tag}/?page={page}&limit=20&safeSearch=strict', timeout=120)
            t = r.text.replace('\\"','"').replace('\\u0026','&')
            starts = [m.start() for m in re.finditer(r'\{"group":\{"id":\d+', t)]
            codes = [(m.start(), m.group(1)) for m in re.finditer(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])', t)]
            if len(codes) >= 8 and len(starts) >= 8:
                return t, starts, codes
            print(f'  p{page} attempt {attempt}: thin (blocks={len(starts)} codes={len(codes)}), retry', flush=True)
        except Exception as e:
            print(f'  p{page} attempt {attempt}: FAIL {str(e)[:60]}', flush=True)
    return None, [], []

def parse_groups(t, starts, codes):
    def f(b, pat):
        m = re.search(pat, b, re.DOTALL); return m.group(1) if m else ''
    out = []
    for cs, code in codes:
        blk = max([x for x in starts if x < cs], default=None)
        if blk is None: continue
        b = t[blk:blk+2500]
        title = f(b, r'"group_title":"((?:[^"\\]|\\.)*)"')
        cat = f(b, r'"category_name":"([^"]+)"')
        ctry = f(b, r'"country":\{"id":\d+,"name":"([^"]+)"')
        try: title = title.encode().decode('unicode_escape')
        except: pass
        out.append({'code': code, 'title': title.strip(), 'cat': cat, 'country': ctry})
    # dedupe codes within page (keep first)
    seen = {}
    for g in out:
        seen.setdefault(g['code'], g)
    return list(seen.values())

CC = {'United States':'US','United Kingdom':'UK','India':'IN','Pakistan':'PK','Indonesia':'ID',
      'Canada':'CA','Sri Lanka':'LK','Afghanistan':'AF','United Arab Emirates':'AE','Australia':'AU',
      'Puerto Rico':'PR','Malaysia':'MY','Bangladesh':'BD','Nepal':'NP','Philippines':'PH'}

def main():
    tag = sys.argv[1]; pages = [int(x) for x in sys.argv[2].split(',')]
    union = pickle.load(open(WD + '/union.pkl', 'rb'))
    verified = json.load(open(WD + '/team39_verified_working.json')) if os.path.exists(WD + '/team39_verified_working.json') else []
    have = set(g['code'] for g in verified) | set(union)
    porn_drops = 0; adult_excl = 0; scam_excl = 0
    new_verified = []
    for p in pages:
        print(f'== {tag} page {p} ==', flush=True)
        t, starts, codes = fetch_page(tag, p)
        if not t:
            print('  SKIP (fetch failed)'); continue
        groups = parse_groups(t, starts, codes)
        cands = []
        for g in groups:
            title, code, cat = g['title'], g['code'], g['cat']
            if code in have: continue
            if cat == 'Adult' or 'Adult' in cat:
                adult_excl += 1; continue
            if PORN_RE.search(title) or EMOJI_RE.search(title) or VULGAR_RE.search(title):
                porn_drops += 1; continue
            if cat in OUT_OF_SLICE: continue
            if cat not in CATMAP: continue
            have.add(code)
            cands.append(g)
        print(f'  candidates: {len(cands)} (porn_drops={porn_drops} adult_excl={adult_excl})', flush=True)
        # verify
        def check(g):
            s = requests.Session(); s.headers.update(UA)
            try:
                r = s.get(f"https://chat.whatsapp.com/{g['code']}", timeout=300)
                m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
                title = html.unescape(m.group(1)).strip() if m else ''
                return (g, 'live' if title else 'dead', title)
            except Exception as e:
                return (g, 'pending', str(e)[:60])
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            for g, st, og in ex.map(check, cands):
                print(f'  {g["code"]} {st} {og[:40]!r}', flush=True)
                if st == 'live':
                    new_verified.append({'code': g['code'], 'title': g['title'], 'og': og,
                                         'gcat': g['cat'], 'country': g['country']})
    verified.extend(new_verified)
    json.dump(verified, open(WD + '/team39_verified_working.json', 'w'), indent=1)
    print(f'DONE pages={pages} new_verified={len(new_verified)} total={len(verified)} porn_drops={porn_drops} adult_excl={adult_excl}')

if __name__ == '__main__':
    main()
