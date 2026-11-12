# TEAM 03 — wave 20261112, tglinkhub verify2 resume: banking script.
# Adapted from wave_20261111/bank_team31.py: same screens; fixes 'Buy Sell' ->
# 'Buy & Sell' (task category list) and description to 'Join <name>, ...' form.
# Banks live codes (Nov-10 results + this run's results) into the team31 output files.
# Screening: banked name AND og:title; negated-prohibition sentences stripped
# before the adult-emoji screen; dedupe vs .existing_codes.json.
import json, re, html as H, collections, sys
RAW='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
OUT='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
W11='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/'
BASE='/home/hatch/workspace/whatsapp-groups-site/'

recs=json.load(open(f'{RAW}tg_code_recs.json'))
src2=json.load(open(f'{RAW}tg_code2src.json'))
for _c,_v in src2.items():
    if _c not in recs and _v:
        _link,_title=_v[0]
        _slug=_link.rstrip('/').split('/')[-1]
        recs[_c]={'name':'','section':'','post_title':_title,'post_link':_link,'slug':_slug,'post_cats':[]}

res=[]
for path in (f'{RAW}verify2_results.jsonl', f'{W11}verify2_results_20261111.jsonl', f'{OUT}verify2_results_20261112.jsonl'):
    try:
        for line in open(path):
            res.append(json.loads(line))
    except FileNotFoundError:
        pass
# dedupe by code (later run wins)
bycode={}
for r in res: bycode[r['code']]=r
res=list(bycode.values())
live=[r for r in res if r['status']=='live']
dead=[r for r in res if r['status']=='dead']
pend=[r for r in res if r['status']=='pending']
print("checked:",len(res),"live:",len(live),"dead:",len(dead),"pending:",len(pend))

existing=set(json.load(open(f'{BASE}.existing_codes.json')))
print("existing codes:",len(existing))

# --- screens ---
# strip negated-prohibition sentences first (a group saying 'no porn' is not porn)
NEG=re.compile(r'[^.!?\n]*\b(no|not allowed|prohibited|strictly no|no\s+allowed)\b[^.!?\n]*(porn|xxx|sex|nude|adult|18\+|hot\s+video)[^.!?\n]*[.!?\n]?', re.I)
def strip_negations(t):
    return NEG.sub(' ', t or '')
ADULT=re.compile(r'🔞|🥵|🍆|👙|se+x|hookup|escort|porn|x{3,}|xnxx|xxnx|\bpussy\b|seksi|boobs|navel|panty|\bbra\b|shagger|leak|nude|\bcum\b|randi|muth|puku|dengutha|molai|iduppu|గుద్ధ|വെടി|nsfw|hotness|f[u_]+ck|naughty america|18\+\s*(hot|adult|sex|video|porn)|hot\s+(girls?|bhabhi|aunty|video|actress|bollywood)|chuchi|\blund\b|chut|\bchoot\b|\bgaand\b|bhosda',re.I)
SCAM=re.compile(r'b-?love|forsage|shey[iy]|holiverse|meta[\s\-]?whale|paypal loader|bitfinex|counterfeit|crypto.?doubling|carding|double (your|the) (money|investment|usdt|trx|btc)|airdrop|money\s*drop',re.I)
PHONE=re.compile(r'(\+?\d[\d\s\-]{8,}\d)')
BETTING=re.compile(r'match\s*fix|fix\s*report|\bfix\b.*\bipl\b|\bipl\b.*\bfix\b|real\s*bet|\bbetting\b|tipper|toss[^A-Za-z]{0,12}(report|killer|kings)|match\s*report|1xbet|opportunit\w*\s+paris',re.I)
RICHSCHEME=re.compile(r'ficar rico|way to get rich|make \d+k with|millionaire blueprint|\d+k-\d+k monthly',re.I)
HACKED=re.compile(r'\bhacked\b|virus in group|virus.*attacking',re.I)
GIRLSNUM=re.compile(r'(girls?|aunty|bhabhi|women|ladies)\s*(numbers?|number|num)',re.I)
JUNKNAME=re.compile(r'^(x{2,}(\s+left)?|xx|gg|\|?\s*)$',re.I)

def category_for(r, name=''):
    text=((r.get('post_title') or '')+' '+r.get('slug','')+' '+(' '.join(r.get('post_cats') or []))+' '+name).lower()
    if any(k in text for k in ['forex','trading','share market','stock market']): return 'Finance'
    if any(k in text for k in ['amazon','deals','shopping','offers','discount','flipkart']): return 'Buy & Sell'
    if 'attari' in text or 'الحمد' in text: return 'Islamic'
    if 'job' in text: return 'Jobs'
    if any(k in text for k in ['education','upsc','ssc','ibps','railway','nda','study','exam','college','school','gk','general knowledge','university','scholarship']): return 'Education'
    if any(k in text for k in ['islam','quran','muslim','allah','naat','madrasa']): return 'Islamic'
    if any(k in text for k in ['sport','ipl','cricket','football','kabaddi','hockey']): return 'Sports'
    if 'news' in text: return 'News'
    if any(k in text for k in ['business','digital marketing','marketing','entrepreneur']): return 'Business'
    if any(k in text for k in ['gaming','pubg','free fire','clash']): return 'Gaming'
    if any(k in text for k in ['movie','movies','status','song','music','actress','actor','entertainment','video']): return 'Entertainment'
    if any(k in text for k in ['health','fitness','doctor','medical']): return 'Health'
    if any(k in text for k in ['funny','joke','meme','comedy']): return 'Funny'
    if any(k in text for k in ['buy','sell','shopping','market']): return 'Buy & Sell'
    if any(k in text for k in ['finance','forex','crypto','trading','share market','stock']): return 'Finance'
    if any(k in text for k in ['tech','technology','computer','software']): return 'Technology'
    return 'Community & Social'

def country_for(r):
    text=((r.get('post_title') or '')+' '+r.get('slug','')).lower()
    m={'portugal':'PT','malaya':'MY','karnataka':'IN','tamil':'IN','telugu':'IN','kannada':'IN','kerala':'IN','malayalam':'IN','hindi':'IN','delhi':'IN','rajasthan':'IN','indian':'IN','india':'IN','bhojpuri':'IN','marathi':'IN','gujarati':'IN','punjabi':'IN','bengali':'IN','urdu':'PK','pakistani':'PK','pakistan':'PK','south-africa':'ZA','canada':'CA','uk-':'GB','usa':'US','america':'US','dubai':'AE','uae':'AE','ghana':'GH','tanzania':'TZ','indonesia':'ID','brazil':'BR','sri-lanka':'LK','bangladesh':'BD','nepal':'NP','nigeria':'NG','kenya':'KE','australia':'AU','germany':'DE','france':'FR','spain':'ES','italy':'IT','turkey':'TR','saudi':'SA','qatar':'QA','kuwait':'KW','oman':'OM','bahrain':'BH'}
    for k,v in m.items():
        if k in text: return v
    return ''

CATDESC={
 'Entertainment':'An entertainment group for sharing videos, movies, songs and fun updates with members.',
 'Jobs':'A jobs group sharing vacancies, walk-in alerts and career updates for members.',
 'Education':'An education group for study material, exam preparation and learning resources.',
 'Islamic':'An Islamic group for religious reminders, Quranic learning and faith discussions.',
 'Sports':'A sports group for match updates, scores and discussion among fans.',
 'Community & Social':'A community group for chatting, meeting new people and sharing everyday updates.',
 'Finance':'A finance group for market updates, trading discussion and money tips.',
 'Funny':'A fun group for jokes, memes and light-hearted entertainment.',
 'Buy & Sell':'A buy and sell group for deals, offers and marketplace listings.',
 'Health':'A health group for wellness tips, fitness and healthy living discussion.',
 'News':'A news group sharing daily headlines and current-affairs updates.',
 'Gaming':'A gaming group for players to chat, share tips and team up for games.',
 'Technology':'A technology group for tech news, tips and discussion.',
 'Business':'A business group for entrepreneurs, marketing ideas and networking.',
 'Crypto':'A crypto group for cryptocurrency news, discussion and market updates.',
 'Scholarship':'A scholarship group sharing funding opportunities and application guidance.',
 'Freelance':'A freelance group for gig work, clients and freelancing tips.',
 'Travel':'A travel group for trip ideas, destinations and travel discussion.',
 'Poetry':'A poetry group for sharing poems, verses and literary discussion.',
 'Cooking':'A cooking group for recipes, food tips and kitchen discussion.',
 'Online Earning':'An online earning group for legit ways to earn money online.',
 'Real Estate':'A real estate group for property listings, buying and selling.',
}

items=[]; exclusions=[]
for r in live:
    code=r['code']; og=(r.get('og_title') or '').strip()
    rec=recs.get(code,{})
    name=og or rec.get('name','')
    name=H.unescape(name)
    name=re.sub(r'\s+',' ',name).strip()
    if not name or name.lower() in ('whatsapp group invite','whatsapp group'):
        name=rec.get('name') or rec.get('post_title') or 'WhatsApp Group'
    _alnum0=re.sub(r'[^A-Za-z0-9]','',name)
    _is_junk=len(_alnum0)<2 or bool(JUNKNAME.match(name.strip()))
    if _is_junk:
        _pt0=re.sub(r'\s*WhatsApp Group Links?\s*','',rec.get('post_title','')).strip()
        name=(_pt0+' Group') if _pt0 else 'WhatsApp Group'
    _check='' if _is_junk else og
    _check_clean=strip_negations(_check)
    _name_clean=strip_negations(name)
    if ADULT.search(_check_clean) or ADULT.search(_name_clean):
        exclusions.append({'code':code,'reason':'adult-sexual signal in og:title/name: '+og}); continue
    if 'bold' in og.lower() and re.search(r'celebs?|actress|videos?|pics?',og,re.I):
        exclusions.append({'code':code,'reason':'unsure-adult: bold-celebrity title, dropped per rule: '+og}); continue
    _ol=og.lower()
    if 'actress' in _ol and 'hot' in _ol:
        exclusions.append({'code':code,'reason':'adult-sexual signal in og:title/name: '+og}); continue
    if '💦' in og and ('✊' in og or 'actress' in _ol):
        exclusions.append({'code':code,'reason':'adult-sexual signal in og:title/name: '+og}); continue
    if re.search(r'\bsax\b', _ol) and 'hot' in _ol:
        exclusions.append({'code':code,'reason':'adult-sexual signal in og:title/name: '+og}); continue
    if 'അടി' in og:
        exclusions.append({'code':code,'reason':'unsure-adult: ambiguous slang in og:title, dropped per rule: '+og}); continue
    if SCAM.search(_check) or SCAM.search(name):
        exclusions.append({'code':code,'reason':'scam signal in og:title/name: '+og}); continue
    if BETTING.search(_check):
        exclusions.append({'code':code,'reason':'betting/match-fixing tipster group: '+og}); continue
    if RICHSCHEME.search(_check):
        exclusions.append({'code':code,'reason':'get-rich-scheme title: '+og}); continue
    if HACKED.search(_check):
        exclusions.append({'code':code,'reason':'hacked/virus warning in title; unusable group: '+og}); continue
    if GIRLSNUM.search(_check):
        exclusions.append({'code':code,'reason':'shares girls phone numbers (personal info): '+og}); continue
    if PHONE.search(name):
        exclusions.append({'code':code,'reason':'name looks like a phone number/personal info: '+og}); continue
    if re.search(r'lesbian babies', og, re.I):
        exclusions.append({'code':code,'reason':'unsure-adult: ambiguous og:title, dropped per rule: '+og}); continue
    if re.search(r'hot\s+seat', og, re.I):
        exclusions.append({'code':code,'reason':'unsure-adult: suggestive og:title, dropped per rule: '+og}); continue
    if re.search(r'\*\d|\d+%\+\$', og):
        exclusions.append({'code':code,'reason':'unsure: og:title reads like betting/odds spam, dropped per rule: '+og}); continue
    if code in existing:
        exclusions.append({'code':code,'reason':'duplicate of existing groups.json code'}); continue
    cat=category_for(rec, name); ctry=country_for(rec)
    _base=CATDESC.get(cat,'A community group for chatting and sharing updates with members.')
    desc=f'Join {name}, '+_base[0].lower()+_base[1:]
    items.append({'name':name[:100],'category':cat,'country':ctry,'description':desc,'invite':f'https://chat.whatsapp.com/{code}'})

# dedupe banked items by code (keep first)
seen=set(); uniq=[]
for it in items:
    c=it['invite'].rsplit('/',1)[-1]
    if c in seen: continue
    seen.add(c); uniq.append(it)
items=uniq

pend_items=[]
for r in pend:
    rec=recs.get(r['code'],{})
    pend_items.append({'name':(rec.get('name') or ''),'category':'','country':'','description':'','invite':"https://chat.whatsapp.com/"+r['code'],'reason':r.get('reason','transport failure')})

# leads: codes still unverified (not in any results file) — as strings
fresh=json.load(open(f'{RAW}tg_fresh_codes.json'))
excl=json.load(open(f'{RAW}tg_name_exclusions.json'))
checked_codes=set(bycode.keys())
remaining=[c for c in fresh if c not in excl and c not in checked_codes]
leads=remaining  # list of codes still unverified

json.dump(items,open(f'{OUT}team03-tglinkhub-candidates.json','w'),ensure_ascii=False,indent=1)
json.dump(pend_items,open(f'{OUT}team03-tglinkhub-pending.json','w'),ensure_ascii=False,indent=1)
json.dump(leads,open(f'{OUT}team03-tglinkhub-leads.json','w'),ensure_ascii=False,indent=1)
summary={
 'team':'team03','slice':'tglinkhub verify2 resume',
 'sources':['tglinkhub.com via wave_20261110/team32_raw (tg_fresh_codes.json, tg_code_recs.json)'],
 'verified':len(items),'pending':len(pend_items),'leads':len(leads),
 'dead':len(dead),'exclusions':exclusions,
 'resume':'verify2_results_20261112.jsonl in wave_20261112 dir; re-run verify2_team03.py (it resumes from Nov10 + Nov11 + this run results) then re-run bank_team03.py',
 'notes':[
   f"checked total (Nov10 + this run): {len(res)}; live {len(live)}; dead {len(dead)}; pending {len(pend)}",
   f"banked verified: {len(items)}; excluded after screening: {len(exclusions)} (incl. existing-code dupes)",
   f"codes still unverified (leads): {len(leads)}",
   "country is '' when not determinable from post title/slug (no 'International' placeholder).",
   "Adult screen strips negated-prohibition sentences ('no porn' etc.) before matching.",
 ]}
json.dump(summary,open(f'{OUT}team03-tglinkhub-summary.json','w'),ensure_ascii=False,indent=1)
print("verified items:",len(items),"exclusions:",len(exclusions),"pending:",len(pend_items),"leads:",len(leads))
print("categories:",collections.Counter(i['category'] for i in items).most_common())
print("exclusion reasons:",collections.Counter(e['reason'].split(':')[0] for e in exclusions).most_common())
