import json, re, time, requests
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
s = requests.Session()
s.headers.update({'User-Agent': UA})
pages = json.load(open(f"{WD}/team18_ltg_listing_pages.json"))
names = json.load(open(f"{WD}/team18_ltg_listing_names.json"))
known = set(pages.keys())
INDEX = [
    ("pakistan", "https://linktogroups.com/en/pakistan"),
    ("india", "https://linktogroups.com/en/india"),
    ("australia", "https://linktogroups.com/en/australia"),
    ("canada", "https://linktogroups.com/en/canada"),
    ("ethiopia", "https://linktogroups.com/en/ethiopia"),
    ("malaysia", "https://linktogroups.com/en/malaysia"),
    ("philippines", "https://linktogroups.com/en/philippines"),
    ("russia", "https://linktogroups.com/en/russia"),
    ("singapore", "https://linktogroups.com/en/singapore"),
    ("iran", "https://linktogroups.com/en/iran"),
]
log = json.load(open(f"{WD}/team18_ltg_fetch_log.json"))
for tag, url in INDEX:
    done = False
    for attempt in range(3):
        try:
            r = s.get(url, timeout=60)
            open(f"{WD}/team18_ltg_{tag}.html", "w", encoding="utf-8").write(r.text)
            ids = re.findall(r'/en/listing/([a-z0-9\-]+)-(\d+)', r.text)
            uniq = sorted(set(i for _, i in ids))
            new_here = [i for i in uniq if i not in known]
            print(tag, r.status_code, len(r.text), "listings:", len(uniq), "new_ids:", new_here, flush=True)
            log.append({"tag": tag, "url": url, "status": r.status_code,
                        "listings": len(uniq), "new_ids": new_here})
            for slug, lid in set(ids):
                if lid not in pages: pages[lid] = [tag]
                elif tag not in pages[lid]: pages[lid].append(tag)
            for m in re.finditer(r'"name":"((?:[^"\\]|\\.)*)","url":"https://linktogroups\.com/en/listing/[^"]*-(\d+)"', r.text):
                names.setdefault(m.group(2), m.group(1))
            done = True
            break
        except Exception as e:
            print(tag, "attempt", attempt, "FAIL", str(e)[:150], flush=True)
            time.sleep(8)
    if not done:
        log.append({"tag": tag, "url": url, "status": 0, "error": "3 attempts failed"})
    time.sleep(2)
json.dump(log, open(f"{WD}/team18_ltg_fetch_log.json", "w"), indent=1)
json.dump(pages, open(f"{WD}/team18_ltg_listing_pages.json", "w"), indent=1)
json.dump(names, open(f"{WD}/team18_ltg_listing_names.json", "w"), ensure_ascii=False, indent=1)
new_ids = sorted(set(pages.keys()) - known, key=int)
print("NEW ids from extra countries:", new_ids, flush=True)
json.dump(new_ids, open(f"{WD}/team18_ltg_new_ids_extra.json", "w"))
print("DONE EXTRA FETCH")
