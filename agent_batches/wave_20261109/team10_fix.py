import json, re, html

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
verify = json.load(open(WAVE + 'team10_verify.json'))
cands = json.load(open(WAVE + 'team10-candidates.json'))
dropped = json.load(open(WAVE + 'team10-dropped.json'))

DROP_CODES = {
    'B5XRRdctEWCEHN5Yy8Xmiv': 'scam/money-pitch: te ensino a ganha dinheiro',
    'C5zWxTHBjD0IRTlUo7r6LJ': 'fraud: fake CNH/atestado document service',
    'Cpfr6hz2m1MAcFNrqcFOwg': 'scam/money-app: kwai impulso paid-boost scheme',
    'EpjGlg5B3XAHuh2Xj43OPf': 'scam: predatory easy-loan pitch',
    'GLrd6M2n4ZaDDvjfO0yJ2T': 'fraud-adjacent: buying LinkedIn accounts',
    'ICyWTuXW8dXLC30b2WgWsZ': 'adult: AREA SECRETA + 18+ marker',
    'IpW7w9NG1ov6sfIsSv8ygq': 'scam/money-pitch: first-sale-a-day income promise',
    'Jup8qAEbFBD5vTCj6S85DU': 'adult: name is only hot-face emoji',
    'KMZS4K5eE7oGpzix2t51qf': 'scam/money-pitch: guaranteed Pix prize',
    'KZU3UESvUa25LCpCp8Hie2': 'scam/money-pitch: secret-method VIP money group',
    'Kki0hRBgkcXHNsU12YWjvi': 'fraud: fake CNH via DETRAN system',
    'KqxIoqQkvyp5KUCyvVm4cG': 'scam/money-pitch: fazendo dinheiro em casa',
}

RENAME = {
    'EpA2TiHCQtl7H192d5YmnA': 'Radar de Ofertas ❤️',
    'INKWHBsHHR40px7ErsAYpq': 'Clube Unipress',
    'LdILjRIEfIJFtePA6zJPAD': 'OFERTAS - DROGARIA SÃO PAULO',
}

RECATEGORIZE = {
    # offer/coupon groups -> Buy Sell
    'J0d9V5GEClXEdY30s71knz': None,  # placeholder removed below
}
# by code, from manual review
RECATEGORIZE = {
    'DVT1UItF9jaAjKVillWp47': 'Community & Social',
    'DQ2WtmnHVpaGShYBzAGf7y': 'Technology',
    'IotVEj00BQAKlB9D8CPmz3': 'Technology',
    'H0U9zYq9FkNBpQ0kNsm7o3': 'Entertainment',
    'IC5kkKWDHDf9zKgf4D1wXN': 'Business',
    'GQR3uNP4dQQ2ttRs5iWOfl': 'Entertainment',
}
OFFER_TO_BUYSELL = {
    'JwUAYGjWJuPGq9hYApaofR',  # BRASIL Cupons + Links Baratos
    'EpyEHGCiCwfEnfzMrQLNC7',  # Promo Relampago
    'ByMYxB12kHC4qu1SuHzzaA',  # Promocoes Shopee VIP 1
    'G5WptYCddI93j1oMS9m67t',  # NO COCO (offers? no - skip)
}
# decide offer recategorization by name keywords instead (safer)
OFFER_WORDS = ['oferta', 'ofertas', 'promo', 'cupom', 'cupons', 'achadinho',
               'achadinhos', 'achados', 'desconto', 'shopee', 'magalu',
               'mercado livre', 'temu', 'tiktok shop', 'radar de ofertas']

FLAG_COUNTRY = {'🇦🇴': 'AO', '🇵🇹': 'PT', '🇲🇿': 'MZ', '🇧🇷': 'BR',
                '🇨🇻': 'CV', '🇬🇼': 'GW', '🇸🇹': 'ST', '🇹🇱': 'TL'}

CAT_WORD = {'Friendship': 'make new friends and chat',
            'Gaming': 'games and gaming chat',
            'Education': 'learning and study resources',
            'Jobs': 'job opportunities and career talk',
            'Buy Sell': 'buying, selling and deals',
            'Sports': 'sports talk and fans',
            'Entertainment': 'entertainment and fun',
            'Technology': 'technology talk',
            'Funny': 'funny content and laughs',
            'Finance': 'money and finance talk',
            'Health': 'health and wellness',
            'News': 'news and updates',
            'Business': 'business talk',
            'Online Earning': 'online earning ideas',
            'Community & Social': 'community chat',
            'Islamic': 'Islamic discussion'}

PROHIBIT_RE = re.compile(
    r'[^.!?\n]*(?:proibido|não é permitido|nao e permitido|não compartilhe|'
    r'nao compartilhe|não envie|nao envie|não poste|proibida|proibidas|'
    r'não é permitida|nao permitido|sem pornografia|sem conteúdo adulto|'
    r'conteúdo inapropriado|conteudo inapropriado|não compartilhem)[^.!?\n]*[.!?\n]?',
    re.I)

def rebuild_description(name, cat, page_desc):
    d = (page_desc or '').strip()
    # robust boilerplate strip: drop everything through 'na categoria X.'
    d = re.sub(r'^.*?na categoria\s+[^.]+\.\s*', '', d, flags=re.I | re.S)
    d = re.sub(r'^Grupo de WhatsApp[^.]*\.\s*', '', d, flags=re.I)
    d = PROHIBIT_RE.sub(' ', d)
    d = html.unescape(d)
    d = re.sub(r'https?://\S+|chat\.whatsapp\.com/\S+', ' ', d)
    d = re.sub(r'\+?\d[\d\s().-]{7,}\d', ' ', d)
    d = re.sub(r'\s+', ' ', d).strip()
    sents = [s for s in re.split(r'(?<=[.!?])\s+', d) if len(s) > 3]
    core = ' '.join(sents[:2]).strip()
    if len(core) > 280:
        core = core[:280].rsplit(' ', 1)[0].strip()
    if core and not core.endswith(('.', '!', '?')):
        core += '.'
    cw = CAT_WORD.get(cat, 'community chat')
    if len(core) > 15:
        desc = f'Join {name}, a WhatsApp group for {cw}. {core}'
    else:
        desc = f'Join {name}, a WhatsApp group for {cw}.'
    return re.sub(r'\s+', ' ', desc).strip()[:500]

def clean_name(n):
    n = re.sub(r'^\*+|\*+$', '', n).strip()  # decorative asterisks
    return re.sub(r'\s+', ' ', n).strip()

kept, new_drops = [], []
for c in cands:
    code = c['invite'].split('/')[-1]
    r = verify[code]
    if code in DROP_CODES:
        new_drops.append({'code': code, 'name': c['name'], 'reason': DROP_CODES[code],
                          'og_title': r.get('og_title', ''),
                          'page_title': r.get('page_title', '')})
        continue
    name = RENAME.get(code, clean_name(c['name']))
    cat = RECATEGORIZE.get(code, c['category'])
    low = name.lower()
    if cat in ('Community & Social', 'Finance') and any(
            w in low for w in OFFER_WORDS):
        cat = 'Buy Sell'
    country = 'BR'
    for flag, cc in FLAG_COUNTRY.items():
        if flag in (r.get('og_title', '') + ' ' + r.get('page_title', '')):
            country = cc
            break
    desc = rebuild_description(name, cat, r.get('page_desc', ''))
    kept.append({'name': name, 'category': cat, 'country': country,
                 'description': desc, 'invite': c['invite']})

json.dump(kept, open(WAVE + 'team10-candidates.json', 'w'), ensure_ascii=False, indent=1)
json.dump(dropped + new_drops, open(WAVE + 'team10-dropped.json', 'w'),
          ensure_ascii=False, indent=1)
from collections import Counter
print('kept:', len(kept), 'newly dropped:', len(new_drops))
print(Counter(x['category'] for x in kept))
print(Counter(x['country'] for x in kept))
for d in new_drops:
    print('DROP', d['code'], d['reason'], '|', d['name'][:50])
