import requests, re, json, time
from xml.etree import ElementTree as ET

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
s = requests.Session(); s.headers.update(UA)
base = 'https://groupsinvite.link'

def get(url, tries=3):
    for i in range(tries):
        try:
            r = s.get(url, timeout=60)
            if r.status_code == 200 and r.text.strip():
                return r.text
            print('  status', r.status_code, 'for', url)
        except Exception as e:
            print('  err', e, url)
        time.sleep(5*(i+1))
    return None

idx = get(base + '/sitemap.xml')
open('team21-sitemap-index.xml','w').write(idx or '')
print('index bytes:', len(idx or ''))
subs = re.findall(r'<loc>(https://groupsinvite\.link/[^<]*sitemap[^<]*)</loc>', idx or '')
print('sub-sitemaps:', subs)
all_locs = []
index_lastmods = {}
for sub in subs:
    txt = get(sub)
    fn = 'team21-' + sub.rsplit('/',1)[-1]
    open(fn,'w').write(txt or '')
    locs = re.findall(r'<loc>([^<]+)</loc>', txt or '')
    lms = re.findall(r'<lastmod>([^<]+)</lastmod>', txt or '')
    print(sub, 'entries:', len(locs), 'lastmod sample:', sorted(set(lms))[:3], 'max:', max(lms) if lms else None)
    all_locs.extend(locs)
    index_lastmods[sub] = {'count': len(locs), 'lastmods': sorted(set(lms))}
json.dump({'index_lastmods': index_lastmods, 'total_locs': len(all_locs), 'locs': sorted(set(all_locs))}, open('team21-sitemap-all.json','w'), indent=1)
print('TOTAL unique locs:', len(set(all_locs)))
# homepage
hp = get(base + '/')
open('team21-homepage.html','w').write(hp or '')
print('homepage bytes:', len(hp or ''))
hp_links = sorted(set(re.findall(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', hp or '')))
print('homepage listing slugs:', len(hp_links))
json.dump(hp_links, open('team21-homepage-slugs.json','w'), indent=1)
# find page totalCount
f = get(base + '/group/find/')
open('team21-find.html','w').write(f or '')
m = re.search(r'totalCount[^0-9]{0,5}(\d+)', f or '')
print('find totalCount:', m.group(1) if m else None, '| find bytes:', len(f or ''))
