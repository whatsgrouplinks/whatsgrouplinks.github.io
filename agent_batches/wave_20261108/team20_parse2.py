import requests, re, json, time, html
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buf=[]  # recent text chunks
        self.results=[]
    def handle_data(self, d):
        d=d.strip()
        if d: self.buf.append(d[-120:])
        if len(self.buf)>6: self.buf=self.buf[-6:]
    def handle_starttag(self, tag, attrs):
        if tag=='a':
            href=dict(attrs).get('href','')
            m=re.match(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', href)
            if m:
                # name = last meaningful text chunk before this link
                name=''
                for t in reversed(self.buf):
                    if t and 'Join' not in t and len(t)>1:
                        name=t; break
                self.results.append({"code":m.group(1),"name_raw":name,"ctx":" | ".join(self.buf[-3:])})

def fetch(url):
    r=requests.get(url, headers=UA, timeout=40)
    print(url, r.status_code, len(r.text))
    return r.text

# 1) whatsgroupslinkspk homepage re-parse
txt=fetch("https://whatsgroupslinkspk.com/")
p=P(); p.feed(txt)
print("anchors:", len(p.results))
fresh=[x for x in p.results if x["code"] not in union]
print("fresh:", len(fresh))
json.dump(fresh, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_wglpk_fresh.json","w"), ensure_ascii=False, indent=1)
for x in fresh[:40]: print(x["code"], "|", x["name_raw"])

# 2) standalone scholarship codes from search results
for code, name, cat in [
 ("CHpcgYzLoTkCMDNZC06OCa","WAAW Foundation Scholarship 2026","Scholarship"),
 ("ExqJkk0jJLK8BszF36QsJc","Santoor Womens Scholarship 2026-27","Scholarship"),
 ("EnyeREwpivBLPxv3VOqIdw","Pharmacy Students SuperSTARS","Education"),
 ("LQZoftVxndC8Lmv9ThePCQ","Scholarship Updates CV Templates","Scholarship"),
 ("JptmiERLg05DwZboPy8jwc","Kings Cambridge International Freshers","Education"),
 ("H59esmUSSMbKCPYn1ii5Md","Ludwigsburg Exchange Students and Buddies","Education"),
 ("K1R9M1CI5SgE7MFR2g9Lil","English Language Practice","Education"),
 ("6MThniQ9eo6DJiknA5fjpM","IELTS Preparation Group","Education"),
]:
    print(code, "IN UNION" if code in union else "FRESH", name)
