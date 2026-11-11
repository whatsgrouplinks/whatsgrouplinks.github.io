import json, re, subprocess, time, html, os, sys

WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# All listing pages from post-sitemap.xml (2026-11-11), minus channel-only pages
PAGES = [
 ("karachi","https://77links.com/karachi-whatsapp-group-links/","PK"),
 ("islamic","https://77links.com/islamic-whatsapp-group-links/","PK"),
 ("canada","https://77links.com/canada-whatsapp-group-links/","CA"),
 ("indonesia","https://77links.com/indonesia-whatsapp-group-links/","ID"),
 ("islamabad","https://77links.com/islamabad-whatsapp-group-links/","PK"),
 ("lahore","https://77links.com/lahore-whatsapp-group-links/","PK"),
 ("pakistan-cricket","https://77links.com/pakistan-cricket-whatsapp-group-links/","PK"),
 ("photo-editing","https://77links.com/photo-editing-whatsapp-group-links/","PK"),
 ("psl","https://77links.com/psl-whatsapp-group-links/","PK"),
 ("sri-lanka","https://77links.com/sri-lanka-whatsapp-group-links/","LK"),
 ("tamil","https://77links.com/tamil-whatsapp-group-links/",""),
 ("usa","https://77links.com/usa-whatsapp-group-links/","US"),
 ("arabic","https://77links.com/arabic-whatsapp-group-links/",""),
 ("dawateislami","https://77links.com/dawateislami-whatsapp-group-links/","PK"),
 ("madani-channel","https://77links.com/madani-channel-whatsapp-group-links/","PK"),
 ("quran","https://77links.com/quran-whatsapp-group-links/","PK"),
 ("ramadan","https://77links.com/ramadan-whatsapp-group-links/","PK"),
 ("educational","https://77links.com/educational-whatsapp-group-links/","PK"),
 ("entertainment","https://77links.com/entertainment-whatsapp-group-links/","PK"),
 ("jobs","https://77links.com/jobs-whatsapp-group-links/","PK"),
 ("news","https://77links.com/news-whatsapp-group-links/","PK"),
 ("poetry","https://77links.com/poetry-whatsapp-group-links/","PK"),
 ("romantic","https://77links.com/romantic-whatsapp-group-links/","PK"),
 ("status","https://77links.com/status-whatsapp-group-links/","PK"),
 ("gaming","https://77links.com/amazing-gaming-whatsapp-group-links/","PK"),
 ("anime","https://77links.com/anime-whatsapp-group-links/","PK"),
 ("balochistan","https://77links.com/balochistan-whatsapp-group-links/","PK"),
 ("buy-and-sell","https://77links.com/buy-and-sell-whatsapp-group-links/","PK"),
 ("cooking","https://77links.com/cooking-whatsapp-group-links/","PK"),
 ("courses-training","https://77links.com/courses-and-training-whatsapp-group-links/","PK"),
 ("cryptocurrency","https://77links.com/cryptocurrency-whatsapp-group-links/","PK"),
 ("digital-marketing","https://77links.com/digital-marketing-whatsapp-group-links/","PK"),
 ("english-learning","https://77links.com/english-learning-whatsapp-group-links/","PK"),
 ("fashion","https://77links.com/fashion-whatsapp-group-links/","PK"),
 ("forex-trading","https://77links.com/forex-trading-whatsapp-group-links/","PK"),
 ("freefire","https://77links.com/freefire-whatsapp-group-links/","PK"),
 ("friendship","https://77links.com/friendship-whatsapp-group-links/","PK"),
 ("funny-video","https://77links.com/funny-video-whatsapp-group-links/","PK"),
 ("general-knowledge","https://77links.com/general-knowledge-whatsapp-group-links/","PK"),
 ("graphic-design","https://77links.com/graphic-design-whatsapp-group-links/","PK"),
 ("drama","https://77links.com/indian-and-pakistani-drama-whatsapp-group-links/","PK"),
 ("international-business","https://77links.com/international-business-whatsapp-group-links/",""),
 ("kerala","https://77links.com/kerala-whatsapp-group-links/","IN"),
 ("kurulus-osman","https://77links.com/kurulus-osman-whatsapp-group-links/","PK"),
 ("malayalam","https://77links.com/malayalam-whatsapp-group-links/","IN"),
 ("marriage","https://77links.com/marriage-whatsapp-group-links/","PK"),
 ("movies","https://77links.com/movies-whatsapp-group-links/","PK"),
 ("music","https://77links.com/music-whatsapp-group-links/","PK"),
 ("novels","https://77links.com/novels-whatsapp-group-links/","PK"),
 ("online-earning","https://77links.com/online-earning-whatsapp-groups/","PK"),
 ("pakistan","https://77links.com/pakistan-whatsapp-group-links/","PK"),
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
 ("urdu","https://77links.com/urdu-whatsapp-group-links/","PK"),
 ("viral-tiktok","https://77links.com/viral-tiktok-whatsapp-group-links/","PK"),
 ("viral-video","https://77links.com/viral-video-whatsapp-group-links/","PK"),
 ("stickers","https://77links.com/whatsapp-stickers-group-links/","PK"),
 ("youtube","https://77links.com/youtube-whatsapp-group-links/","PK"),
 ("zambia","https://77links.com/zambia-whatsapp-group-links/","ZM"),
 ("cartoon","https://77links.com/cartoon-whatsapp-group-links/","PK"),
 ("class","https://77links.com/class-whatsapp-group-links/","PK"),
 ("hamster-kombat","https://77links.com/active-hamster-kombat-whatsapp-group/",""),
 ("all-groups","https://77links.com/all-whatsapp-groups/",""),
 ("pakistan-dating","https://77links.com/pakistan-dating-whatsapp-group/","PK"),
]

def curl(url, out):
    p=subprocess.run(["curl","-s","-A",UA,"--max-time","30","-o",out,"-w","%{http_code}",url],
                     capture_output=True,text=True,timeout=45)
    return p.stdout.strip()

def extract(fn):
    t=open(os.path.join(WD,fn),encoding='utf-8',errors='ignore').read()
    pat=re.compile(r'wp-block-columns[^>]*>.*?<p[^>]*>(.*?)</p>.*?href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', re.S)
    d={}
    for name,code in pat.findall(t):
        name=html.unescape(re.sub(r'<[^>]+>','',name))
        name=re.sub(r'\s+',' ',name).strip()
        d.setdefault(code,name)
    # fallback: any chat link not caught above
    for code in re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})', t):
        d.setdefault(code,"")
    return d

allc={}  # code -> {label, page, country}
fetch_log=[]
for slug,url,country in PAGES:
    fn=f"team14_page_{slug}.html"
    st=curl(url, os.path.join(WD,fn))
    if st!="200":
        fetch_log.append({"slug":slug,"url":url,"status":st,"codes":0})
        print(slug,"HTTP",st, flush=True); continue
    d=extract(fn)
    for code,label in d.items():
        if code not in allc:
            allc[code]={"label":label,"page":slug,"country":country,"url":url}
    fetch_log.append({"slug":slug,"url":url,"status":st,"codes":len(d)})
    print(slug,st,len(d), flush=True)
    time.sleep(0.3)

json.dump(allc, open(os.path.join(WD,"team14_all_extracted.json"),'w'), ensure_ascii=False, indent=1)
json.dump(fetch_log, open(os.path.join(WD,"team14_fetch_log.json"),'w'), indent=1)
print("TOTAL codes:", len(allc), flush=True)
