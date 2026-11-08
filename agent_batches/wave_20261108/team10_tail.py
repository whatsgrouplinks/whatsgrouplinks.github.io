import json, re, subprocess, time, html
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD=['sex','porn','xxx','nude','escort','call girl','callgirl','video call','phone sex','live sex',
 'baise','fuck','bhabhi sex','leak video','leaked video','cp video','child','bacchi','xxnxx','xvideos',
 'sexy','hot girl','hot video','nangi','nanga','mms video','viral videoo','all type video','freaky',
 'satta','khaiwal','1xbet','1x bet','binance millionaire','bitfinex','prono','prixal','winning zone',
 'roland tips','king of virtual','free money','سكس','نودز','جنس','بورنو','नंगी','नग्न','सेक्स','पोर्न']
PHONE_RE=re.compile(r'\b\d{10,}\b')
def bad_text(t):
    s=(t or '').lower().replace('ß','ss')
    if any(e in s for e in ADULT_EMOJI): return 'adult-emoji'
    for b in BAD:
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
data=json.load(open(WAVE+'team10_gs_raw.json'))
meta={}; seen=set()
for rec in data:
    if str(rec.get('platform','')).lower()!='whatsapp': continue
    c=fix_code(rec.get('inviteLink') or '')
    if not c or c in union or c in seen: continue
    seen.add(c)
    name=(rec.get('name') or '').strip(); desc=(rec.get('description') or '').strip()
    tags=' '.join(rec.get('tags') or [])
    if not name or name.startswith('http'): continue
    if bad_text(name+' '+desc+' '+tags): continue
    meta[c]={'name':name,'desc':desc,'cat':CATMAP.get((rec.get('category') or '').lower().strip(),'Community & Social'),
             'country':(rec.get('country') or 'International')[:2] or 'International','src':'groupssor'}
print("gs candidates rebuilt:", len(meta), flush=True)
CATMAP2={'game':'Gaming','news':'News','religion':'Islamic','technology':'Technology','trade':'Business',
 'travel':'Travel','food':'Cooking','student':'Education','series-movie':'Entertainment',
 'job-postings':'Jobs','music':'Entertainment','chat-friendship':'Friendship','chat-friendship-p2':'Friendship'}
redir=json.load(open(WAVE+'team10_gb/redirects.json'))
def country_for(name, desc):
    s=(name+' '+desc).lower()
    if 'international' in s or 'global' in s or 'world' in s: return 'International'
    if '🇦🇪' in s or ' uae' in s: return 'AE'
    if '🇩🇪' in s or '🇺🇸' in s: return 'International'
    return 'TR'
n0=len(meta)
for gid,v in redir.items():
    code=v.get('code')
    if not code or code in union: continue
    name=(v.get('name') or '').strip(); desc=(v.get('desc') or '').strip()
    if not name: continue
    if bad_text(name+' '+desc): continue
    if code in meta: continue
    meta[code]={'name':name,'desc':desc,'cat':CATMAP2.get(v.get('src_slug',''),'Community & Social'),
                'country':country_for(name,desc),'src':'grupbul'}
print("gb candidates added:", len(meta)-n0, "total meta:", len(meta), flush=True)
# empties: all meta except the one known-live-adult groupssor code (dropped by title filter anyway)
tocheck=sorted(c for c in meta if c!='J6yVkaaOraRGBnzYLxuApi')
print("recheck list:", len(tocheck), flush=True)
json.dump({'meta':meta,'tocheck':tocheck}, open(WAVE+'team10_meta.json','w'), ensure_ascii=False, indent=1)
# tail: last 30 (positions 109..138) — covers the killed pass's unobserved tail + overlap
tail=tocheck[109:]
print("tail to verify:", len(tail), tail, flush=True)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def check(code):
    for attempt in range(2):
        try:
            r=subprocess.run(['curl','-s','-m','25','-A',UA,f'https://chat.whatsapp.com/{code}'],
                             capture_output=True, text=True, timeout=30)
            out=r.stdout or ''
            m=re.search(r'<meta property="og:title" content="([^"]*)"', out)
            title=html.unescape(m.group(1)).strip() if m else ''
            if not title or title in ('WhatsApp Group','Join this group on WhatsApp'):
                if attempt==0:
                    time.sleep(6); continue
                return ('empty','')
            return ('live',title)
        except Exception:
            if attempt==0:
                time.sleep(6); continue
            return ('transport','')
    return ('empty','')
outf=open(WAVE+'team10_tail_results.jsonl','w')
verified=[]; pending=[]
for i,code in enumerate(tail):
    m=meta[code]
    st,title=check(code)
    outf.write(json.dumps({'code':code,'status':st,'title':title,'src':m['src'],'name':m['name']},ensure_ascii=False)+'\n'); outf.flush()
    if st=='live':
        if bad_text(title):
            print(i,'DROP-BY-TITLE',code,title, flush=True); continue
        name=title if title.lower()!=m['name'].lower() else m['name']
        desc=m['desc']
        if not desc or len(desc)<10 or bad_text(desc):
            desc=f"Join {name}, a WhatsApp group listed under {m['cat']}. Connect with members, share updates and chat with the community."
        verified.append({'name':name,'category':m['cat'],'country':m['country'],
                         'description':desc[:300],'invite':'https://chat.whatsapp.com/'+code,'image':''})
        print(i,'LIVE',code,'|',name[:50],'|',m['cat'],'|',m['src'], flush=True)
    elif st=='transport':
        pending.append({'name':m['name'],'category':m['cat'],'country':m['country'],
                        'description':(m['desc'] or f"Join {m['name']}, a WhatsApp group listed under {m['cat']}.")[:300],
                        'invite':'https://chat.whatsapp.com/'+code,'image':'','reason':'transport'})
        print(i,'TRANSPORT',code, flush=True)
    time.sleep(2.0)
outf.close()
json.dump(verified, open(WAVE+'team10_tail_verified.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open(WAVE+'team10_tail_pending.json','w'), ensure_ascii=False, indent=1)
print('TAIL DONE live=%d transport=%d'%(len(verified),len(pending)), flush=True)
