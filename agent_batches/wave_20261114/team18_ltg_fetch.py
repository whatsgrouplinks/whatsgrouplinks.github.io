import json, re, time, html, requests
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
OLD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

s = requests.Session()
s.headers.update({'User-Agent': UA})

def og_title(code):
    try:
        r = s.get(f"https://chat.whatsapp.com/{code}", timeout=90, allow_redirects=True)
        if r.status_code == 429:
            return ("http429", "")
        m = TITLE_RE.search(r.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return (str(r.status_code), t)
    except Exception as e:
        return ("transport", str(e))

# ---- CONTROLS (one keep-alive session) ----
live_status, live_title = og_title("KrDwdK8EIkB6vgauHg5M7N")
fab_status, fab_title = og_title("ZzZzZzZzZzZzZzZzZzZzZzZz")
print("CONTROL live:", live_status, repr(live_title), flush=True)
print("CONTROL fab :", fab_status, repr(fab_title), flush=True)
controls = {
    "live": {"code": "KrDwdK8EIkB6vgauHg5M7N", "http": live_status, "og_title": live_title,
             "expected": "JAY - PHP & Python Full Stack Developer",
             "pass": live_title == "JAY - PHP & Python Full Stack Developer"},
    "fabricated": {"code": "ZzZzZzZzZzZzZzZzZzZzZzZz", "http": fab_status, "og_title": fab_title,
                   "expected": "", "pass": fab_title == ""},
}
print("CONTROLS PASS:", controls["live"]["pass"] and controls["fabricated"]["pass"], flush=True)
json.dump(controls, open(f"{WD}/team18-controls.json", "w"), indent=1)
if not (controls["live"]["pass"] and controls["fabricated"]["pass"]):
    print("CONTROLS FAILED - STOPPING", flush=True)
    raise SystemExit(1)

# ---- FETCH LTG listing pages ----
old_pages = json.load(open(f"{OLD}/ltg_listing_pages.json"))
old_names = json.load(open(f"{OLD}/ltg_listing_names.json"))
old_ids = set(old_pages.keys())
pages = dict(old_pages)
names = dict(old_names)

INDEX = [
    ("whatsapp-groups", "https://linktogroups.com/en/whatsapp-groups"),
    ("whatsapp-groups-p2", "https://linktogroups.com/en/whatsapp-groups?page=2"),
    ("whatsapp-groups-p3", "https://linktogroups.com/en/whatsapp-groups?page=3"),
    ("whatsapp-groups-p4", "https://linktogroups.com/en/whatsapp-groups?page=4"),
    ("whatsapp-groups-p5", "https://linktogroups.com/en/whatsapp-groups?page=5"),
    ("ghana", "https://linktogroups.com/en/ghana"),
    ("kenya", "https://linktogroups.com/en/kenya"),
    ("nigeria", "https://linktogroups.com/en/nigeria"),
    ("nigeria-p2", "https://linktogroups.com/en/nigeria?page=2"),
    ("nigeria-p3", "https://linktogroups.com/en/nigeria?page=3"),
    ("nigeria-p4", "https://linktogroups.com/en/nigeria?page=4"),
    ("nigeria-p5", "https://linktogroups.com/en/nigeria?page=5"),
    ("nigeria-p6", "https://linktogroups.com/en/nigeria?page=6"),
    ("saudi-arabia", "https://linktogroups.com/en/saudi-arabia"),
]
fetch_log = []
for tag, url in INDEX:
    for attempt in range(3):
        try:
            r = s.get(url, timeout=60)
            open(f"{WD}/team18_ltg_{tag}.html", "w", encoding="utf-8").write(r.text)
            ids = re.findall(r'/en/listing/([a-z0-9\-]+)-(\d+)', r.text)
            uniq = sorted(set(i for _, i in ids))
            new_here = [i for i in uniq if i not in old_ids]
            print(tag, r.status_code, len(r.text), "listings:", len(uniq), "new_ids:", new_here, flush=True)
            fetch_log.append({"tag": tag, "url": url, "status": r.status_code,
                              "listings": len(uniq), "new_ids": new_here})
            for slug, lid in set(ids):
                if lid not in pages: pages[lid] = [tag]
                elif tag not in pages[lid]: pages[lid].append(tag)
            for m in re.finditer(r'"name":"((?:[^"\\]|\\.)*)","url":"https://linktogroups\.com/en/listing/[^"]*-(\d+)"', r.text):
                names.setdefault(m.group(2), m.group(1))
            break
        except Exception as e:
            print(tag, "attempt", attempt, "FAIL", str(e)[:200], flush=True)
            if attempt == 2:
                fetch_log.append({"tag": tag, "url": url, "status": 0, "error": str(e)})
            time.sleep(8)
    time.sleep(2)

# home page: discover country pages
countries = []
try:
    r = s.get("https://linktogroups.com/en", timeout=60)
    open(f"{WD}/team18_ltg_home.html", "w", encoding="utf-8").write(r.text)
    countries = sorted(set(re.findall(r'href="https://linktogroups\.com/en/([a-z\-]+)"', r.text)))
    print("homepage country links:", countries, flush=True)
except Exception as e:
    print("home FAIL", e, flush=True)
    fetch_log.append({"tag": "home", "url": "https://linktogroups.com/en", "status": 0, "error": str(e)})

json.dump(fetch_log, open(f"{WD}/team18_ltg_fetch_log.json", "w"), indent=1)
json.dump(pages, open(f"{WD}/team18_ltg_listing_pages.json", "w"), indent=1)
json.dump(names, open(f"{WD}/team18_ltg_listing_names.json", "w"), ensure_ascii=False, indent=1)
json.dump(countries, open(f"{WD}/team18_ltg_home_countries.json", "w"))
new_ids = sorted(set(pages.keys()) - old_ids, key=int)
print("NEW listing ids vs Nov13:", new_ids, flush=True)
json.dump(new_ids, open(f"{WD}/team18_ltg_new_ids.json", "w"))
print("DONE FETCH")
