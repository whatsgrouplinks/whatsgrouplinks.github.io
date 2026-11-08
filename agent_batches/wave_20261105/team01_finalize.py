#!/usr/bin/env python3
"""team01 finalize: build outputs from team01_progress.jsonl.
- team01-groups1-pool-a.json : verified only, exact 6-field schema
- team01-unverified-pending.json : {code, name if known, note}
- team01-leads.json : [] (no new directory leads found this run)
Drops (pre + post og:title blocks) are excluded from both files and
recorded in team01_dropped_post.json / team01_dropped_pre.json."""
import json, re, sys

BASE = '/home/hatch/workspace/whatsapp-groups-site/'
WAVE = BASE + 'agent_batches/wave_20261105/'
POOL = BASE + 'agent_batches/wave_20261104/team14-unverified-pending.json'
CAND = '/home/hatch/workspace/team28_work/candidates.json'

BLOCK_PATTERNS = [
    ('porn', r'porn'), ('xxx', r'xxx'), ('xvideo', r'x ?video'), ('pornhub', r'pornhub'),
    ('onlyfans', r'onlyfans'), ('escort', r'escort'), ('callgirl', r'call\s*girl'),
    ('nude', r'nud[ei]'), ('naked', r'naked'), ('sexvideo', r'sex\s*video'),
    ('sexy', r'sexy'), ('erotic', r'erotic'), ('adult', r'\badult\b'), ('sex', r'\bsex\b'),
    ('hyip', r'hyip'), ('satta', r'satta'), ('matka', r'matka'),
    ('dblmoney', r'(double|doubling).{0,10}money|money.{0,10}(double|doubling)'),
    ('cryptopump', r'crypto.{0,10}pump|pump.{0,10}signal'),
    ('counterfeit', r'counterfeit|fake (currency|note|money)'),
    ('moneymule', r'money\s*mule'),
    ('drugs', r'\b(cocaine|heroin|charas|weed|ganja)\b'),
    ('urlname', r'https?://|www\.|\.com\b'),
    ('phone', r'\+\d[\d\s\-]{7,}\d'),
    ('email', r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'),
]
MINOR_SEX = re.compile(r'(teen|school\s*girl|underage|child|minor|young\s*girl).{0,20}(sex|porn|xxx|nude|hot)|(sex|porn|xxx|nude).{0,20}(teen|school\s*girl|underage|child|minor)', re.I)

def blocked_reason(text):
    low = (text or '').lower()
    for name, pat in BLOCK_PATTERNS:
        if re.search(pat, low):
            return name
    if MINOR_SEX.search(low):
        return 'minor-sex'
    return None

def clean_title(t):
    t = (t or '').strip()
    t = re.sub(r'\s+whatsapp group link\s*$', '', t, flags=re.I)
    t = re.sub(r'\s+whatsapp group\s*$', '', t, flags=re.I)
    return t.strip()

COUNTRY_WORDS = {
    'pakistan': 'PK', 'india': 'IN', 'indian': 'IN', 'bangladesh': 'BD', 'nepal': 'NP',
    'sri lanka': 'LK', 'nigeria': 'NG', 'kenya': 'KE', 'ghana': 'GH',
    'south africa': 'ZA', 'usa': 'US', 'united states': 'US', 'america': 'US',
    'uk': 'GB', 'england': 'GB', 'canada': 'CA', 'australia': 'AU',
    'uae': 'AE', 'saudi arabia': 'SA', 'indonesia': 'ID', 'malaysia': 'MY',
    'philippines': 'PH', 'egypt': 'EG', 'morocco': 'MA', 'turkey': 'TR',
    'brazil': 'BR', 'mexico': 'MX', 'tanzania': 'TZ', 'uganda': 'UG',
    'zimbabwe': 'ZW', 'zambia': 'ZM', 'ethiopia': 'ET', 'myanmar': 'MM',
    'thailand': 'TH', 'vietnam': 'VN', 'china': 'CN', 'japan': 'JP',
    'korea': 'KR', 'russia': 'RU', 'germany': 'DE', 'france': 'FR',
    'italy': 'IT', 'spain': 'ES', 'netherlands': 'NL', 'poland': 'PL',
}

def infer_country(name, title):
    text = f' {name} {title} '.lower()
    for word, code in COUNTRY_WORDS.items():
        if f' {word} ' in text or text.startswith(f' {word}') or text.endswith(f'{word} '):
            return code
    return 'International'

CAT_MAP = {'Other': 'Community'}

DESC_TEMPLATES = {
    'Education': 'Join {n}, a WhatsApp group for education, study resources and learning updates. Connect with members sharing notes, exam preparation tips and the latest educational information.',
    'Jobs': 'Join {n}, a WhatsApp group for job updates, openings and hiring alerts. Connect with members sharing the latest job opportunities, career tips and employment news.',
    'Business': 'Join {n}, a WhatsApp group for business discussions, opportunities and networking. Connect with members sharing business ideas, updates and growth tips.',
    'Friendship': 'Join {n}, a WhatsApp group to make new friends and chat with friendly members. Connect with people sharing fun conversations, friendship and good company.',
    'Girls': 'Join {n}, a WhatsApp group for girls to chat, share and make new friends. Connect with friendly members for fun conversations and friendship.',
    'News': 'Join {n}, a WhatsApp group for the latest news updates and headlines. Connect with members sharing breaking news, current affairs and daily updates.',
    'Islamic': 'Join {n}, a WhatsApp group for Islamic discussions, reminders and learning. Connect with members sharing Islamic knowledge, quotes and guidance.',
    'Gaming': 'Join {n}, a WhatsApp group for gamers to discuss games, tips and updates. Connect with fellow players sharing gaming news, tricks and fun gameplay.',
    'Entertainment': 'Join {n}, a WhatsApp group for entertainment, fun and the latest updates. Connect with members sharing videos, music, movies and entertaining content.',
    'Movies': 'Join {n}, a WhatsApp group for movie lovers to discuss films, trailers and reviews. Connect with members sharing the latest movie updates and recommendations.',
    'Technology': 'Join {n}, a WhatsApp group for technology discussions, gadgets and tech news. Connect with members sharing tech tips, updates and the latest innovations.',
    'Travel': 'Join {n}, a WhatsApp group for travel lovers to share destinations, tips and experiences. Connect with members discussing trips, tours and travel plans.',
    'Food': 'Join {n}, a WhatsApp group for food lovers to share recipes, cooking tips and food updates. Connect with members discussing delicious dishes and restaurants.',
    'Music': 'Join {n}, a WhatsApp group for music lovers to share songs, artists and updates. Connect with members discussing the latest music, lyrics and performances.',
    'Health': 'Join {n}, a WhatsApp group for health tips, fitness and wellness discussions. Connect with members sharing healthy living advice and wellness updates.',
    'Pets': 'Join {n}, a WhatsApp group for pet lovers to share photos, care tips and stories. Connect with members discussing pets, animals and pet care.',
    'Buy-Sell': 'Join {n}, a WhatsApp group for buying and selling products and deals. Connect with members sharing buy and sell offers, prices and marketplace updates.',
    'Regional': 'Join {n}, a WhatsApp group for regional community discussions and local updates. Connect with members sharing local news, events and community information.',
    'Community': 'Join {n}, a WhatsApp group for community discussions, updates and friendly chat. Connect with members sharing news, information and helpful conversations.',
}

def description_for(name, cat):
    cat_key = cat if cat in DESC_TEMPLATES else 'Community'
    return DESC_TEMPLATES[cat_key].format(n=name)

def main():
    pool = json.load(open(POOL))
    slice_codes = pool['codes'][0:5892]
    union = set(json.load(open(WAVE + 'dedupe_union.json')))
    cand = {}
    for e in json.load(open(CAND)):
        cand.setdefault(e['code'], e)
    pre_dropped = json.load(open(WAVE + 'team01_dropped_pre.json'))
    pre_drop_codes = {d['code'] for d in pre_dropped}

    recs = {}
    for line in open(WAVE + 'team01_progress.jsonl'):
        try:
            d = json.loads(line)
            recs[d['code']] = d
        except Exception:
            pass

    attempted = [c for c in slice_codes if c in recs]
    missing = [c for c in slice_codes if c not in recs and c not in union and c not in pre_drop_codes]
    print(f'slice={len(slice_codes)} attempted={len(attempted)} missing-records={len(missing)}')

    verified, pending, post_dropped = [], [], []
    seen = set()
    for code in attempted:
        r = recs[code]
        og = (r.get('og_title') or '').strip()
        meta = cand.get(code, {})
        cat_raw = meta.get('cat') or 'Community'
        cat = CAT_MAP.get(cat_raw, cat_raw)
        name_known = clean_title(meta.get('post_title') or '')
        if og:
            reason = blocked_reason(og)
            if reason:
                post_dropped.append({'code': code, 'name': og, 'reason': reason})
                continue
            if code in union or code in seen:
                continue
            seen.add(code)
            name = og
            verified.append({
                'name': name,
                'category': cat,
                'country': infer_country(name, name_known),
                'description': description_for(name, cat),
                'invite': f'https://chat.whatsapp.com/{code}',
                'image': '',
            })
        else:
            note = r.get('note') or 'empty-og-title'
            if r.get('status') not in (200, None):
                note = f"http-{r.get('status')}"
            pending.append({'code': code, 'name': name_known, 'note': note})
    # codes never attempted (should be none if run completed) -> pending
    for code in missing:
        meta = cand.get(code, {})
        pending.append({'code': code, 'name': clean_title(meta.get('post_title') or ''),
                        'note': 'not-attempted: verifier stopped before this code'})

    # safety: no source name/link anywhere in verified output
    for v in verified:
        for k, val in v.items():
            assert 'groups1' not in val.lower(), f'source leak in {v}'
            assert 'http' not in val.lower() or k == 'invite', f'link leak in {v}'
    # dedupe verified by invite
    seen_inv = set()
    ded = []
    for v in verified:
        if v['invite'] in seen_inv:
            continue
        seen_inv.add(v['invite'])
        ded.append(v)
    verified = ded

    json.dump(verified, open(WAVE + 'team01-groups1-pool-a.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + 'team01-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump([], open(WAVE + 'team01-leads.json', 'w'))
    json.dump(post_dropped, open(WAVE + 'team01_dropped_post.json', 'w'), ensure_ascii=False, indent=1)
    print(f'verified={len(verified)} pending={len(pending)} post-dropped={len(post_dropped)} pre-dropped={len(pre_dropped)}')
    print('pending note breakdown:')
    from collections import Counter
    print(Counter(p['note'] for p in pending).most_common(10))
    print('verified category breakdown:')
    print(Counter(v['category'] for v in verified).most_common(20))
    print('verified country breakdown:')
    print(Counter(v['country'] for v in verified).most_common(10))

if __name__ == '__main__':
    main()
