import json, re, sys, time, html
sys.path.insert(0,'.')
from curlutil import fetch
from bs4 import BeautifulSoup
links=json.load(open('tugrupo_links.json'))
recs={}
try: recs=json.load(open('tugrupo_raw.json'))
except Exception: pass
for i,u in enumerate(sorted(links)):
    if u in recs and recs[u].get('code'): continue
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
        # category from URL path segment
        m=re.match(r'https://tugrupo\.online/whatsapp/([a-z\-]+)/',u)
        cat=m.group(1) if m else ''
        recs[u]={'title':title,'desc':desc,'code':codes[0] if codes else '','allcodes':sorted(set(codes)),'cat':cat}
        print(i,u,'code=',recs[u]['code'],'|',title[:60],flush=True)
    json.dump(recs,open('tugrupo_raw.json','w'),ensure_ascii=False,indent=1)
    time.sleep(0.5)
print('DONE',len(recs),'with code:',sum(1 for r in recs.values() if r.get('code')),flush=True)
