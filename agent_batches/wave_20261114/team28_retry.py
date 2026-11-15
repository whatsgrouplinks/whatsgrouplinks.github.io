import requests, re, json, time
from team28_mine import extract, UA

RETRY = [
    ("grouplinks-chelsea", "https://grouplinks.co.uk/chelsea-whatsapp-group-links/"),
    ("grouplinks-manutd", "https://grouplinks.co.uk/manchester-united-whatsapp-group-links/"),
    ("grouplinks-glasgow", "https://grouplinks.co.uk/glasgow-whatsapp-group-links/"),
    ("grouplinks-manchester", "https://grouplinks.co.uk/manchester-whatsapp-group-links/"),
    ("grouplinks-uk-education", "https://grouplinks.co.uk/uk-education-whatsapp-groups/"),
    ("grouplinks-freelancing", "https://grouplinks.co.uk/freelancing-whatsapp-group-links/"),
    ("grouplinks-movies", "https://grouplinks.co.uk/movies-whatsapp-group-links/"),
    ("grouplinks-islamic", "https://grouplinks.co.uk/islamic-whatsapp-group-links/"),
    ("grouplinks-pakistani-uk", "https://grouplinks.co.uk/pakistani-whatsapp-group-links-uk/"),
    ("grouplinks-all", "https://grouplinks.co.uk/all-whatsapp-groups/"),
    ("whtsagroupslinks-home", "https://www.whtsagroupslinks.com/"),
]
mined = json.load(open('team28-mined.json'))
items = {x['code']: x for x in mined['items']}
report = {x['label']: x for x in mined['sources']}
s = requests.Session()
for label, url in RETRY:
    ok = False
    for attempt in range(3):
        try:
            r = s.get(url, headers=UA, timeout=60)
            if r.status_code == 200:
                found = extract(r.text, url)
                for code, name in found.items():
                    if code not in items:
                        items[code] = {"code": code, "name": name, "sources": [label]}
                    else:
                        if not items[code]["name"] and name:
                            items[code]["name"] = name
                        if label not in items[code]["sources"]:
                            items[code]["sources"].append(label)
                report[label] = {"url": url, "label": label, "codes_found": len(found), "note": "retry attempt %d succeeded" % (attempt+1)}
                print(label, len(found), "codes (attempt %d)" % (attempt+1))
                ok = True
                break
            else:
                print(label, "HTTP", r.status_code, "attempt", attempt+1)
        except Exception as e:
            print(label, "ERROR", type(e).__name__, "attempt", attempt+1)
        time.sleep(10)
    if not ok:
        report[label] = {"url": url, "label": label, "codes_found": 0, "note": "retry x3 failed (proxy disconnect / HTTP non-200); banked as lead"}
        print(label, "FAILED after 3 attempts")
    time.sleep(3)
mined['items'] = list(items.values())
mined['sources'] = list(report.values())
json.dump(mined, open('team28-mined.json','w'), ensure_ascii=False, indent=1)
print("TOTAL unique codes mined now:", len(items))
