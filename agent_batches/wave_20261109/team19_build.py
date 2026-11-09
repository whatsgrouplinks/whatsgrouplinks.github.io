import json, re, html, os
from collections import Counter

CATS=["Gaming","Education","Online Earning","Community & Social","Business","Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports","Health","News"]
CATMAP={'entertainment':'Entertainment','dating':'Friendship','news':'News','business':'Business',
 'gaming':'Gaming','crypto':'Finance','education':'Education','shopping':'Buy Sell','sports':'Sports',
 'jobs':'Jobs','health':'Health','religion':'Islamic','technology':'Technology','travel':'Community & Social',
 'music':'Entertainment','friends':'Friendship','friendship':'Friendship','online earning':'Online Earning',
 'islamic':'Islamic','funny':'Funny','community & social':'Community & Social','buy sell':'Buy Sell','finance':'Finance'}
COUNTRY_WORDS={'indonesia':'ID','indonesian':'ID','malaysia':'MY','malay':'MY','philippines':'PH','filipino':'PH',
 'thailand':'TH','thai':'TH','vietnam':'VN','pakistan':'PK','pakistani':'PK','india':'IN','indian':'IN','usa':'US',
 'america':'US','american':'US','uk':'GB','britain':'GB','england':'GB','london':'GB','canada':'CA','australia':'AU',
 'bangladesh':'BD','sri lanka':'LK','nepal':'NP','nigeria':'NG','kenya':'KE','ghana':'GH','egypt':'EG','cairo':'EG',
 'saudi':'SA','uae':'AE','dubai':'AE','turkey':'TR','turkish':'TR','brazil':'BR','brasil':'BR','mexico':'MX',
 'spain':'ES','spanish':'ES','france':'FR','germany':'DE','german':'DE','italy':'IT','panama':'PA','paraguay':'PY',
 'bolivia':'BO','cochabamba':'BO','ecuador':'EC','venezuela':'VE','peru':'PE','peruvian':'PE','chile':'CL',
 'costa rica':'CR','uruguay':'UY','honduras':'HN','guatemala':'GT','nicaragua':'NI','dominican':'DO','colombia':'CO',
 'argentina':'AR','portugal':'PT','netherlands':'NL','russia':'RU','ukraine':'UA','poland':'PL','morocco':'MA',
 'algeria':'DZ','tunisia':'TN','iraq':'IQ','iran':'IR','afghanistan':'AF','myanmar':'MM','cambodia':'KH',
 'laos':'LA','singapore':'SG','japan':'JP','korea':'KR','china':'CN','chinese':'CN','taiwan':'TW','hong kong':'HK',
 'bangkok':'TH','jakarta':'ID','kuala lumpur':'MY','manila':'PH','chiang mai':'TH','phuket':'TH','koh phangan':'TH',
 'pattaya':'TH','kathmandu':'NP','colombo':'LK','dhaka':'BD','karachi':'PK','lahore':'PK','mumbai':'IN','delhi':'IN'}
DROP_RE=re.compile(r'\b(xxx|porn|porno|sex|sexy|escort|cam[- ]?girl|hookup|hook[- ]?up|nude|naked|erotic|onlyfans|call[- ]?girl|b-?love|forsage|sheyi|airdrop|free\s*money|desi\s*sex|hot\s*video|leak(ed)?\s*(video|mms)|mms\s*leak|randi)\b', re.I)
PHONE_RE=re.compile(r'(\+\d[\d\s\-]{7,}\d|\b\d{10,}\b)')
import unicodedata
def norm_text(s):
    s=html.unescape(s or '')
    s=unicodedata.normalize('NFKD', s)
    s=s.replace('\u1e9e','S').replace('\u00df','s')
    s=''.join(c for c in s if not unicodedata.combining(c))
    t=''
    for ch in s:
        o=ord(ch)
        if 0xFF01<=o<=0xFF5E: t+=chr(o-0xFEE0)
        else: t+=ch
    return t
DROP_RE2=re.compile(r'(madarchod|bhosd|chut|chodi|randi|leaks?\s*(hub|video|mms)|leaked|\u092e\u093e\u0926\u0930\u091a\u094b\u0926|\u091a\u094b\u0926\u0940|\u092d\u094b\u0938\u0921)', re.I)

def clean_name(s):
    s=html.unescape(s or '')
    s=re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]+',' ',s)  # strip emoji
    s=re.sub(r'\s+',' ',s).strip(' -–—|•·\"\'')
    return s.strip()

def guess_country(text, fallback):
    t=' '+text.lower()+' '
    for w,cc in sorted(COUNTRY_WORDS.items(), key=lambda kv:-len(kv[0])):
        if w in t: return cc
    return fallback

def guess_category(text, fallback='Community & Social'):
    t=text.lower()
    if re.search(r'\b(id sell|id sale|account sale|seller|shop|store|market|sale|sell)\b', t): return 'Buy Sell'
    if 'free fire' in t or 'pubg' in t or 'gaming' in t or 'game' in t or 'clan' in t or 'esports' in t or 'juegos' in t or 'gta' in t or 'minecraft' in t or 'efootball' in t or 'duel links' in t: return 'Gaming'
    if 'amistad' in t or 'amigos' in t or 'conocer gente' in t or 'socializar' in t or 'amor' in t or 'pareja' in t or 'chicas' in t: return 'Friendship'
    if 'ventas' in t or 'venta' in t or 'compra' in t or 'mercado' in t or 'e-commerce' in t or 'dropshipping' in t or 'bazar' in t or 'tiendita' in t: return 'Buy Sell'
    if 'empleo' in t or 'trabajo' in t or 'trabajos' in t or 'bolsa de trabajo' in t or 'reclutamiento' in t: return 'Jobs'
    if 'musica' in t or 'música' in t or 'peliculas' in t or 'películas' in t or 'cine' in t or 'anime' in t or 'stickers' in t or 'series' in t: return 'Entertainment'
    if 'memes' in t or 'humor' in t or 'locura' in t: return 'Funny'
    if 'futbol' in t or 'fútbol' in t: return 'Sports'
    if 'cursos' in t or 'curso' in t or 'ingles' in t or 'programacion' in t: return 'Education'
    if 'negocios' in t or 'emprendedores' in t: return 'Business'
    if 'id sell' in t or 'buy' in t or 'sell' in t or 'shop' in t or 'store' in t or 'market' in t: return 'Buy Sell'
    if 'job' in t or 'hiring' in t or 'vacancy' in t or 'work' in t: return 'Jobs'
    if 'study' in t or 'exam' in t or 'education' in t or 'learn' in t or 'course' in t or 'school' in t or 'college' in t: return 'Education'
    if 'cricket' in t or 'football' in t or 'soccer' in t or 'sport' in t or 'ipl' in t: return 'Sports'
    if 'islam' in t or 'quran' in t or 'muslim' in t or 'allah' in t or 'namaz' in t or 'ramadan' in t: return 'Islamic'
    if 'funny' in t or 'meme' in t or 'joke' in t or 'comedy' in t or 'humor' in t: return 'Funny'
    if 'news' in t or 'breaking' in t or 'newspaper' in t: return 'News'
    if 'health' in t or 'fitness' in t or 'doctor' in t or 'wellbeing' in t or 'mental' in t: return 'Health'
    if 'business' in t or 'entrepreneur' in t or 'startup' in t: return 'Business'
    if 'crypto' in t or 'bitcoin' in t or 'trading' in t or 'forex' in t or 'invest' in t: return 'Finance'
    if 'tech' in t or 'programming' in t or 'coding' in t or 'developer' in t: return 'Technology'
    if 'movie' in t or 'film' in t or 'music' in t or 'song' in t or 'drama' in t or 'entertainment' in t or 'anime' in t or 'sticker' in t: return 'Entertainment'
    if 'girl' in t or 'friend' in t or 'friendship' in t or 'dating' in t or 'single' in t or 'chat' in t: return 'Friendship'
    if 'earn' in t or 'earning' in t or 'money' in t: return 'Online Earning'
    return fallback

def main():
    verify={}
    for fn in ('team19_verify.jsonl','team19_verify2.jsonl'):
        if not os.path.exists(fn): continue
        for line in open(fn):
            r=json.loads(line); verify[r['code']]=r
    allrec={r['code']:r for r in json.load(open('team19_raw_all.json'))}
    # batch2 raw (all already in existing, but keep for completeness)
    if os.path.exists('team19_raw_batch2.json'):
        for r in json.load(open('team19_raw_batch2.json')): allrec.setdefault(r['code'],r)
    freewa={}
    if os.path.exists('team19_fresh_freewa.json'):
        for r in json.load(open('team19_fresh_freewa.json')): allrec.setdefault(r['code'],r)
    gsmap={}
    if os.path.exists('team19_gs_country.json'):
        gsmap=json.load(open('team19_gs_country.json'))
    live=[]; dead=[]; pending=[]; dropped=[]
    for code,v in verify.items():
        rec=allrec.get(code,{'code':code,'name':'','heading':'','source':'?','desc':''})
        if v['http']==0:
            pending.append({**rec,'verify':v}); continue
        if v['http']==200 and v.get('og_title'):
            name=clean_name(v['og_title'])
            if not name or name.lower() in ('whatsapp group invite','whatsapp group','join group') or len(name)<2:
                dead.append({**rec,'verify':v,'reason':'generic/empty og:title after clean'}); continue
            if PHONE_RE.search(name):
                dropped.append({**rec,'verify':v,'reason':'phone number in og:title'}); continue
            if DROP_RE.search(norm_text(name)) or DROP_RE.search(rec.get('desc','')) or DROP_RE2.search(norm_text(name)) or DROP_RE2.search(norm_text(rec.get('desc',''))):
                dropped.append({**rec,'verify':v,'reason':'screen keyword in og:title/desc'}); continue
            live.append((code,rec,v,name))
        else:
            dead.append({**rec,'verify':v,'reason':f"http {v['http']} empty og:title after {v.get('attempts')} attempts"})
    print("live:",len(live),"dead:",len(dead),"pending(transport):",len(pending),"dropped(screen):",len(dropped))
    print("live by source:", Counter(r['source'] for _,r,_,_ in live))
    cands=[]
    for code,rec,v,name in live:
        gs_cat=CATMAP.get((rec.get('heading') or '').strip().lower(), None) if rec.get('source')=='groupssor-api' else None
        cat=gs_cat or guess_category(name + ' ' + (rec.get('desc','') or ''))
        if cat=='Community & Social' and rec.get('source')=='glfy_ff':
            cat='Gaming'
        if cat=='Community & Social':
            cat=guess_category(f"{name} {rec.get('heading','')} {rec.get('name','')}")
        ctx=f"{name} {rec.get('heading','')} {rec.get('name','')} {rec.get('desc','')}" 
        if code in gsmap and gsmap[code].get('country'):
            country=gsmap[code]['country']
        else:
            country=guess_country(ctx, 'IN')
        desc=clean_name(rec.get('desc',''))
        # strip prohibition sentences from desc before use
        desc=re.sub(r'[^.!?\n]*(inappropriate|porn|xxx|sex|adult|abuse|spam)[^.!?\n]*(na karein|not allowed|prohibited|mana hai|not allow|strictly prohibited|is not allowed)[^.!?\n]*[.!?\n]?',' ',desc,flags=re.I)
        desc=re.sub(r'\s+',' ',desc).strip()
        if not desc or len(desc)<10:
            desc=f"A {cat} WhatsApp group where members chat, share updates and connect with each other."
        else:
            # first 1-2 sentences
            sents=re.split(r'(?<=[.!?])\s+', desc)
            desc=' '.join(sents[:2])[:220]
            if DROP_RE.search(desc) or PHONE_RE.search(desc):
                desc=f"A {cat} WhatsApp group where members chat, share updates and connect with each other."
        if cat not in CATS: cat='Community & Social'
        cands.append({"name":name[:100],"category":cat,"country":country,"description":desc,"invite":f"https://chat.whatsapp.com/{code}"})
    # dedupe by code (should already be unique)
    seen=set(); out=[]
    for c in cands:
        code=c['invite'].split('/')[-1]
        if code in seen: continue
        seen.add(code); out.append(c)
    print("candidates:",len(out))
    print("by category:", Counter(c['category'] for c in out))
    print("by country:", Counter(c['country'] for c in out).most_common(10))
    json.dump(out, open('team19-candidates.json','w'), ensure_ascii=False, indent=1)
    json.dump(pending, open('team19-pending.json','w'), ensure_ascii=False, indent=1)
    json.dump(dead, open('team19_dead.json','w'), ensure_ascii=False, indent=1)
    json.dump(dropped, open('team19_dropped_postverify.json','w'), ensure_ascii=False, indent=1)
    return out
if __name__=='__main__':
    main()
