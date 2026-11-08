import requests, re, json
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))
for sm in ["https://grouplink.com.in/sitemap_index.xml","https://grouplink.com.in/sitemap.xml",
            "https://whatsgroupslinkspk.com/sitemap.xml","https://groupsinvite.link/sitemap.xml",
            "https://newgrouplinks.pk/sitemap.xml","https://whgroups.link/sitemap.xml"]:
    try:
        r=requests.get(sm, headers=UA, timeout=25)
        print(sm, r.status_code, len(r.text))
        urls=re.findall(r'<loc>([^<]+)</loc>', r.text)
        print("  locs:", len(urls))
        for u in urls[:40]: print("   ", u)
    except Exception as e:
        print(sm, "ERR", e)
