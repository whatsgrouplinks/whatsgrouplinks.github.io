import json, re, subprocess, time, html
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
D=WAVE+'team10_gb/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
redir=json.load(open(D+'redirects.json'))
ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD_SUBS=['sex','porn','xxx','nude','escort','call girl','callgirl','video call','phone sex','live sex',
 'baise','fuck','bhabhi sex','leak video','leaked video','cp video','child','bacchi','xxnxx','xvideos',
 'sexy','hot girl','hot video','nangi','nanga','mms video','viral videoo','all type video','freaky',
 'satta','khaiwal','1xbet','1x bet','binance millionaire','bitfinex','prono','prixal','winning zone',
 'roland tips','king of virtual','free money','سكس','نودز','جنس','بورنو','नंगी','नग्न','सेक्स','पोर्न']
PHONE_RE=re.compile(r'\b\d{10,}\b')
def bad_text(t):
    s=(t or '').lower().replace('ß','ss')
    if any(e in s for e in ADULT_EMOJI): return 'adult-emoji'
    for b in BAD_SUBS:
        if b in s: return 'bad:'+b
    if PHONE_RE.search(s): return 'phone-number'
    return None
CATMAP={'game':'Gaming','news':'News','religion':'Islamic','technology':'Technology','trade':'Business',
 'travel':'Travel','food':'Cooking','student':'Education','series-movie':'Entertainment',
 'job-postings':'Jobs','music':'Entertainment','chat-friendship':'Friendship','chat-friendship-p2':'Friendship'}
TR_HINTS=['sohbete','arkadas','tanisma','ingilizce','öğren','konuş','türk','turkish','romantik','gel ']
def country_for(name, desc):
    s=(name+' '+desc).lower()
    if 'international' in s or 'global' in s or 'world' in s: return 'International'
    if '🇦🇪' in s or ' uae' in s or 'uae ' in s: return 'AE'
    if '🇩🇪' in s or '🇺🇸' in s: return 'International'
    return 'TR'
cands=[]
for gid,v in redir.items():
    code=v.get('code')
    if not code: continue
    if code in union: 
        print(gid,'IN-UNION',code, flush=True); continue
    name=(v.get('name') or '').strip()
    desc=(v.get('desc') or '').strip()
    if not name: continue
    reason=bad_text(name+' '+desc)
    if reason:
        print(gid,'FILTERED',reason,'|',name[:50], flush=True); continue
    slug=v.get('src_slug','')
    cands.append({'code':code,'gid':gid,'name':name,'desc':desc,
                  'cat':CATMAP.get(slug,'Community & Social'),
                  'country':country_for(name,desc),'slug':slug})
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
                return ('empty','')
            return ('live',title)
        except Exception:
            if attempt==0:
                time.sleep(5); continue
            return ('transport','')
    return ('empty','')
outf=open('/tmp/gb_results.jsonl','w')
verified=[]; pending=[]; dead=0
for i,it in enumerate(cands):
    st,title=check(it['code'])
    rec={'code':it['code'],'gid':it['gid'],'name':it['name'],'cat':it['cat'],'country':it['country'],'desc':it['desc'],'status':st,'title':title}
    outf.write(json.dumps(rec,ensure_ascii=False)+'\n'); outf.flush()
    if st=='live':
        if bad_text(title):
            print(i,'DROP-BY-TITLE',it['code'],title, flush=True); dead+=1; continue
        name=it['name']
        desc=it['desc']
        if not desc or len(desc)<10 or bad_text(desc):
            desc=f"Join {name}, a WhatsApp group listed under {it['cat']}. Connect with members, share updates and chat with the community."
        verified.append({'name':name,'category':it['cat'],'country':it['country'],
                         'description':desc[:300],'invite':'https://chat.whatsapp.com/'+it['code'],'image':''})
        print(i,'LIVE',it['code'],'|',name[:45],'|',it['cat'],'|',it['country'], flush=True)
    elif st=='transport':
        pending.append({'name':it['name'],'category':it['cat'],'country':it['country'],
                        'description':(it['desc'] or f"Join {it['name']}, a WhatsApp group listed under {it['cat']}.")[:300],
                        'invite':'https://chat.whatsapp.com/'+it['code'],'image':'','reason':'transport'})
        print(i,'TRANSPORT',it['code'], flush=True)
    else:
        dead+=1
    time.sleep(1.5)
outf.close()
json.dump(verified, open('/tmp/gb_verified.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open('/tmp/gb_pending.json','w'), ensure_ascii=False, indent=1)
print('DONE live=%d transport=%d dead=%d'%(len(verified),len(pending),dead), flush=True)
