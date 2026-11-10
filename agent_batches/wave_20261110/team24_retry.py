import urllib.request, json, time, os
# identity encoding (no gzip) to dodge truncated gzip streams; salvage partial on IncompleteRead
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36","Accept":"text/html;q=0.9,*/*;q=0.8","Accept-Encoding":"identity"}
def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        partial = getattr(e, 'partial', None)
        if partial:
            try: return partial.decode('utf-8', errors='replace')
            except Exception: pass
        raise
targets = json.load(open("team24_sitemap_urls.json"))
pages = [(u,d) for u,d in targets[:30]]
pages.append(("https://whtspgrouplink.com/","2026-08-17"))
missing = []
for url, lastmod in pages:
    slug = url.rstrip('/').split('/')[-1] or 'home'
    fn = f"team24_raw/{slug}.html"
    if not os.path.exists(fn) or os.path.getsize(fn) < 50000:
        missing.append((slug, url))
print("missing:", [s for s,_ in missing], flush=True)
for slug, url in missing:
    ok=False
    for attempt in range(3):
        try:
            t0=time.time()
            page = fetch(url)
            open(f"team24_raw/{slug}.html","w").write(page)
            print(f"{slug}: {len(page)} bytes {time.time()-t0:.1f}s attempt {attempt+1}", flush=True)
            ok=True; break
        except Exception as e:
            print(f"{slug}: attempt {attempt+1} ERR {type(e).__name__} {e}", flush=True)
            time.sleep(3)
    if not ok: print(f"{slug}: FAILED all attempts", flush=True)
    time.sleep(1.0)
print("RETRY DONE")
