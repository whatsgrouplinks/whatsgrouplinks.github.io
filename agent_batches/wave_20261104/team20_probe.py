import requests, re, json, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
s = requests.Session()
s.headers.update(UA)

urls = {
  "whatgroups-pk": "https://whatgroups.com/whatsapp-group-links-pakistan/",
  "whatgroups-bd": "https://whatgroups.com/bangladesh-whatsapp-group-links/",
  "whatz-bd": "https://whatzgrouplink.com/bangladesh-whatsapp-group-link/",
  "wahublink": "https://wahublink.com/",
  "wagroup-lk": "https://wagroup.in/tag/lanka-whatsapp-groups/",
  "glfy-country": "https://www.grouplinksforyou.com/search/label/Country?&max-results=5",
  "fortress": "http://fortress786.blogspot.com/2026/10/whatsapp-group-links-available.html",
}

CODE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
for key, u in urls.items():
    try:
        r = s.get(u, timeout=50, allow_redirects=True)
        codes = CODE.findall(r.text)
        uniq = sorted(set(codes))
        # also check for codes hidden behind shorteners/redirect params
        short = re.findall(r'(?:join-chat|click|goto|out|redirect)[^"\']*?chat\.whatsapp\.com[^"\']*', r.text)
        print(f"[{key}] status={r.status_code} len={len(r.text)} codes={len(codes)} uniq={len(uniq)} shortener-links={len(short)}")
        if uniq:
            print("   sample:", uniq[:5])
        # save page for later analysis
        open(f"team20_probe_{key}.html","w").write(r.text)
    except Exception as e:
        print(f"[{key}] ERROR {type(e).__name__}: {e}")
