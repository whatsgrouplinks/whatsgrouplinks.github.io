import subprocess, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
urls = {
 "grouplink_buysell": "https://grouplink.com.in/2300-buy-sell-whatsapp-group-for-explosive-earnings/",
 "whatstele_yoga": "https://whatstele.com/whatsapp/group-links/yoga/",
 "whtsp_weightloss": "https://whtspgrouplink.com/tag/weight-whatsapp-group-link/",
 "whtsagrouplinks": "https://www.whtsagrouplinks.com/",
 "activewagroup_pk": "https://activewagroup.com/pakistani-whatsapp-group-links/",
 "whatsgroup_in": "https://www.whatsgroup.in/",
 "grouplink_intl": "https://grouplink.com.in/1300-international-whatsapp-group-link/",
}
for name, url in urls.items():
    out = f"team23_raw/{name}.html"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(name, "cached", os.path.getsize(out)); continue
    subprocess.run(["curl","-sL","--max-time","60","-A",UA,url,"-o",out], capture_output=True)
    print(name, os.path.getsize(out) if os.path.exists(out) else "MISSING")
