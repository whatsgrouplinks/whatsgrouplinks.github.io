import json, re, subprocess, time, html
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
fresh=json.load(open('/tmp/gs_fresh.json'))
ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD_SUBS=['sex','porn','xxx','nude','escort','call girl','callgirl','video call','phone sex','live sex',
 'baise','fuck','bhabhi sex','leak video','leaked video','cp video','child','bacchi','xxnxx','xvideos',
 'sexy','hot girl','hot video','nangi','nanga','mms video','viral videoo','all type video','freaky',
 'satta','khaiwal','1xbet','1x bet','binance millionaire','bitfinex','prono','prixal','winning zone',
 'roland tips','king of virtual','free money']
PHONE_RE=re.compile(r'\b\d{10,}\b')
def bad_text(t):
    s=(t or '').lower().replace('ß','ss')
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
cands=[]; seen=set()
for item in fresh:
    rec=item['rec']
    c=fix_code(rec.get('inviteLink') or '')
    if not c or c in union or c in seen: continue
    seen.add(c)
    name=(rec.get('name') or '').strip(); desc=(rec.get('description') or '').strip()
    tags=' '.join(rec.get('tags') or [])
    if not name or name.startswith('http'): continue
    if bad_text(name+' '+desc+' '+tags): continue
    cands.append({'code':c,'name':name,'desc':desc,'cat':CATMAP.get((rec.get('category') or '').lower().strip(),'Community & Social'),
                  'country':(rec.get('country') or 'International')[:2] or 'International'})
print("candidates:", len(cands), flush=True)
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
                    time.sleep(5); continue
                return ('empty', '')
            return ('live', title)
        except Exception as e:
            if attempt==0:
                time.sleep(5); continue
            return ('transport', '')
    return ('empty','')
outf=open('/tmp/gs2_results.jsonl','w')
verified=[]; pending=[]; dead=0
for i,it in enumerate(cands):
    st,title=check(it['code'])
    rec={'code':it['code'],'name':it['name'],'cat':it['cat'],'country':it['country'],'desc':it['desc'],'status':st,'title':title}
    outf.write(json.dumps(rec,ensure_ascii=False)+'\n'); outf.flush()
    if st=='live':
        if bad_text(title):
            print(i,'DROP-BY-TITLE',it['code'],title, flush=True); dead+=1; continue
        name=title if it['name'].lower() in ('whatsapp group',) else it['name']
        desc=it['desc']
        if not desc or len(desc)<10 or bad_text(desc):
            desc=f"Join {name}, a WhatsApp group listed under {it['cat']}. Connect with members, share updates and chat with the community."
        verified.append({'name':name,'category':it['cat'],'country':it['country'],
                         'description':desc[:300],'invite':'https://chat.whatsapp.com/'+it['code'],'image':''})
        print(i,'LIVE',it['code'],'|',name,'|',it['cat'], flush=True)
    elif st=='transport':
        pending.append({'name':it['name'],'category':it['cat'],'country':it['country'],
                        'description':(it['desc'] or f"Join {it['name']}, a WhatsApp group listed under {it['cat']}.")[:300],
                        'invite':'https://chat.whatsapp.com/'+it['code'],'image':'','reason':'transport'})
        print(i,'TRANSPORT',it['code'], flush=True)
    else:
        dead+=1
    time.sleep(1.0)
outf.close()
json.dump(verified, open('/tmp/gs2_verified.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open('/tmp/gs2_pending.json','w'), ensure_ascii=False, indent=1)
print('DONE live=%d transport=%d dead=%d'%(len(verified),len(pending),dead), flush=True)
