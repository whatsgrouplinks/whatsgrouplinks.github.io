import re, html, json

def clean(s):
    s = html.unescape(s or '')
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip(' \t\r\n-–—:|•»«')
    return s.strip()

def extract_lists(path):
    """Section-aware extraction of <li>NAME - <a chat.whatsapp.com> items."""
    t = open(path, encoding='utf-8', errors='ignore').read()
    # split by h2/h3 headings keeping order
    parts = re.split(r'(<h[23][^>]*>.*?</h[23]>)', t, flags=re.S | re.I)
    section = ''
    out = []
    for p in parts:
        m = re.match(r'<h[23][^>]*>(.*?)</h[23]>', p, flags=re.S | re.I)
        if m:
            section = clean(m.group(1))
            continue
        # list items in this chunk
        for li in re.findall(r'<li[^>]*>(.*?)</li>', p, flags=re.S | re.I):
            cm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', li)
            if not cm: continue
            code = cm.group(1)
            # name = text before the anchor
            pre = li.split('<a ', 1)[0]
            name = clean(pre)
            name = re.sub(r'\s*(Join|Join Now|Join Group|–|-)\s*$', '', name).strip(' -–—:')
            out.append({'name': name, 'code': code, 'section': section, 'src': path})
        # table rows
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', p, flags=re.S | re.I):
            cm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', tr)
            if not cm: continue
            code = cm.group(1)
            cells = [clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.S | re.I)]
            name = cells[0] if cells else ''
            out.append({'name': name, 'code': code, 'section': section, 'src': path})
    return out

def extract_cards(path):
    """groupwa wagd-card extraction: cat, desc, link, country, language."""
    t = open(path, encoding='utf-8', errors='ignore').read()
    out = []
    for m in re.finditer(r'wagd-card"[^>]*data-cat="([^"]*)" data-desc="([^"]*)" data-link="(https://chat\.whatsapp\.com/([^"&]+))"[^>]*>(.*?)<div class="wagd-ft">', t, flags=re.S):
        cat, desc, link, code, body = m.groups()
        meta = re.findall(r'</svg>([^<]+)</span>', body)
        country = meta[0].strip() if len(meta) > 0 else ''
        lang = meta[1].strip() if len(meta) > 1 else ''
        out.append({'name': '', 'desc': html.unescape(desc), 'code': code, 'section': cat,
                    'country_raw': country, 'lang': lang, 'src': path})
    return out

if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        items = extract_lists(f)
        print(f, 'list items:', len(items))
        for it in items[:5]: print('   ', it)

def extract_paras(path):
    """<p>NAME ➪ <a chat.whatsapp.com> items (whatz style)."""
    t = open(path, encoding='utf-8', errors='ignore').read()
    parts = re.split(r'(<h[23][^>]*>.*?</h[23]>)', t, flags=re.S | re.I)
    section = ''
    out = []
    for p in parts:
        m = re.match(r'<h[23][^>]*>(.*?)</h[23]>', p, flags=re.S | re.I)
        if m:
            section = clean(m.group(1)); continue
        for para in re.findall(r'<p[^>]*>(.*?)</p>', p, flags=re.S | re.I):
            cm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', para)
            if not cm: continue
            code = cm.group(1)
            pre = para.split('<a ', 1)[0]
            name = clean(pre)
            name = re.sub(r'\s*(➪|⇒|>|Join.*)$', '', name).strip(' -–—:')
            out.append({'name': name, 'code': code, 'section': section, 'src': path})
    return out
