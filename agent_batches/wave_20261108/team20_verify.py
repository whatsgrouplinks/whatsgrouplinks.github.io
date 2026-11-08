import requests, re, json, time, html
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
GENERIC = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group on whatsapp"}

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in (1, 2):
        try:
            s = requests.Session()
            r = s.get(url, headers=UA, timeout=20)
            m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', r.text, re.I)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', r.text, re.I)
            title = html.unescape(m.group(1)).strip() if m else ""
            if r.status_code == 200 and title and title.lower() not in GENERIC:
                return {"code": code, "status": "live", "og_title": title, "http": r.status_code}
            if r.status_code == 200 and not title:
                if attempt == 1:
                    time.sleep(3)
                    continue
                return {"code": code, "status": "dead", "og_title": "", "http": r.status_code, "note": "200-empty-after-retry"}
            return {"code": code, "status": "dead", "og_title": title, "http": r.status_code}
        except Exception as e:
            if attempt == 1:
                time.sleep(3)
                continue
            return {"code": code, "status": "pending", "og_title": "", "http": 0, "note": f"transport:{type(e).__name__}"}
    return {"code": code, "status": "dead", "og_title": "", "http": 0}

# build candidate list
cands = {}
def add(code, name, src, cat):
    if code not in cands:
        cands[code] = {"code": code, "name_raw": name, "src": src, "cat_hint": cat}

for o in json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_fresh2.json")):
    add(o["code"], o.get("name_raw",""), o.get("src",""), "")
for o in json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_wglpk_inscope.json")):
    add(o["code"], o.get("name_raw",""), "whatsgroupslinkspk", o.get("cat",""))
for code, name, cat in [
 ("EOy0rloJ3CL5USQiQl0ySq","English club","Education"),
 ("JlZnZPTK7bX7spEebjn3Py","English learning","Education"),
 ("GuyhfJ9wqdpJuknoZ5lJju","AlphaFX Insights","Online Earning"),
 ("EnyeREwpivBLPxv3VOqIdw","Pharmacy Students SuperSTARS","Education"),
 ("LQZoftVxndC8Lmv9ThePCQ","Scholarship Updates","Scholarship"),
 ("H59esmUSSMbKCPYn1ii5Md","Ludwigsburg Exchange Students and Buddies","Education"),
]:
    add(code, name, "standalone-search", cat)
# Devanagari govt-jobs name from wglpk fresh2
for o in json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_wglpk_fresh2.json")):
    if o["code"]=="FJ72NaDuMb62mCMVI07my3":
        add(o["code"], o.get("name_raw",""), "whatsgroupslinkspk", "Jobs")

lst = list(cands.values())
print("candidates:", len(lst), flush=True)
json.dump(lst, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_candidates.json","w"), ensure_ascii=False, indent=1)
results = []
for i, c in enumerate(lst):
    r = check(c["code"])
    r.update({"name_raw": c["name_raw"], "src": c["src"], "cat_hint": c["cat_hint"]})
    results.append(r)
    print(i+1, "/", len(lst), c["code"], r["status"], repr(r["og_title"][:60]), flush=True)
    time.sleep(0.6)
json.dump(results, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_verified.json","w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r["status"] for r in results), flush=True)
