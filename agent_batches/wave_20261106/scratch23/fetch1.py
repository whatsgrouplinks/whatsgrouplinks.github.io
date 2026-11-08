import requests, re, json, os
S="~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch23"
S=os.path.expanduser(S)
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
def get(u,fn):
    try:
        r=requests.get(u,headers=UA,timeout=60)
        print(u, r.status_code, len(r.content))
        if r.status_code==200:
            open(os.path.join(S,fn),'w',encoding='utf-8').write(r.text)
        return r
    except Exception as e:
        print(u,"ERR",repr(e)[:120]); return None
r=get("https://groupda.com/category/dating/","gd_cat_dating.html")
if r is not None and r.status_code==200:
    t=r.text
    codes=sorted(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})',t)))
    print("codes on page:",len(codes),codes[:10])
    links=sorted(set(re.findall(r'href="(https://groupda\.com/[^"]+)"',t)))
    print("internal links:",len(links))
    for l in links[:60]: print(" ",l)
