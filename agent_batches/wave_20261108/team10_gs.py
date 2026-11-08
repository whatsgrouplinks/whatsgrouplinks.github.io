import json, re, time, html, requests
from concurrent.futures import ThreadPoolExecutor

WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
fresh=json.load(open('/tmp/gs_fresh.json'))  # [{'code','rec'}] - code regex may be >22 chars; fix below

ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD_SUBS=['sex','porn','xxx','nude','escort','call girl','callgirl','video call','phone sex','live sex',
 'baise','fuck','bhabhi sex','leak video','leaked video','cp video','child','bacchi','xxnxx','xvideos',
 'sexy','hot girl','hot video','nangi','nanga','mms video','viral videoo','all type video',
 'satta','khaiwal','1xbet','1x bet','binance millionaire','bitfinex','prono','prixal','winning zone',
 'roland tips','king of virtual','free money','payal','paytm sex']
PHONE_RE=re.compile(r'\b\d{10,}\b')

def bad_text(t):
    s=(t or '').lower()
    if any(e in s for e in ADULT_EMOJI): return 'adult-emoji'
    for b in BAD_SUBS:
        if b in s: return 'bad:'+b
    if PHONE_RE.search(s): return 'phone-number'
    return None

def fix_code(link):
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})(?![A-Za-z0-9])', link or '')
    return m.group(1) if m else None

CATMAP={'entertainment':'Entertainment','dating':'Friendship','business':'Business','gaming':'Gaming',
 'crypto':'Crypto','education':'Education','jobs':'Jobs','shopping':'Buy & Sell','sports':'Sports',
 'news':'News','religion':'Islamic','technology':'Technology','music':'Entertainment','health':'Health',
 'travel':'Travel','friendship':'Friendship','friends':'Friendship'}

cands=[]
seen=set()
for item in fresh:
    rec=item['rec']
    c=fix_code(rec.get('inviteLink') or '')
    if not c or c in union or c in seen: continue
    seen.add(c)
    name=(rec.get('name') or '').strip()
    desc=(rec.get('description') or '').strip()
    tags=' '.join(rec.get('tags') or [])
    if not name: continue
    if name.startswith('http'): continue
    reason=bad_text(name+' '+desc+' '+tags)
    if reason:
        continue
    cands.append({'code':c,'name':name,'desc':desc,'cat':CATMAP.get((rec.get('category') or '').lower().strip(),'Community & Social'),
                  'country':(rec.get('country') or 'International')[:2] or 'International'})
print("candidates after content filter:", len(cands))

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
def check(item):
    code=item['code']
    for attempt in range(2):
        try:
            r=requests.get('https://chat.whatsapp.com/'+code, headers=UA, timeout=25)
            if r.status_code!=200:
                return (item, None, 'http%d'%r.status_code)
            m=re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            title=html.unescape(m.group(1)).strip() if m else ''
            if not title or title in ('WhatsApp Group','Join this group on WhatsApp'):
                if attempt==0:
                    time.sleep(3); continue
                return (item, None, 'empty-title')
            return (item, title, 'live')
        except Exception as e:
            if attempt==0:
                time.sleep(3); continue
            return (item, None, 'transport:'+type(e).__name__)
    return (item, None, 'unknown')

results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    futs=[ex.submit(check, it) for it in cands]
    for i,f in enumerate(futs):
        results.append(f.result())
        time.sleep(0.5)
        if i%20==0: print(i, 'done')

from collections import Counter
print(Counter(r[2] if r[2]!='live' else 'live' for r in results))
verified=[]; pending=[]
for item,title,status in results:
    if status!='live':
        if status.startswith('transport'):
            pending.append({**item,'reason':'transport'})
        continue
    # re-filter on live og:title
    reason=bad_text(title)
    if reason:
        print('DROP-BY-TITLE', item['code'], title, reason); continue
    name=title if item['name'].lower() in ('whatsapp group',) or item['name'].startswith('http') else item['name']
    desc=item['desc']
    if not desc or len(desc)<10 or bad_text(desc):
        desc=f"Join {name}, a WhatsApp group listed under {item['cat']}. Connect with members, share updates and chat with the community."
    desc=desc[:300]
    verified.append({'name':name,'category':item['cat'],'country':item['country'],
                     'description':desc,'invite':'https://chat.whatsapp.com/'+item['code'],'image':''})
    print('OK', item['code'], '|', name, '|', item['cat'], '|', item['country'])
print('VERIFIED', len(verified), 'PENDING', len(pending))
json.dump(verified, open('/tmp/gs_verified.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open('/tmp/gs_pending.json','w'), ensure_ascii=False, indent=1)
