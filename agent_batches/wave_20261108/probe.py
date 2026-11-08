import requests, re, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
urls=[
 "https://linkado.app/sitemap.xml",
 "https://grupbul.com/en/category/whatsapp/5/game-groups",
 "https://groupsinvite.link/",
 "https://groupsinvite.link/group/education/",
 "https://whatsappkanali.com/sehir/tekirdag/sohbet",
 "https://gruposdewats.com/",
 "https://www.whatshub.es/",
 "https://losgrupos.app/grupos",
 "https://groupsinvite.link/add-group-link/",
]
for u in urls:
    try:
        r=requests.get(u,headers=UA,timeout=25)
        codes=len(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})',r.text)))
        print(u,'->',r.status_code,'len',len(r.text),'codes',codes,'final',r.url)
    except Exception as e:
        print(u,'-> ERR',type(e).__name__,str(e)[:120])
    time.sleep(1)
