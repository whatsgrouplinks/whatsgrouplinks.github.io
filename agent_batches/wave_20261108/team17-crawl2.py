import requests, re, json, time
from html import unescape
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
def clean(s):
    s=unescape(re.sub(r'<[^>]+>','',s or '')).strip()
    return re.sub(r'\s+',' ',s)
def add(code,name,cat,country,page):
    code=code.strip()
    if len(code)<20 or len(code)>24 or code in union: return
    name=clean(name)
    if not name: return
    if code not in cands: cands[code]={'name':name,'cat':cat,'country':country,'page':page}
    elif len(name)>len(cands[code]['name']): cands[code]['name']=name

# GLS Bangladesh cards
try:
    r=requests.get('https://grouplinkshare.com/bangladesh-whatsapp-group-links/',headers=UA,timeout=25)
    cards=re.findall(r'<a href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"[^>]*>.*?<span[^>]*>(.*?)</span>', r.text, re.S)
    print('GLS-BD cards:',len(cards))
    for code,name in cards: add(code,name,'Community & Social','BD','https://grouplinkshare.com/bangladesh-whatsapp-group-links/')
    print('total now:',len(cands))
except Exception as e: print('GLS err',e)

# WTG jobs retry (redirect target)
for u in ['https://wtgrouplinks.com/job-whatsapp-group-links/','https://wtgrouplinks.com/jobs-whatsapp-group-links/']:
    try:
        r=requests.get(u,headers=UA,timeout=25)
        rows=re.findall(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text, re.S)
        print('WTG',u,r.status_code,'rows',len(rows))
        for name,code in rows: add(code,name,'Jobs','IN',u)
        print('total now:',len(cands))
        break
    except Exception as e: print('WTG err',u,e)

# grouplinks.app: collect group slugs from homepage + browse pages
slugs=set()
try:
    r=requests.get('https://www.grouplinks.app/',headers=UA,timeout=25)
    slugs |= set(re.findall(r'href="/group/([a-z0-9\-]+)"', r.text))
    print('grouplinks.app homepage slugs:',len(slugs))
    for cat in ['whatsapp','telegram']:
        try:
            r=requests.get(f'https://www.grouplinks.app/{cat}',headers=UA,timeout=25)
            slugs |= set(re.findall(r'href="/group/([a-z0-9\-]+)"', r.text))
            print(' after',cat,len(slugs))
        except Exception as e: print(' app cat err',e)
except Exception as e: print('app err',e)
print('total slugs:',len(slugs))
n=0
for s in sorted(slugs):
    try:
        r=requests.get(f'https://www.grouplinks.app/group/{s}',headers=UA,timeout=25)
        codes=re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text)
        if codes:
            m=re.search(r'<title>(.*?)</title>', r.text, re.S)
            title=clean(m.group(1)).replace(' - Group Links | Group Links','').replace(' - Group Links','') if m else s
            add(codes[0], title, 'Community & Social','International',f'https://www.grouplinks.app/group/{s}')
            n+=1
        time.sleep(0.25)
    except Exception as e: print(' app group err',s,e)
print('app groups with codes:',n,'total cands:',len(cands))
json.dump(cands, open(WAVE+'team17-scratch-cands.json','w'), ensure_ascii=False, indent=1)
print('SAVED',len(cands))
