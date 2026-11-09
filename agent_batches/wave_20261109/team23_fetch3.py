import subprocess, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
urls = {
 "links77_islamic": "https://77links.com/islamic-whatsapp-group-links/",
 "links77_karachi": "https://77links.com/karachi-whatsapp-group-links/",
 "groupwa": "https://groupwa.link/",
 "whatgroups_news": "https://whatgroups.com/news-whatsapp-group-links/",
 "newgrouplinks_news": "https://newgrouplinks.pk/news-whatsapp-group-links/",
 "whtsp_main": "https://whtspgrouplink.com/",
}
for name, url in urls.items():
    out = f"team23_raw/{name}.html"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(name, "cached", os.path.getsize(out)); continue
    subprocess.run(["curl","-sL","--max-time","60","-A",UA,url,"-o",out], capture_output=True)
    print(name, os.path.getsize(out) if os.path.exists(out) else "MISSING")
