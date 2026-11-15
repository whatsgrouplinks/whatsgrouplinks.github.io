import json, time, uuid, requests
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
pages = json.load(open(f"{WD}/team18_ltg_listing_pages.json"))
names = json.load(open(f"{WD}/team18_ltg_listing_names.json"))
new_ids = json.load(open(f"{WD}/team18_ltg_new_ids_extra.json"))
# also include the first batch's resolved file for completeness check
done_ids = set()
try:
    prev = json.load(open(f"{WD}/team18_ltg_new_resolved.json"))
    done_ids = {r["id"] for r in prev}
except Exception:
    prev = []
new_ids = [i for i in new_ids if i not in done_ids]
s = requests.Session()
s.headers.update({'User-Agent': UA})
out = list(prev)
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
    time.sleep(1)
json.dump(out, open(f"{WD}/team18_ltg_new_resolved_all.json", "w"), ensure_ascii=False, indent=1)
print("DONE RESOLVE ALL, total:", len(out), flush=True)
