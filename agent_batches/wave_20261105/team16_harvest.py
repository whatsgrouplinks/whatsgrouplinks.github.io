#!/usr/bin/env python3
"""Team16 wave 20261105 — groupjoin.link harvest (funny/health/community/girls).
State + scripts live in agent_batches/wave_20261105/ (NOT /tmp: /tmp gets wiped).
Slow cadence. Dedupe vs dedupe_union.json before verifying.
Usage: python3 team16_harvest.py phase1   (totals already known; harvests pages)
"""
import re, json, time, random, html, os, sys, subprocess, unicodedata

WORK = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
UA_STR = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BS = chr(92)
VAL = r'((?:\\.|[^"\\])*)'   # a JSON string value (escaped)

union = set(json.load(open(f'{WORK}/dedupe_union.json')))
print('union size', len(union), flush=True)

def fetch(url, timeout=30):
    # groupjoin.link drops Python urllib (RemoteDisconnected); curl works.
    for attempt in range(2):
        try:
            p = subprocess.run(
                ['curl', '-sL', '-A', UA_STR, '--max-time', str(timeout), url],
                capture_output=True, timeout=timeout + 10)
            if p.returncode == 0 and p.stdout:
                return p.stdout.decode('utf-8', 'ignore'), 200
        except Exception:
            if attempt == 1:
                raise
        time.sleep(2)
    raise RuntimeError(f'curl fetch failed: {url}')

def decode_page(html_text):
    # Flight payload escapes every quote as \". Replace ONLY \" -> " ;
    # keep \n, \uXXXX, \/ intact (valid JSON escapes, handled by json.loads).
    return html_text.replace(BS + chr(34), chr(34))

def unesc(v):
    if v is None:
        return None
    try:
        return json.loads(chr(34) + v + chr(34))
    except Exception:
        return v.replace(BS + chr(34), chr(34)).replace(BS + 'u0026', '&')

def field(span, name):
    m = re.search(name + r'":"' + VAL + r'"', span)
    return unesc(m.group(1)) if m else None

def numfield(span, name):
    m = re.search(name + r'":(\d+)', span)
    return int(m.group(1)) if m else None

def boolfield(span, name):
    m = re.search(name + r'":(true|false|\d+)', span)
    if not m:
        return None
    v = m.group(1)
    return True if v in ('true', '1') else False

def parse_cards(html_text):
    """Extract group records from a groupjoin.link tag page."""
    t = decode_page(html_text)
    recs = []
    for m in re.finditer(r'group_uid', t):
        span = t[m.start():m.start() + 4500]
        uid = field(span, 'group_uid')
        title = field(span, 'group_title')
        desc = field(span, 'group_desc')
        img = field(span, 'group_img')
        link = field(span, 'link')
        cat = field(span, 'category_name')
        iso = field(span, 'iso2')
        nsfw = boolfield(span, 'nsfw')
        rating = numfield(span, 'contentRating')
        created = field(span, 'created_at')
        tm = re.search(r'"tags":\[([^\]]*)\]', span)
        tags = tm.group(1) if tm else ''
        if uid and link:
            recs.append(dict(uid=uid, title=title, desc=desc, img=img, link=link,
                             cat=cat, iso=iso, nsfw=nsfw, rating=rating,
                             created=created, tags=tags))
    return recs

def extract_code(link):
    if not link:
        return None
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', link)
    return m.group(1) if m else None

# ---------------- content filter ----------------
SEXUAL = re.compile(r'porn|xxx|nude|naked|sex\s*(video|call|chat|tape)|video\s*call\s*(girl|sex)|call\s*girl|escort|leak(ed)?\s*(video|mms|photo)|viral\s*video|vairal|desi\s*video|dasi\s*video|bro\s*sis|mms|hot\s*video|sexy|18\s*\+|blue\s*film|bf\s*video|\bcp\b.{0,12}video|child\s*(video|sex|porn)|rape|school\s*girl|teen\s*(girl|sex)|bhabhi\s*(video|sex|hot)|aunty\s*(video|sex|hot)|xxx|hentai|onlyfans|realmeet|video\s*call\s*\d|face\s*video\s*call', re.I)
ADULT_SOFT = re.compile(r'live\s*show|realmeet|video\s*call|sexy|hot|saxy|adlut|adult', re.I)
SCAM = re.compile(r'hyip|double\s*(your|the)?\s*money|satta|matka|crypto\s*pump|pump\s*(signal|group)|counterfeit|fake\s*(passport|note|id|document)|money\s*mule|drug|weed|cocaine|heroin|opium|charas|buy\s*(cocaine|weed|heroin)|earn\s*\d+\s*(per|daily)|investment\s*double', re.I)
PHONE = re.compile(r'\+?\d[\d\s\-]{8,}\d')
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
URLRE = re.compile(r'https?://\S+|www\.\S+')

def blocked_reason(rec):
    name = (rec.get('title') or '')
    desc = (rec.get('desc') or '')
    tags = (rec.get('tags') or '')
    blob = f'{name} {desc} {tags}'
    link = rec.get('link') or ''
    if '/channel/' in link:
        return 'channel-link'
    if SEXUAL.search(blob):
        return 'sexual/porn-content'
    if SCAM.search(blob):
        return 'scam/fraud/drug'
    if re.search(r'\b(child|minor)\b', blob, re.I) and re.search(r'video|sex|nude|hot|porn', blob, re.I):
        return 'sexualising-minors'
    if URLRE.search(name) or re.match(r'^(https?://|www\.)', name.strip()):
        return 'name-is-url'
    if PHONE.search(name):
        return 'name-is-phone'
    # Directory contentRating is 18 for nearly every group on these tags
    # (incl. clean comedy/shayari), so rating/nsfw alone are NOT a block.
    # Block Adult-category groups only with a sexual signal (tags/name/desc/nsfw).
    if (rec.get('cat') or '').lower() == 'adult':
        if rec.get('nsfw') is True or ADULT_SOFT.search(blob):
            return 'adult-sexual'
    return None

CATMAP = {
    'entertainment': 'Entertainment', 'funny': 'Entertainment', 'fun': 'Entertainment',
    'comedy': 'Entertainment', 'jokes': 'Entertainment', 'memes': 'Entertainment',
    'videos': 'Entertainment', 'songs': 'Entertainment', 'tiktok': 'Entertainment',
    'dance': 'Entertainment', 'anime': 'Entertainment', 'reels': 'Entertainment',
    'drama': 'Entertainment', 'clips': 'Entertainment', 'stories': 'Entertainment',
    'cartoons': 'Entertainment', 'masti': 'Entertainment', 'status': 'Entertainment',
    'health': 'Health', 'community': 'Community & Social', 'girls': 'Friendship',
    'friendship': 'Friendship', 'love & relationship': 'Friendship',
    'love': 'Friendship', 'education': 'Education', 'news': 'News', 'sports': 'Sports',
    'gaming': 'Gaming', 'business': 'Business', 'technology': 'Technology',
    'islamic': 'Islamic', 'jobs': 'Jobs',
}

def clean_text(t):
    if not t:
        return ''
    t = html.unescape(t)
    t = unicodedata.normalize('NFKD', t)  # fancy bold/script letters -> ASCII
    t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Cf')  # drop ZWJ/ZWNJ etc.
    t = URLRE.sub(' ', t)
    t = EMAIL.sub(' ', t)
    t = PHONE.sub(' ', t)
    t = re.sub(r'groupjoin\.?link', ' ', t, flags=re.I)
    t = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', t)   # literal \uXXXX leftovers
    t = re.sub(r'\\[ntr]', ' ', t)              # literal \n \t \r leftovers
    t = t.replace(chr(92), ' ')
    # strip emoji / symbols, keep letters, numbers, basic punctuation
    t = ''.join(ch for ch in t if ord(ch) < 0x2500 and ch not in '�')
    t = re.sub(r'\s+', ' ', t).strip(' .,-:|')
    return t.strip()

def build_description(rec, category):
    d = clean_text(rec.get('desc') or '')
    name = clean_text(rec.get('title') or '')
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', d) if s.strip()]
    sents = [s for s in sents if len(s) > 8]
    topic = {'Entertainment': 'funny videos, jokes and memes',
             'Health': 'health tips, fitness and wellness',
             'Community & Social': 'community chat and social discussions',
             'Friendship': 'friendship, chatting and meeting new people'}.get(category, 'chatting and community discussions')
    # generic directory boilerplate ("Welcome to my whatsapp group X. Please join...") carries no content
    boiler = {'welcome', 'to', 'my', 'whatsapp', 'group', 'please', 'join', 'the', 'and', 'a', 'an'}
    def is_boiler(s):
        name_words = set(re.findall(r'[a-z]+', name.lower()))
        words = [w for w in re.findall(r'[a-z]+', s.lower()) if w not in name_words]
        content = [w for w in words if w not in boiler]
        return not content
    sents = [s for s in sents if not is_boiler(s)]
    if not sents:
        base = f'Join {name}, a WhatsApp group for {topic}.' if name else f'A WhatsApp group for {topic}.'
        return base + f' Share {topic} and connect with members from around the world.'
    desc = ' '.join(sents[:2])
    if len(desc) < 25:
        desc = desc.rstrip('.!? ') + f'. A WhatsApp group for {topic} — chat, share and connect with members.'
    return desc[:500]

def build_entry(rec, source_tag):
    cat_dir = (rec.get('cat') or '').strip()
    category = CATMAP.get(cat_dir.lower(), CATMAP.get(source_tag.lower(), 'Entertainment'))
    name = clean_text(rec.get('title') or '')
    code = extract_code(rec.get('link'))
    img = rec.get('img') or ''
    if img.startswith('https://static.whatsapp.net'):
        img = ''
    img = html.unescape(img).replace('&amp;', '&') if img else ''
    country = (rec.get('iso') or '').strip().upper() or 'International'
    if len(country) != 2:
        country = 'International'
    return {
        'name': name,
        'category': category,
        'country': country,
        'description': build_description(rec, category),
        'invite': f'https://chat.whatsapp.com/{code}',
        'image': img,
        '_code': code,
        '_og': None,
    }

# ---------------- PHASE 1: harvest (totals already known) ----------------
# Totals measured 2026-11-05 ~07:00 PKT: funny 693, health 93, community 262,
# girls 730. All 17 baseline tags EXACTLY at Nov 4 baseline (risen: none):
# entertainment 327, videos 1941, fun 347, masti 255, comedy 290, jokes 251,
# status 279, songs 226, tiktok 190, dance 95, anime 87, memes 33, reels 39,
# drama 28, clips 18, stories 13, cartoons 5.
TOTALS = {'funny': 693, 'health': 93, 'community': 262, 'girls': 730}

def sleep_slow(a=2.0, b=4.0):
    time.sleep(random.uniform(a, b))

def harvest_tag_pages(tag, pages, out, seen_codes):
    for p in pages:
        url = f'https://groupjoin.link/tag/{tag}?limit=20&page={p}'
        try:
            body, st = fetch(url)
        except Exception as e:
            print(f'HARVEST {tag} p{p}: fetch error {e}', flush=True)
            sleep_slow()
            continue
        cards = parse_cards(body)
        print(f'HARVEST {tag} p{p}: http {st}, cards {len(cards)}', flush=True)
        for rec in cards:
            code = extract_code(rec.get('link'))
            if not code:
                continue
            if code in union:
                out['dup_union'] += 1
                continue
            if code in seen_codes:
                out['dup_batch'] += 1
                continue
            seen_codes.add(code)
            reason = blocked_reason(rec)
            if reason:
                out['blocked'].append({'code': code, 'name': rec.get('title'), 'reason': reason, 'tag': tag, 'page': p})
                continue
            entry = build_entry(rec, tag)
            if not entry['name']:
                out['noname'].append({'code': code, 'tag': tag, 'page': p})
                continue
            entry['_tag'] = tag
            entry['_page'] = p
            entry['_title_raw'] = rec.get('title')
            entry['_desc_raw'] = rec.get('desc')
            out['candidates'].append(entry)
        sleep_slow()

def checkpoint(out):
    json.dump(out, open(f'{WORK}/team16_candidates_ckpt.json', 'w'), ensure_ascii=False, indent=1)

def main():
    out = {'candidates': [], 'blocked': [], 'noname': [], 'dup_union': 0, 'dup_batch': 0}
    seen = set()
    harvest_tag_pages('funny', range(4, 36), out, seen)
    checkpoint(out)
    harvest_tag_pages('health', range(2, 6), out, seen)
    checkpoint(out)
    ct = TOTALS['community']
    harvest_tag_pages('community', range(1, -(-ct // 20) + 1), out, seen)
    checkpoint(out)
    gt = TOTALS['girls']
    harvest_tag_pages('girls', range(1, min(30, -(-gt // 20)) + 1), out, seen)
    checkpoint(out)
    json.dump(out, open(f'{WORK}/team16_candidates.json', 'w'), ensure_ascii=False, indent=1)
    print(f"PHASE1 DONE candidates={len(out['candidates'])} blocked={len(out['blocked'])} "
          f"noname={len(out['noname'])} dup_union={out['dup_union']} dup_batch={out['dup_batch']}", flush=True)

if __name__ == '__main__':
    main()
