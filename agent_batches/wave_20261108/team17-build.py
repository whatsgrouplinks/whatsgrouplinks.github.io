import json, re
from html import unescape
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
CANON=["Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health","Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"]
def cat_for(name, page_cat):
    n=name.lower()
    if any(k in n for k in ['scholarship']): return 'Scholarship'
    if any(k in n for k in ['study','exam','ssc','jee','neet','upsc','board','12th','10th','class ','student','school','college','university','education','spoken english','admission','coaching']): return 'Education'
    if any(k in n for k in ['job','jobs','sarkari','naukri','vacanc','recruit','rozgar','employment','career']): return 'Jobs'
    if any(k in n for k in ['cricket','ipl','football','sports','psl']): return 'Sports'
    if any(k in n for k in ['islam','quran','muslim','deen','madrasa','masjid','namaz','ramadan','hadees','taleem']): return 'Islamic'
    if any(k in n for k in ['news','breaking','headlines']): return 'News'
    if any(k in n for k in ['bgmi','free fire','pubg','clash of clans','gaming','game','esports','e-sports','gamer']): return 'Gaming'
    if any(k in n for k in ['crypto','bitcoin','binance','ethereum']): return 'Crypto'
    if any(k in n for k in ['forex','trading','fx ','signal','stock market','share market','invest']): return 'Finance'
    if any(k in n for k in ['earn','earning','refer and earn','online earning','work from home','part time']): return 'Online Earning'
    if any(k in n for k in ['movie','movies','song','music','lyrics','youtube','entertainment','drama','status','shayari','poetry']): return 'Poetry' if any(k in n for k in ['shayari','poetry']) else 'Entertainment'
    if any(k in n for k in ['health','fitness','yoga','weight loss']): return 'Health'
    if any(k in n for k in ['buy','sell','shopping','shop ','store','market','deal','bazar','business','resell']): return 'Buy & Sell' if any(k in n for k in ['buy','sell','shopping','shop ','store','market','deal','bazar']) else 'Business'
    if any(k in n for k in ['funny','joke','meme','comedy','hasi','fun ']): return 'Funny'
    if any(k in n for k in ['tech','programming','code','html','css','developer','computer']): return 'Technology'
    if any(k in n for k in ['girl','girls','friend','friendship','boys','aunty','chat ','chatting']): return 'Friendship'
    if any(k in n for k in ['travel','tourism','tour']): return 'Travel'
    if any(k in n for k in ['cook','recipe','food']): return 'Cooking'
    if any(k in n for k in ['freelanc']): return 'Freelance'
    if any(k in n for k in ['property','real estate','plot','house for']): return 'Real Estate'
    return page_cat if page_cat in CANON else 'Community & Social'

def clean_name(s):
    s=unescape(s or '').strip()
    s=re.sub(r'\s+',' ',s)
    s=s.strip(' -–—•·👉')
    s=re.sub(r'\s*(–|-|:)\s*(join now|click here|join group)\s*$','',s,flags=re.I)
    return s.strip(' -–—•·')

def junk_name(name):
    stripped=re.sub(r'[^\w\s]','',name,flags=re.UNICODE).strip()
    if len(stripped)<2: return True
    if re.match(r'^(group|join|click here)\s*\d*$',name.strip(),re.I): return True
    return False

res=json.load(open(WAVE+'team17-verify6.json'))
verified=[]; pending=[]
for code,(v) in res.items():
    cand=v['cand']; status,info=v['res']
    if status=='pending':
        pending.append({"name":clean_name(cand['name']),"category":cat_for(cand['name'],cand['cat']),"country":cand['country'],
                        "description":f"Join {clean_name(cand['name'])}, a WhatsApp group listed under {cat_for(cand['name'],cand['cat'])}. Open the invite link to join the group on WhatsApp.",
                        "invite":f"https://chat.whatsapp.com/{code}","image":"","reason":"transport"})
        continue
    if status!='live': continue
    ogtitle=info
    name=clean_name(cand['name'])
    if junk_name(name):
        name=clean_name(ogtitle)
    if junk_name(name): continue
    cat=cat_for(name,cand['cat'])
    verified.append({"name":name,"category":cat,"country":cand['country'],
                     "description":f"Join {name}, a WhatsApp group listed under {cat}. Open the invite link to join the group on WhatsApp.",
                     "invite":f"https://chat.whatsapp.com/{code}","image":""})
# dedupe by code (already unique) and sort by category then name
verified.sort(key=lambda g:(g['category'],g['name'].lower()))
pending.sort(key=lambda g:g['name'].lower())
json.dump(verified, open(WAVE+'team17-newdirs-southasia.json','w'), ensure_ascii=False, indent=1)
json.dump(pending, open(WAVE+'team17-newdirs-southasia-pending.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print('verified:',len(verified))
print(Counter(g['category'] for g in verified))
print(Counter(g['country'] for g in verified))
print('pending:',len(pending))
