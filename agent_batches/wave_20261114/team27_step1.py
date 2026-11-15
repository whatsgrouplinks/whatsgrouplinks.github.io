#!/usr/bin/env python3
"""team27 step1: controls + discover category pages."""
import requests, re, json, time, sys
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
S = requests.Session(); S.headers.update(UA)

def og_title(code):
    try:
        r = S.get(f"https://chat.whatsapp.com/{code}", timeout=75)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        return (m.group(1) if m else ""), r.status_code
    except Exception as e:
        return f"ERR:{e}", 0

print("CONTROL live:", og_title("KrDwdK8EIkB6vgauHg5M7N"))
print("CONTROL fab :", og_title("ZzZzZzZzZzZzZzZzZzZzZz"))

# discover homepages
for url in ["https://wahublink.com/", "https://wagroupshub.com/", "https://activewagroup.com/",
            "https://grouplink.com.in/", "https://newgrouplinks.pk/", "https://groupwa.link/",
            "https://wagroupslink.com/", "https://whatgroups.com/"]:
    try:
        r = S.get(url, timeout=60)
        hrefs = sorted(set(re.findall(r'href="([^"]+)"', r.text)))
        cats = [h for h in hrefs if any(k in h.lower() for k in ["whatsapp-group", "group-link", "category"])][:120]
        print(f"\n== {url} status={r.status_code} len={len(r.text)}")
        for c in cats: print("  ", c)
    except Exception as e:
        print(f"\n== {url} ERR {e}")
