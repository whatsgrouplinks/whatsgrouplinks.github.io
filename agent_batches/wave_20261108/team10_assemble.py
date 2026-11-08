import json, re, subprocess, time, html, os
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
CANON={'Education','Jobs','Entertainment','Islamic','News','Sports','Technology','Health','Business',
 'Gaming','Friendship','Community & Social','Online Earning','Crypto','Cooking','Poetry','Travel',
 'Scholarship','Freelance','Real Estate','Buy & Sell','Finance','Funny'}
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

verified=[]; pending=[]
def load_verified(path, src):
    try:
        items=json.load(open(path))
    except Exception as e:
        print(src,'no verified file:',e); return
    for it in items:
        code=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})', it.get('invite','') or '')
        code=code.group(1) if code else None
        if not code: print('BAD-INVITE', it); continue
        if code in union: print('UNION-DROP', code); continue
        if any(v['invite'].endswith(code) for v in verified): print('DUP-DROP', code); continue
        if it.get('category') not in CANON: print('BAD-CAT', it); continue
        r=bad_text(it.get('name','')+' '+it.get('description',''))
        if r: print('POSTFILTER-DROP', code, r, it.get('name')); continue
        if not it.get('country'): it['country']='International'
        verified.append(it)
    print(src,'loaded, total verified now', len(verified))
def load_pending(path, src):
    try: items=json.load(open(path))
    except Exception as e: print(src,'no pending file:',e); return
    for it in items:
        pending.append(it)
    print(src,'pending loaded, total', len(pending))

load_verified('/tmp/gs2_verified.json','groupssor')
load_verified('/tmp/gb_verified.json','grupbul')
load_pending('/tmp/gs2_pending.json','groupssor')
load_pending('/tmp/gb_pending.json','grupbul')

# supplementary: HYxIXc2kv6CJG7TW5CrHSn re-verify live right now, then add
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
code='HYxIXc2kv6CJG7TW5CrHSn'
live=False; title=''
for attempt in range(2):
    r=subprocess.run(['curl','-s','-m','25','-A',UA,f'https://chat.whatsapp.com/{code}'],
                     capture_output=True, text=True, timeout=30)
    m=re.search(r'<meta property="og:title" content="([^"]*)"', r.stdout or '')
    title=html.unescape(m.group(1)).strip() if m else ''
    if title and title not in ('WhatsApp Group','Join this group on WhatsApp'):
        live=True; break
    time.sleep(5)
print('HYxIXc re-verify:', live, '|', title)
if live and code not in union and not any(v['invite'].endswith(code) for v in verified):
    verified.append({'name':'SHEYI LEGIT ONLINE UPDATE','category':'Crypto','country':'NG',
        'description':'NAIRA & CRYPTO UPDATES — DAILY. Free daily updates on paying crypto offers: airdrops, FCFS claims, giveaways, sign-up bonuses and free-money updates — posted fast, as they drop. For Nigerians who don\'t want to miss out. Join free and start catching updates today.',
        'invite':'https://chat.whatsapp.com/'+code,'image':''})

# leads
leads=[
 {"url":"https://grupbul.com/en/category/whatsapp/15/chat-friendship","source":"grupbul"},
 {"url":"https://grupbul.com/en/category/whatsapp/53/food","source":"grupbul"},
 {"url":"https://grupbul.com/en/category/whatsapp/8/news","source":"grupbul"},
 {"url":"https://grupbul.com/en/category/whatsapp/54/travel","source":"grupbul"},
 {"url":"https://grupbul.com/en/category/whatsapp/29/trade","source":"grupbul"},
 {"url":"https://grupbul.com/en/category/whatsapp/47/series-movie","source":"grupbul"},
 {"url":"https://groupssor-api.blog-99n.workers.dev/api/groups","source":"groupssor-api"},
]

def write_retry(path, data):
    txt=json.dumps(data, ensure_ascii=False, indent=1)
    for attempt in range(5):
        try:
            with open(path,'w',encoding='utf-8') as f:
                f.write(txt)
            print('WROTE', path, len(txt), 'bytes,', len(data), 'records')
            return True
        except Exception as e:
            print('WRITE-FAIL', path, attempt, repr(e)); time.sleep(3)
    print('WRITE-GAVE-UP', path); return False

# final validation
seen=set()
for v in verified:
    c=re.search(r'([A-Za-z0-9]{22})$', v['invite']).group(1)
    assert c not in seen, 'dup '+c
    seen.add(c)
    assert v['category'] in CANON, v
    assert v['country'], v
    assert v['description'], v
assert all(p.get('reason')=='transport' for p in pending)
write_retry(WAVE+'team10-groupssor-grupbul.json', verified)
write_retry(WAVE+'team10-groupssor-grupbul-pending.json', pending)
write_retry(WAVE+'team10-groupssor-grupbul-leads.json', leads)
print('FINAL verified=%d pending=%d leads=%d'%(len(verified),len(pending),len(leads)))
for v in verified: print(' ', v['invite'], '|', v['name'][:50], '|', v['category'], '|', v['country'])
