#!/usr/bin/env python3
"""Wave 20261112 coordinator consolidation.
Reads the 36 per-team final verified files, cross-team dedupes (first-team-wins),
checks against the union (.existing_codes.json), screens porn/scam/phone,
aggregates pending + leads (incl. team01 merged/deep candidates as code-string
leads, minus clean/union/pending), writes wave_20261112_clean.json +
excluded/dups/leaks/schema/pending/leads files.
Adapted from coordinator_build_clean_20261111.py. Changes vs Nov 11:
- 36 teams, this wave's filenames (team01/05 use .json not -candidates.json).
- Screen: word-boundary for 'sex'/'chut' (sexta-feira, chutar false positives),
  leetspeak adult terms (pir4nhas, ninf4tas, saf4dinhas, vaz4dinhos, put4ria),
  PT/ES sexual terms (putero, putas, prostitut*, morbo), betting terms
  (aposta, palpite). Casino/slots (tigrinho etc.) KEPT per the task's written
  screen (sports-betting only) and flagged for the parent in the manifest.
- og:description is NEVER a live signal (generic on dead pages) — teams that
  used it as fallback corrected themselves; coordinator spot-verify is og:title-only.
- Descriptions not starting with 'Join ' are normalized to the template form
  (team05 banked listing-text descriptions; schema requires 'Join <name>, ...').
- pending_all / leads_all exclude codes already in clean or the union.
- team02 awaiting-verification.json is STALE (all resolved via verify-state),
  so it is NOT banked as leads; only codes unresolved anywhere are banked.
Country '' is kept as '' (NOT defaulted to IN).
"""
import json, re, unicodedata, os
from collections import Counter

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112'
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

PORN = ['porn','xxx','xnxx','xxnx','sexy','hookup','escort','cam girl','camgirl',
        'call girl','callgirl','bokep','nude','naked','desi sex','hot girl','sexy girl',
        'erotic','fuck','pussy','dick','boobs','s3x','\u1e9eex','sexo','sexchat','sexting',
        'masturbat','horny','naughty','fwb','friends with benefits','kambi','desi bhabhi',
        'aunty sex','girls sex','boys sex','video call girl','leak','leaked','mms',
        'viral mms','onlyfans','pornhub','xvideos','redtube','brazzers','hentai','nekopoi',
        'jav ','18+','\U0001f51e','\U0001f346','\U0001f348','putaria',
        'chuchi','lund','choot','gaand','bhosda',
        'pir4nhas','ninf4tas','ninfet4as','saf4dinhas','vaz4dinhos','put4ria',
        'putero','putas','prostitut','morbo','lesbianas hot','sex talk','cruising']
PORN_WORD = ['sex', 'chut']  # word-boundary only: 'sexta-feira' and 'chutar' are KEEP
SCAM = ['b-love','blove','forsage','sheyi','pearlvine','holiverse','meta-whale','metawhale',
        'unick forex','airdrop','free money','earn money without investment','usdt flash',
        'btc flash','binary option','carding','stolen cc','dark web','data hack',
        'hack software','free fire hack','paid hack','aposta','palpite',
        'venda de xit', 'crypto-hacker']

ADULT_SITE_CODES = {
    'C9BRC2yDkizLr4y9kMsCv7': 'groupjoin site-category Adult — blanket Adult exclusion per Nov-10 precedent',
    'HJS2ZkSzI99B7ldzHA7rhW': 'groupjoin site-category Adult — blanket Adult exclusion per Nov-10 precedent',
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
                                  'sem putaria','proibido pornografia','prohibido',
                                  'no xxx','no de sexo','sem pornografia','no pornografia',
                                  'no sexual','no contenido sexual']):
            continue
        out.append(sent)
    return ' '.join(out)

def screen(name, desc, code):
    if code in ADULT_SITE_CODES:
        return 'adult-site:' + ADULT_SITE_CODES[code]
    text = fold(name) + ' ' + fold(strip_prohibitions(desc))
    food_emojis = ['\U0001f345', '\U0001f347', '\U0001f349', '\U0001f350', '\U0001f355',
                   '\U0001f356', '\U0001f357', '\U0001f32e', '\U0001f32f', '\U0001f950',
                   '\U0001f951', '\U0001f95a', '\U0001f414']
    has_food = any(e in text for e in food_emojis)
    for p in PORN:
        if p in text:
            if p == '\U0001f346' and has_food and 'cook' in fold(name) + fold(desc):
                continue
            return 'porn:' + p
    for p in PORN_WORD:
        if re.search(r'\b' + p + r'\b', text):
            return 'porn-word:' + p
    for p in SCAM:
        if p in text: return 'scam:' + p
    if re.search(r'\d{7,}', fold(name) + ' ' + fold(desc)): return 'phone'
    return None

TEAM_FILES = [
    (1, 'team01-leads-slice1.json'),
    (2, 'team02-leads-slice2-candidates.json'),
    (3, 'team03-tglinkhub-candidates.json'),
    (4, 'team04-listicles-mixed-candidates.json'),
    (5, 'team05-leads-slice4.json'),
    (6, 'team06-leads-slice7-pending-candidates.json'),
    (7, 'team07-linkado-2700-candidates.json'),
    (8, 'team08-linkado-3100-candidates.json'),
    (9, 'team09-leads-slice3-candidates.json'),
    (10, 'team10-leads-slice5-candidates.json'),
    (11, 'team11-leads-slice6-candidates.json'),
    (12, 'team12-leads-slice8-candidates.json'),
    (13, 'team13-pending-recheck-candidates.json'),
    (14, 'team14-linktogroups-candidates.json'),
    (15, 'team15-groupslinks-candidates.json'),
    (16, 'team16-whtsclub-candidates.json'),
    (17, 'team17-tugrupo-online-candidates.json'),
    (18, 'team18-igrupos-candidates.json'),
    (19, 'team19-groupjoin-candidates.json'),
    (20, 'team20-77links-candidates.json'),
    (21, 'team21-grupbul-candidates.json'),
    (22, 'team22-groupssor-candidates.json'),
    (23, 'team23-groupsinvite-candidates.json'),
    (24, 'team24-whtspgrouplink-candidates.json'),
    (25, 'team25-wglfinder-candidates.json'),
    (26, 'team26-freewagroup-candidates.json'),
    (27, 'team27-groupsnest-candidates.json'),
    (28, 'team28-grouplinksforyou-candidates.json'),
    (29, 'team29-walink-candidates.json'),
    (30, 'team30-newdirs-southasia-candidates.json'),
    (31, 'team31-newdirs-africa-mideast-candidates.json'),
    (32, 'team32-newdirs-seasia-candidates.json'),
    (33, 'team33-newdirs-latam-gulf-candidates.json'),
    (34, 'team34-listicles-edu-jobs-candidates.json'),
    (35, 'team35-discovery-global-candidates.json'),
    (36, 'team36-discovery-categories-candidates.json'),
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
        if not desc.startswith('Join '):
            desc = f"Join {name}, a WhatsApp group listed under {cat}."
        cc = str(it.get('country', '')).strip()
        clean[code] = {'name': name, 'category': cat, 'country': cc, 'description': desc,
                       'invite': f'https://chat.whatsapp.com/{code}', '_team': n}

print('raw team items:', raw_total)
print('clean unique:', len(clean))
print('cross-team dups:', len(dups))
print('union leaks:', len(union_leaks))
print('schema errors:', len(schema_err))
print('screen-excluded:', len(excluded))
print('per-team kept:', dict(sorted(Counter(c['_team'] for c in clean.values()).items())))

json.dump(dups, open(os.path.join(WAVE_DIR, 'wave_20261112_cross_dups.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261112_excluded.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(schema_err, open(os.path.join(WAVE_DIR, 'wave_20261112_schema_err.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(union_leaks, open(os.path.join(WAVE_DIR, 'wave_20261112_union_leaks.json'), 'w'), indent=1)
out = [{k: v for k, v in c.items() if k != '_team'} for c in clean.values()]
json.dump(out, open(os.path.join(WAVE_DIR, 'wave_20261112_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump({code: c['_team'] for code, c in clean.items()}, open(os.path.join(WAVE_DIR, 'wave_20261112_clean_teams.json'), 'w'), indent=1)
print('wrote wave_20261112_clean.json with', len(out), 'groups')

# --- aggregate pending across all teams (dedupe by code; drop clean/union codes) ---
PENDING_FILES = []
for n, f in TEAM_FILES:
    if f.endswith('-candidates.json'):
        pf = f[:-len('-candidates.json')] + '-pending.json'
    elif f.endswith('.json'):
        pf = f[:-5] + '-pending.json'
    else:
        pf = f + '-pending'
    PENDING_FILES.append((n, pf))
pending_all = []
seen_pend = set()
for n, f in PENDING_FILES:
    p = os.path.join(WAVE_DIR, f)
    if not os.path.exists(p):
        print('MISSING pending', f); continue
    for it in json.load(open(p)):
        if isinstance(it, str):
            code = it.strip().split('/')[-1].split('?')[0].split('#')[0]
            item = {'code': code, 'invite': f'https://chat.whatsapp.com/{code}'}
        else:
            code = str(it.get('invite', '') or it.get('code', '')).rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
            item = dict(it)
        if not code or code in seen_pend or code in clean or code in union:
            continue
        seen_pend.add(code)
        item['_team_file'] = f
        pending_all.append(item)
json.dump(pending_all, open(os.path.join(WAVE_DIR, 'wave_20261112_pending_all.json'), 'w'), indent=1, ensure_ascii=False)
print('pending all:', len(pending_all))

# --- aggregate leads (dedupe strings; drop codes already clean/union/pending) ---
LEADS_FILES = []
for n, f in TEAM_FILES:
    if f.endswith('-candidates.json'):
        lf = f[:-len('-candidates.json')] + '-leads.json'
    elif f.endswith('.json'):
        lf = f[:-5] + '-leads.json'
    else:
        lf = f + '-leads'
    LEADS_FILES.append((n, lf))
leads_all = []
seen_leads = set()
def add_lead(s):
    s = str(s).strip()
    if not s or s in seen_leads: return
    # code-like string already resolved? drop if in clean/union/pending
    code = s.rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
    if code in clean or code in union or code in seen_pend: return
    seen_leads.add(s); leads_all.append(s)
for n, f in LEADS_FILES:
    p = os.path.join(WAVE_DIR, f)
    if not os.path.exists(p):
        print('MISSING leads', f); continue
    for s in json.load(open(p)):
        if isinstance(s, dict):
            s = s.get('url') or s.get('invite') or s.get('code') or ''
        add_lead(s)
# team01 merged-candidates (1123 unverified) + team01 deep-candidates (1738 unverified)
extra = 0
for fname in ['team01-merged-candidates.json', 'team01-deep-candidates.json']:
    try:
        mc = json.load(open(os.path.join(WAVE_DIR, fname)))
        for code in (mc.keys() if isinstance(mc, dict) else [str(x) for x in mc]):
            before = len(leads_all)
            add_lead(code)
            if len(leads_all) > before: extra += 1
    except Exception as e:
        print(fname, 'skip:', e)
# team03 tglinkhub leads file already aggregated above (3600 code strings).
print('extra code-string leads (team01 merged + deep):', extra)
json.dump(leads_all, open(os.path.join(WAVE_DIR, 'wave_20261112_leads_all.json'), 'w'), indent=1, ensure_ascii=False)
print('leads all:', len(leads_all))
