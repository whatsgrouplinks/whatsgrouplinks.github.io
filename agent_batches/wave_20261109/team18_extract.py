import json, re, html
ex = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
def norm(c): return c.split('?')[0].split('#')[0].rstrip('/')
def extract(fname, source):
    raw = open('team18_raw/'+fname, encoding='utf-8', errors='ignore').read()
    # find codes with position; grab preceding 400 chars of tag-stripped text
    out = {}
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})', raw):
        code = norm(m.group(1))
        if code in ex or code in out: continue
        seg = raw[max(0,m.start()-600):m.start()]
        seg = re.sub(r'<script.*?</script>', ' ', seg, flags=re.S|re.I)
        seg = re.sub(r'<style.*?</style>', ' ', seg, flags=re.S|re.I)
        seg = re.sub(r'<[^>]+>', ' ', seg)
        seg = html.unescape(seg)
        seg = re.sub(r'\s+', ' ', seg).strip()[-300:]
        out[code] = {'code': code, 'from_url': source, 'context': seg}
    return list(out.values())
res = {}
res['wagroupshub'] = extract('probe_94e5f0c9.html', 'https://wagroupshub.com/')
res['groupsnest'] = extract('probe_3e35f267.html', 'https://groupsnest.com/')
res['wglfinder'] = extract('probe_c6d98798.html', 'https://wglfinder.com/')
for k,v in res.items():
    print(k, 'fresh:', len(v))
    json.dump(v, open(f'team18_raw/{k}_fresh.json','w'), indent=1)
# overlap check vs groupssor
gs = set(x['code'] for x in json.load(open('team18_raw/groupssor_fresh.json')))
for k,v in res.items():
    ov = sum(1 for x in v if x['code'] in gs)
    print(k, 'overlap with groupssor fresh:', ov)

res2 = {}
res2['groupjoin_ng'] = extract('team18_groupjoin_ng.html', 'https://www.groupjoin.link/country/161')
res2['groupjoin_za'] = extract('gj_za.html', 'https://www.groupjoin.link/country/204')
res2['groupjoin_dz'] = extract('gj_dz.html', 'https://www.groupjoin.link/country/4')
res2['groupwa_zw'] = extract('gwa_zw.html', 'https://groupwa.com/country/zimbabwe-whatsapp-groups/')
res2['groupwa_jeddah'] = extract('gwa_jeddah.html', 'https://groupwa.com/city/jeddah-whatsapp-groups/')
res2['links77_ar'] = extract('links77_ar.html', 'https://77links.com/arabic-whatsapp-group-links/')
for k,v in res2.items():
    print(k, 'fresh:', len(v))
    json.dump(v, open(f'team18_raw/{k}_fresh.json','w'), indent=1)

res3 = {}
res3['groupjoin_ng2'] = extract('gj_ng2.html', 'https://www.groupjoin.link/country/161?page=2')
res3['groupjoin_za2'] = extract('gj_za2.html', 'https://www.groupjoin.link/country/204?page=2')
res3['groupjoin_dz2'] = extract('gj_dz2.html', 'https://www.groupjoin.link/country/4?page=2')
res3['dubai'] = extract('dubai.html', 'https://www.grouplinksforyou.com/2023/04/dubai-whatsapp-group-links.html')
res3['kenya'] = extract('kenya.html', 'https://techsslash.com/kenya-whatsapp-group-links/')
for k,v in res3.items():
    print(k, 'fresh:', len(v))
    json.dump(v, open(f'team18_raw/{k}_fresh.json','w'), indent=1)
