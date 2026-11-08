import json, re, sys, time, html
sys.path.insert(0,'.')
from curlutil import fetch
from bs4 import BeautifulSoup
links=json.load(open('tugrupo_links.json'))
recs=json.load(open('tugrupo_raw.json'))
missing=[u for u in links if u not in recs and '/mundial/' not in u]
print('to fetch:',len(missing),flush=True)
for i,u in enumerate(sorted(missing)):
    htmltxt=fetch(u)
    if not htmltxt:
        recs[u]={'err':'fetch-fail'}; print(i,'FAIL',u,flush=True)
    else:
        soup=BeautifulSoup(htmltxt,'html.parser')
        t=soup.find('title')
        title=html.unescape(t.text.strip()) if t else ''
        md=soup.find('meta',attrs={'name':'description'})
        desc=html.unescape(md['content'].strip()) if md and md.get('content') else ''
        codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',htmltxt)
        m=re.match(r'https://tugrupo\.online/whatsapp/([a-z\-]+)/',u)
        recs[u]={'title':title,'desc':desc,'code':codes[0] if codes else '','allcodes':sorted(set(codes)),'cat':m.group(1) if m else ''}
        print(i,u,'code=',recs[u]['code'],'|',title[:60],flush=True)
    json.dump(recs,open('tugrupo_raw.json','w'),ensure_ascii=False,indent=1)
    time.sleep(0.5)
print('DONE total',len(recs),'with code:',sum(1 for r in recs.values() if r.get('code')),flush=True)
