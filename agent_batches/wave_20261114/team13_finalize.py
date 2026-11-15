#!/usr/bin/env python3
"""team13 finalize: build candidates/leads/pending/summary from state."""
import json, re, os

WAVE = os.path.dirname(os.path.abspath(__file__))
st = json.load(open(f'{WAVE}/team13-state.json'))

def clean_name(n):
    n = n.strip()
    n = re.sub(r'\s+Grupo de WhatsApp\s*$', '', n)
    n = n.strip().strip('"').strip()
    n = re.sub(r'\s+', ' ', n)
    return n

CAT_OVERRIDES = [
    (re.compile(r'oferta laboral|oferta de trabajo|empleos?|vacantes?|trabajo', re.I), 'Jobs'),
    (re.compile(r'\bcursos?\b|estudio|aprender|aprendizaje|clases', re.I), 'Education'),
    (re.compile(r'viajes?|acampar', re.I), 'Travel'),
    (re.compile(r'comidas?|cocina|recetas?', re.I), 'Cooking'),
    (re.compile(r'\bapk\b|android|tecnolog', re.I), 'Technology'),
    (re.compile(r'memes?', re.I), 'Funny'),
    (re.compile(r'binance|cripto|crypto', re.I), 'Crypto'),
    (re.compile(r'mundial|f[uú]tbol', re.I), 'Sports'),
]
COUNTRY_RULES = [
    (re.compile(r'bolivia', re.I), 'BO', 'Bolivia'),
    (re.compile(r'uruguay', re.I), 'UY', 'Uruguay'),
    (re.compile(r'el salvador', re.I), 'SV', 'El Salvador'),
    (re.compile(r'\bindia\b', re.I), 'IN', 'India'),
    (re.compile(r'puerto montt', re.I), 'CL', 'Chile'),
    (re.compile(r'barcelona|c[aá]diz|veggies', re.I), 'ES', 'Spain'),
]

cands = []
flagged = []
for code, v in sorted(st['verified'].items()):
    name = clean_name(v['name'])
    # Puerto Montt listing title was truncated; live og:title is the real name
    if code == 'Ep8XBMOYlE1CFK1RY9y6no':
        name = 'Oferta laboral Puerto Montt'
    cat = v['category']
    for pat, c in CAT_OVERRIDES:
        if pat.search(name) or pat.search(v.get('og_title', '')):
            cat = c
            break
    country, cname = '', ''
    for pat, cc, cn in COUNTRY_RULES:
        if pat.search(name) or pat.search(v.get('og_title', '')):
            country, cname = cc, cn
            break
    desc = f'Join {name}, an active WhatsApp group for {cat.lower()}.'
    if country:
        desc += f' Connect with members from {cname}.'
    desc += ' Chat, share and connect with people who share your interests.'
    cands.append({'name': name, 'category': cat, 'country': country,
                  'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})
    # flags for coordinator review (kept per when-in-doubt-keep rule)
    if code == 'C516urnVfHg4P6yjwbKcR2':
        flagged.append({'code': code, 'name': name, 'og_title': v['og_title'],
                        'note': 'KEPT but flagged: live og:title is sexualized ("Chicas con senos") while directory listing is a Free Fire gaming group; not hard porn/xxx wording, so kept per when-in-doubt-keep; coordinator may drop.'})
    if code == 'Cf9Hk8PCbg7Ajxt8JbqUaH':
        flagged.append({'code': code, 'name': name, 'og_title': v['og_title'],
                        'note': 'KEPT but flagged: "Binance Actividades y Recompensas" is crypto-rewards themed; no explicit airdrop/free-money wording, so kept per when-in-doubt-keep; recategorized to Crypto; coordinator may drop.'})

assert len({c['invite'] for c in cands}) == len(cands), 'duplicate invite in candidates'

pending = [{'code': c, 'reason': v['reason'], 'detail': v.get('detail', '')}
            for c, v in sorted(st['pending'].items())]

leads = [f'https://tugrupo.online/whatsapp/?query-eb715b85={p}' for p in range(20, 111)]
leads.append('https://tugrupo.online/whatsapp/diversion/gymrat/')
leads.append('https://tugrupo.online/whatsapp/chat/tecnologia/')

json.dump(cands, open(f'{WAVE}/team13-candidates.json', 'w'), ensure_ascii=False, indent=1)
json.dump(leads, open(f'{WAVE}/team13-leads.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(f'{WAVE}/team13-pending.json', 'w'), ensure_ascii=False, indent=1)

n_detail = len(st['detail'])
n_with_code = sum(1 for v in st['detail'].values() if v.get('code'))
summary = {
    'team': 13,
    'slice': 'tugrupo.online — pagination page 4 onwards (pages 4, 11-19 mined) + 26 detail pages from wave_20261112 team17 leads',
    'sources': ['https://tugrupo.online/whatsapp/', 'https://tugrupo.online/whatsapp/?query-eb715b85=N (N=4,11..19)'],
    'controls': st['controls'],
    'counts': {
        'pages_mined': sorted(st['pages_done']),
        'pages_failed': st['pages_failed'],
        'listings_mined_unique': len(st['listings']),
        'detail_pages_attempted': len(st['listings']) + 26,
        'detail_pages_processed': n_detail,
        'detail_pages_with_code': n_with_code,
        'raw_fresh_codes_checked': n_with_code,
        'verified_kept': len(st['verified']),
        'dupes': 41,
        'dupes_union': 40,
        'dupes_team17_candidates': 0,
        'dupes_within_team': 1,
        'dead_no_og_title': len(st['dead']),
        'excluded': len(st['excluded']),
        'pending': len(st['pending']),
        'leads_banked': len(leads),
    },
    'excluded': [{'code': c, 'name': v.get('name', ''), 'og_title': v.get('og_title', ''), 'reason': v['reason']}
                for c, v in sorted(st['excluded'].items())],
    'flagged_kept_for_review': flagged,
    'dead_codes': sorted(st['dead'].keys()),
    'no_code_detail_pages': [u for u, v in sorted(st['detail'].items()) if not v.get('code')],
    'resume': 'Pagination pages 20-110 unmined (banked as leads; site has 110 pages total per its own pagination). Detail lead gymrat loaded but carries no invite code on the page; tecnologia URL is a category page, not a group. Next wave: resume at page 20.',
    'notes': [
        'Page 4 (never loaded by team17) recovered: 19 listings.',
        'First run stopped early at page 14: the fetch returned a Cloudflare "One moment, please..." challenge page (no listings), which the stop rule misread as end-of-pagination. Patched fetcher to detect challenge pages and retry; page 14 re-mined cleanly (19 listings).',
        'Proxy errors (RemoteDisconnected) hit roughly every other tugrupo.online request; retries with backoff recovered nearly all fetches.',
        '16 no-code detail pages retried in a second pass: 13 recovered a code (7 kept, 3 dead, 3 dup-union), 1 (gymrat) loads but has no invite code, 2 were dup-union on retry.',
        'No source name/link and no personal info stored in candidates; descriptions are generated from name/category/country only.',
        'Country set only where unambiguous from group name/live title (BO/UY/SV/IN/CL/ES); otherwise empty.',
    ],
}
json.dump(summary, open(f'{WAVE}/team13-summary.json', 'w'), ensure_ascii=False, indent=1)
print('candidates:', len(cands), 'leads:', len(leads), 'pending:', len(pending))
print('flagged:', len(flagged))
from collections import Counter
print(Counter(c['category'] for c in cands))
