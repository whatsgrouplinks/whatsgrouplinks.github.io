import urllib.request, urllib.error, re, json, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
def fetch(url, timeout=60):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()
urls=[
 ('home','https://walink.pk/'),
 ('cat','https://walink.pk/category/whatsapp-group-links/'),
 ('pak-link','https://walink.pk/whatsapp-group-link-pakistan/'),
 ('girls','https://walink.pk/girls-whatsapp-group/'),
 ('desi-girl','https://walink.pk/desi-girl-whatsapp-group/'),
 ('viral-video','https://walink.pk/pakistan-viral-video-whatsapp-group/'),
 ('xxiv','https://walink.pk/whatsapp-group-xxiv-girl/'),
 ('1000-members','https://walink.pk/1000-members-whatsapp-group-link/'),
 ('81','https://walink.pk/81-whatsapp-group-link/'),
 ('porn','https://walink.pk/porn-whatsapp-group/'),
 ('sexy','https://walink.pk/sexy-whatsapp-group/'),
 ('xxx','https://walink.pk/xxx-whatsapp-group/'),
]
results={}
for name,url in urls:
    try:
        st,data=fetch(url)
        fn=f'team22_page_{name}.html'
        open(fn,'wb').write(data)
        codes=len(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', data.decode('utf-8','ignore'))))
        print(name, st, len(data), 'unique codes:', codes)
        results[name]={'url':url,'status':st,'bytes':len(data),'codes':codes}
        time.sleep(1)
    except Exception as e:
        print(name,'ERR',type(e).__name__,e)
        results[name]={'url':url,'error':str(e)}
# wp-json pages list for lead discovery
try:
    st,data=fetch('https://walink.pk/wp-json/wp/v2/pages?per_page=100')
    open('team22_wp_pages.json','wb').write(data)
    pages=json.loads(data)
    print('wp pages:', len(pages))
    for p in pages:
        print(' -', p.get('slug'), '|', p.get('link'))
except Exception as e:
    print('wp-json ERR', e)
json.dump(results, open('team22_fetch_log.json','w'), indent=1)
