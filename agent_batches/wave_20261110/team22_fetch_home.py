import urllib.request, re, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
def fetch(url, timeout=60):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data=r.read()
        return r.status, data
st, data = fetch('https://walink.pk/')
print('status', st, 'bytes', len(data))
open('team22_home.html','wb').write(data)
html=data.decode('utf-8','ignore')
codes=re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', html)
print('codes found:', len(codes), 'unique:', len(set(codes)))
channels=re.findall(r'whatsapp\.com/channel/([A-Za-z0-9_-]+)', html)
print('channels:', len(channels))
hrefs=re.findall(r'href="(https?://walink\.pk[^"]*)"', html)
from collections import Counter
paths=Counter()
for h in hrefs:
    p=h.replace('https://walink.pk','').split('?')[0]
    paths[p]+=1
print('distinct internal hrefs:', len(paths))
for p,c in sorted(paths.items())[:120]:
    print(c, p)
