import requests, re, json, time
from html import unescape
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
def clean(s):
    s=unescape(re.sub(r'<[^>]+>','',s or '')).strip()
    return re.sub(r'\s+',' ',s).strip(' –-👉 ')
def add(code,name,cat,country,page):
    code=code.strip()
    if len(code)<20 or len(code)>24 or code in union: return
    name=clean(name)
    if not name: return
    if code not in cands: cands[code]={'name':name,'cat':cat,'country':country,'page':page}
    elif len(name)>len(cands[code]['name']): cands[code]['name']=name
wtg_pages=['https://wtgrouplinks.com/job-whatsapp-group-links/',
 'https://wtgrouplinks.com/12th-class-study-whatsapp-group-link/',
 'https://wtgrouplinks.com/marathi-whatsapp-group-link/',
 'https://wtgrouplinks.com/refer-and-earn-whatsapp-group-link/',
 'https://wtgrouplinks.com/education-news-whatsapp-group-link/']
for p in wtg_pages:
    slug=p.rstrip('/').split('/')[-1]
    cat='Community & Social'
    if 'job' in slug: cat='Jobs'
    elif 'study' in slug or 'education' in slug: cat='Education'
    elif 'refer' in slug or 'earn' in slug: cat='Online Earning'
    try:
        r=requests.get(p,headers=UA,timeout=25); time.sleep(0.3)
        lis=re.findall(r'<li[^>]*>(.*?)<a href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', r.text, re.S)
        for name,code in lis: add(code,name,cat,'IN',p)
        print(slug,'li-rows',len(lis),'total',len(cands))
    except Exception as e: print('err',p,e)
json.dump(cands, open(WAVE+'team17-scratch-cands.json','w'), ensure_ascii=False, indent=1)
print('SAVED',len(cands))
