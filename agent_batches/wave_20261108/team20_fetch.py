import requests, re, json, time, html
from urllib.parse import urlparse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
URLS = [
 ("grouplink-study", "https://grouplink.com.in/all-india-study-whatsapp-group-links/", "Education"),
 ("grouplink-kota", "https://grouplink.com.in/kota-university-whatsapp-group-links-for-students/", "Education"),
 ("grouplink-govtjobs", "http://grouplink.com.in/3000-indian-govt-jobs-whatsapp-group-links-group-link/", "Jobs"),
 ("whgroups-pkjobs", "https://whgroups.link/pakistan-jobs-whatsapp-group-links/", "Jobs"),
 ("newgrouplinks-jobs", "https://newgrouplinks.pk/jobs-whatsapp-group-links/", "Jobs"),
 ("77links-students", "https://77links.com/students-whatsapp-group-links/", "Education"),
 ("77links-edu", "https://77links.com/educational-whatsapp-group-links/", "Education"),
 ("wahublink-earning", "https://wahublink.com/online-earning-whatsapp-group-links/", "Freelance"),
 ("ccsupsc", "https://ccsupsc.com/join-upsc-jpsc-bpsc-whatsapp-group/", "Education"),
 ("hubrecipes-english", "https://hubrecipes.com/active-english-learning-whatsapp-group-links/", "Education"),
 ("groupsinvite-english", "https://groupsinvite.link/education/study/english-learning/", "Education"),
 ("englishan", "https://englishan.com/english-whatsapp-group-link-2021/", "Education"),
 ("sarkarijobs", "https://www.sarkarijobs.com/join-whatsapp-groups-links-for-sarkari-jobs-sarkari-result/", "Jobs"),
 ("whatsgroupslinkspk", "https://whatsgroupslinkspk.com/", "Jobs"),
]
out = []
for label, url, cat in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(label, r.status_code, len(r.text))
        txt = r.text
        # find all chat.whatsapp.com codes with surrounding context
        for m in re.finditer(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', txt):
            code = m.group(1)
            start = max(0, m.start()-400)
            ctx = re.sub(r'<[^>]+>', ' ', txt[start:m.start()+50])
            ctx = html.unescape(re.sub(r'\s+', ' ', ctx)).strip()
            out.append({"code": code, "src": label, "url": url, "cat": cat, "ctx": ctx[-300:]})
        time.sleep(1)
    except Exception as e:
        print(label, "ERR", e)
print("total raw hits:", len(out))
uniq = {}
for o in out:
    uniq.setdefault(o["code"], o)
print("unique codes:", len(uniq))
json.dump(list(uniq.values()), open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_raw.json","w"), ensure_ascii=False, indent=1)
