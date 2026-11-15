#!/usr/bin/env python3
"""team16 detail-page fetch — wave 20261114.
Fetches https://groupjoin.link/group/<group_uid> for fresh non-Adult items,
cross-checks invite code + title vs API record. Saves raw HTML.
"""
import json, re, time, requests, os

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
HTMLDIR = os.path.join(WD, "team16-detail-html")
os.makedirs(HTMLDIR, exist_ok=True)

raw = json.load(open(os.path.join(WD, "team16-api-raw.json")))
cutoff = "2026-11-12 16:26:43"
fresh = []
for pg in ("page1", "page2"):
    for it in raw[pg]["data"]:
        if it["created_at"][:19] > cutoff and it["category"]["category_slug"] != "adult":
            fresh.append(it)

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                  "Referer": "https://groupjoin.link/"})
out = []
for it in fresh:
    uid = it["group_uid"]
    code_api = it["link"].split("chat.whatsapp.com/")[1].split("?")[0]
    url = f"https://groupjoin.link/group/{uid}"
    rec = {"uid": uid, "created_at": it["created_at"], "api_title": it["group_title"],
           "api_code": code_api, "category": it["category"]["category_name"],
           "country": it["country"]["iso2"]}
    try:
        r = s.get(url, timeout=60)
        rec["http"] = r.status_code
        html = r.text
        with open(os.path.join(HTMLDIR, uid + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
        codes = sorted(set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", html)))
        rec["detail_codes"] = codes
        rec["code_match"] = code_api in codes
        m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        rec["detail_title_tag"] = (m.group(1).strip()[:120] if m else "")
    except Exception as e:
        rec["http"] = 0
        rec["error"] = repr(e)[:200]
    out.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    time.sleep(5)

with open(os.path.join(WD, "team16-detail-check.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved team16-detail-check.json; n =", len(out))
