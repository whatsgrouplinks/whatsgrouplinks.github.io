import requests, re, time, json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
urls=[
 "https://groupchatconnect.info/groupe/300",
 "https://groupchatconnect.info/groupe/310",
 "https://groupchatconnect.info/groupe/1450",
 "https://groupchatconnect.info/groupe/2386",
 "https://groupchatconnect.info/groupe/3397",
 "https://groupchatconnect.info/channel/3229",
 "https://groupchatconnect.info/channel/3283",
]
for u in urls:
    try:
        r=requests.get(u, headers=UA, timeout=25)
        html=r.text
        wa=re.findall(r'chat\.whatsapp\.com/[A-Za-z0-9_-]+', html)
        inv=re.findall(r'whatsapp\.com/invite/[A-Za-z0-9_-]+', html)
        tg=re.findall(r't\.me/[A-Za-z0-9_]+', html)
        title=re.search(r'<title>(.*?)</title>', html, re.S)
        print('---',u,'status',r.status_code,'len',len(html))
        print(' title:', (title.group(1).strip()[:150] if title else None))
        print(' wa links:', wa[:5], 'count', len(wa))
        print(' invite links:', inv[:5], 'count', len(inv))
        print(' t.me:', tg[:5], 'count', len(tg))
        # snippet of body text
        txt=re.sub(r'<[^>]+>',' ',html)
        txt=re.sub(r'\s+',' ',txt)
        print(' text snippet:', txt[:400])
    except Exception as e:
        print('---',u,'ERROR',repr(e))
    time.sleep(1)
