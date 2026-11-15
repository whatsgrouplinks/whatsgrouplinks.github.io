#!/usr/bin/env python3
"""Fetch groupsor.in SA-category detail pages, extract true-case codes via golink href."""
import json, re, time, requests, html

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
cats = json.load(open(f"{WD}/team23_groupsorin_cats.json"))
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))

sess = requests.Session()
found = {}
for cat, urls in cats.items():
    for u in urls:
        try:
            r = sess.get(u, headers=H, timeout=40)
            if r.status_code != 200:
                print("FAIL", u, r.status_code); continue
            t = r.text
            m = re.search(r"/golink/wagroups-([A-Za-z0-9]{15,30})", t)
            if not m:
                print("NOCODE", u); continue
            code = m.group(1)
            tm = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
            name = ""
            if tm:
                name = html.unescape(tm.group(1)).replace(" WhatsApp Group Link - GroupSor", "").strip()
            found[code] = {"name": name, "category_dir": cat, "page": u, "site": "groupsor.in"}
            print(cat, code, name[:60])
        except Exception as e:
            print("ERR", u, e)
        time.sleep(0.3)
json.dump(found, open(f"{WD}/team23_groupsorin_raw.json", "w"), ensure_ascii=False, indent=1)
fresh = {c: v for c, v in found.items() if c not in union}
print("TOTAL", len(found), "FRESH", len(fresh))
json.dump(fresh, open(f"{WD}/team23_groupsorin_fresh.json", "w"), ensure_ascii=False, indent=1)
