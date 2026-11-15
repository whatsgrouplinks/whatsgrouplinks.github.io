import json, sys, time, html
sys.path.insert(0, '.')
from team24_verify import check
import requests

data = json.load(open("team24_all_raw.json"))
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
fresh = [e for e in data["entries"] if e["code"] not in union]
# allow extra codes file (whts) to be merged later; support --extra path
extra = sys.argv[1] if len(sys.argv) > 1 else None
if extra:
    ex = json.load(open(extra))
    have = {e["code"] for e in fresh}
    for e in ex:
        if e["code"] not in have and e["code"] not in union:
            fresh.append(e)
print("verifying:", len(fresh))
s = requests.Session()
out = {}
for i, e in enumerate(fresh):
    st, title, err = check(s, e["code"])
    out[e["code"]] = {"status": st, "og_title": html.unescape(title) if title else "", "err": err,
                      "source": e["source"], "dir_name": e["dir_name"], "dir_cat": e["dir_cat"], "country": e["country"]}
    if i % 10 == 0:
        print(i, e["code"], st, out[e["code"]]["og_title"][:50])
        json.dump(out, open("team24_verify_out.json","w"), ensure_ascii=False, indent=1)
    time.sleep(0.5)
json.dump(out, open("team24_verify_out.json","w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(v["status"] for v in out.values()))
