import json, re, subprocess, time, html, os
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PAGES=[
 ("karachi","https://77links.com/karachi-whatsapp-group-links/","PK"),
 ("islamic","https://77links.com/islamic-whatsapp-group-links/","PK"),
 ("kurulus-osman","https://77links.com/kurulus-osman-whatsapp-group-links/","PK"),
 ("malayalam","https://77links.com/malayalam-whatsapp-group-links/","IN"),
 ("marriage","https://77links.com/marriage-whatsapp-group-links/","PK"),
 ("online-earning","https://77links.com/online-earning-whatsapp-groups/","PK"),
 ("pdf-books","https://77links.com/pdf-books-whatsapp-group-links/","PK"),
 ("pti","https://77links.com/pti-whatsapp-group-links/","PK"),
 ("pubg","https://77links.com/pubg-whatsapp-group-links/","PK"),
]
def curl(url,out):
    p=subprocess.run(["curl","-s","-A",UA,"--max-time","60","-o",out,"-w","%{http_code}",url],capture_output=True,text=True,timeout=75)
    return p.stdout.strip()
def extract(fn):
    t=open(os.path.join(WD,fn),encoding='utf-8',errors='ignore').read()
    pat=re.compile(r'wp-block-columns[^>]*>.*?<p[^>]*>(.*?)</p>.*?href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', re.S)
    d={}
    for name,code in pat.findall(t):
        name=html.unescape(re.sub(r'<[^>]+>','',name))
        name=re.sub(r'\s+',' ',name).strip()
        d.setdefault(code,name)
    for code in re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})', t):
        d.setdefault(code,"")
    return d
allc={}
fetch_log=[]
for slug,url,country in PAGES:
    fn=f"team20_page_{slug}.html"
    st="000"
    for attempt in range(3):
        st=curl(url, os.path.join(WD,fn))
        if st=="200": break
        print(slug,"attempt",attempt+1,"HTTP",st,flush=True)
        time.sleep(5)
    if st!="200":
        fetch_log.append({"slug":slug,"url":url,"status":st,"codes":0})
        print(slug,"FAILED HTTP",st,flush=True); continue
    d=extract(fn)
    for code,label in d.items():
        if code not in allc:
            allc[code]={"label":label,"page":slug,"country":country,"url":url}
    fetch_log.append({"slug":slug,"url":url,"status":st,"codes":len(d)})
    print(slug,st,len(d),flush=True)
    time.sleep(0.5)
json.dump(allc, open(os.path.join(WD,"team20_all_extracted.json"),'w'), ensure_ascii=False, indent=1)
json.dump(fetch_log, open(os.path.join(WD,"team20_fetch_log.json"),'w'), indent=1)
print("TOTAL codes:",len(allc),flush=True)
