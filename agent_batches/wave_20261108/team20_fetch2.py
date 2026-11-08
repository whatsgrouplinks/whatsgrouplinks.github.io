import requests, re, json, time
from html.parser import HTMLParser
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buf=[]; self.results=[]
    def handle_data(self, d):
        d=d.strip()
        if d:
            self.buf.append(d[-120:])
            if len(self.buf)>6: self.buf=self.buf[-6:]
    def handle_starttag(self, tag, attrs):
        if tag=='a':
            href=dict(attrs).get('href','')
            m=re.match(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', href)
            if m:
                name=''
                for t in reversed(self.buf):
                    if t and 'Join' not in t and 'Click' not in t and len(t)>1: name=t; break
                self.results.append({"code":m.group(1),"name_raw":name})

GL = ["scholarship-whatsapp-group-links","ielts-whatsapp-group-links","neet-whatsapp-group-links",
"freelancer-whatsapp-group-links","education-whatsapp-group-links","top-500-jobs-whatsapp-groups-for-career-success",
"2500-online-earning-whatsapp-groups-links","1000-join-active-placement-whatsapp-group-links-for-job-updates",
"all-exams-whatsapp-group-links-boost-success-with-ease-now","join-active-bank-exam-whatsapp-group-links-for-preparations",
"study-material-whatsapp-group-links-for-quick-access","3200-indian-job-whatsapp-group-links",
"data-entry-whatsapp-group-links-skills-and-career","uk-student-whatsapp-group-links",
"12th-class-student-whatsapp-group-links","join-the-board-exam-whatsapp-group-links-for-study-support",
"private-job-whatsapp-group-links","bank-jobs-whatsapp-group-links","europe-jobs-whatsapp-group-links",
"gulf-jobs-whatsapp-group-links-for-bright-careers","qatar-job-vacancy-whatsapp-group-links",
"pharma-jobs-whatsapp-group-links","airport-jobs-whatsapp-group-links",
"exclusive-reliable-hotel-job-whatsapp-group-links","female-job-whatsapp-group-links",
"kerala-jobs-whatsapp-group-links","kolkata-job-whatsapp-group-links-for-fast-and-easy-job-alerts",
"3000-noida-job-whatsapp-group-links","join-powerful-bihar-student-whatsapp-group-links-for-growth",
"llb-whatsapp-group-links-students-seeking-success","exclusive-bba-whatsapp-group-links-smart-learning",
"hbse-whatsapp-group-links-for-students-teachers-and-updates","polytechnic-whatsapp-group-links-for-learning-now",
"maths-whatsapp-group-links-for-smart-learners-now","powerful-python-whatsapp-group-links-for-learning",
"civil-engineering-whatsapp-group-links-for-learn","join-latest-english-grammar-whatsapp-group-links",
"sarkari-result-whatsapp-group-links","sarkari-network-whatsapp-group-links-for-updates",
"top-english-whatsapp-group-links-for-learning-now","join-best-study-whatsapp-group-links-for-success",
"ultimate-exciting-free-job-alert-whatsapp-group-links-guide","exclusive-bsf-whatsapp-group-links-for-daily-jobs",
"join-the-active-finance-jobs-whatsapp-group-links","software-jobs-whatsapp-group-links-instant-hiring",
"it-jobs-whatsapp-group-links","3000-indian-govt-jobs-whatsapp-group-links-group-link"]
URLS=[("gl-"+s, f"https://grouplink.com.in/{s}/") for s in GL]
URLS += [
 ("whatstele-pk","https://whatstele.com/whatsapp/group-links/pakistani/"),
 ("glf-pakistani","https://www.grouplinksforyou.com/2023/03/1000-active-pakistani-whatsapp-group.html"),
 ("sociallykeeda-pk","https://www.sociallykeeda.com/pakistani-whatsapp-group/"),
 ("joingram-earning","https://joingram.in/online-earning-whatsapp-group-links/"),
 ("whatinfotech-earning","https://whatinfotech.com/1000-active-whatsapp-online-earning-groups-2026-free-join-links-for-make-money-online-ideas/"),
]
out=[]
for label, url in URLS:
    try:
        r=requests.get(url, headers=UA, timeout=30)
        p=P(); p.feed(r.text)
        print(label, r.status_code, "anchors:", len(p.results), flush=True)
        for x in p.results:
            x["src"]=label; x["url"]=url
            out.append(x)
        time.sleep(0.7)
    except Exception as e:
        print(label, "ERR", e, flush=True)
uniq={}
for o in out: uniq.setdefault(o["code"], o)
fresh=[o for o in uniq.values() if o["code"] not in union]
print("TOTAL unique:", len(uniq), "FRESH:", len(fresh), flush=True)
json.dump(list(uniq.values()), open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_raw2.json","w"), ensure_ascii=False, indent=1)
json.dump(fresh, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_fresh2.json","w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(o["src"] for o in fresh), flush=True)
for o in fresh: print(o["code"], o["src"], "|", o["name_raw"][:70], flush=True)
