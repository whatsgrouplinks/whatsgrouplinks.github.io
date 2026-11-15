import json, re, time, requests
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
PAGES={
 "karachi":"https://77links.com/karachi-whatsapp-group-links/",
 "islamic":"https://77links.com/islamic-whatsapp-group-links/",
 "kurulus-osman":"https://77links.com/kurulus-osman-whatsapp-group-links/",
 "malayalam":"https://77links.com/malayalam-whatsapp-group-links/",
 "marriage":"https://77links.com/marriage-whatsapp-group-links/",
 "online-earning":"https://77links.com/online-earning-whatsapp-groups/",
 "pdf-books":"https://77links.com/pdf-books-whatsapp-group-links/",
 "pti":"https://77links.com/pti-whatsapp-group-links/",
 "pubg":"https://77links.com/pubg-whatsapp-group-links/",
 "lahore":"https://77links.com/lahore-whatsapp-group-links/",
 "friendship":"https://77links.com/friendship-whatsapp-group-links/",
 "jobs":"https://77links.com/jobs-whatsapp-group-links/",
 "pakistan-cricket":"https://77links.com/pakistan-cricket-whatsapp-group-links/",
}
S=requests.Session(); S.headers.update(UA)
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
fresh=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113/team20_fresh_77.json"))
w12=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team20_all_extracted.json"))
w12set=set(w12 if isinstance(w12,list) else w12.keys())
log=[]; new={}
for slug,url in PAGES.items():
    try:
        r=S.get(url, timeout=60)
        codes=re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,30})', r.text)
        # keep order, dedupe within page
        seen=[]; 
        for c in codes:
            if c not in seen: seen.append(c)
        fresh_new=[c for c in seen if c not in union and c not in fresh and c not in w12set and c not in new]
        for c in fresh_new:
            new[c]={"page":slug,"country":"PK","url":url,"label":""}
        log.append({"slug":slug,"url":url,"status":str(r.status_code),"codes_on_page":len(seen),"new":len(fresh_new)})
        print(slug, r.status_code, len(seen), "new", len(fresh_new), flush=True)
    except Exception as e:
        log.append({"slug":slug,"url":url,"status":f"error {type(e).__name__}: {e}","codes_on_page":0,"new":0})
        print(slug,"ERROR",e,flush=True)
    time.sleep(2)
json.dump({"fetch_log":log,"new_codes":[c for c in new]}, open(WD+"/team17_poll_raw.json","w"), ensure_ascii=False, indent=1)
json.dump(list(new.keys()), open(WD+"/team17_poll_new_codes.json","w"))
json.dump(new, open(WD+"/team17_poll_new.json","w"), ensure_ascii=False, indent=1)
print("TOTAL NEW:",len(new))
