#!/usr/bin/env python3
"""team12 wave_20261104: groupjoin.link entertainment tag + entertainment-adjacent tags.
Harvest via api.groupjoin.link (curl --http1.1), dedupe vs union + Nov-3 banked sets,
porn/scam/minors filter, verify via chat.whatsapp.com og:title (keep-alive sessions).
Outputs JSON to STDOUT between markers; parent writes the files.
"""
import subprocess, json, re, time, html as htmllib, os, sys
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
W3 = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261103')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# tag -> pages @limit=20
TAGS = {'entertainment': 17, 'videos': 98, 'fun': 18, 'masti': 13, 'comedy': 15,
        'jokes': 13, 'status': 14, 'songs': 12, 'tiktok': 10, 'dance': 5,
        'anime': 5, 'memes': 2, 'reels': 2, 'drama': 2, 'clips': 1,
        'stories': 1, 'cartoons': 1}

CODE_RE = re.compile(r'chat\.whatsapp\.com/(invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
OG_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

PORN_RE = re.compile(
    r'porn|pornhub|xnxx|xvideos|xhamster|redtube|\bxxx\b|nude|naked|'
    r'sex\s*(video|chat|call|tape|clip|service)?|sexy\s*(video|call|girl|bhabhi|aunty|nude)|'
    r'escort|call\s*girl|video\s*call\s*(girl|sex)|nude\s*video\s*call|'
    r'fuck|dick|pussy|boobs?|anal|blowjob|handjob|horny|orgasm|slut|whore|'
    r'cumshot|deepthroat|masturbat|bokep|'
    r'مزا دینے|مزہ دینے|مزے دینے|سیکس|سیکسی|ننگی|ننگا|فحش|چدائی|گرم لڑکی|شہوت انگیز|'
    r'सेक्स|सेक्सी|नंगी|नंगा|अश्लील|म[ज़ज]ा देने|चुदाई|गर्म लड़की|'
    r'\U0001f975|\U0001f346|\U0001f351|\U0001f51e|\U0001f4a6|\U0001f445|\U0001f444|\U0001f48b',
    re.I)
SCAM_RE = re.compile(
    r'satta|matka|double (?:your|the) money|hyip|money (?:doubler|multiplier)|'
    r'paypal (?:receiver|loader)|dumps|fullz|phishing|aviator (?:predictor|hack)|'
    r'betting (?:tips|fixed match)|investment (?:double|2x|5x|10x)', re.I)
MINOR_RE = re.compile(
    r'\bteen(?:s|age)?\s*(?:dating|girls?|boys?|love)|school\s*(?:girls?|boys?)|'
    r'under\s*1[0-7]|underage|minor\s*(?:dating|girls?|boys?)|بچی|چھوٹی لڑکی|नाबालिग', re.I)
PERSONAL_RE = re.compile(r'\+\d[\d ()\-]{7,}|[\w.]+@[\w.]+\.\w+')

def load_exclusions():
    excl = set(json.load(open(WAVE + '/dedupe_union.json')))
    m = json.load(open(W3 + '/team14_merged.json'))
    excl |= set(m.keys())
    for it in json.load(open(W3 + '/team14-unverified-pending.json')):
        c = it.get('code', '')
        if re.fullmatch(r'[A-Za-z0-9]{20,24}', c):
            excl.add(c)
    for fn in ('team12-gjl-entertainment.json', 'team12-unverified-pending.json'):
        for it in json.load(open(W3 + '/' + fn)):
            mm = CODE_RE.search(it.get('invite', ''))
            if mm:
                excl.add(mm.group(2))
    return excl

def fetch_page(tag, page):
    url = f'https://api.groupjoin.link/groups?tag={tag}&page={page}&limit=20&safeSearch=blur'
    last_err = ''
    for attempt in range(3):
        try:
            out = subprocess.run(['curl', '-s', '-m', '45', '--http1.1', '-A', UA, url],
                                 capture_output=True, text=True, timeout=55)
            body = (out.stdout or '').strip()
            if not body:
                last_err = f'empty_body rc={out.returncode}'
            else:
                j = json.loads(body)
                if isinstance(j, dict) and isinstance(j.get('data'), list):
                    return j['data']
                last_err = 'BADJSON:' + body[:80]
        except Exception as e:
            last_err = type(e).__name__ + ':' + str(e)[:80]
        time.sleep(4)
    return 'FAIL:' + last_err

def fix_mojibake(s):
    if any(x in s for x in ('Ã', 'â€', 'ðŸ')):
        try:
            return s.encode('latin-1').decode('utf-8')
        except Exception:
            return s
    return s

def clean_title(s):
    s = htmllib.unescape(s or '')
    s = fix_mojibake(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def pick_category(title, tags, api_cat):
    t = (title + ' ' + ' '.join(tags)).lower()
    if any(w in t for w in ('movie', 'film', 'cinema', 'netflix', 'web series', 'drama serial', 'kdrama')):
        return 'Movies'
    if any(w in t for w in ('song', 'music', 'singer', 'dj ', 'gana', 'geet')):
        return 'Music'
    if any(w in t for w in ('meme', 'funny', 'comedy', 'joke', 'haha', 'humor', 'humour', 'hasna', 'latifa')):
        return 'Funny'
    if any(w in t for w in ('game', 'gaming', 'pubg', 'free fire', 'bgmi', 'gamer')):
        return 'Gaming'
    if any(w in t for w in ('dating', 'date ', 'love', 'shadi', 'rishta', 'dost', 'girlfriend', 'boyfriend', 'girls only', 'girls group')):
        return 'Girls'
    if any(w in t for w in ('friend', 'dosti', 'yaari')):
        return 'Friendship'
    m = {'Entertainment': 'Entertainment', 'Friendship': 'Friendship', 'Music': 'Music',
         'Movies': 'Movies', 'Comedy': 'Funny', 'Gaming': 'Gaming', 'News': 'News',
         'Education': 'Education', 'Sports': 'Sports'}
    return m.get(api_cat, 'Entertainment')

def make_desc(title, category, country_name):
    topic = re.sub(r'[^\w\s\-&]', ' ', title)
    topic = re.sub(r'\s+', ' ', topic).strip()[:60] or 'fun and entertainment'
    cn = country_name if country_name else 'global'
    kw = {'Entertainment': 'funny videos, memes and daily entertainment',
          'Funny': 'funny memes, jokes and comedy clips',
          'Music': 'songs, music videos and audio entertainment',
          'Movies': 'movie updates, clips and film entertainment',
          'Girls': 'friendly chat, fun and social entertainment',
          'Friendship': 'friendly chat, fun and social entertainment',
          'Gaming': 'games, gaming videos and fun entertainment'}.get(category, 'videos, memes and daily entertainment')
    return (f'A lively {cn} {category.lower()} WhatsApp group around {topic}. '
            f'Members share {kw} with an active community.')

def main():
    print('STEP 1: loading exclusions...', flush=True)
    excl = load_exclusions()
    print(f'exclusion set: {len(excl)}', flush=True)

    print('STEP 2: harvesting API pages...', flush=True)
    jobs = [(t, p) for t, np in TAGS.items() for p in range(1, np + 1)]
    print(f'{len(jobs)} page fetches queued', flush=True)
    records = []
    fails = []
    def one(job):
        tag, page = job
        return tag, page, fetch_page(tag, page)
    from concurrent.futures import as_completed
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(one, job): job for job in jobs}
        done = 0
        for fut in as_completed(futs):
            tag, page = futs[fut]
            done += 1
            try:
                _t, _p, data = fut.result()
            except Exception as e:
                data = 'EXC:' + str(e)[:80]
            if isinstance(data, list):
                records.extend((tag, r) for r in data)
                if done % 10 == 0 or done <= 5:
                    print(f'  page ok {done}/{len(jobs)} ({tag} p{page}): records={len(records)}', flush=True)
            else:
                fails.append((tag, page, data))
                print(f'  PAGE FAIL {done}/{len(jobs)}: {tag} p{page}: {str(data)[:100]}', flush=True)
    print(f'harvest done: {len(records)} records, {len(fails)} page fails', flush=True)
    if fails:
        print('FAIL_SAMPLE:' + json.dumps(fails[:10]), flush=True)

    print('STEP 3: dedupe + filter...', flush=True)
    seen = set()
    cands, porn_drops, scam_drops, minor_drops, dup_drops, bad_code = 0, 0, 0, 0, 0, 0
    todo = []
    for tag, r in records:
        link = r.get('link', '') or ''
        mm = CODE_RE.search(link)
        if not mm:
            bad_code += 1
            continue
        if mm.group(1):
            continue  # /invite/ channel
        code = mm.group(2)
        if code in excl or code in seen:
            dup_drops += 1
            continue
        seen.add(code)
        title = clean_title(r.get('group_title', ''))
        desc = clean_title(r.get('group_desc', ''))
        blob = title + ' ' + desc
        if PERSONAL_RE.search(title):
            continue
        if PORN_RE.search(blob):
            porn_drops += 1
            continue
        if SCAM_RE.search(blob):
            scam_drops += 1
            continue
        if MINOR_RE.search(blob):
            minor_drops += 1
            continue
        api_cat = (r.get('category') or {}).get('category_name', '')
        if api_cat.lower() == 'adult':
            # keep only clearly clean dating-social; everything else dropped
            tl = blob.lower()
            if not any(w in tl for w in ('dating', 'friend', 'dosti', 'girls', 'love', 'chat', 'shadi', 'rishta')):
                porn_drops += 1
                continue
        country = (r.get('country') or {})
        todo.append({'code': code, 'title': title, 'tags': r.get('tags') or [],
                     'api_cat': api_cat,
                     'iso2': country.get('iso2') or 'International',
                     'cname': country.get('name') or ''})
        cands += 1
    stats = {'records': len(records), 'page_fails': len(fails), 'dup_drops': dup_drops,
             'bad_code': bad_code, 'porn_drops': porn_drops, 'scam_drops': scam_drops,
             'minor_drops': minor_drops, 'candidates': cands}
    print('FILTER_STATS:' + json.dumps(stats), flush=True)

    print('STEP 4: verifying via chat.whatsapp.com...', flush=True)
    import threading
    tls = threading.local()
    stop429 = {'hit': False}
    def get_session():
        if not hasattr(tls, 's'):
            tls.s = requests.Session()
            tls.s.headers.update({'User-Agent': UA})
        return tls.s
    def verify(c):
        if stop429['hit']:
            return c, 'rate-limited-stop', None
        url = 'https://chat.whatsapp.com/' + c['code']
        try:
            r = get_session().get(url, timeout=60)
            if r.status_code == 429:
                stop429['hit'] = True
                return c, 'rate-limited', None
            m = OG_RE.search(r.text)
            title = htmllib.unescape(m.group(1)).strip() if m else ''
            if title:
                return c, 'ok', clean_title(title)
            return c, 'dead', None
        except Exception as e:
            return c, 'transport:' + type(e).__name__, None
    verified, pending = [], []
    with ThreadPoolExecutor(max_workers=30) as ex:
        n = 0
        for c, st, og in ex.map(verify, todo):
            n += 1
            if st == 'ok':
                cat = pick_category(og, c['tags'], c['api_cat'])
                verified.append({
                    'name': og,
                    'category': cat,
                    'country': c['iso2'] if re.fullmatch(r'[A-Z]{2}', c['iso2']) else 'International',
                    'description': make_desc(og, cat, c['cname']),
                    'invite': 'https://chat.whatsapp.com/' + c['code'],
                    'image': ''})
            elif st.startswith('transport') or st == 'rate-limited':
                pending.append({'code': c['code'], 'title': c['title'], 'tag': '',
                                'note': 'transport failure' if st.startswith('transport') else 'rate-limited'})
            if n % 50 == 0:
                print(f'  verified {n}/{len(todo)}: ok={len(verified)} pending={len(pending)}', flush=True)
    print(f'verify done: ok={len(verified)} pending={len(pending)} dead-or-dropped={len(todo)-len(verified)-len(pending)}', flush=True)
    print('BEGIN_VERIFIED_JSON')
    print(json.dumps(verified, ensure_ascii=False))
    print('END_VERIFIED_JSON')
    print('BEGIN_PENDING_JSON')
    print(json.dumps(pending, ensure_ascii=False))
    print('END_PENDING_JSON')

if __name__ == '__main__':
    main()
