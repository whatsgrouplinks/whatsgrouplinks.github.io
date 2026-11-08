import requests, re, json
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
domains = [
  "https://whatzclub.com/",
  "https://whatgrouplinks.com/",
  "https://groupswp.com/",
  "https://newgrouplink.com/",
  "https://whatgrouplink.com/",
  "https://whatsgrouplink.com/",
  "https://realgrouplinks.com/",
  "https://wagrouplink.com/",
  "https://groupsjoin.com/",
  "https://wishthisyear.com/",
  "https://grouplinksor.com/",
  "https://groupsgyani.com/",
  "https://invitelinks.com/",
  "https://findgroups.net/",
  "https://whatsappgroupinviteslink.blogspot.com/",
  "https://globalwpgroups.com/",
  "https://bestwhatsappgrouplink.com/",
  "https://activewpgroups.com/",
  "https://groupouts.com/",
  "https://globylink.com/",
]
kw = ["turkey","turkish","kazakhstan","uzbekistan","kyrgyzstan","turkmenistan","tajikistan","istanbul","turkiye","turkiya","azerbaijan"]
def probe(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=25, allow_redirects=True)
        html = r.text
        codes = set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', html))
        hits = sorted(set(k for k in kw if k in html.lower()))
        title = re.search(r'<title>(.*?)</title>', html, re.I|re.S)
        return {"url":url,"final":r.url,"status":r.status_code,"len":len(html),
                "codes":len(codes),"kw":hits,"title":(title.group(1)[:90] if title else "")}
    except Exception as e:
        return {"url":url,"error":str(e)[:100]}
with ThreadPoolExecutor(max_workers=20) as ex:
    res = list(ex.map(probe, domains))
print(json.dumps(res, indent=1))
