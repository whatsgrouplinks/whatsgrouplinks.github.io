import json, time, uuid, requests
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
pages = json.load(open(f"{WD}/team18_ltg_listing_pages.json"))
names = json.load(open(f"{WD}/team18_ltg_listing_names.json"))
new_ids = json.load(open(f"{WD}/team18_ltg_new_ids.json"))
# patch 4024 name from listing slug/card text found in html
names.setdefault("4024", "Danish FX | GOLD Signals - Forex & BTC Analysis | XAUUSD | Free Signals")
s = requests.Session()
s.headers.update({'User-Agent': UA})
out = []
for lid in new_ids:
    dest = ""; status = 0; err = ""
    for attempt in range(3):
        try:
            r = requests.post(f'https://linktogroups.com/api/v1/listings/{lid}/click',
                headers={'User-Agent': UA, 'Accept': 'application/json',
                         'X-Visitor-Id': f'team18-{uuid.uuid4().hex[:8]}',
                         'Content-Type': 'application/json'},
                json={}, timeout=60)
            status = r.status_code
            if r.status_code == 200:
                dest = r.json().get('data', {}).get('destination_url', '')
                break
            time.sleep(5)
        except Exception as e:
            status = 0; err = str(e); time.sleep(5)
    rec = {"id": lid, "name": names.get(lid, ""), "pages": pages.get(lid, []),
           "destination": dest, "status": status, "error": err}
    out.append(rec)
    print(rec, flush=True)
    time.sleep(2)
json.dump(out, open(f"{WD}/team18_ltg_new_resolved.json", "w"), ensure_ascii=False, indent=1)
json.dump(names, open(f"{WD}/team18_ltg_listing_names.json", "w"), ensure_ascii=False, indent=1)
print("DONE RESOLVE")
