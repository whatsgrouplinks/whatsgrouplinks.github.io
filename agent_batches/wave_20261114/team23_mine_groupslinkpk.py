#!/usr/bin/env python3
import requests, json, sys, time
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team23_mine import extract

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
H = {"User-Agent": "Mozilla/5.0"}
sm = json.load(open(f"{WD}/team23_groupslinkpk_sitemap.json"))
keep = ["jobs-whatsapp-groups-pakistan", "cities-whatsapp-groups-pakistan",
        "worldwide-whatsapp-group-links", "online-earning", "funny-whatsapp",
        "friendship-whatsapp", "pakistan-whatsapp-group-link",
        "whatsapp-groups-links-pakistan", "whatsapp-group-join-link",
        "join-group-whatsapp"]
urls = [u for u in sm["cats"] + sm["posts"] if any(k in u for k in keep)]
print("urls:", len(urls))
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
s = requests.Session()
found = {}
for u in urls:
    try:
        r = s.get(u, headers=H, timeout=40)
        items = extract(r.text, u)
        print(u, r.status_code, "codes:", len(set(c for c, _ in items)),
              "fresh:", len(set(c for c, _ in items if c not in union)), flush=True)
        for c, n in items:
            if c not in found:
                found[c] = {"name": n, "page": u, "site": "groupslink.pk"}
    except Exception as e:
        print(u, "ERR", e)
    time.sleep(1)
fresh = {c: v for c, v in found.items() if c not in union}
print("TOTAL", len(found), "FRESH", len(fresh))
json.dump(found, open(f"{WD}/team23_groupslinkpk_raw.json", "w"), ensure_ascii=False, indent=1)
json.dump(fresh, open(f"{WD}/team23_groupslinkpk_fresh.json", "w"), ensure_ascii=False, indent=1)
for c, v in fresh.items():
    print("FRESH", c, v)
