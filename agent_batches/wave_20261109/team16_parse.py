import re, json, html as H

existing = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
def norm(code):
    code = code.split('?')[0].split('#')[0].rstrip('/')
    return code

def parse_file(path, source):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    # tokenize: find h2 headings and li items in order
    # simpler: split by <li ...> blocks; track last h2 before each li
    events = []
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>|<li[^>]*>(.*?)</li>', txt, re.S):
        if m.group(1) is not None:
            t = re.sub(r'<[^>]+>','', m.group(1)).strip()
            events.append(('h2', t))
        else:
            events.append(('li', m.group(2)))
    out = {}
    cur = ''
    for kind, val in events:
        if kind == 'h2':
            cur = val
        else:
            codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]+)', val)
            if not codes: continue
            name = re.sub(r'<[^>]+>', ' ', val)
            name = H.unescape(name)
            name = re.sub(r'\s+', ' ', name).strip()
            # strip trailing "Join Now" etc
            name = re.sub(r'\s*(Join Now|Join Group|Join|Click Here).*$', '', name, flags=re.I).strip(' -–—:|')
            for c in codes:
                c = norm(c)
                if c not in out:
                    out[c] = {'code': c, 'name': name[:120], 'section': cur, 'source': source}
    return out

allc = {}
pages = {
 'team16_wglpk_home.html': 'whatsgroupslinkspk.com homepage',
 'team16_wglpk_all-groups.html': 'whatsgroupslinkspk.com/all-groups',
 'team16_wglpk_jobs-whatsapp-group-links.html': 'whatsgroupslinkspk.com/jobs',
 'team16_wglpk_poetry-whatsapp-group-links.html': 'whatsgroupslinkspk.com/poetry',
 'team16_wglpk_dubai-whatsapp-group-links.html': 'whatsgroupslinkspk.com/dubai',
}
for f, src in pages.items():
    d = parse_file(f, src)
    print(f, len(d))
    for k, v in d.items():
        allc.setdefault(k, v)
print('TOTAL unique codes:', len(allc))
fresh = {k: v for k, v in allc.items() if k not in existing}
print('FRESH (not in existing):', len(fresh))
json.dump(allc, open('team16_all_parsed.json','w'), indent=1, ensure_ascii=False)
json.dump(fresh, open('team16_fresh.json','w'), indent=1, ensure_ascii=False)
for k, v in list(fresh.items())[:40]:
    print(k, '|', v['section'], '|', v['name'])
