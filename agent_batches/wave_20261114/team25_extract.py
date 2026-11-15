import re, json, sys, html
from html.parser import HTMLParser

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
BAD = ('join','join group','join now','click here','link','join in','join link','join link – click here to join')

def clean(t):
    return html.unescape(re.sub(r'\s+', ' ', t or '')).strip()

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = {}
        self.stack = []  # (tag, attrs)
        self.last_title = ''
        self.in_a = False
        self.a_href = ''
        self.a_text = ''
        self.row_cells = []
        self.in_tr = False
    def _title_ctx(self):
        for tag, attrs in reversed(self.stack):
            if tag in ('h1','h2','h3','h4','h5','h6','td','th','strong'):
                return True
            if tag == 'p':
                cls = attrs.get('class','')
                if 'heading' in cls or 'title' in cls:
                    return True
        return False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.stack.append((tag, d))
        if tag == 'tr':
            self.in_tr = True; self.row_cells = []
        elif tag == 'a':
            self.in_a = True; self.a_href = d.get('href',''); self.a_text = ''
    def handle_endtag(self, tag):
        while self.stack and self.stack[-1][0] != tag:
            self.stack.pop()
        if self.stack: self.stack.pop()
        if tag == 'tr': self.in_tr = False
        elif tag == 'a' and self.in_a:
            self.in_a = False
            m = CODE_RE.search(self.a_href or '')
            if m:
                code = m.group(1)
                name = clean(self.a_text)
                if not name or name.lower() in BAD:
                    cells = [c for c in self.row_cells if c and c.lower() not in BAD]
                    name = cells[0] if cells else self.last_title
                if code not in self.items or (name and len(name) > len(self.items[code])):
                    self.items[code] = name
    def handle_data(self, data):
        t = clean(data)
        if not t: return
        if self.in_a: self.a_text += data
        if self._title_ctx():
            self.last_title = t
        if self.stack and self.stack[-1][0] in ('td','th'):
            self.row_cells.append(t)

def extract(path):
    p = P()
    p.feed(open(path, encoding='utf-8', errors='ignore').read())
    return p.items

if __name__ == "__main__":
    out = {}
    for path in sys.argv[1:]:
        items = extract(path)
        out[path] = items
        print(f"{path}: {len(items)} codes")
        for c, n in items.items():
            print(f"  {c} | {n[:100]}")
    json.dump(out, open("team25_raw/extracted.json","w"), indent=1, ensure_ascii=False)
