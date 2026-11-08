import json, re, sys, time
sys.path.insert(0,'.')
from curlutil import fetch
from bs4 import BeautifulSoup
cats=['amor','anime','chat','destacados','diversion','juegos','memes','mundial','musica','peliculas','rol','stickers']
links=set(json.load(open('tugrupo_links.json')))
for c in cats:
    html=fetch(f'https://tugrupo.online/whatsapp/{c}/')
    if not html: print(c,'FAIL',flush=True); continue
    soup=BeautifulSoup(html,'html.parser')
    ds=[a['href'] for a in soup.find_all('a',href=re.compile(r'^https://tugrupo\.online/whatsapp/[a-z\-]+/[a-z0-9\-]+/?$'))]
    print(c,len(ds),flush=True)
    links.update(ds)
    time.sleep(1)
print('total unique:',len(links),flush=True)
json.dump(sorted(links),open('tugrupo_links.json','w'))
