#!/usr/bin/env python3
"""Team39 probe: fetch listing pages, extract chat.whatsapp.com codes + context names."""
import re, sys, os, requests, pickle, html

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team39_work')
union = pickle.load(open(WD + '/union.pkl', 'rb'))
print('union size', len(union), file=sys.stderr)

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')

def probe(url, label):
    s = requests.Session()
    s.headers.update(UA)
    try:
        r = s.get(url, timeout=45, allow_redirects=True)
        print(f'{label}: HTTP {r.status_code} bytes={len(r.content)}', file=sys.stderr)
        if r.status_code != 200:
            return None, 0
        t = r.text
        codes = CODE_RE.findall(t)
        # count raw chat.whatsapp.com mentions
        raw = len(re.findall(r'chat\.whatsapp\.com', t))
        print(f'{label}: raw chat.whatsapp.com mentions={raw}, 20-24 codes={len(codes)} ({len(set(codes))} unique)', file=sys.stderr)
        open(f'{WD}/probe_{label}.html', 'w').write(t)
        new = [c for c in set(codes) if c not in union]
        print(f'{label}: NEW vs union: {len(new)}', file=sys.stderr)
        return t, len(new)
    except Exception as e:
        print(f'{label}: FETCH FAIL {e}', file=sys.stderr)
        return None, 0

if __name__ == '__main__':
    urls = [
        ('https://wahublink.com/entertainment-whatsapp-group-links/', 'wahublink_ent'),
        ('https://whatsagroupslinks.com/gym-whatsapp-group-links/', 'whatsagroupslinks_gym'),
        ('https://wagrouplinks.online/memes-whatsapp-group-links/', 'wagrouplinks_memes'),
        ('https://wagroupshub.com/single-girl-whatsapp-group-links/', 'wagroupshub_girls'),
        ('https://www.whtsagrouplinks.com/active-girls-whatsapp-groups-link/', 'whtsagrouplinks_girls'),
    ]
    for u, l in urls:
        probe(u, l)
