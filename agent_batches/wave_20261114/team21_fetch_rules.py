import requests, re, json, time, html
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
s = requests.Session(); s.headers.update(UA)
def get(url, tries=3):
    for i in range(tries):
        try:
            r = s.get(url, timeout=60)
            if r.status_code == 200 and r.text.strip(): return r.text
            print('  status', r.status_code, url)
        except Exception as e:
            print('  err', e, url)
        time.sleep(4*(i+1))
    return ''
slugs = ['bswnell8v3i6yjn5klpefu','eragqcckhyidmzne1rz0xw','ifhz4vcoosskateqhii9y3','iukepbfzeoi4mqeaehhjnj','l98idhx9brwbhn7dttkzpi']
out = {}
for slug in slugs:
    url = f'https://groupsinvite.link/group/rules/{slug}/'
    t = get(url)
    open(f'team21-rules-{slug}.html','w').write(t)
    codes = sorted(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,})', t)))
    print(slug, '| bytes', len(t), '| codes:', codes)
    out[slug] = codes
    time.sleep(2)
json.dump(out, open('team21-rules-extract.json','w'), indent=1)
