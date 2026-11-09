import subprocess, re, json, os, html
WD = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WD, "team22_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PAGES = [
 ("movies_drama_whatz", "https://whatzgrouplink.com/movies-and-drama-whatsapp-group-link/"),
 ("ent_techpuran", "https://techpuran.in/best-entertainment-whatsapp-group-links/"),
 ("drama_newgrouplinks", "https://newgrouplinks.pk/pakistani-drama-whatsapp-group-links/"),
 ("music_whatsgroup_in", "https://www.whatsgroup.in/"),
 ("music_1000_whtsp", "https://whtspgrouplink.com/1000-members-whatsapp-group-links/"),
 ("memes_whatstele", "https://whatstele.com/whatsapp/group-links/memes-stickers/"),
 ("jokers_grouplink_in", "https://grouplink.com.in/1000-best-jokers-whatsapp-group-links/"),
 ("latest_whatz", "https://whatzgrouplink.com/latest-whatsapp-group-links/"),
 ("funny_logicalshout", "https://logicalshout.com/whatsapp-group-links/"),
 ("joinnchat_home", "https://joinnchat.com/"),
 ("groupjoin_netflix", "https://www.groupjoin.link/tag/netflix?limit=20&safeSearch=strict"),
 ("groupwa_gallery", "https://groupwa.link/groups-gallery/"),
 ("whtsp_home", "https://whtspgrouplink.com/"),
 ("whtsgrouplink_home", "https://whtsgrouplink.com/"),
]
def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","40","-A",UA,url], capture_output=True, text=True, timeout=60)
        return r.stdout or ""
    except Exception:
        return ""
all_codes = {}
for slug, url in PAGES:
    h = fetch(url)
    open(os.path.join(RAW, slug+".html"),"w",encoding="utf-8",errors="ignore").write(h)
    print(slug, len(h), flush=True)
    for m in re.finditer(r'<a[^>]*href=["\']https?://chat\.whatsapp\.com/([A-Za-z0-9_\-]+)[^"\']*["\'][^>]*>(.*?)</a>', h, re.S|re.I):
        code = m.group(1).strip()
        txt = re.sub(r'\s+',' ', html.unescape(re.sub(r'<[^>]+>','', m.group(2))).strip())
        if code and len(code)>=10:
            e = all_codes.setdefault(code, {"name_hint":"", "sources":[]})
            if txt and len(txt)>1 and len(txt)<80 and not e["name_hint"] and txt.lower() not in ("link","join","click here","join now","join chat","join group"):
                e["name_hint"]=txt
            if url not in e["sources"]: e["sources"].append(url)
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)', h):
        code=m.group(1).strip()
        if code and len(code)>=10 and code not in all_codes:
            all_codes[code]={"name_hint":"","sources":[url]}
print("TOTAL codes extracted:", len(all_codes))
json.dump(all_codes, open(os.path.join(WD,"team22_raw_codes2.json"),"w"), indent=1, ensure_ascii=False)
