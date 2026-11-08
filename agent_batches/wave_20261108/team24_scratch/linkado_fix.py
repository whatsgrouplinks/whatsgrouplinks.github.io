import json, re, sys, time
sys.path.insert(0,'.')
from curlutil import fetch
d=json.load(open('linkado_raw.json'))
multi=[k for k,v in d.items() if len(v.get('allcodes',[]))>1]
spot=[k for k,v in d.items() if len(v.get('allcodes',[]))==1][:3]
def entrar_code(html):
    # find 'Entrar no Grupo' and look backwards for the nearest href
    idx=html.find('Entrar no Grupo')
    if idx<0: return ''
    seg=html[max(0,idx-1200):idx]
    hrefs=re.findall(r'href\\*":\\*"?(https://chat\.whatsapp\.com/[A-Za-z0-9_\-]+)',seg)
    hrefs+=re.findall(r'href="(https://chat\.whatsapp\.com/[A-Za-z0-9_\-]+)"',seg)
    hrefs+=re.findall(r'href\\":\\"https://chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',seg)
    if not hrefs:
        # last chat.whatsapp code before Entrar
        codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',seg)
        return codes[-1] if codes else ''
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',hrefs[-1])
    return m.group(1) if m else ''
out={}
for u in multi+spot:
    htmltxt=fetch('https://linkado.app'+u)
    code=entrar_code(htmltxt) if htmltxt else ''
    out[u]={'entrar':code,'allcodes':d[u]['allcodes'],'title':d[u]['title']}
    print(u,'entrar=',code,'allcodes=',d[u]['allcodes'],flush=True)
    time.sleep(0.6)
json.dump(out,open('linkado_entrar_check.json','w'),ensure_ascii=False,indent=1)
