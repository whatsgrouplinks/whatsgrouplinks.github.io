import json, re, subprocess, time, os
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
RETRY=[("whatsapp-groups-p2","https://linktogroups.com/en/whatsapp-groups?page=2"),
 ("whatsapp-groups-p4","https://linktogroups.com/en/whatsapp-groups?page=4"),
 ("ghana","https://linktogroups.com/en/ghana"),
 ("nigeria","https://linktogroups.com/en/nigeria"),
 ("nigeria-p3","https://linktogroups.com/en/nigeria?page=3"),
 ("nigeria-p5","https://linktogroups.com/en/nigeria?page=5"),
 ("saudi-arabia","https://linktogroups.com/en/saudi-arabia")]
pages=json.load(open(f"{WD}/ltg_listing_pages.json"))
names=json.load(open(f"{WD}/ltg_listing_names.json"))
old_ids=set(pages.keys())
log=json.load(open(f"{WD}/ltg_fetch_log.json"))
for tag,url in RETRY:
    fn=f"{WD}/ltg_{tag}.html"
    st="000"
    for attempt in range(3):
        p=subprocess.run(["curl","-s","-A",UA,"--max-time","60","-o",fn,"-w","%{http_code}",url],capture_output=True,text=True,timeout=75)
        st=p.stdout.strip()
        if st=="200": break
        print(tag,"attempt",attempt+1,"HTTP",st,flush=True); time.sleep(8)
    if st!="200":
        print(tag,"FAILED HTTP",st,flush=True)
        log.append({"tag":tag,"url":url,"status":st,"listings":0,"retry_failed":True}); continue
    t=open(fn,encoding='utf-8',errors='ignore').read()
    ids=re.findall(r'/en/listing/([a-z0-9\-]+)-(\d+)', t)
    uniq=sorted(set(i for _,i in ids))
    print(tag, st, len(t), "listings:", len(uniq), "new_ids:", [i for i in uniq if i not in old_ids], flush=True)
    log.append({"tag":tag,"url":url,"status":st,"listings":len(uniq),"new_ids":[i for i in uniq if i not in old_ids]})
    for slug,lid in set(ids):
        if lid not in pages: pages[lid]=[tag]
        elif tag not in pages[lid]: pages[lid].append(tag)
    for m in re.finditer(r'"name":"((?:[^"\\]|\\.)*)","url":"https://linktogroups\.com/en/listing/[^"]*-(\d+)"', t):
        names.setdefault(m.group(2), m.group(1))
    time.sleep(2)
json.dump(log, open(f"{WD}/ltg_fetch_log.json",'w'), indent=1)
json.dump(pages, open(f"{WD}/ltg_listing_pages.json",'w'), indent=1)
json.dump(names, open(f"{WD}/ltg_listing_names.json",'w'), ensure_ascii=False, indent=1)
new_ids=sorted(set(pages.keys())-{"4020"}-set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team14_raw/listing_pages.json")).keys()), key=int)
# recompute properly: new vs team14 old set
old14=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team14_raw/listing_pages.json")).keys())
new_ids=sorted(set(pages.keys())-old14, key=int)
print("ALL NEW listing ids vs Nov 12:", new_ids, flush=True)
json.dump(new_ids, open(f"{WD}/ltg_new_ids.json",'w'))
print("DONE RETRY")
