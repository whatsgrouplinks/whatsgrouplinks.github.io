import json, re

DROP_RE = re.compile(r'porn|xxx|sex(y|ual)?|hookup|escort|cam[- ]?girl|camgirl|nude|naked|adult\s*video|b[-\s]?love|forsage|suryodaya|shey?i\b|airdrop|free\s*money|double\s*your\s*money|onlyfans|desi\s*viral\s*video|ننگی|ہاٹ|सविता भाभी|കളിവീട്', re.I)
PROHIB_RE = re.compile(r'[^.!?\n]*(not allowed|prohibit|na\s*karein|don\'?t\s+share|do\s+not\s+share|no\s+porn|no\s+xxx|strictly\s+prohibited|not\s+share|allowed\s+nahi|mana\s+hai)[^.!?\n]*[.!?\n]?', re.I)
PHONE_RE = re.compile(r'\+?\d[\d\s\-()]{7,}\d')

def clean_screen_text(t):
    t = t or ''
    t = PROHIB_RE.sub(' ', t)
    return t

def screened_out(name, desc):
    t = clean_screen_text((name or '') + ' ' + (desc or ''))
    m = DROP_RE.search(t)
    return m.group(0) if m else None

CATMAP = {'entertainment':'Entertainment','dating':'Friendship','business':'Business',
 'gaming':'Gaming','crypto':'Finance','education':'Education','jobs':'Jobs','sports':'Sports',
 'shopping':'Buy Sell','health':'Health','news':'News','technology':'Technology',
 'music':'Entertainment','travel':'Community & Social','friends':'Friendship',
 'friendship, games, entertainment':'Friendship','friendship, fun, games':'Friendship',
 'religion':'Community & Social'}

def map_cat(c, name='', desc=''):
    c = (c or '').strip().lower()
    if c == 'religion':
        return 'Islamic' if re.search(r'islam|muslim|quran|qur\'?an|masjid|allah', (name+' '+desc), re.I) else 'Community & Social'
    return CATMAP.get(c, 'Community & Social')

pool = {}   # code -> record
dropped = []
def add(code, rec):
    if code not in pool: pool[code] = rec

# --- groupssor (rich metadata) ---
gs = json.load(open('team18_raw/groupssor_fresh.json'))
for g in gs:
    code = g['code']; name = (g.get('name') or '').strip(); desc = (g.get('description') or '').strip()
    reason = screened_out(name, desc)
    if reason:
        dropped.append({'code':code,'source':'groupssor','reason':'screen:'+reason,'name':name}); continue
    if len(re.sub(r'[^\w]', '', name or '', flags=re.UNICODE)) < 2:
        dropped.append({'code':code,'source':'groupssor','reason':'junk name','name':name}); continue
    desc1 = re.sub(r'\s+',' ', PHONE_RE.sub('', desc)).strip()
    # keep first 2 sentences max
    sents = re.split(r'(?<=[.!?])\s+', desc1)
    desc1 = ' '.join(sents[:2])[:300]
    if not desc1:
        desc1 = f"A WhatsApp community for {map_cat(g.get('category'),name,desc).lower()} discussions and updates."
    country = (g.get('country') or 'IN')[:2].upper() or 'IN'
    add(code, {'code':code,'name':name,'category':map_cat(g.get('category'),name,desc),
               'country':country,'description':desc1,'invite':f'https://chat.whatsapp.com/{code}',
               'src':'groupssor','src_category':g.get('category')})

# --- listing-extracted sources ---
SRC_META = [
 ('groupsnest_fresh.json','groupsnest','IN'),
 ('wglfinder_fresh.json','wglfinder','IN'),
 ('groupjoin_ng_fresh.json','groupjoin_ng','NG'),
 ('groupjoin_za_fresh.json','groupjoin_za','ZA'),
 ('groupjoin_dz_fresh.json','groupjoin_dz','DZ'),
 ('groupwa_zw_fresh.json','groupwa_zw','ZW'),
 ('groupwa_jeddah_fresh.json','groupwa_jeddah','SA'),
 ('groupjoin_za2_fresh.json','groupjoin_za2','ZA'),
 ('groupjoin_dz2_fresh.json','groupjoin_dz2','DZ'),
 ('dubai_fresh.json','dubai','AE'),
]
KW_CAT = [(r'job|vacanc|hiring|employment','Jobs'),(r'student|study|exam|school|universit|scholarship|notes','Education'),
 (r'cricket|football|soccer|sport|betting|bet ','Sports'),(r'islam|quran|muslim|allah|masjid','Islamic'),
 (r'pubg|free fire|gaming|game','Gaming'),(r'crypto|forex|bitcoin|trading|invest','Finance'),
 (r'business|entrepreneur|earn money|earning','Business'),(r'news|breaking','News'),
 (r'health|fitness|weight','Health'),(r'funny|meme|joke','Funny'),(r'movie|music|song|drama','Entertainment'),
 (r'buy|sell|shop|store|market','Buy Sell'),(r'tech|program|cyber|hack','Technology'),
 (r'friend|chat|social|dating|girl','Friendship')]
def infer_cat(ctx):
    for pat, cat in KW_CAT:
        if re.search(pat, ctx, re.I): return cat
    return 'Community & Social'
def infer_country(ctx, default):
    m = re.search(r'\b(nigeria|kenya|south africa|zimbabwe|algeria|egypt|saudi|jeddah|dubai|uae|morocco|ghana)\b', ctx, re.I)
    mp = {'nigeria':'NG','kenya':'KE','south africa':'ZA','zimbabwe':'ZW','algeria':'DZ','egypt':'EG','saudi':'SA','jeddah':'SA','dubai':'AE','uae':'AE','morocco':'MA','ghana':'GH'}
    return mp[m.group(1).lower()] if m else default

for fn, src, defct in SRC_META:
    try: items = json.load(open('team18_raw/'+fn))
    except FileNotFoundError: continue
    for it in items:
        code = it['code']; ctx = it.get('context','')
        reason = screened_out('', ctx)
        if reason:
            dropped.append({'code':code,'source':src,'reason':'screen:'+reason,'context':ctx[-120:]}); continue
        cat = infer_cat(ctx); country = infer_country(ctx, defct)
        # provisional name: last meaningful words of context
        words = re.sub(r'[^\w\s]',' ', ctx).split()
        prov = ' '.join(words[-6:]).strip() or 'WhatsApp Group'
        desc = f"A WhatsApp community for {cat.lower()} discussions and updates" + (f" in {country}." if country!='IN' else ".") + " Members share updates, discussions and helpful posts."
        add(code, {'code':code,'name':prov,'category':cat,'country':country,'description':desc,
                   'invite':f'https://chat.whatsapp.com/{code}','src':src,'provisional_name':True,'context':ctx})

print('POOL:', len(pool))
print('DROPPED:', len(dropped))
from collections import Counter
print('pool by src:', Counter(v['src'] for v in pool.values()))
print('pool by cat:', Counter(v['category'] for v in pool.values()))
print('pool by country:', Counter(v['country'] for v in pool.values()).most_common(12))
json.dump(list(pool.values()), open('team18_raw/team18_pool.json','w'), indent=1)
json.dump(dropped, open('team18_raw/team18_screened_out.json','w'), indent=1)
for d in dropped[:25]: print('DROP', d.get('reason'), '|', (d.get('name') or d.get('context',''))[:70])
