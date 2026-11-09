import subprocess, re, json, os, html
WD = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WD, "team22_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PAGES = [
 ("cricket_whatgroups", "https://whatgroups.com/cricket-whatsapp-group-links/"),
 ("cricket_newgrouplinks", "https://newgrouplinks.pk/cricket-whatsapp-group-links/"),
 ("movies_whtsa", "https://www.whtsagrouplinks.com/movies-whatsapp-group-link/"),
 ("sports_whtsa", "https://www.whtsagrouplinks.com/sports-whatsapp-group-links/"),
 ("ent_wahublink", "https://wahublink.com/entertainment-whatsapp-group-links/"),
 ("sports_wahublink", "https://wahublink.com/sports-whatsapp-group-links/"),
 ("sports_grouplink_in", "https://grouplink.com.in/active-sports-whatsapp-group-links-2026/"),
 ("football_appgrouplink", "https://appgrouplink.com/football-whatsapp-group-links/"),
 ("viral_techpuran", "https://techpuran.in/indian-viral-video-whatsapp-group-link-join/"),
 ("messi_wagrouplinks", "https://wagrouplinks.net/lionel-messi-fans-whatsapp-group-links/"),
 ("movies_whatgroups_home", "https://whatgroups.com/"),
 ("sports_wagroupshub", "https://wagroupshub.com/sports-whatsapp-group-links/"),
 ("pakistani_whtsa", "https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/"),
 ("entertainment_whatgroups", "https://whatgroups.com/entertainment-whatsapp-group-links/"),
]
def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","40","-A",UA,url], capture_output=True, text=True, timeout=60)
        return r.stdout or ""
    except Exception as e:
        return ""
all_codes = {}  # code -> {name_hint, sources[]}
for slug, url in PAGES:
    h = fetch(url)
    fn = os.path.join(RAW, slug+".html")
    open(fn,"w",encoding="utf-8",errors="ignore").write(h)
    print(slug, len(h))
    # anchor-based extraction
    for m in re.finditer(r'<a[^>]*href=["\']https?://chat\.whatsapp\.com/([A-Za-z0-9_\-]+)[^"\']*["\'][^>]*>(.*?)</a>', h, re.S|re.I):
        code = m.group(1).strip()
        txt = re.sub(r'<[^>]+>','', m.group(2))
        txt = html.unescape(txt).strip()
        txt = re.sub(r'\s+',' ',txt)
        if code and len(code)>=10:
            e = all_codes.setdefault(code, {"name_hint":"", "sources":[]})
            if txt and len(txt)>1 and len(txt)<80 and not e["name_hint"]:
                e["name_hint"]=txt
            if url not in e["sources"]: e["sources"].append(url)
    # bare codes not in anchors
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)', h):
        code=m.group(1).strip()
        if code and len(code)>=10 and code not in all_codes:
            all_codes[code]={"name_hint":"","sources":[url]}
print("TOTAL codes extracted:", len(all_codes))
json.dump(all_codes, open(os.path.join(WD,"team22_raw_codes.json"),"w"), indent=1, ensure_ascii=False)
