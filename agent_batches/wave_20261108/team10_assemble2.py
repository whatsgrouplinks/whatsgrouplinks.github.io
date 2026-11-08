import json, re, subprocess, time, html
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

verified=json.load(open(WAVE+'team10_tail_verified.json'))
pending=json.load(open(WAVE+'team10_tail_pending.json'))
print('tail verified:', len(verified), 'pending:', len(pending), flush=True)

# supplementary: HYxIXc2kv6CJG7TW5CrHSn — groupssor crypto group, excluded from the
# main filter only by the 'free money' tag; verified live 3x already, re-verify now.
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
    time.sleep(6)
print('HYxIXc re-verify:', live, '|', title, flush=True)
if live and code not in union and not any(v['invite'].endswith(code) for v in verified) and not bad_text(title):
    verified.append({'name':'SHEYI LEGIT ONLINE UPDATE','category':'Crypto','country':'NG',
        'description':'NAIRA & CRYPTO UPDATES — DAILY. Free daily updates on paying crypto offers: airdrops, FCFS claims, giveaways, sign-up bonuses and free-money updates — posted fast, as they drop. For Nigerians who don\'t want to miss out. Join free and start catching updates today.',
        'invite':'https://chat.whatsapp.com/'+code,'image':''})

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
            print('WROTE', path, len(txt), 'bytes,', len(data), 'records', flush=True)
            return True
        except Exception as e:
            print('WRITE-FAIL', path, attempt, repr(e), flush=True); time.sleep(3)
    print('WRITE-GAVE-UP', path, flush=True); return False

seen=set()
for v in verified:
    c=re.search(r'([A-Za-z0-9]{22})$', v['invite']).group(1)
    assert c not in seen, 'dup '+c
    assert c not in union, 'union '+c
    seen.add(c)
    assert v['category'] in CANON, v
    assert v['country'], v
    assert v['description'], v
    assert not bad_text(v['name']+' '+v['description']), v
assert all(p.get('reason')=='transport' for p in pending)
write_retry(WAVE+'team10-groupssor-grupbul.json', verified)
write_retry(WAVE+'team10-groupssor-grupbul-pending.json', pending)
write_retry(WAVE+'team10-groupssor-grupbul-leads.json', leads)
print('FINAL verified=%d pending=%d leads=%d'%(len(verified),len(pending),len(leads)), flush=True)
for v in verified: print(' ', v['invite'], '|', v['name'], '|', v['category'], '|', v['country'], flush=True)
