import json, re, time, sys
sys.path.insert(0,'.')
from curlutil import fetch, fetch_headers, verify
from bs4 import BeautifulSoup
union=set(json.load(open('../dedupe_union.json')))
ADULT=['hentai','dildo','fantasia','porno','xxx','sexo','caliente','puta','tetas','culo','pene','verga','+18','18+','adultos','erotic','onlyfans','nudes','desnudo','cachondo','trio','swinger']
def is_adult(t):
    t=t.lower(); return any(w in t for w in ADULT)
groups={}
for page in [1,2]:
    html=fetch(f'https://losgrupos.app/grupos?page={page}&sort=newest')
    print('listing p',page,'ok' if html else 'FAIL',len(html) if html else 0, flush=True)
    if not html: continue
    soup=BeautifulSoup(html,'html.parser')
    for a in soup.find_all('a',href=re.compile(r'^/grupo/\d+-')):
        m=re.match(r'/grupo/(\d+)-(.+)',a['href'])
        if m: groups[m.group(1)]={'id':m.group(1),'slug':m.group(2),'url':'https://losgrupos.app'+a['href']}
print('listing groups:',len(groups), flush=True)
for gid,g in list(groups.items()):
    html=fetch(g['url'])
    if html:
        soup=BeautifulSoup(html,'html.parser')
        t=soup.find('title')
        g['name']=(t.text.split(' - ')[0].strip() if t else g['slug'])
        md=soup.find('meta',attrs={'name':'description'})
        g['desc']=md['content'].strip() if md and md.get('content') else ''
        cat=soup.find('a',href=re.compile(r'^/categoria/'))
        g['cat_raw']=cat.text.strip() if cat else ''
    time.sleep(0.3)
    print(gid,g.get('name'),'|',g.get('cat_raw'), flush=True)
json.dump(groups,open('losgrupos_raw.json','w'),ensure_ascii=False,indent=1)
for gid,g in groups.items():
    if is_adult(g.get('name','')+' '+g.get('slug','')+' '+g.get('cat_raw','')+' '+g.get('desc','')):
        g['skip']='adult'; continue
    st,loc=fetch_headers(f'https://losgrupos.app/grupo/{gid}/join')
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',loc)
    g['code']=m.group(1) if m else ''
    g['join_status']=st
    time.sleep(0.4)
    print(gid,'code=',g.get('code'),'in_union=',(g.get('code') in union) if g.get('code') else '-', flush=True)
json.dump(groups,open('losgrupos_raw.json','w'),ensure_ascii=False,indent=1)
fresh=[g for g in groups.values() if g.get('code') and g['code'] not in union]
print('FRESH codes:',len(fresh), flush=True)
for g in fresh:
    st,info=verify(g['code'])
    g['verify']=st; g['ogtitle']=info
    print(g['id'],g['code'],st,info, flush=True)
    time.sleep(0.6)
json.dump(groups,open('losgrupos_raw.json','w'),ensure_ascii=False,indent=1)
print('DONE live:',sum(1 for g in fresh if g.get('verify')=='live'),'transport:',sum(1 for g in fresh if g.get('verify')=='transport'), flush=True)
