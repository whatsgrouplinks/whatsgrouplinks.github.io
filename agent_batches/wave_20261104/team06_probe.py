import requests, re
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
s = requests.Session()
for url in [
  "https://www.grouplinksforyou.com/2023/04/cryptocurrency-whatsapp-group-links.html",
  "https://www.grouplinksforyou.com/2023/04/online-earning-whatsapp-group-link.html",
]:
    r = s.get(url, headers=UA, timeout=60)
    print(url, r.status_code, len(r.text))
    open(f"_probe_{url.split('/')[-1]}.html","w").write(r.text)
