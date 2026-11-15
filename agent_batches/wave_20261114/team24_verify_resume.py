import json, sys, time, html
sys.path.insert(0, '.')
from team24_verify import check
import requests

out = json.load(open("team24_verify_out.json"))
data = json.load(open("team24_all_raw.json"))
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
fresh = [e for e in data["entries"] if e["code"] not in union]
todo = [e for e in fresh if e["code"] not in out]
print("remaining:", len(todo))
s = requests.Session()
for i, e in enumerate(todo):
    st, title, err = check(s, e["code"])
    out[e["code"]] = {"status": st, "og_title": html.unescape(title) if title else "", "err": err,
                      "source": e["source"], "dir_name": e["dir_name"], "dir_cat": e["dir_cat"], "country": e["country"]}
    print(i, e["code"], st, out[e["code"]]["og_title"][:60])
    json.dump(out, open("team24_verify_out.json","w"), ensure_ascii=False, indent=1)
    time.sleep(0.5)
from collections import Counter
print(Counter(v["status"] for v in out.values()))
