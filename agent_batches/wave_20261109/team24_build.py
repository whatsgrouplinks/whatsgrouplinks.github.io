#!/usr/bin/env python3
"""Team24 build: screen verified-live codes, format candidates/pending/leads/summary."""
import json, re, html, unicodedata

def _norm(s):
    # NFKD folds mathematical-bold/fancy unicode letters to plain ASCII
    return unicodedata.normalize('NFKD', s or '')

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
ALLOWED_CATS = ['Gaming','Education','Online Earning','Community & Social','Business',
                'Friendship','Finance','Buy Sell','Islamic','Entertainment','Jobs',
                'Technology','Funny','Sports','Health','News']

ADULT_EMOJI = set('\U0001f975\U0001f346\U0001f351\U0001f51e\U0001f4a6\U0001f445\U0001f444\U0001f48b')
BAD = ['porn','xxx','xvideos','xxnxx','nude','escort','call girl','callgirl','cam girl',
       'camgirl','phone sex','live sex','video call sex','sex','hookup','sexy','hot girl',
       'hot video','bhabhi sex','leak video','leaked video','mms video','nangi','nanga',
       'fuck','b-love','b love','blove','forsage','sheyi','free money','airdrop',
       '18+ video','adult video','desi sex','nekopoi','hentai','social logs','\u0633\u0643\u0633','\u0646\u0648\u062f\u0632',
       '\u062c\u0646\u0633','\u0628\u0628\u0628','\u0928\u0902\u0917\u0940','\u0928\u0917\u094d\u0928',
       '\u0938\u0947\u0915\u094d\u0938','\u092a\u094b\u0930\u094d\u0928']
PROHIBIT = ['na karein','na karen','not allowed','prohibited','mana hai','mana h',
            "don't share",'do not share','no porn','no sex','no adult','galat content',
            'inappropriate content','gandi video','gandi pic','abuse na karein',
            'no abuse','link share na','no link share']
PHONE_RE = re.compile(r'\b\d{10,}\b')

def strip_prohibitions(text):
    parts = re.split(r'(?<=[.!?])\s+', text or '')
    keep = [p for p in parts if not any(ph in p.lower() for ph in PROHIBIT)]
    return ' '.join(keep)

def screen(text):
    s = _norm(strip_prohibitions(text or ''))
    low = s.lower().replace('\u00df', 'ss')
    if any(e in s for e in ADULT_EMOJI):
        return 'adult-emoji'
    for b in BAD:
        if b in low:
            return 'bad:' + b
    if PHONE_RE.search(s):
        return 'phone-number'
    return None

def clean_name(name):
    n = html.unescape(name or '').strip()
    n = re.sub(r'\s+', ' ', n)
    for suf in [' WhatsApp Group | Groupizo', ' WhatsApp Group de Entertainment',
                ' WhatsApp Group', ' | Groupizo', ' - \u0648\u0627\u0679\u0633 \u0627\u06cc\u067e \u06af\u0631\u0648\u067e',
                ' - \u0642\u0631\u0648\u0628 \u0648\u0627\u062a\u0633\u0627\u0628',
                ' - \u0935\u094d\u0939\u093e\u091f\u094d\u0938\u090f\u092a \u0917\u094d\u0930\u0941\u092a \u0932\u093f\u0902\u0915',
                ' - \u0648\u0627\u062a\u0633\u0627\u0628 \u06af\u0631\u0648\u0628']:
        if n.endswith(suf):
            n = n[:-len(suf)].strip()
    n = re.sub(r'\s+WhatsApp Group.*$', '', n).strip()
    return n

def clean_desc(desc, name, cat):
    d = html.unescape(desc or '').strip()
    d = re.sub(r'\s+', ' ', d)
    d = re.sub(r'\s*on Groupizo\.?\s*$', '', d)
    d = re.sub(r'listed under \S+ on Groupizo', f'listed under {cat}', d)
    d = re.sub(r'\bGroupizo\b', '', d)
    d = re.sub(r'\s+on\s+\.\s*', ' ', d)
    d = re.sub(r'\s+', ' ', d).strip(' .')
    d = strip_prohibitions(d)
    trunc = bool(re.search(r'(and\.?|&|«|\*\|)\s*$', d)) or '*|' in d or 'Topics include' in d and d.rstrip('.').endswith('and')
    if len(d) < 15 or screen(d) or trunc:
        d = (f'{name}, a WhatsApp group for {cat.lower()} fans to chat, share updates and connect with the community.'
             if name.lower().startswith('join ')
             else f'Join {name}, a WhatsApp group for {cat.lower()} fans to chat, share updates and connect with the community.')
    # keep max 2 sentences / 300 chars
    sents = re.split(r'(?<=[.!?])\s+', d)
    d = ' '.join(sents[:2])[:300].strip()
    d = re.sub(r'\.{2,}$', '.', d)
    d = re.sub(r'।\.$', '।', d)
    if not d.endswith(('.', '!', '?', '।')):
        d += '.'
    return d

GZ_CAT = [
    (['islamic','quran','hamd','naat','ramadan','bhakti','bible','religious','religion'], 'Islamic'),
    (['forex','bet','odds','aviator','signal','deriv','victory code','slot'], 'Finance'),
    (['job','jobs','qatar job'], 'Jobs'),
    (['funny'], 'Funny'),
    (['song','music','anime','movie','video','entertainment'], 'Entertainment'),
    (['jb ','gb ','store','shop','stok','jual','beli','sell','buy','market','ress','saller'], 'Buy Sell'),
    (['game','gaming','free fire','minecraft','roblox','pubg','ff ','ft cs','valorant'], 'Gaming'),
    (['study','knowledge','education','school','learn'], 'Education'),
    (['friend','chat','ngopi','global friends','meet'], 'Friendship'),
    (['business'], 'Business'),
    (['earn','earning','money','store'], 'Online Earning'),
    (['health','smoker'], 'Health'),
]
def _kw(s, kw):
    return re.search(r'(?<![a-z0-9])' + re.escape(kw.strip()) + r'(?![a-z0-9])', s)

def gz_category(url, title, desc):
    s = (url + ' ' + title + ' ' + desc).lower()
    for kws, cat in GZ_CAT:
        if any(_kw(s, k) for k in kws):
            return cat
    return 'Community & Social'

GZ_COUNTRY = [
    (['srilanka','\U0001f1f1\U0001f1f0','sinhala','mage yaluwek','\u0dbd\u0dbd'], 'LK'),
    (['uganda','\U0001f1fa\U0001f1ec'], 'UG'),
    (['qatar'], 'QA'),
    (['india','tamil','punjabi','kerala','jaffna','bhabhi'], 'IN'),
    (['pakistan','urdu','\u067e\u0627\u06a9\u0633\u062a\u0627\u0646'], 'PK'),
    (['indonesia','ngopi','mabar','jual','beli'], 'ID'),
    (['malaysia'], 'MY'),
    (['bangladesh','bangla'], 'BD'),
]
def gz_country(url, title, desc):
    s = (url + ' ' + title + ' ' + desc).lower()
    for kws, cc in GZ_COUNTRY:
        if any(k in s for k in kws):
            return cc
    return 'IN'

IG_CAT = {'amistad': 'Friendship', 'amor': 'Friendship', 'gamers': 'Gaming',
          'free fire': 'Gaming', 'lesbianas': 'Community & Social',
          'musica': 'Entertainment', 'futbol': 'Sports', 'humor': 'Funny',
          'anime': 'Entertainment', 'negocios': 'Business', 'educacion': 'Education'}
FLAG_CC = {'ES':'ES','MX':'MX','AR':'AR','CO':'CO','CL':'CL','PE':'PE','VE':'VE',
           'BR':'BR','US':'US','EC':'EC','BO':'BO','PY':'PY','UY':'UY','GT':'GT',
           'CU':'CU','DO':'DO','CR':'CR','PA':'PA','SV':'SV','AD':'AD'}

results = json.load(open(WAVE+'team24_verify_raw.json'))
verified, pending, dropped = [], [], []
for r in results:
    code, src, meta, title = r['code'], r['source'], r['meta'], r['title']
    if r['status'] == 'transport':
        # build a pending entry from listing metadata
        if src == 'groupizo':
            nm = clean_name(meta.get('title') or meta.get('h1') or '')
            ds = meta.get('desc') or ''
            cat = gz_category(meta.get('url',''), nm, ds)
            cc = gz_country(meta.get('url',''), nm, ds)
        else:
            nm = clean_name(meta.get('title') or '')
            ds = meta.get('detail_desc') or meta.get('desc') or ''
            cat = IG_CAT.get((meta.get('category_raw') or '').lower().strip(), 'Community & Social')
            cc = FLAG_CC.get(meta.get('flag',''), 'IN')
        if not nm:
            nm = 'WhatsApp Group'
        pending.append({'name': nm, 'category': cat, 'country': cc,
                        'description': clean_desc(ds, nm, cat),
                        'invite': 'https://chat.whatsapp.com/'+code, 'reason': 'transport'})
        continue
    if r['status'] != 'live':
        continue
    og = clean_name(title)
    if src == 'groupizo':
        listing_name = clean_name(meta.get('title') or meta.get('h1') or '')
        name = og or listing_name
        ds = meta.get('desc') or ''
        cat = gz_category(meta.get('url',''), name + ' ' + listing_name, ds)
        cc = gz_country(meta.get('url',''), name + ' ' + listing_name, ds)
        screen_text = name + ' ' + og + ' ' + ds
    else:
        listing_name = clean_name(meta.get('title') or '')
        name = og or listing_name
        ds = meta.get('detail_desc') or meta.get('desc') or ''
        cat = IG_CAT.get((meta.get('category_raw') or '').lower().strip(), 'Community & Social')
        cc = FLAG_CC.get(meta.get('flag',''), 'IN')
        screen_text = name + ' ' + og + ' ' + ds
    if not name or name in ('.', ''):
        dropped.append({'code': code, 'source': src, 'reason': 'empty-name', 'title': title})
        continue
    bad = screen(screen_text)
    if bad:
        dropped.append({'code': code, 'source': src, 'reason': bad, 'name': name, 'title': title})
        continue
    if PHONE_RE.search(name):
        dropped.append({'code': code, 'source': src, 'reason': 'phone-in-name', 'name': name})
        continue
    verified.append({'name': name, 'category': cat, 'country': cc,
                     'description': clean_desc(ds, name, cat),
                     'invite': 'https://chat.whatsapp.com/'+code})

# leads: igrupos new gids whose detail page exposed no invite (JS-gated / no code)
det = json.load(open(WAVE+'team24_raw/igrupos_details.json'))
new = json.load(open(WAVE+'team24_raw/igrupos_new.json'))
leads = []
for gid in new['new_gids']:
    v = det.get(gid)
    if not v or not v.get('codes'):
        leads.append({'url': f'https://www.igrupos.com/grupo/{gid}',
                      'source': 'igrupos', 'note': 'NEEDS-BROWSER-LEG',
                      'title': new['cards'].get(gid, {}).get('title','')})
leads.append({'url': 'https://groupizo.com/sitemaps/sitemap-groups-12.xml',
              'source': 'groupizo', 'note': 'sitemap-groups-12 re-check next wave'})
leads.append({'url': 'https://ongrupos.com/', 'source': 'ongrupos',
              'note': 'home + 41 category p1 re-check next wave; all Nov 8-9 slugs already in existing codes'})

json.dump(verified, open(WAVE+'team24-candidates.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open(WAVE+'team24-pending.json','w'), ensure_ascii=False, indent=1)
json.dump(leads, open(WAVE+'team24-leads.json','w'), ensure_ascii=False, indent=1)
json.dump({'dropped': dropped, 'live_by_source':
           {'groupizo': sum(1 for r in results if r['status']=='live' and r['source']=='groupizo'),
            'igrupos': sum(1 for r in results if r['status']=='live' and r['source']=='igrupos')}},
          open(WAVE+'team24_dropped.json','w'), ensure_ascii=False, indent=1)
print(f"verified={len(verified)} pending={len(pending)} dropped={len(dropped)} leads={len(leads)}")
for d in dropped:
    print('DROP', d)
for v in verified:
    print('KEEP', v['name'][:50], '|', v['category'], '|', v['country'], '|', v['invite'])
