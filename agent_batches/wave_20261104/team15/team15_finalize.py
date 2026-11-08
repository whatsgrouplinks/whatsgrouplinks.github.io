"""TEAM15 finalize: team15-groupsinvite.json + pending + leads (wave 20261104)."""
import json, re, sys
T = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team15'
WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104'
sys.path.insert(0, T)
from maps import COUNTRY_ISO, SITE_CAT, PORN_WORDS, ISLAMIC_WORDS, MULE_WORDS

PORN_WORDS = PORN_WORDS + ['bokep', 'مزا دینے', 'مزہ دینے', 'مزے دینے', 'مزا دے', 'seks']

def porn_hit(text):
    t = text.lower()
    return any(w in t for w in PORN_WORDS)

def mule_hit(text):
    t = text.lower()
    return any(w in t for w in MULE_WORDS)

def pick_category(site_cats, title):
    tl = title.lower()
    if 'religion-devotional-faith' in site_cats and any(w in tl for w in ISLAMIC_WORDS):
        return 'Islamic'
    for sc in site_cats:
        cat = SITE_CAT.get(sc, 'Other')
        if cat != 'Other' or sc == site_cats[0]:
            base = cat
            break
    else:
        base = 'Other'
    if base == 'Sports' and any(w in tl for w in ['game', 'gaming', 'pubg', 'free fire', 'ff ', 'bgmi']):
        return 'Gaming'
    if base == 'Entertainment' and any(w in tl for w in ['funny', 'comedy', 'meme', 'joke']):
        return 'Funny'
    return base

def country_for(countries):
    for c in countries:
        iso = COUNTRY_ISO.get(c)
        if iso:
            return iso
    return 'International'

def make_desc(title, cat, iso):
    t = title.strip()
    ctry = 'international' if iso == 'International' else iso
    kw = {'Sports': 'sports fans', 'Gaming': 'gamers', 'Jobs': 'job seekers',
          'Education': 'students and learners', 'Entertainment': 'entertainment lovers',
          'Friendship': 'making new friends', 'News': 'news updates',
          'Islamic': 'Islamic community', 'Business': 'business networking',
          'Finance': 'finance and investing', 'Buy-Sell': 'buying and selling',
          'Health': 'health and wellness', 'Community': 'community members',
          'Technology': 'tech enthusiasts', 'Crypto': 'crypto traders',
          'Travel': 'travel lovers', 'Music': 'music lovers', 'Movies': 'movie fans',
          'Food': 'food lovers', 'Pets': 'pet lovers', 'Funny': 'fun and laughter',
          'Girls': 'girls community', 'Regional': 'local community',
          'Other': 'members'}.get(cat, 'members')
    d = f'Join "{t}", a {cat.lower()} WhatsApp group for {kw} ({ctry}). Share updates, chat and connect with people who share your interests.'
    return d[:280]

def clean_title(t):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'\s*\|\s*GroupsInvite\s*$', '', t, flags=re.I)
    t = re.sub(r'\s*WhatsApp Group( Invite Link|/Channel Invite Link)?\s*$', '', t, flags=re.I)
    t = re.sub(r'\s*\|\s*WhatsApp Group Link\s*$', '', t, flags=re.I)
    return t.strip()[:120]

def main():
    verify = json.load(open(f'{T}/verify.json'))
    try:
        classify = json.load(open(f'{T}/classify.json'))
    except Exception:
        classify = {}
    try:
        slug_meta = json.load(open(f'{T}/slug_meta.json'))
    except Exception:
        slug_meta = {}
    try:
        detail_meta = json.load(open(f'{T}/detail_meta.json'))
    except Exception:
        detail_meta = {}

    union = set(x.lower() for x in json.load(open(f'{WAVE}/dedupe_union.json')))
    try:
        t30 = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/team30R-groupsinvite.json'))
        union |= set(re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', i['invite']).group(1).lower() for i in t30)
    except Exception as e:
        print('team30R exclusion unavailable:', e, flush=True)

    items, pending = [], []
    seen_codes = set()
    porn_drops = 0
    mule_flags = 0
    skipped_union = 0

    for code, v in verify.items():
        status = v['status']
        slug = v.get('slug', '')
        if status == 'verified':
            key = code.lower()
            if key in union or key in seen_codes:
                skipped_union += 1
                continue
            title = clean_title(v.get('title', '') or '')
            sm = slug_meta.get(slug, {})
            if not title and sm.get('titles'):
                title = clean_title(sm['titles'][0])
            dm = detail_meta.get(slug, {})
            if not title and dm.get('title'):
                title = clean_title(dm['title'])
            if not title:
                continue
            if porn_hit(title):
                porn_drops += 1
                continue
            if mule_hit(title):
                mule_flags += 1
                continue
            site_cats = list(sm.get('cats', []) or []) + [c for c in dm.get('cats', []) if c not in sm.get('cats', [])]
            countries = list(sm.get('countries', []) or []) + [c for c in dm.get('countries', []) if c not in sm.get('countries', [])]
            cat = pick_category(site_cats, title) if site_cats else 'Other'
            iso = country_for(countries)
            items.append({
                'name': title,
                'category': cat,
                'country': iso,
                'description': make_desc(title, cat, iso),
                'invite': f'https://chat.whatsapp.com/{code}',
                'image': '',
            })
            seen_codes.add(key)
        elif status in ('transport', 'rate-limited', 'stopped'):
            cl = classify.get(slug, {})
            title = ''
            sm = slug_meta.get(slug, {})
            if sm.get('titles'):
                title = clean_title(sm['titles'][0])
            pending.append({
                'name': title or slug,
                'category': 'Other',
                'country': 'International',
                'description': f'Unverified groupsinvite.link group listing (slug {slug}).',
                'invite': f'https://chat.whatsapp.com/{cl.get("code", slug)}',
                'image': '',
                'note': status,
            })

    json.dump(items, open(f'{WAVE}/team15-groupsinvite.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(f'{WAVE}/team15-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    classify = json.load(open(f'{T}/classify.json'))
    n_class = len(classify)
    leads = [{
        'domain': 'groupsinvite.link',
        'url': 'https://groupsinvite.link/group/rules/<slug>/',
        'why': (f'Resume: rules-page classification at {T}/classify.json '
                f'covers {n_class} of 2326 group-candidate slugs; re-run team15_classify.py then '
                'team15_verify.py then team15_details.py then team15_finalize.py. 231 channel-pattern slugs '
                '(0029v*/029v*) excluded as channels; 1173 /group/<tag>/ listing pages untouched (listing_meta.json).'),
    }]
    json.dump(leads, open(f'{WAVE}/team15-leads.json', 'w'), ensure_ascii=False, indent=1)
    print(f'verified items: {len(items)}')
    print(f'pending: {len(pending)}')
    print(f'porn drops: {porn_drops}')
    print(f'mule flags: {mule_flags}')
    print(f'skipped (union/own-dup): {skipped_union}')

if __name__ == '__main__':
    main()
