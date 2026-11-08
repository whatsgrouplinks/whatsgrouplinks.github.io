import re, json, time, html
import requests

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/'
DIR=WAVE+'team32-scratch/'

cands=json.load(open(DIR+'candidates.json'))
print('candidates:', len(cands))

PORN_PAT=re.compile(r'porn|pornhub|\bxxx\b|nude|\bsex\b|sexual|escort|call girl|fuck|dick|pussy|boobs|anal|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)
FRAUD_PAT=re.compile(r'\byahoo\b|format chat|pick.?up|loader|passcode|counterfeit', re.I)

def liveness(code):
    url='https://chat.whatsapp.com/'+code
    try:
        r=requests.get(url, headers={'User-Agent':UA}, timeout=25)
        if r.status_code==429:
            return ('ratelimited','',429)
        m=re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title=html.unescape(m.group(1)).strip() if m else ''
        return ('ok', title, r.status_code)
    except Exception as e:
        return ('transport', str(e)[:80], 0)

CATMAP={
 'sports-and-fitness':'Sports','sports':'Sports','gaming':'Gaming','games':'Gaming',
 'jobs':'Jobs','education':'Education','entertainment':'Entertainment',
 'friendship':'Friendship','news-and-politics':'News','news':'News','islamic':'Islamic',
 'business':'Business','finance':'Finance','buy-and-sell':'Buy-Sell','health':'Health',
 'community':'Community','technology':'Technology','crypto':'Crypto','money':'Finance',
 'travel-and-tourism':'Travel','music':'Music','movies':'Movies','food':'Food','pets':'Pets',
 'funny':'Funny','girls':'Girls','flirting':'Friendship','regional':'Regional',
 'earn-money-online':'Finance','fan-club':'Entertainment',
}
CATWORDS={'Sports':'sports fans and betting tips','Gaming':'gamers and betting fans',
 'Jobs':'job seekers and vacancy alerts','Education':'students and study updates',
 'Entertainment':'entertainment and gist','Friendship':'making new friends','News':'news and current affairs',
 'Islamic':'Islamic discussions','Business':'business owners and vendors','Finance':'finance and online earning',
 'Buy-Sell':'buying and selling','Health':'health tips','Community':'community chat',
 'Technology':'tech enthusiasts','Crypto':'crypto traders','Travel':'travel lovers','Music':'music fans',
 'Movies':'movie lovers','Food':'food lovers','Pets':'pet lovers','Funny':'fun and memes',
 'Girls':'girls community','Regional':'Nigerians','Other':'members'}

def map_cat(slug):
    s=(slug or '').lower().strip()
    if s in CATMAP: return CATMAP[s]
    for k,v in CATMAP.items():
        if k and k in s: return v
    return 'Other'

def clean(s):
    return re.sub(r'\s+',' ',(s or '')).strip()

def make_desc(title, gdesc, slug):
    cat=map_cat(slug); cw=CATWORDS.get(cat,'members')
    gd=clean(gdesc)
    # strip porn/adult remnants already excluded; keep it short
    base=f'A Nigerian WhatsApp group for {cw}.'
    if gd and len(gd)>10 and not PORN_PAT.search(gd):
        gd=gd[:140]
        return f'{base} {clean(title)}: {gd[0].upper()+gd[1:] if gd else ""}'.strip()[:400]
    return f'{base} Join {clean(title)} to chat, share updates and connect with fellow Nigerians.'

verified=[]; pending=[]; porn=0; fraud=0; dead=0
for i,c in enumerate(cands):
    code=c['code']
    blob=(c['title']+' '+c['desc']).strip()
    if PORN_PAT.search(blob):
        porn+=1; continue
    if FRAUD_PAT.search(blob):
        fraud+=1; continue
    st,title,sc=liveness(code)
    if st=='ratelimited':
        pending.append({'name':clean(c['title'])[:80],'category':map_cat(c.get('category_slug')),'country':'NG',
            'description':'Nigerian WhatsApp group.','invite':'https://chat.whatsapp.com/'+code,
            'image':'','note':'rate-limited'})
        # bank the rest too
        for c2 in cands[i+1:]:
            pending.append({'name':clean(c2['title'])[:80],'category':map_cat(c2.get('category_slug')),'country':'NG',
                'description':'Nigerian WhatsApp group.','invite':'https://chat.whatsapp.com/'+c2['code'],
                'image':'','note':'rate-limited'})
        print('RATE LIMITED at index',i,'- banked rest'); break
    if st=='ok' and title:
        name=clean(title) if len(clean(title))<=70 else clean(c['title'])
        verified.append({
            'name': name,
            'category': map_cat(c.get('category_slug')),
            'country': 'NG',
            'description': make_desc(c['title'], c['desc'], c.get('category_slug')),
            'invite': 'https://chat.whatsapp.com/'+code,
            'image': ''
        })
    elif st=='ok':
        dead+=1
    else:
        pending.append({'name':clean(c['title'])[:80],'category':map_cat(c.get('category_slug')),'country':'NG',
            'description':'Nigerian WhatsApp group.','invite':'https://chat.whatsapp.com/'+code,
            'image':'','note':'transport failure'})
    time.sleep(0.8)

# 7hubent own-group code from lagoswiki float button (server-rendered)
st,title,sc=liveness('LGaUJdCBKkLFay6icky2Ov')
print('7hubent code:', st, repr(title)[:70])
if st=='ok' and title and not PORN_PAT.search(title):
    verified.append({'name':clean(title)[:70],'category':'Business','country':'NG',
        'description':'A Nigerian WhatsApp group for business owners and vendors to advertise products and services for free. Join to network, share offers and grow your business with fellow Nigerians.',
        'invite':'https://chat.whatsapp.com/LGaUJdCBKkLFay6icky2Ov','image':''})

json.dump(verified, open(WAVE+'team32-nigeria.json','w'), indent=1, ensure_ascii=False)
if pending:
    json.dump(pending, open(WAVE+'team32-unverified-pending.json','w'), indent=1, ensure_ascii=False)
print('VERIFIED:',len(verified),'PENDING:',len(pending),'DEAD:',dead,'PORN_DROPPED:',porn,'FRAUD_EXCLUDED:',fraud)
