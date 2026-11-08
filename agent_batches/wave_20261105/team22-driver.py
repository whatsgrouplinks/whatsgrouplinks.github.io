#!/usr/bin/env python3
"""team22 driver: harvest groupsinvite.link cards (curl), fetch rules pages for
invite codes, dedupe vs union, verify via chat.whatsapp.com og:title.
Checkpoints written to the wave dir (survives /tmp wipes)."""
import re, json, time, subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
from html import unescape

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
UA_GB = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
UA_CH = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
UA_WA = 'Mozilla/5.0'

def curl(url, ua, max_time=25):
    try:
        r = subprocess.run(['curl', '-sL', '--max-time', str(max_time), '-A', ua,
                            '-w', '\n%{http_code}', url],
                           capture_output=True, text=True, timeout=max_time + 15)
        out = r.stdout
        code = out.rsplit('\n', 1)[-1].strip()
        body = out[:out.rfind('\n')]
        return code, body
    except Exception as e:
        return f'ERR:{e}', ''

CARD_RE = re.compile(r'<div class="group-item">(.*?)</div>\s*</div>', re.S)

def parse_cards(h):
    out = {}
    for b in CARD_RE.findall(h):
        m = re.search(r'/group/link/([A-Za-z0-9]+)/', b)
        if not m:
            continue
        slug = m.group(1)
        nm = re.search(r'class="group-name-link"[^>]*>(.*?)</a>', b, re.S)
        name = unescape(re.sub(r'<[^>]+>', '', nm.group(1))).strip() if nm else ''
        cat = re.search(r'class="category-chip"[^>]*>(.*?)</a>', b, re.S)
        category = unescape(re.sub(r'<[^>]+>', '', cat.group(1))).strip() if cat else ''
        desc = re.search(r'data-full-description="([^"]*)"', b, re.S)
        description = unescape(desc.group(1)).strip() if desc else ''
        img = re.search(r'data-src="(https://pps\.whatsapp\.net/[^"]+)"', b)
        image = unescape(img.group(1)).replace('&amp;', '&') if img else ''
        country = re.search(r'/group/country/([a-z\-]+)/"><i[^>]*></i>([^<]+)</a>', b)
        country_name = country.group(2).strip() if country else ''
        country_slug = country.group(1) if country else ''
        tags = [unescape(t).strip() for t in re.findall(r'class="tag-pill"[^>]*>([^<]+)</a>', b)]
        out[slug] = dict(slug=slug, name=name, category=category,
                         description=description, image=image,
                         country=country_name, country_slug=country_slug, tags=tags)
    return out

def log(*a):
    print(*a, flush=True)

# ---- Phase 1: harvest cards ----
cards = {}
home = open(f'{WAVE}/team22-checkpoint-home.html', encoding='utf-8', errors='ignore').read()
cards.update(parse_cards(home))
log('homepage cards:', len(cards))
cats = ['business', 'education', 'dating', 'gaming', 'chatting', 'friendship',
        'learning', 'career', 'finance', 'entertainment', 'community', 'job']
for c in cats:
    code, h = curl(f'https://groupsinvite.link/group/{c}/', UA_GB, 30)
    before = len(cards)
    if code == '200' and h:
        cards.update(parse_cards(h))
    log(f'{c}: {code} +{len(cards)-before} total={len(cards)}')
    time.sleep(0.8)
json.dump(cards, open(f'{WAVE}/team22-cards.json', 'w'), ensure_ascii=False, indent=1)
log('TOTAL cards:', len(cards))

# ---- Phase 2: rules pages -> invite codes ----
def get_code(slug):
    code, h = curl(f'https://groupsinvite.link/group/rules/{slug}/', UA_GB, 20)
    if code != '200' or not h:
        code2, h2 = curl(f'https://groupsinvite.link/group/rules/{slug}/', UA_CH, 20)
        if code2 == '200' and h2:
            code, h = code2, h2
    if code != '200' or not h:
        return slug, None, f'rules:{code}'
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})', h)
    if not m:
        return slug, None, 'rules-no-invite'
    time.sleep(0.3)
    return slug, m.group(1), 'ok'

slugs = sorted(cards)
codes, failed = {}, {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for slug, c, note in ex.map(get_code, slugs):
        if c:
            codes[slug] = c
        else:
            failed[slug] = note
log('rules ok:', len(codes), 'failed:', len(failed))
json.dump({'codes': codes, 'failed': failed}, open(f'{WAVE}/team22-codes.json', 'w'))
if failed:
    from collections import Counter
    log('fail reasons:', Counter(failed.values()))

# ---- Phase 3: dedupe + content filter ----
union = set(json.load(open(f'{WAVE}/dedupe_union.json')))
union_low = {c.lower() for c in union}
BLOCK_RE = re.compile(r'\b(xxx|porn|sex|nude|onlyfans|escort|call\s*girl|satta|matka|betting|casino|1xbet|91club|aviator|hyip|double\s*your|money\s*double|crypto\s*pump|pump\s*signal|forex\s*signal|drug|weed|cocaine|heroin|mdma|dark\s*web|hacker|icloud\s*unlock|sim\s*unlock|child|teen\s*girl|school\s*girl|loli)\b', re.I)
SCAM_CATS = {'cryptocurrency', 'bitcoin', 'binance', 'altcoins', 'blockchain', 'btc', '91club', 'betting'}
fresh, blocked, dupes = {}, [], 0
for slug, code in codes.items():
    if code.lower() in union_low:
        dupes += 1
        continue
    c = cards[slug]
    hay = ' '.join([c['name'], c['category'], ' '.join(c['tags']), c['description'][:300]])
    if BLOCK_RE.search(hay) or (c['category'] or '').strip().lower() in SCAM_CATS:
        blocked.append({'code': code, 'name': c['name'], 'note': 'content-blocked'})
        continue
    if 'http' in c['name'].lower() or 'www.' in c['name'].lower():
        blocked.append({'code': code, 'name': c['name'], 'note': 'name-is-url'})
        continue
    fresh[slug] = code
log('dupes in union:', dupes, 'blocked:', len(blocked), 'fresh to verify:', len(fresh))
json.dump({'blocked': blocked}, open(f'{WAVE}/team22-blocked.json', 'w'))

# ---- Phase 4: verify via chat.whatsapp.com og:title ----
def verify(item):
    slug, code = item
    c, h = curl(f'https://chat.whatsapp.com/{code}', UA_WA, 20)
    if c != '200' or not h:
        return slug, code, None, f'wa:{c}'
    m = re.search(r'<meta property="og:title" content="([^"]*)"', h)
    title = unescape(m.group(1)).strip() if m else ''
    time.sleep(0.6)
    return slug, code, (title if title else None), ('ok' if title else 'empty-og-title')

verified, pending = [], []
with ThreadPoolExecutor(max_workers=4) as ex:
    for slug, code, title, note in ex.map(verify, sorted(fresh.items())):
        if title:
            verified.append({'slug': slug, 'code': code, 'og_title': title})
        else:
            pending.append({'code': code, 'name': cards[slug]['name'] or None, 'note': f'verify:{note}'})
log('verified:', len(verified), 'pending:', len(pending))
json.dump({'verified': verified, 'pending': pending}, open(f'{WAVE}/team22-verified.json', 'w'))
for v in verified:
    log('V', v['code'], '|', cards[v['slug']]['name'], '| og:', v['og_title'][:60])
log('DRIVER DONE')
