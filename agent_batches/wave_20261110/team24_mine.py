import urllib.request, gzip, re, json, time, html as htmllib, os

UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36","Accept":"text/html;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate"}
def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding',''): raw = gzip.decompress(raw)
        return raw.decode('utf-8', errors='replace')

targets = json.load(open("team24_sitemap_urls.json"))  # list of [url,lastmod] sorted desc
pages = [(u,d) for u,d in targets[:30]]
pages.append(("https://whtspgrouplink.com/","2026-08-17"))
os.makedirs("team24_raw", exist_ok=True)
cands = []  # {name, code, source}
seen_codes = set()
for url, lastmod in pages:
    slug = url.rstrip('/').split('/')[-1] or 'home'
    try:
        t0=time.time()
        page = fetch(url)
        dt=time.time()-t0
        open(f"team24_raw/{slug}.html","w").write(page)
        # extract li items with chat links
        n=0
        for li in re.findall(r"<li[^>]*>(.*?)</li>", page, flags=re.S|re.I):
            m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', li)
            if not m: continue
            code = m.group(1)
            if 'whatsapp.com/channel' in li: continue
            name_html = li[:m.start()].strip()
            name = re.sub(r'<[^>]+>', '', name_html)
            name = htmllib.unescape(name)
            name = re.sub(r'\s+', ' ', name).strip(' \t-–—|')
            if code in seen_codes: continue
            seen_codes.add(code)
            cands.append({"name":name,"code":code,"source":url,"lastmod":lastmod})
            n+=1
        print(f"{slug}: {len(page)} bytes {dt:.1f}s -> {n} codes", flush=True)
    except Exception as e:
        print(f"{slug}: FETCH ERR {e}", flush=True)
    time.sleep(1.0)
json.dump(cands, open("team24_candidates_raw.json","w"), indent=1, ensure_ascii=False)
print("TOTAL candidates:", len(cands))
