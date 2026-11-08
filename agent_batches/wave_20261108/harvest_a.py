import requests, re, json, time, html
from concurrent.futures import ThreadPoolExecutor

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
slice_data=json.load(open(WAVE+'leads_slice_01.json'))
CODE_RE=re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})\b')
ADULT_EMOJI=set(['🥵','🍆','🍑','🔞','💦','👅','👄','💋'])
GENERIC_TITLES={'whatsapp group','join this group on whatsapp','whatsapp','join group on whatsapp'}
SCAM_PATTERNS=[r'paypal\s*loader',r'bitfinexinvest',r'counterfeit\s*(currency|money|note)',r'escort',r'call[- ]?girl',r'fake\s*(currency|note|money)',r'money\s*mule']
PORN_WORDS=[r'\bporn\b',r'\bxxx\b',r'\bsex\b',r'18\+',r'onlyfans',r'porno',r'cinsel',r'fetis',r'feti',r'swinger']

def fetch(url, timeout=30):
    try:
        r=requests.get(url,headers=UA,timeout=timeout)
        return r.status_code, r.text, r.url
    except Exception as e:
        return None, '', str(e)

def og_title(text):
    m=re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']',text,re.I)
    if not m:
        m=re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']',text,re.I)
    return html.unescape(m.group(1)).strip() if m else ''

def verify(code):
    """returns (status, title) status in live/dead/transport"""
    url='https://chat.whatsapp.com/'+code
    for attempt in range(2):
        try:
            r=requests.get(url,headers=UA,timeout=25)
            if r.status_code!=200:
                return ('dead','')
            t=og_title(r.text)
            if t and t.lower() not in GENERIC_TITLES:
                return ('live',t)
            if attempt==0:
                time.sleep(4)
                continue
            return ('dead',t)
        except Exception as e:
            if attempt==0:
                time.sleep(4); continue
            return ('transport','')
    return ('dead','')

# ---------- Step A: status pass over slice ----------
status_log=[]
wk_skip_tags=[]  # whatsappkanali skipped-by-rule / empty-archive: do not fetch
for i,e in enumerate(slice_data):
    u=e['url']; what=e.get('what','')
    if 'whatsappkanali.com/etiket/' in u or 'whatsappkanali.com/kategori/' in u:
        status_log.append((i,u,'SKIP-RULE (per slice note)',0)); continue
    if 'whatsappkanali.com/sehir/tekirdag/sohbet' in u:
        status_log.append((i,u,'DEEP-HARVEST (below)',0)); continue
    st,txt,fin=fetch(u,timeout=20)
    n=len(set(CODE_RE.findall(txt))) if txt else 0
    status_log.append((i,u,f'HTTP {st}',n))
    print(i,u,'->',st,'codes',n,flush=True)
    time.sleep(0.4)

json.dump(status_log,open(WAVE+'team01-status-pass.json','w'),ensure_ascii=False,indent=1)
print('STATUS PASS DONE',flush=True)

# ---------- Step B: whatsappkanali deep harvest ----------
wk_pages=[
 ("https://whatsappkanali.com/sehir/tekirdag/sohbet","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/canakkale/sohbet","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/edirne/sohbet","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/istanbul/sohbet","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/kirklareli/sohbet","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/tekirdag/alim-satim","TR","Buy & Sell"),
 ("https://whatsappkanali.com/sehir/tekirdag/arkadaslik","TR","Friendship"),
 ("https://whatsappkanali.com/sehir/tekirdag/burc","TR","Community & Social"),
 ("https://whatsappkanali.com/sehir/tekirdag/emlak","TR","Real Estate"),
 ("https://whatsappkanali.com/sehir/tekirdag/etkinlik","TR","Community & Social"),
 ("https://whatsappkanali.com/sehir/tekirdag/fal","TR","Community & Social"),
 ("https://whatsappkanali.com/sehir/tekirdag/is-ilanlari","TR","Jobs"),
 ("https://whatsappkanali.com/sehir/tekirdag/ogrenci","TR","Education"),
 ("https://whatsappkanali.com/sehir/tekirdag/oyun","TR","Gaming"),
 ("https://whatsappkanali.com/sehir/tekirdag/tanisma","TR","Friendship"),
]
# extract records: JSON blobs with title/description/inviteUrl
rec_re=re.compile(r'\\"title\\":\\"((?:[^"\\]|\\.)*)\\",\\"description\\":\\"((?:[^"\\]|\\.)*)\\",\\"categoryName\\":\\"((?:[^"\\]|\\.)*)\\".{0,600}?\\"inviteUrl\\":\\"https://chat\.whatsapp\.com/([A-Za-z0-9]{22})',re.S)
candidates={}  # code -> {name, desc, category, country, src}
new_leads=[]
for url,country,cat in wk_pages:
    st,txt,fin=fetch(url,timeout=30)
    print('WK',url,'->',st,'len',len(txt),flush=True)
    if st!=200: continue
    new_leads.append({"url":url,"source":"whatsappkanali city/subcat"})
    # also discover more /sehir/ links
    for s in sorted(set(re.findall(r'href="(/sehir/[^"]+)"',txt))):
        full='https://whatsappkanali.com'+s
        if full not in [p[0] for p in wk_pages] and '/kanallar' not in s and '/kripto' not in s and '/para-kazanma' not in s:
            new_leads.append({"url":full,"source":"whatsappkanali discovered city page"})
    found=0
    for m in rec_re.finditer(txt):
        title=html.unescape(m.group(1)).encode().decode('unicode_escape',errors='ignore') if '\\u' in m.group(1) else html.unescape(m.group(1))
        desc=html.unescape(m.group(2))
        code=m.group(4)
        title=title.strip(); desc=desc.strip()
        if code not in candidates:
            candidates[code]={'name':title,'desc':desc,'category':cat,'country':country,'src':url}
            found+=1
    # fallback: bare inviteUrl matches without title context
    for m in re.finditer(r'inviteUrl\\?":\\?"?https://chat\.whatsapp\.com/([A-Za-z0-9]{22})',txt):
        code=m.group(1)
        if code not in candidates:
            candidates[code]={'name':'','desc':'','category':cat,'country':country,'src':url}
    print('  records so far:',len(candidates),flush=True)
    time.sleep(0.5)

# whatshub 2 community codes: verify for report, exclude as communities
for c in ['LUMZAqG2aGV6Jhs3NUFt5q','JPBvIpyfjDnJAbqY6eYLWn']:
    candidates[c]={'name':'__WHATSAPPHUB_COMMUNITY__','desc':'','category':'Community & Social','country':'ES','src':'https://www.whatshub.es/'}

json.dump({k:v for k,v in candidates.items()},open(WAVE+'team01-candidates-raw.json','w'),ensure_ascii=False,indent=1)
fresh={c:v for c,v in candidates.items() if c not in union}
print('CANDIDATES',len(candidates),'FRESH',len(fresh),'IN-UNION',len(candidates)-len(fresh),flush=True)

# ---------- Step C: verify fresh codes (max 3 parallel, staggered) ----------
def check(item):
    code,rec=item
    time.sleep(0.6)
    st,title=verify(code)
    return code,rec,st,title

verified=[]; pending=[]; dead=[]
items=list(fresh.items())
with ThreadPoolExecutor(max_workers=3) as ex:
    for code,rec,st,title in ex.map(check,items):
        if st=='live':
            name=title.strip()
            # content filters
            blob=(name+' '+rec.get('desc','')+' '+rec.get('name','')).lower()
            if any(e in name or e in rec.get('desc','') for e in ADULT_EMOJI):
                dead.append((code,'adult-emoji',title)); continue
            if any(re.search(p,blob) for p in SCAM_PATTERNS):
                dead.append((code,'scam',title)); continue
            if rec.get('name')=='__WHATSAPPHUB_COMMUNITY__':
                dead.append((code,'community-not-group',title)); continue
            if rec.get('name')=='Endless Talks' and 'adult' in rec.get('src',''):
                pass
            # adult avatar flag from listing
            if rec.get('name')=='Endless Talks':
                dead.append((code,'adult-avatar+paid-desc',title)); continue
            if any(re.search(p,blob) for p in PORN_WORDS):
                dead.append((code,'porn-word',title)); continue
            desc=rec.get('desc','')
            if not desc or desc in ('$73',) or len(desc)<3:
                desc=f"Join {name}, a WhatsApp group listed under {rec['category']}."
            else:
                desc=desc.replace('\\n',' ').replace('\\r',' ').strip()
                if len(desc)>400: desc=desc[:400]
            verified.append({"name":name,"category":rec['category'],"country":rec['country'],
                             "description":desc,"invite":"https://chat.whatsapp.com/"+code,"image":""})
            print('LIVE',code,name,flush=True)
        elif st=='transport':
            pending.append({"name":rec.get('name') or code,"category":rec['category'],"country":rec['country'],
                            "description":rec.get('desc') or f"Join {rec.get('name') or code}, a WhatsApp group listed under {rec['category']}.",
                            "invite":"https://chat.whatsapp.com/"+code,"image":"","reason":"transport"})
            print('PENDING',code,flush=True)
        else:
            dead.append((code,'dead',title)); print('DEAD',code,title,flush=True)

def w(path,data):
    for attempt in range(5):
        try:
            with open(path,'w') as f: json.dump(data,f,ensure_ascii=False,indent=1)
            return True
        except Exception as e:
            print('WRITE FAIL',path,attempt,e,flush=True); time.sleep(2)
    return False

w(WAVE+'team01-leads-harvest-a.json',verified)
w(WAVE+'team01-leads-harvest-a-pending.json',pending)
# dedupe leads
seen=set(); leads=[]
for l in new_leads:
    if l['url'] not in seen:
        seen.add(l['url']); leads.append(l)
w(WAVE+'team01-leads-harvest-a-leads.json',leads)
json.dump({'verified':len(verified),'pending':len(pending),'dead':dead,'status_log':status_log,'leads':len(leads)},
          open(WAVE+'team01-summary.json','w'),ensure_ascii=False,indent=1)
print('DONE verified',len(verified),'pending',len(pending),'dead',len(dead),'leads',len(leads),flush=True)
