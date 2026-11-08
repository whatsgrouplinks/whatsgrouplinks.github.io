import json, re, time, sys
sys.path.insert(0,'.')
from curlutil import fetch
from bs4 import BeautifulSoup
UA="x"
# 1) collect grupo links from homepage p4-6 (already fetched) + category pages
links=set(l.strip() for l in open('linkado_p456_links.txt') if l.strip())
for cat in ['amizade','trabalho','esportes','educacao']:
    html=fetch(f'https://linkado.app/categoria/{cat}')
    print('cat',cat,'ok' if html else 'FAIL', len(html) if html else 0, flush=True)
    if html:
        soup=BeautifulSoup(html,'html.parser')
        for a in soup.find_all('a',href=re.compile(r'^/grupo/[0-9a-f]{24}$')):
            links.add(a['href'])
    time.sleep(1)
print('total unique grupo links:',len(links), flush=True)
json.dump(sorted(links),open('linkado_links.json','w'))
# 2) fetch each detail page, extract Entrar href + title + desc
recs={}
for i,href in enumerate(sorted(links)):
    html=fetch(f'https://linkado.app{href}')
    if not html:
        recs[href]={'err':'fetch-fail'}; print(i,'FAIL',href, flush=True); continue
    soup=BeautifulSoup(html,'html.parser')
    t=soup.find('title')
    title=t.text.strip() if t else ''
    md=soup.find('meta',attrs={'name':'description'})
    desc=md['content'].strip() if md and md.get('content') else ''
    # Entrar no Grupo href: search RSC payload for href near 'Entrar no Grupo'
    m=re.search(r'"href":"(https://chat\.whatsapp\.com/[^"]+)"',html)
    code=''
    if m:
        cm=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',m.group(1))
        code=cm.group(1) if cm else ''
    # also any chat.whatsapp link anywhere
    allcodes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',html)
    other=None
    m2=re.search(r'Entrar no Grupo.{0,400}',html)
    recs[href]={'title':title,'desc':desc,'code':code,'allcodes':sorted(set(allcodes))}
    print(i,href,'code=',code,'|',title[:70], flush=True)
    time.sleep(0.5)
json.dump(recs,open('linkado_raw.json','w'),ensure_ascii=False,indent=1)
print('DONE',len(recs),'with code:',sum(1 for r in recs.values() if r.get('code')), flush=True)
