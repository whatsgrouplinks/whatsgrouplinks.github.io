import re, subprocess, json, os, sys
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
urls = {
 "whatgroups_islamic": "https://whatgroups.com/islamic-whatsapp-group-link/",
 "whatgroups_quran": "https://whatgroups.com/online-quran-students-whatsapp-group-links/",
 "links77_quran": "https://77links.com/quran-whatsapp-group-links/",
 "whatzgrouplink_pk_islamic": "https://whatzgrouplink.com/pakistani-islamic-whatsapp-group-link/",
 "meraonline_islamic": "https://meraonlineworld.com/latest-islamic-whatsapp-group-links/",
 "sociallykeeda_pk": "https://www.sociallykeeda.com/pakistani-whatsapp-group/",
 "grouplinksforyou_dubai": "https://www.grouplinksforyou.com/2023/04/dubai-whatsapp-group-links.html",
 "navsari": "https://thewhatspgrouplinks.com/navsari-whatsapp-group-links/",
}
for name, url in urls.items():
    out = f"team23_raw/{name}.html"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(name, "cached", os.path.getsize(out)); continue
    r = subprocess.run(["curl","-sL","--max-time","60","-A",UA,url,"-o",out], capture_output=True, text=True)
    print(name, os.path.getsize(out) if os.path.exists(out) else "MISSING")
