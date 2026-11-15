import json, sys, time, html
from team25_verify import check, og_title
import requests

fresh = json.load(open('team25_raw/fresh.json'))
pool = json.load(open('team25_raw/pool.json'))
codes = list(fresh.keys())
print(f"verifying {len(codes)} fresh codes", flush=True)
sess = requests.Session()
results = {}
for i, code in enumerate(codes):
    st, why, title = check(sess, code)
    title = html.unescape(title)
    results[code] = {"status": st, "why": why, "og_title": title,
                     "name": pool[code]["name"], "country": pool[code]["country"],
                     "source": pool[code]["source"], "section": pool[code].get("section","")}
    print(f"{i+1}/{len(codes)} {code} {st} {title[:70]!r}", flush=True)
    json.dump(results, open('team25_raw/verify_results.json','w'), indent=1, ensure_ascii=False)
    time.sleep(1.2)
print("DONE")
