import json, re, subprocess, time, html, os

WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

PAGES = [
 ("english-learning","https://77links.com/english-learning-whatsapp-group-links/","PK"),
 ("funny-video","https://77links.com/funny-video-whatsapp-group-links/","PK"),
 ("graphic-design","https://77links.com/graphic-design-whatsapp-group-links/","PK"),
 ("drama","https://77links.com/indian-and-pakistani-drama-whatsapp-group-links/","PK"),
 ("kerala","https://77links.com/kerala-whatsapp-group-links/","IN"),
 ("kurulus-osman","https://77links.com/kurulus-osman-whatsapp-group-links/","PK"),
 ("malayalam","https://77links.com/malayalam-whatsapp-group-links/","IN"),
 ("marriage","https://77links.com/marriage-whatsapp-group-links/","PK"),
 ("music","https://77links.com/music-whatsapp-group-links/","PK"),
 ("novels","https://77links.com/novels-whatsapp-group-links/","PK"),
 ("online-earning","https://77links.com/online-earning-whatsapp-groups/","PK"),
 ("pdf-books","https://77links.com/pdf-books-whatsapp-group-links/","PK"),
 ("pti","https://77links.com/pti-whatsapp-group-links/","PK"),
 ("pubg","https://77links.com/pubg-whatsapp-group-links/","PK"),
 ("rawalpindi","https://77links.com/rawalpindi-whatsapp-group-links/","PK"),
 ("real-estate","https://77links.com/real-estate-whatsapp-group-links/","PK"),
 ("science-technology","https://77links.com/science-and-technology-whatsapp-group-links/","PK"),
 ("shopping","https://77links.com/shopping-whatsapp-group-links/","PK"),
 ("sindhi","https://77links.com/sindhi-whatsapp-group-links/","PK"),
 ("students","https://77links.com/students-whatsapp-group-links/","PK"),
 ("sub4sub","https://77links.com/sub4sub-whatsapp-group-links/","PK"),
 ("tlp","https://77links.com/tlp-whatsapp-group-links/","PK"),
 ("turkish","https://77links.com/turkish-whatsapp-group-links/","TR"),
 ("viral-tiktok","https://77links.com/viral-tiktok-whatsapp-group-links/","PK"),
 ("stickers","https://77links.com/whatsapp-stickers-group-links/","PK"),
 ("youtube","https://77links.com/youtube-whatsapp-group-links/","PK"),
 ("zambia","https://77links.com/zambia-whatsapp-group-links/","ZM"),
 ("class","https://77links.com/class-whatsapp-group-links/","PK"),
]

def curl(url, out):
    p=subprocess.run(["curl","-s","-A",UA,"--max-time","45","-o",out,"-w","%{http_code}",url],
                     capture_output=True,text=True,timeout=60)
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

allc=json.load(open(os.path.join(WD,"team14_all_extracted.json")))
log=json.load(open(os.path.join(WD,"team14_fetch_log.json")))
for slug,url,country in PAGES:
    fn=f"team14_page_{slug}.html"
    st=curl(url, os.path.join(WD,fn))
    if st!="200":
        print(slug,"HTTP",st, flush=True)
        log.append({"slug":slug,"url":url,"status":st,"codes":0,"retry":2})
        continue
    d=extract(fn)
    for code,label in d.items():
        if code not in allc:
            allc[code]={"label":label,"page":slug,"country":country,"url":url}
    log.append({"slug":slug,"url":url,"status":st,"codes":len(d),"retry":2})
    print(slug,st,len(d), flush=True)
    time.sleep(1.5)

json.dump(allc, open(os.path.join(WD,"team14_all_extracted.json"),'w'), ensure_ascii=False, indent=1)
json.dump(log, open(os.path.join(WD,"team14_fetch_log.json"),'w'), indent=1)
print("TOTAL codes:", len(allc), flush=True)
