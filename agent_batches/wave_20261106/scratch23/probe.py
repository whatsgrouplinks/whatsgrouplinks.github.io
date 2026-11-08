import requests
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
def get(u):
    try:
        r=requests.get(u,headers=UA,timeout=60)
        print(u, r.status_code, len(r.content), r.url)
        return r
    except Exception as e:
        print(u,"ERR",repr(e)[:150]); return None
r=get("https://groupda.com/wp-sitemap.xml")
if r is not None: print(r.text[:2000])
