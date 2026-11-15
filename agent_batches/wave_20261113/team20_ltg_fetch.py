import json, re, requests, time, uuid, os
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
s=requests.Session(); s.headers.update({'User-Agent':UA})
# old ids/names from team14
OLD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team14_raw"
pages=json.load(open(f"{OLD}/listing_pages.json"))
names=json.load(open(f"{OLD}/listing_names.json"))
old_ids=set(pages.keys())
print("old ids:", len(old_ids), flush=True)

INDEX=[("whatsapp-groups",f"https://linktogroups.com/en/whatsapp-groups"),
 ("whatsapp-groups-p2","https://linktogroups.com/en/whatsapp-groups?page=2"),
 ("whatsapp-groups-p3","https://linktogroups.com/en/whatsapp-groups?page=3"),
 ("whatsapp-groups-p4","https://linktogroups.com/en/whatsapp-groups?page=4"),
 ("whatsapp-groups-p5","https://linktogroups.com/en/whatsapp-groups?page=5"),
 ("ghana","https://linktogroups.com/en/ghana"),
 ("kenya","https://linktogroups.com/en/kenya"),
 ("nigeria","https://linktogroups.com/en/nigeria"),
 ("nigeria-p2","https://linktogroups.com/en/nigeria?page=2"),
 ("nigeria-p3","https://linktogroups.com/en/nigeria?page=3"),
 ("nigeria-p4","https://linktogroups.com/en/nigeria?page=4"),
 ("nigeria-p5","https://linktogroups.com/en/nigeria?page=5"),
 ("nigeria-p6","https://linktogroups.com/en/nigeria?page=6"),
 ("saudi-arabia","https://linktogroups.com/en/saudi-arabia")]
fetch_log=[]
for tag,url in INDEX:
    try:
        r=s.get(url, timeout=60)
        fn=f"{WD}/ltg_{tag}.html"
        open(fn,'w',encoding='utf-8').write(r.text)
        ids=re.findall(r'/en/listing/([a-z0-9\-]+)-(\d+)', r.text)
        uniq=sorted(set(i for _,i in ids))
        # pagination presence
        has_next = bool(re.search(r'page=\d+', r.text))
        print(tag, r.status_code, len(r.text), "listings:", len(uniq), "new_ids:", [i for i in uniq if i not in old_ids], flush=True)
        fetch_log.append({"tag":tag,"url":url,"status":r.status_code,"listings":len(uniq),"new_ids":[i for i in uniq if i not in old_ids]})
        for slug,lid in set(ids):
            if lid not in pages: pages[lid]=[tag]
            elif tag not in pages[lid]: pages[lid].append(tag)
        for m in re.finditer(r'"name":"((?:[^"\\]|\\.)*)","url":"https://linktogroups\.com/en/listing/[^"]*-(\d+)"', r.text):
            names.setdefault(m.group(2), m.group(1))
        # also try name from listing cards: data or title attr
        time.sleep(1)
    except Exception as e:
        print(tag,"FAIL",e, flush=True)
        fetch_log.append({"tag":tag,"url":url,"status":0,"error":str(e)})
json.dump(fetch_log, open(f"{WD}/ltg_fetch_log.json",'w'), indent=1)
json.dump(pages, open(f"{WD}/ltg_listing_pages.json",'w'), indent=1)
json.dump(names, open(f"{WD}/ltg_listing_names.json",'w'), ensure_ascii=False, indent=1)
new_ids=sorted(set(pages.keys())-old_ids, key=int)
print("NEW listing ids:", new_ids, flush=True)
json.dump(new_ids, open(f"{WD}/ltg_new_ids.json",'w'))
# homepage: discover country pages
try:
    r=s.get("https://linktogroups.com/en", timeout=60)
    open(f"{WD}/ltg_home.html",'w',encoding='utf-8').write(r.text)
    countries=sorted(set(re.findall(r'href="https://linktogroups\.com/en/([a-z\-]+)"', r.text)))
    print("homepage country links:", countries, flush=True)
    json.dump(countries, open(f"{WD}/ltg_home_countries.json",'w'))
except Exception as e:
    print("home FAIL", e, flush=True)
print("DONE FETCH")
