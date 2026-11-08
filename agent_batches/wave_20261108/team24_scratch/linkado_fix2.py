import json, re, sys, time
sys.path.insert(0,'.')
from curlutil import fetch
d=json.load(open('linkado_raw.json'))
multi=[k for k,v in d.items() if len(v.get('allcodes',[]))>1]
spot=[k for k,v in d.items() if len(v.get('allcodes',[]))==1][:3]
def entrar_code(html):
    noscript=re.sub(r'<script.*?</script>','',html,flags=re.S)
    for m in re.finditer(r'<a[^>]*href="(https://chat\.whatsapp\.com/[A-Za-z0-9_\-]+)"[^>]*>(.*?)</a>', noscript, re.S):
        txt=re.sub(r'<[^>]+>','',m.group(2)).strip()
        if 'Entrar no Grupo' in txt:
            return re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)',m.group(1)).group(1)
    return ''
out={}
for u in multi+spot:
    htmltxt=fetch('https://linkado.app'+u)
    code=entrar_code(htmltxt) if htmltxt else ''
    out[u]={'entrar':code,'allcodes':d[u]['allcodes'],'title':d[u]['title']}
    print(u,'entrar=',code,'allcodes=',d[u]['allcodes'],flush=True)
    time.sleep(0.6)
json.dump(out,open('linkado_entrar_check.json','w'),ensure_ascii=False,indent=1)
