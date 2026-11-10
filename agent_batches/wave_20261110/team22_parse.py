import re, json, html, glob, os
from html.parser import HTMLParser

# Parse: track current h2 section; each h3 name followed by nearest chat.whatsapp.com link
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section=''; self.in_h2=False; self.in_h3=False
        self.pending_name=None; self.entries=[]
        self.buf=''
    def handle_starttag(self, tag, attrs):
        if tag=='h2': self.in_h2=True; self.buf=''
        if tag=='h3': self.in_h3=True; self.buf=''
        if tag=='a':
            d=dict(attrs)
            href=d.get('href','')
            m=re.match(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', href)
            if m and self.pending_name:
                self.entries.append({'name':self.pending_name.strip(),'section':self.section.strip(),'code':m.group(1)})
                self.pending_name=None
    def handle_endtag(self, tag):
        if tag=='h2': self.in_h2=False; self.section=self.buf.strip()
        if tag=='h3':
            self.in_h3=False
            # only keep h3 as pending name if it looks like a group name (short)
            t=self.buf.strip()
            if t and len(t)<=120: self.pending_name=t
    def handle_data(self, data):
        if self.in_h2 or self.in_h3: self.buf+=data

all_entries=[]
for f in sorted(glob.glob('team22_page_*.html'))+['team22_home.html']:
    p=P()
    p.feed(open(f,encoding='utf-8',errors='ignore').read())
    src=os.path.basename(f)
    for e in p.entries:
        e['source_file']=src
    print(src, 'entries:', len(p.entries))
    all_entries.extend(p.entries)

# dedupe by code, keep first occurrence
by_code={}
for e in all_entries:
    by_code.setdefault(e['code'], e)
print('total raw entries:', len(all_entries), 'unique codes:', len(by_code))
json.dump(list(by_code.values()), open('team22_raw_entries.json','w'), ensure_ascii=False, indent=1)

# load existing codes
exist=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
gj=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
gj_codes=set()
if isinstance(gj, list):
    for g in gj:
        inv=g.get('invite','')
        m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', inv)
        if m: gj_codes.add(m.group(1))
union=exist|gj_codes
print('existing:',len(exist),'groups.json codes:',len(gj_codes),'union:',len(union))
fresh=[e for e in by_code.values() if e['code'] not in union]
dup=len(by_code)-len(fresh)
print('fresh (not in union):', len(fresh), 'already known:', dup)
json.dump(fresh, open('team22_fresh_raw.json','w'), ensure_ascii=False, indent=1)

# section distribution of fresh
from collections import Counter
print(Counter(e['section'] for e in fresh))
print(Counter(e['source_file'] for e in fresh))
