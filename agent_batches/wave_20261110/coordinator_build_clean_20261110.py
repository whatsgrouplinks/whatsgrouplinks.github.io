#!/usr/bin/env python3
"""Wave 20261110 coordinator consolidation (repair run).
Reads the 21 per-team final verified files, cross-team dedupes (first-team-wins),
checks against the union (.existing_codes.json), screens porn/scam/phone,
writes wave_20261110_clean.json + excluded/dups/leaks/schema files.
Adapted from wave 20261109 coordinator_build_clean.py (same PORN/SCAM lists)."""
import json, re, unicodedata, os
from collections import Counter

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
SITE = '/home/hatch/workspace/whatsapp-groups-site'
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))
print('union codes:', len(union))

CANON = {'Gaming','Education','Online Earning','Community & Social','Business','Friendship','Finance','Buy Sell','Islamic','Entertainment','Jobs','Technology','Funny','Sports','Health','News'}
CATFIX = {'buy-sell':'Buy Sell','buysell':'Buy Sell','buy & sell':'Buy Sell','movies':'Entertainment','music':'Entertainment','finance':'Finance','funny':'Funny','education':'Education','business':'Business','general':'Community & Social'}

PORN = ['porn','xxx','sex','sexy','hookup','escort','cam girl','camgirl','call girl','callgirl','bokep','nude','naked','desi sex','hot girl','sexy girl','erotic','fuck','pussy','dick','boobs','s3x','\u1e9eex','sexo','sexchat','sexting','masturbat','horny','naughty','fwb','friends with benefits','kambi','desi bhabhi','aunty sex','girls sex','boys sex','video call girl','leak','leaked','mms','viral mms','onlyfans','pornhub','xvideos','redtube','brazzers','hentai','nekopoi','jav ','18+','\U0001f51e','\U0001f346','\U0001f348']
SCAM = ['b-love','blove','forsage','sheyi','pearlvine','holiverse','meta-whale','metawhale','unick forex','airdrop','free money','earn money without investment','usdt flash','btc flash','binary option','carding','stolen cc','dark web','data hack','hack software','free fire hack','paid hack']

def fold(s):
    return unicodedata.normalize('NFKD', str(s or '')).lower()

def strip_prohibitions(s):
    s = str(s or '')
    out = []
    for sent in re.split(r'(?<=[.!?])\s+|\n', s):
        low = fold(sent)
        if any(w in low for w in ['na karein','not allowed','prohibit','forbidden','no porn','no adult','no 18+','no sex','do not share','dont share','strictly prohibited','not allow']):
            continue
        out.append(sent)
    return ' '.join(out)

def screen(name, desc):
    text = fold(name) + ' ' + fold(strip_prohibitions(desc))
    # food-context guard: eggplant emoji among food emojis is cooking, not porn
    food_emojis = ['\U0001f345', '\U0001f347', '\U0001f349', '\U0001f350', '\U0001f355', '\U0001f356', '\U0001f357', '\U0001f32e', '\U0001f32f', '\U0001f950', '\U0001f951', '\U0001f95a', '\U0001f414']
    has_food = any(e in text for e in food_emojis)
    for p in PORN:
        if p in text:
            if p == '\U0001f346' and has_food and 'cook' in fold(name) + fold(desc):
                continue
            return 'porn:' + p
    for p in SCAM:
        if p in text: return 'scam:' + p
    if re.search(r'\d{7,}', fold(name) + ' ' + fold(desc)): return 'phone'
    return None

# (team, file) in team-number order — first-team-wins
TEAM_FILES = [
    (1, 'team01-leads-slice1.json'),
    (4, 'team04-leads-slice4.json'),
    (5, 'team05-leads-slice5.json'),
    (7, 'team07-leads-slice7.json'),
    (8, 'team08-leads-slice8.json'),
    (10, 'team10-linkado-1900.json'),
    (11, 'team11-linkado-0-499.json'),
    (12, 'team12-linkado-500-999.json'),
    (14, 'team14-77links.json'),
    (17, 'team17-groupssor.json'),
    (18, 'team18-grouplinksforyou.json'),
    (20, 'team20-wglfinder.json'),
    (23, 'team23-groupsinvite.json'),
    (24, 'team24-whtspgrouplink.json'),
    (25, 'team25-newdirs-southasia.json'),
    (26, 'team26-newdirs-africa-mideast.json'),
    (27, 'team27-newdirs-seasia.json'),
    (28, 'team28-newdirs-latam-gulf.json'),
    (29, 'team29-listicles-edu-jobs.json'),
    (30, 'team30-listicles-mixed.json'),
    (32, 'team32-tglinkhub-igrupos.json'),
]

raw_total = 0; clean = {}; excluded = []; dups = []; union_leaks = []; schema_err = []
for n, f in TEAM_FILES:
    p = os.path.join(WAVE_DIR, f)
    if not os.path.exists(p):
        print('MISSING', f); continue
    items = json.load(open(p))
    raw_total += len(items)
    for it in items:
        code = it.get('invite', '').rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
        if not code or len(code) < 10:
            schema_err.append({'team': n, 'reason': 'bad-code', 'item': it}); continue
        if code in union:
            union_leaks.append({'team': n, 'code': code}); continue
        cat = it.get('category', '')
        if cat not in CANON:
            fixed = CATFIX.get(fold(cat).strip())
            if fixed: cat = fixed
            else:
                schema_err.append({'team': n, 'reason': 'bad-cat', 'item': it}); continue
        if code in clean:
            dups.append({'team': n, 'code': code, 'first': 'team-' + str(clean[code]['_team'])}); continue
        name = str(it.get('name', '')).strip()
        desc = str(it.get('description', '')).strip()
        if not name or not desc:
            schema_err.append({'team': n, 'reason': 'empty-name-desc', 'item': it}); continue
        reason = screen(name, desc)
        if reason:
            excluded.append({'team': n, 'code': code, 'name': name, 'reason': reason}); continue
        cc = str(it.get('country', '')).strip() or 'IN'
        clean[code] = {'name': name, 'category': cat, 'country': cc, 'description': desc,
                       'invite': f'https://chat.whatsapp.com/{code}', '_team': n}

print('raw team items:', raw_total)
print('clean unique:', len(clean))
print('cross-team dups:', len(dups))
print('union leaks:', len(union_leaks))
print('schema errors:', len(schema_err))
print('screen-excluded:', len(excluded))
print('per-team kept:', dict(Counter(c['_team'] for c in clean.values())))

json.dump(dups, open(os.path.join(WAVE_DIR, 'wave_20261110_cross_dups.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261110_excluded.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(schema_err, open(os.path.join(WAVE_DIR, 'wave_20261110_schema_err.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(union_leaks, open(os.path.join(WAVE_DIR, 'wave_20261110_union_leaks.json'), 'w'), indent=1)
out = [{k: v for k, v in c.items() if k != '_team'} for c in clean.values()]
json.dump(out, open(os.path.join(WAVE_DIR, 'wave_20261110_clean.json'), 'w'), indent=1, ensure_ascii=False)
# keep team attribution for the manifest
json.dump({code: c['_team'] for code, c in clean.items()}, open(os.path.join(WAVE_DIR, 'wave_20261110_clean_teams.json'), 'w'), indent=1)
print('wrote wave_20261110_clean.json with', len(out), 'groups')
