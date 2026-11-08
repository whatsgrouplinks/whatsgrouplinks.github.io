import requests, re, json
from html.parser import HTMLParser
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buf=[]; self.results=[]; self.section=""; self.in_head=False; self.head_txt=""
    def handle_starttag(self, tag, attrs):
        if tag in ("h1","h2","h3","h4"): self.in_head=True; self.head_txt=""
        if tag=='a':
            href=dict(attrs).get('href','')
            m=re.match(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', href)
            if m:
                name=''
                for t in reversed(self.buf):
                    if t and 'Join' not in t and len(t)>1: name=t; break
                self.results.append({"code":m.group(1),"name_raw":name,"section":self.section})
    def handle_endtag(self, tag):
        if tag in ("h1","h2","h3","h4"):
            self.in_head=False
            if self.head_txt.strip(): self.section=self.head_txt.strip()
    def handle_data(self, d):
        d=d.strip()
        if self.in_head: self.head_txt+=d+" "
        if d:
            self.buf.append(d[-120:])
            if len(self.buf)>6: self.buf=self.buf[-6:]

r=requests.get("https://whatsgroupslinkspk.com/", headers=UA, timeout=40)
p=P(); p.feed(r.text)
fresh=[x for x in p.results if x["code"] not in union]
print("total anchors:", len(p.results), "fresh:", len(fresh))
from collections import Counter
print(Counter(x["section"] for x in fresh))
json.dump(fresh, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_wglpk_fresh2.json","w"), ensure_ascii=False, indent=1)
for x in fresh:
    print(repr(x["section"])[:60], "|", x["code"], "|", x["name_raw"][:60])
print("KtKZUohUV8iKD6q0T2UGtJ in union:", "KtKZUohUV8iKD6q0T2UGtJ" in union)
