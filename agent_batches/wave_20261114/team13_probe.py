import requests, re, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'es-ES,es;q=0.9,en;q=0.8'}
s=requests.Session(); s.headers.update(UA)
for url in ['https://tugrupo.online/whatsapp/','https://tugrupo.online/whatsapp/?query-eb715b85=4','https://tugrupo.online/whatsapp/?query-eb715b85=11']:
    try:
        r=s.get(url,timeout=60)
        print('===',url,'->',r.status_code,'len',len(r.text),'final',r.url)
        open('team13_probe_%s.html'%url.split('=')[-1].replace('/','_'),'w').write(r.text)
        print(r.text[:600].replace('\n',' ')[:600])
    except Exception as e:
        print('===',url,'ERR',repr(e))
    time.sleep(3)
