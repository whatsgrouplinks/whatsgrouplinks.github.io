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
slugs = ['bswnell8v3i6yjn5klpefu','cziwcbpfyh042axcvnzzzj','d49mrjmbhgobosewryxusi','e4kmpg9bswxgrcf9bkox8d','egnx4wxgg1da6xnlrznlax','ehuc7wa3x6adgkpudzisww','eragqcckhyidmzne1rz0xw','f4uhdchxqvchs3yc1puxbf','hexuha9nbfr0nsjt1tznrv','hxu35klknjnks4lvbbapai','ifhz4vcoosskateqhii9y3','inowymkjuoobg1jtlk2pb4','iukepbfzeoi4mqeaehhjnj','jh6u5ecj4ji9cveehulyue','jho142hs7esblnatve0p2c','jx15kwhiimp9r3ysab3mfr','l2nagbv0j0p2ymwv6z50lp','l98idhx9brwbhn7dttkzpi','lfo3dltmkjwfbqnggpmzfx','lpjrez6u10x4lr6z1fzbyi','lvwqgze0ju5kulvjklq3m4']
out = {}
for slug in slugs:
    url = f'https://groupsinvite.link/group/link/{slug}/'
    t = get(url)
    open(f'team21-page-{slug}.html','w').write(t)
    codes = sorted(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,})', t)))
    # name guess: og:title or h1
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', t)
    title = html.unescape(m.group(1)) if m else ''
    print(slug, '| bytes', len(t), '| codes:', codes, '| og:title:', repr(title[:90]))
    out[slug] = {'url': url, 'codes': codes, 'og_title': title, 'bytes': len(t)}
    time.sleep(2)
json.dump(out, open('team21-listing-extract.json','w'), indent=1)
