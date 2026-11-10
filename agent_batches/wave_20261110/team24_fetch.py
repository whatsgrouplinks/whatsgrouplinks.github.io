import urllib.request, gzip, io, re, json, time, ssl

UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept":"text/html,application/xml;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate","Accept-Language":"en-US,en;q=0.9"}

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        enc = r.headers.get('Content-Encoding','')
        if 'gzip' in enc:
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', errors='replace')

# 1. sitemap
sm = fetch("https://whtspgrouplink.com/post-sitemap.xml")
open("team24_post_sitemap.xml","w").write(sm)
urls = re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", sm)
print("post urls:", len(urls))
# also page sitemap
try:
    pg = fetch("https://whtspgrouplink.com/page-sitemap.xml")
    open("team24_page_sitemap.xml","w").write(pg)
    urls2 = re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", pg)
    print("page urls:", len(urls2))
    for u,d in urls2: print("PAGE", d, u)
except Exception as e:
    print("page sitemap err", e)
# sort posts by lastmod desc
urls.sort(key=lambda x: x[1], reverse=True)
for u,d in urls[:60]:
    print(d, u)
json.dump(urls, open("team24_sitemap_urls.json","w"), indent=1)
