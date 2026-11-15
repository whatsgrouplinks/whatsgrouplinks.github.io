import re, json, sys, html
from html.parser import HTMLParser

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
BAD = ('join','join group','join now','click here','link','join in','join link','join link – click here to join')
def clean(t): return html.unescape(re.sub(r'\s+',' ',t or '')).strip()

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []  # (code, name, section)
        self.stack = []
        self.section = ''
        self.in_h = False
        self.h_text = ''
        self.last_title = ''
        self.in_a = False; self.a_href=''; self.a_text=''
        self.row_cells=[]; self.in_tr=False
    def _title_ctx(self):
        for tag, attrs in reversed(self.stack):
            if tag in ('h1','h2','h3','h4','h5','h6','td','th'): return True
            if tag=='p' and ('heading' in attrs.get('class','') or 'title' in attrs.get('class','')): return True
        return False
    def handle_starttag(self, tag, attrs):
        d=dict(attrs); self.stack.append((tag,d))
        if tag in ('h1','h2','h3'): self.in_h=True; self.h_text=''
        if tag=='tr': self.in_tr=True; self.row_cells=[]
        if tag=='a': self.in_a=True; self.a_href=d.get('href',''); self.a_text=''
    def handle_endtag(self, tag):
        while self.stack and self.stack[-1][0]!=tag: self.stack.pop()
        if self.stack: self.stack.pop()
        if tag in ('h1','h2','h3') and self.in_h:
            self.in_h=False
            if tag in ('h1','h2'): self.section = clean(self.h_text)
        if tag=='tr': self.in_tr=False
        if tag=='a' and self.in_a:
            self.in_a=False
            m=CODE_RE.search(self.a_href or '')
            if m:
                code=m.group(1); name=clean(self.a_text)
                if not name or name.lower() in BAD:
                    cells=[c for c in self.row_cells if c and c.lower() not in BAD]
                    name=cells[0] if cells else self.last_title
                self.items.append((code,name,self.section))
    def handle_data(self, data):
        t=clean(data)
        if not t: return
        if self.in_a: self.a_text+=data
        if self.in_h: self.h_text+=data
        if self._title_ctx(): self.last_title=t
        if self.stack and self.stack[-1][0] in ('td','th'): self.row_cells.append(t)

for path in sys.argv[1:]:
    p=P(); p.feed(open(path,encoding='utf-8',errors='ignore').read())
    secs={}
    for c,n,s in p.items: secs.setdefault(s,[]).append((c,n))
    print(f"== {path}: {len(p.items)} codes, {len(secs)} sections")
    for s,items in secs.items():
        print(f"  [{s}] {len(items)}")
    json.dump({f"{path}":[(c,n,s) for c,n,s in p.items]}, open("team25_raw/sections_"+re.sub(r'[^A-Za-z0-9]+','_',path)+".json","w"), indent=1, ensure_ascii=False)
