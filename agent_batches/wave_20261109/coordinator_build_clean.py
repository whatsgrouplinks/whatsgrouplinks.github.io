import json, glob, re, unicodedata, os

WAVE='.'
union=set(json.load(open('../../.existing_codes.json')))
CANON={'Gaming','Education','Online Earning','Community & Social','Business','Friendship','Finance','Buy Sell','Islamic','Entertainment','Jobs','Technology','Funny','Sports','Health','News'}
CATFIX={'buy-sell':'Buy Sell','buysell':'Buy Sell','buy & sell':'Buy Sell','movies':'Entertainment','music':'Entertainment','finance':'Finance','funny':'Funny','education':'Education','business':'Business','general':'Community & Social'}

PORN=['porn','xxx','sex','sexy','hookup','escort','cam girl','camgirl','call girl','callgirl','bokep','nude','naked','desi sex','hot girl','sexy girl','erotic','fuck','pussy','dick','boobs','s3x','s3x','\u1e9eex','sexo','sexchat','sexting','masturbat','horny','naughty','fwb','friends with benefits','kambi','desi bhabhi','aunty sex','girls sex','boys sex','video call girl','leak','leaked','mms','viral mms','onlyfans','pornhub','xvideos','redtube','brazzers','hentai','nekopoi','jav ','18+','\U0001f51e','\U0001f346','\U0001f348']
SCAM=['b-love','blove','forsage','sheyi','pearlvine','holiverse','meta-whale','metawhale','unick forex','airdrop','free money','earn money without investment','usdt flash','btc flash','binary option','carding','stolen cc','dark web','data hack','hack software','free fire hack','paid hack']

def fold(s):
    return unicodedata.normalize('NFKD', str(s or '')).lower()
def strip_prohibitions(s):
    # remove sentences that prohibit adult content (rules), before screening
    s=str(s or '')
    out=[]
    for sent in re.split(r'(?<=[.!?])\s+|\n', s):
        low=fold(sent)
        if any(w in low for w in ['na karein','not allowed','prohibit','forbidden','no porn','no adult','no 18+','no sex','do not share','dont share','strictly prohibited','not allow']):
            continue
        out.append(sent)
    return ' '.join(out)

def screen(name, desc):
    text=fold(name)+' '+fold(strip_prohibitions(desc))
    for p in PORN:
        if p in text: return 'porn:'+p
    for p in SCAM:
        if p in text: return 'scam:'+p
    # phone numbers: long digit runs
    if re.search(r'\d{7,}', fold(name)+' '+fold(desc)): return 'phone'
    return None

raw_total=0; clean={}; excluded=[]; dups=[]; union_leaks=[]; schema_err=[]
for n in range(1,25):
    f=f'team{n:02d}-candidates.json'
    if not os.path.exists(f): print(f'MISSING {f}'); continue
    items=json.load(open(f))
    raw_total+=len(items)
    for it in items:
        code=it.get('invite','').rstrip('/').split('/')[-1].split('?')[0].split('#')[0]
        if not code or len(code)<10:
            schema_err.append((n,'bad-code',it)); continue
        if code in union:
            union_leaks.append((n,code)); continue
        cat=it.get('category','')
        if cat not in CANON:
            fixed=CATFIX.get(fold(cat).strip())
            if fixed: cat=fixed
            else:
                schema_err.append((n,'bad-cat',it)); continue
        if code in clean:
            dups.append((n,code,'first-team-'+str(clean[code]['_team']))); continue
        name=str(it.get('name','')).strip()
        desc=str(it.get('description','')).strip()
        if not name or not desc:
            schema_err.append((n,'empty-name-desc',it)); continue
        reason=screen(name,desc)
        if reason:
            excluded.append({'team':n,'code':code,'name':name,'reason':reason}); continue
        cc=str(it.get('country','IN')).upper()[:2] or 'IN'
        clean[code]={'name':name,'category':cat,'country':cc,'description':desc,
                     'invite':f'https://chat.whatsapp.com/{code}','_team':n}

print('raw team candidates:',raw_total)
print('clean unique (excl team13 pending re-verify):',len(clean))
print('cross-team dups:',len(dups))
print('union leaks:',len(union_leaks))
print('schema errors:',len(schema_err))
print('screen-excluded:',len(excluded))
json.dump([{'team':n,'code':c,'first':f} for n,c,f in dups],open('wave_20261109_cross_dups.json','w'),indent=1)
json.dump(excluded,open('wave_20261109_excluded.json','w'),indent=1,ensure_ascii=False)
json.dump(schema_err,open('wave_20261109_schema_err.json','w'),indent=1,ensure_ascii=False)
json.dump(union_leaks,open('wave_20261109_union_leaks.json','w'),indent=1)
# save clean without _team marker
out=[{k:v for k,v in c.items() if k!='_team'} for c in clean.values()]
json.dump(out,open('wave_20261109_verified_clean_prelim.json','w'),indent=1,ensure_ascii=False)
# per-team kept counts
from collections import Counter
print(Counter(c['_team'] for c in clean.values()))
