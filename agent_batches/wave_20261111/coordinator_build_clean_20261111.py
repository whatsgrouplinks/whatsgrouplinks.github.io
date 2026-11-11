#!/usr/bin/env python3
"""Wave 20261111 coordinator consolidation.
Reads the 32 per-team final verified files, cross-team dedupes (first-team-wins),
checks against the union (.existing_codes.json), screens porn/scam/phone,
aggregates pending + leads (incl. team01 merged-candidates and team02
awaiting-verification codes as code-string leads), writes
wave_20261111_clean.json + excluded/dups/leaks/schema/pending/leads files.
Adapted from wave 20261110 coordinator_build_clean_20261110.py (same PORN/SCAM
lists, plus xnxx/xxnx + desi-sexual slang + putaria from this wave's team screens).
Country '' is kept as '' (NOT defaulted to IN — teams bank '' for unknown).
"""
import json, re, unicodedata, os
from collections import Counter

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'
SITE = '/home/hatch/workspace/whatsapp-groups-site'
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))
print('union codes:', len(union))

CANON = {'Gaming','Education','Online Earning','Community & Social','Business','Friendship',
         'Finance','Buy Sell','Islamic','Entertainment','Jobs','Technology','Funny','Sports',
         'Health','News','Crypto','Cooking','Poetry','Travel','Scholarship','Freelance',
         'Real Estate'}
CATFIX = {'buy-sell':'Buy Sell','buysell':'Buy Sell','buy & sell':'Buy Sell',
          'buy sell':'Buy Sell','movies':'Entertainment','music':'Entertainment',
          'finance':'Finance','funny':'Funny','education':'Education','business':'Business',
          'general':'Community & Social','other':'Community & Social',
          'regional':'Community & Social','pets':'Community & Social'}

PORN = ['porn','xxx','xnxx','xxnx','sex','sexy','hookup','escort','cam girl','camgirl',
        'call girl','callgirl','bokep','nude','naked','desi sex','hot girl','sexy girl',
        'erotic','fuck','pussy','dick','boobs','s3x','\u1e9eex','sexo','sexchat','sexting',
        'masturbat','horny','naughty','fwb','friends with benefits','kambi','desi bhabhi',
        'aunty sex','girls sex','boys sex','video call girl','leak','leaked','mms',
        'viral mms','onlyfans','pornhub','xvideos','redtube','brazzers','hentai','nekopoi',
        'jav ','18+','\U0001f51e','\U0001f346','\U0001f348','putaria',
        'chuchi','lund','chut','choot','gaand','bhosda']
SCAM = ['b-love','blove','forsage','sheyi','pearlvine','holiverse','meta-whale','metawhale',
        'unick forex','airdrop','free money','earn money without investment','usdt flash',
        'btc flash','binary option','carding','stolen cc','dark web','data hack',
        'hack software','free fire hack','paid hack']

# groupjoin.link site-category Adult — blanket exclusion per Nov-10 team13 precedent
# (Adult-category entries never fetched/verified/banked). The 2 banked copies carry
# vague titles + 'Check bio' descriptions; no porn signal proven, but the
# source-category rule applies. team20 banked one of the same codes too.
ADULT_SITE_CODES = {
    'C9BRC2yDkizLr4y9kMsCv7': 'groupjoin site-category Adult — blanket Adult exclusion per Nov-10 precedent (vague title, Check-bio desc)',
    'HJS2ZkSzI99B7ldzHA7rhW': 'groupjoin site-category Adult — blanket Adult exclusion per Nov-10 precedent (vague title, Check-bio desc)',
}

def fold(s):
    return unicodedata.normalize('NFKD', str(s or '')).lower()

def strip_prohibitions(s):
    s = str(s or '')
    out = []
    for sent in re.split(r'(?<=[.!?])\s+|\n', s):
        low = fold(sent)
        if any(w in low for w in ['na karein','not allowed','prohibit','forbidden','no porn',
                                  'no adult','no 18+','no sex','do not share','dont share',
                                  'strictly prohibited','not allow','nao pode enviar pornografia',
                                  'sem putaria','proibido pornografia']):
            continue
        out.append(sent)
    return ' '.join(out)

def screen(name, desc, code):
    if code in ADULT_SITE_CODES:
        return 'adult-site:' + ADULT_SITE_CODES[code]
    text = fold(name) + ' ' + fold(strip_prohibitions(desc))
    # food-context guard: eggplant emoji among food emojis is cooking, not porn
    food_emojis = ['\U0001f345', '\U0001f347', '\U0001f349', '\U0001f350', '\U0001f355',
                   '\U0001f356', '\U0001f357', '\U0001f32e', '\U0001f32f', '\U0001f950',
                   '\U0001f951', '\U0001f95a', '\U0001f414']
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
    (2, 'team02-leads-slice2.json'),
    (3, 'team03-leads-slice3.json'),
    (4, 'team04-leads-slice4.json'),
    (5, 'team05-leads-slice5.json'),
    (6, 'team06-leads-slice6.json'),
    (7, 'team07-leads-slice7.json'),
    (8, 'team08-leads-slice8.json'),
    (9, 'team09-pending-recheck.json'),
    (10, 'team10-linkado-2300.json'),
    (11, 'team11-linkado-2700.json'),
    (12, 'team12-linkado-0-1499.json'),
    (13, 'team13-groupjoin.json'),
    (14, 'team14-77links.json'),
    (15, 'team15-tugrupo.json'),
    (16, 'team16-grupbul.json'),
    (17, 'team17-groupssor.json'),
    (18, 'team18-grouplinksforyou.json'),
    (19, 'team19-groupsnest.json'),
    (20, 'team20-wglfinder.json'),
    (21, 'team21-freewagroup.json'),
    (22, 'team22-walink.json'),
    (23, 'team23-groupsinvite.json'),
    (24, 'team24-whtspgrouplink.json'),
    (25, 'team25-newdirs-southasia.json'),
    (26, 'team26-newdirs-africa-mideast.json'),
    (27, 'team27-newdirs-seasia.json'),
    (28, 'team28-newdirs-latam-gulf.json'),
    (29, 'team29-listicles-edu-jobs.json'),
    (30, 'team30-listicles-mixed.json'),
    (31, 'team31-tglinkhub-verify2.json'),
    (32, 'team32-igrupos-geogated.json'),
]

raw_total = 0; clean = {}; excluded = []; dups = []; union_leaks = []; schema_err = []
excluded_codes = {}
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
        if code in excluded_codes:
            dups.append({'team': n, 'code': code, 'first': 'excluded-team-' + str(excluded_codes[code])}); continue
        name = str(it.get('name', '')).strip()
        desc = str(it.get('description', '')).strip()
        if not name or not desc:
            schema_err.append({'team': n, 'reason': 'empty-name-desc', 'item': it}); continue
        reason = screen(name, desc, code)
        if reason:
            excluded.append({'team': n, 'code': code, 'name': name, 'reason': reason})
            excluded_codes[code] = n
            continue
        cc = str(it.get('country', '')).strip()  # '' stays '' (unknown)
        clean[code] = {'name': name, 'category': cat, 'country': cc, 'description': desc,
                       'invite': f'https://chat.whatsapp.com/{code}', '_team': n}

print('raw team items:', raw_total)
print('clean unique:', len(clean))
print('cross-team dups:', len(dups))
print('union leaks:', len(union_leaks))
print('schema errors:', len(schema_err))
print('screen-excluded:', len(excluded))
print('per-team kept:', dict(sorted(Counter(c['_team'] for c in clean.values()).items())))

json.dump(dups, open(os.path.join(WAVE_DIR, 'wave_20261111_cross_dups.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261111_excluded.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(schema_err, open(os.path.join(WAVE_DIR, 'wave_20261111_schema_err.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(union_leaks, open(os.path.join(WAVE_DIR, 'wave_20261111_union_leaks.json'), 'w'), indent=1)
out = [{k: v for k, v in c.items() if k != '_team'} for c in clean.values()]
json.dump(out, open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump({code: c['_team'] for code, c in clean.items()}, open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json'), 'w'), indent=1)
print('wrote wave_20261111_clean.json with', len(out), 'groups')

# --- aggregate pending + leads across all teams ---
PENDING_FILES = [
    (1, 'team01-leads-slice1-pending.json'), (2, 'team02-leads-slice2-pending.json'),
    (3, 'team03-leads-slice3-pending.json'), (4, 'team04-leads-slice4-pending.json'),
    (5, 'team05-leads-slice5-pending.json'), (6, 'team06-leads-slice6-pending.json'),
    (7, 'team07-leads-slice7-pending.json'), (8, 'team08-leads-slice8-pending.json'),
    (9, 'team09-pending-recheck-pending.json'), (10, 'team10-linkado-2300-pending.json'),
    (11, 'team11-linkado-2700-pending.json'), (12, 'team12-linkado-0-1499-pending.json'),
    (13, 'team13-groupjoin-pending.json'), (14, 'team14-77links-pending.json'),
    (15, 'team15-tugrupo-pending.json'), (16, 'team16-grupbul-pending.json'),
    (17, 'team17-groupssor-pending.json'), (18, 'team18-grouplinksforyou-pending.json'),
    (19, 'team19-groupsnest-pending.json'), (20, 'team20-wglfinder-pending.json'),
    (21, 'team21-freewagroup-pending.json'), (22, 'team22-walink-pending.json'),
    (23, 'team23-groupsinvite-pending.json'), (24, 'team24-whtspgrouplink-pending.json'),
    (25, 'team25-newdirs-southasia-pending.json'), (26, 'team26-newdirs-africa-mideast-pending.json'),
    (27, 'team27-newdirs-seasia-pending.json'), (28, 'team28-newdirs-latam-gulf-pending.json'),
    (29, 'team29-listicles-edu-jobs-pending.json'), (30, 'team30-listicles-mixed-pending.json'),
    (31, 'team31-tglinkhub-verify2-pending.json'), (32, 'team32-igrupos-geogated-pending.json'),
]
pending_all = []
seen_pend = set()
for n, f in PENDING_FILES:
    p = os.path.join(WAVE_DIR, f)
    if not os.path.exists(p):
        print('MISSING pending', f); continue
    for it in json.load(open(p)):
        code = str(it.get('invite', '')).rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
        if code and code in seen_pend: continue
        seen_pend.add(code)
        it2 = dict(it); it2['_team_file'] = f
        pending_all.append(it2)
json.dump(pending_all, open(os.path.join(WAVE_DIR, 'wave_20261111_pending_all.json'), 'w'), indent=1, ensure_ascii=False)
print('pending all:', len(pending_all))

LEADS_FILES = [
    (1, 'team01-leads-slice1-leads.json'), (2, 'team02-leads-slice2-leads.json'),
    (3, 'team03-leads-slice3-leads.json'), (4, 'team04-leads-slice4-leads.json'),
    (5, 'team05-leads-slice5-leads.json'), (6, 'team06-leads-slice6-leads.json'),
    (7, 'team07-leads-slice7-leads.json'), (8, 'team08-leads-slice8-leads.json'),
    (9, 'team09-pending-recheck-leads.json'), (10, 'team10-linkado-2300-leads.json'),
    (11, 'team11-linkado-2700-leads.json'), (12, 'team12-linkado-0-1499-leads.json'),
    (13, 'team13-groupjoin-leads.json'), (14, 'team14-77links-leads.json'),
    (15, 'team15-tugrupo-leads.json'), (16, 'team16-grupbul-leads.json'),
    (17, 'team17-groupssor-leads.json'), (18, 'team18-grouplinksforyou-leads.json'),
    (19, 'team19-groupsnest-leads.json'), (20, 'team20-wglfinder-leads.json'),
    (21, 'team21-freewagroup-leads.json'), (22, 'team22-walink-leads.json'),
    (23, 'team23-groupsinvite-leads.json'), (24, 'team24-whtspgrouplink-leads.json'),
    (25, 'team25-newdirs-southasia-leads.json'), (26, 'team26-newdirs-africa-mideast-leads.json'),
    (27, 'team27-newdirs-seasia-leads.json'), (28, 'team28-newdirs-latam-gulf-leads.json'),
    (29, 'team29-listicles-edu-jobs-leads.json'), (30, 'team30-listicles-mixed-leads.json'),
    (31, 'team31-tglinkhub-verify2-leads.json'), (32, 'team32-igrupos-geogated-leads.json'),
]
leads_all = []
seen_leads = set()
for n, f in LEADS_FILES:
    p = os.path.join(WAVE_DIR, f)
    if not os.path.exists(p):
        print('MISSING leads', f); continue
    for s in json.load(open(p)):
        if isinstance(s, dict):
            s = s.get('url') or s.get('invite') or ''
        s = str(s).strip()
        if not s or s in seen_leads: continue
        seen_leads.add(s); leads_all.append(s)
# team01 merged-candidates (dict keyed by code) + team02 awaiting-verification
# (list of dicts with invite) — unverified mined codes, banked as code-string leads
extra = 0
try:
    mc = json.load(open(os.path.join(WAVE_DIR, 'team01-merged-candidates.json')))
    for code in mc.keys():
        if code not in seen_leads:
            seen_leads.add(code); leads_all.append(code); extra += 1
except Exception as e:
    print('team01 merged-candidates skip:', e)
try:
    av = json.load(open(os.path.join(WAVE_DIR, 'team02-awaiting-verification.json')))
    for it in av:
        code = str(it.get('invite', '')).rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
        if code and code not in seen_leads:
            seen_leads.add(code); leads_all.append(code); extra += 1
except Exception as e:
    print('team02 awaiting-verification skip:', e)
print('extra code-string leads (team01 merged + team02 awaiting):', extra)
json.dump(leads_all, open(os.path.join(WAVE_DIR, 'wave_20261111_leads_all.json'), 'w'), indent=1, ensure_ascii=False)
print('leads all:', len(leads_all))
