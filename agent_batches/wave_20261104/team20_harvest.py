import requests, re, json, html, time
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
CODE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

def fetch(url):
    s = requests.Session(); s.headers.update(UA)
    try:
        r = s.get(url, timeout=55, allow_redirects=True)
        return (url, r.status_code, r.text, None)
    except Exception as e:
        return (url, None, "", type(e).__name__)

urls = {
 "wg-pk": "https://whatgroups.com/whatsapp-group-links-pakistan/",
 "wg-bd": "https://whatgroups.com/bangladesh-whatsapp-group-links/",
 "wahu-pk": "https://wahublink.com/pakistani-whatsapp-group-links/",
 "wahu-in": "https://wahublink.com/indian-whatsapp-group-links/",
}
with ThreadPoolExecutor(max_workers=4) as ex:
    res = dict((u[0], u) for u in ex.map(fetch, urls.values()))
for key, url in urls.items():
    u, st, text, err = res[url]
    codes = sorted(set(CODE.findall(text))) if text else []
    print(f"[{key}] status={st} len={len(text)} codes={len(codes)} err={err}", flush=True)
    if codes:
        print("   " + ",".join(codes[:8]), flush=True)
print("HARVEST-DONE", flush=True)
