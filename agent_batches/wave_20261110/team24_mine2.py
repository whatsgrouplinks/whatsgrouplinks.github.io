import urllib.request, gzip, json, time, os
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36","Accept":"text/html;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate"}
def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding',''): raw = gzip.decompress(raw)
        return raw.decode('utf-8', errors='replace')
targets = json.load(open("team24_sitemap_urls.json"))
pages = [(u,d) for u,d in targets[:30]]
pages.append(("https://whtspgrouplink.com/","2026-08-17"))
os.makedirs("team24_raw", exist_ok=True)
done = set(os.listdir("team24_raw"))
for url, lastmod in pages:
    slug = url.rstrip('/').split('/')[-1] or 'home'
    fn = f"{slug}.html"
    if fn in done:
        print("skip", slug, flush=True); continue
    try:
        t0=time.time()
        page = fetch(url)
        open(f"team24_raw/{fn}","w").write(page)
        print(f"{slug}: {len(page)} bytes {time.time()-t0:.1f}s", flush=True)
    except Exception as e:
        print(f"{slug}: FETCH ERR {e}", flush=True)
    time.sleep(1.0)
print("MINE2 DONE")
