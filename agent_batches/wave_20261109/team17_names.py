import re, json, os, html
RAW='team17_raw'
pat=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{10,30})')
def clean(s):
    s=html.unescape(re.sub(r'<[^>]+>',' ',s)); s=re.sub(r'\s+',' ',s).strip()
    return s
names={}
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith('.html'): continue
    txt=open(os.path.join(RAW,fn),encoding='utf-8',errors='ignore').read()
    heads=[(m.start(), clean(m.group(1))) for m in re.finditer(r'<h[23][^>]*>(.*?)</h[23]>', txt, re.S)]
    for m in pat.finditer(txt):
        code=m.group(1).rstrip('/')
        nm=''
        # enclosing table row?
        tr_start=txt.rfind('<tr',0,m.start())
        if tr_start>=0 and m.start()-tr_start<1500:
            tr=txt[tr_start:m.start()]
            tds=[clean(t) for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
            tds=[t for t in tds if t and 'click here' not in t.lower() and 'join' not in t.lower()]
            if tds: nm=tds[0]
        if not nm:
            prev=[(pos,h) for pos,h in heads if pos < m.start() and m.start()-pos<600]
            if prev: nm=prev[-1][1]
        # list-item style: preceding <li> text
        if not nm:
            li=txt.rfind('<li',0,m.start())
            if li>=0 and m.start()-li<600:
                nm=clean(txt[li:m.start()])[:120]
        if nm and len(nm)>1:
            # strip trailing 'join'/'click here' junk
            nm=re.sub(r'\s*(join|click here|unirse.*)$','',nm,flags=re.I).strip()
            if code not in names or (len(nm)>3 and len(nm)<len(names[code])):
                names[code]=nm[:120]
json.dump(names,open('team17_listing_names.json','w'),ensure_ascii=False,indent=1)
print('codes with listing name:',len(names))
import collections
print(collections.Counter())
# sample fresh ones
fresh=json.load(open('team17_fresh_raw.json'))
n=0
for c in fresh:
    if c in names:
        print(c,'|',names[c]); n+=1
        if n>40: break
print('fresh with name:', sum(1 for c in fresh if c in names), 'of', len(fresh))
