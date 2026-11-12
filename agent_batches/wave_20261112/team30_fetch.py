#!/usr/bin/env python3
"""TEAM30 fetch: 13 leads (wave 20261111 team25) + whatslinky (29) + pkwhatsgrouplinks (7) + whtsgrouplink category discovery."""
import json, os, re, time, requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SCRATCH = os.path.join(WAVE, "team30_scratch")
os.makedirs(SCRATCH, exist_ok=True)

URLS_20261111 = [
 "https://www.imagesplatform.com/add-whatsapp-group-link",
 "https://wagroupslink.com/whatsapp-group-links/",
 "https://wagroupslink.com/private-whatsapp-group-links/",
 "https://wagroupzone.com/girls-whatsapp-group-links/",
 "https://wahublink.com/boys-whatsapp-group-links/",
 "https://wahublink.com/youtube-whatsapp-group-links/",
 "https://wahublink.com/visa-travel-whatsapp-group-links/",
 "https://wahublink.com/desi-girls-whatsapp-group-links/",
 "https://newgrouplinks.pk/college-girls-whatsapp-group-links/",
 "https://newgrouplinks.pk/pakistani-girls-whatsapp-group-links/",
 "https://newgrouplinks.pk/school-girls-whatsapp-group-links/",
 "https://newgrouplinks.pk/category/all-groups/",
 "https://whtsgrouplink.com/",
]
URLS_20261110 = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team25-newdirs-southasia-leads.json"))
URLS_20261110 = [e["url"] for e in URLS_20261110 if "whatslinky.com" in e["url"] or "pkwhatsgrouplinks.com" in e["url"]]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def slug(u):
    s = re.sub(r"https?://", "", u).strip("/").replace("/", "_")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)[:120]

def fetch(url, session):
    fn = os.path.join(SCRATCH, slug(url) + ".html")
    if os.path.exists(fn) and os.path.getsize(fn) > 1000:
        return fn, "cached", os.path.getsize(fn)
    try:
        r = session.get(url, headers=UA, timeout=60)
        open(fn, "w", encoding="utf-8", errors="ignore").write(r.text)
        return fn, r.status_code, len(r.text)
    except Exception as e:
        return fn, f"ERR {type(e).__name__}: {e}", 0

def main():
    s = requests.Session()
    jobs = []
    all_urls = URLS_20261111 + URLS_20261110
    for u in all_urls:
        fn, st, n = fetch(u, s)
        print(u, "->", st, n, flush=True)
        jobs.append({"url": u, "file": fn, "status": st, "size": n})
        time.sleep(1)
    # discover whtsgrouplink category sub-pages from homepage html
    home = os.path.join(SCRATCH, slug("https://whtsgrouplink.com/") + ".html")
    extra = []
    if os.path.exists(home):
        html = open(home, encoding="utf-8", errors="ignore").read()
        links = sorted(set(re.findall(r'href="(https://whtsgrouplink\.com/[^"]+)"', html)))
        for L in links:
            if any(k in L for k in ("category", "whatsapp-group", "girls", "boys", "jobs", "entertainment", "sports", "funny", "islamic", "education", "news", "movies", "friendship", "pakistani", "indian", "college", "school", "youtube", "crypto", "business")):
                if L.rstrip("/") != "https://whtsgrouplink.com":
                    extra.append(L)
        print("whtsgrouplink discovered:", extra, flush=True)
        for u in extra:
            fn, st, n = fetch(u, s)
            print(u, "->", st, n, flush=True)
            jobs.append({"url": u, "file": fn, "status": st, "size": n})
            time.sleep(1)
    json.dump({"jobs": jobs, "whtsgrouplink_extra": extra}, open(os.path.join(SCRATCH, "fetch_jobs.json"), "w"), indent=1)
    print("DONE", len(jobs), "pages")

if __name__ == "__main__":
    main()
