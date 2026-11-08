import re, html, json, glob

BS = chr(92)
def records(path):
    h = open(path, encoding='utf-8').read()
    q = BS + '"'
    eq = re.escape(q)
    parts = re.split(re.escape('{' + q + 'id' + q + ':'), h)
    recs = []
    for p in parts[1:]:
        chunk = '{' + q + 'id' + q + ':' + p
        def field(name):
            b2 = BS + BS  # regex-escaped backslash
            pat = eq + re.escape(name) + eq + ':' + eq + '((?:[^"' + b2 + ']|' + b2 + '[^"])*)' + eq
            m = re.search(pat, chunk)
            if not m: return ''
            v = m.group(1).replace(BS + 'u0026','&').replace(BS + 'n',' ').replace(BS + '"','"')
            return html.unescape(v)
        m_id = re.match(r'(\d+|"[^"]*")', p)
        rec = {
            'id': m_id.group(1) if m_id else 'x',
            'name': field('name'), 'invite': field('invite_link'),
            'image': field('image_url'), 'desc': field('description'),
            'created': field('created_at'), 'updated': field('updated_at'),
        }
        b2 = BS + BS
        mc = re.search(eq + 'category' + eq + r':\{.*?' + eq + 'name' + eq + ':' + eq + '([^"' + b2 + ']+)', chunk)
        rec['cat'] = mc.group(1) if mc else ''
        mc2 = re.search(eq + 'country' + eq + r':\{.*?' + eq + 'name' + eq + ':' + eq + '([^"' + b2 + ']+)', chunk)
        rec['country'] = mc2.group(1) if mc2 else ''
        recs.append(rec)
    return recs

if __name__ == '__main__':
    from collections import Counter
    cc = Counter(); tot = 0
    for f in sorted(glob.glob('_cat_*.html')):
        rs = records(f); tot += len(rs)
        for r in rs: cc[r['country']] += 1
        print(f, len(rs))
    print('total', tot); print(sorted(cc.items()))
    rs = records('_cat_business.html')
    print(json.dumps(rs[0], indent=1, ensure_ascii=False)[:700])
