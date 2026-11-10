import urllib.request, re, json, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
def fetch(url, timeout=45):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()
for name,url in [('xxiv','https://walink.pk/whatsapp-group-xxiv-girl/'),
                 ('1000-members','https://walink.pk/1000-members-whatsapp-group-link/'),
                 ('81','https://walink.pk/81-whatsapp-group-link/')]:
    try:
        st,data=fetch(url)
        open(f'team22_page_{name}.html','wb').write(data)
        codes=len(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', data.decode('utf-8','ignore'))))
        print(name, st, len(data), 'unique codes:', codes, flush=True)
        time.sleep(1)
    except Exception as e:
        print(name,'ERR',type(e).__name__,e, flush=True)
try:
    st,data=fetch('https://walink.pk/wp-json/wp/v2/pages?per_page=100', timeout=30)
    open('team22_wp_pages.json','wb').write(data)
    pages=json.loads(data)
    print('wp pages:', len(pages))
    for p in pages:
        print(' -', p.get('slug'), '|', p.get('link'))
except Exception as e:
    print('wp-json ERR', type(e).__name__, e)
