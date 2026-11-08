import requests, re, time, json
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
def fetch(url, tries=6):
    s = requests.Session()
    for i in range(tries):
        try:
            r = s.get(url, headers=UA, timeout=60)
            if r.status_code == 200 and len(r.text) > 1000:
                return r.text
        except Exception as e:
            print("try", i, "fail", url, repr(e)[:100])
        time.sleep(5 * (i + 1))
    return None
pages = {
  "crypto": "https://www.grouplinksforyou.com/2023/04/cryptocurrency-whatsapp-group-links.html",
  "earning": "https://www.grouplinksforyou.com/2023/04/online-earning-whatsapp-group-link.html",
  "dubai": "https://www.grouplinksforyou.com/2023/04/dubai-whatsapp-group-links.html",
}
for name, url in pages.items():
    html = fetch(url)
    if html:
        open(f"_t06_{name}.html", "w").write(html)
        print(name, "saved", len(html))
    else:
        print(name, "FAILED")
