#!/usr/bin/env python3
"""team26 miner: fetch directory pages, extract (name, code) pairs."""
import json, re, sys, time
import requests
from html.parser import HTMLParser

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})')

class RowParser(HTMLParser):
    """Collect text of each <li> / <tr> / <p> block; attach wa codes found inside."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, textlist)
        self.rows = []           # (text, code)
        self.cur_heading = None  # (tag, textlist) for h1-h4
        self.last_heading = ''
    def handle_starttag(self, tag, attrs):
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.cur_heading = (tag, [])
        if tag in ('li', 'tr', 'p', 'div', 'td'):
            self.stack.append((tag, []))
        if tag == 'a':
            href = dict(attrs).get('href', '')
            m = CODE_RE.search(href)
            if m:
                # attach to the enclosing <tr> or <li> (name lives in a sibling cell),
                # else to the outermost open container
                target = None
                for t, txt in self.stack:
                    if t in ('tr', 'li'):
                        target = txt
                if target is None and self.stack:
                    target = self.stack[0][1]
                txt = ' '.join(' '.join(target or []).split())
                self.rows.append((txt, m.group(1), self.last_heading))
    def handle_data(self, data):
        if self.cur_heading is not None:
            self.cur_heading[1].append(data)
        if self.stack:
            self.stack[-1][1].append(data)
    def handle_endtag(self, tag):
        if tag in ('h1', 'h2', 'h3', 'h4') and self.cur_heading is not None:
            h = re.sub(r'\s+', ' ', ''.join(self.cur_heading[1])).strip()
            if h:
                self.last_heading = h
            self.cur_heading = None
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

def fetch(url, session, timeout=60):
    r = session.get(url, timeout=timeout)
    return r

def mine(url, session):
    try:
        r = fetch(url, session)
    except Exception as e:
        return {'url': url, 'error': f'{type(e).__name__}: {e}', 'rows': []}
    if r.status_code != 200:
        return {'url': url, 'error': f'HTTP {r.status_code}', 'rows': []}
    p = RowParser()
    try:
        p.feed(r.text)
    except Exception:
        pass
    # also catch bare codes in text (non-anchor)
    codes_in_text = set(CODE_RE.findall(r.text))
    seen = {c for _, c, _ in p.rows}
    extra = [('', c, '') for c in codes_in_text - seen]
    rows = p.rows + extra
    # clean names: strip 'Join', 'Join Group', 'Click Here' etc.
    out = []
    for txt, code, section in rows:
        name = re.sub(r'\s+', ' ', txt).strip()
        name = re.sub(r'(?i)\s*(join group|join now|join|click here|link)\s*$', '', name).strip(' -–—|•')
        name = re.sub(r'(?i)^(join group|join now|join|click here)\s*', '', name).strip()
        out.append({'name': name, 'code': code, 'section': section})
    return {'url': url, 'status': r.status_code, 'rows': out, 'html_len': len(r.text)}

if __name__ == '__main__':
    urls = json.load(open(sys.argv[1]))
    s = requests.Session(); s.headers.update(UA)
    results = []
    for u in urls:
        res = mine(u, s)
        n = len(res.get('rows', []))
        print(f"{u} -> {res.get('error', 'ok')} rows={n}", flush=True)
        results.append(res)
        time.sleep(2)
    json.dump(results, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    print('saved', sys.argv[2])
