import requests, re, json, html, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
t=open('/tmp/linkado_sitemap.xml').read()
locs=re.findall(r'<loc>(https://linkado\.app/grupo/[0-9a-f]+)</loc>',t)
print('grupo urls',len(locs))
sample=locs[::400]  # ~49 pages spread across sitemap
print('sample',len(sample))
out={}
for u in sample:
    try:
        r=requests.get(u,headers=UA,timeout=40)
        codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})\b',r.text)
        title=re.search(r'<title>([^<]*)</title>',r.text)
        h1=re.search(r'<h1[^>]*>([^<]*)</h1>',r.text)
        name=(h1.group(1).strip() if h1 else (title.group(1).strip() if title else ''))
        print(u,'->',r.status_code,'codes',list(set(codes)),'name:',name[:70],flush=True)
        for c in set(codes):
            out[c]={'name':html.unescape(name),'url':u,'desc':''}
    except Exception as e:
        print(u,'ERR',str(e)[:100],flush=True)
    time.sleep(1.5)
json.dump(out,open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team01-linkado-raw.json','w'),ensure_ascii=False,indent=1)
print('LINKADO DONE',len(out),flush=True)
