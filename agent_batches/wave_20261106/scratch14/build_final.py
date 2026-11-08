#!/usr/bin/env python3
"""team14: build final verified file directly from combined-run source.
Same sanitize/drop logic as finalize.py; writes the full JSON array to the
wave dir in one go (exec writes work again as of 08:44 UTC)."""
import json, re, sys

wrap = json.load(open('/tmp/jarvis-tool-output-sEM9dn.json', encoding='utf-8'))
raw = wrap['stdout']
i = raw.find('VERIFIED_JSON ')
j = raw.find('\nPENDING_JSON', i)
live = json.loads(raw[i + len('VERIFIED_JSON '):j])

PHONE_RE = re.compile(r'\+?\(?\d[\d\s\-().]{6,}\d')
URL_RE = re.compile(r'https?://\S+')
WA_RE = re.compile(r'wa\.me/\S+')

def sanitize_desc(d, cat, country):
    d = (d or '')
    d = URL_RE.sub('', d)
    d = WA_RE.sub('', d)
    d = PHONE_RE.sub('', d)
    d = re.sub(r'[ \t]+', ' ', d)
    d = re.sub(r'\n\s*\n+', '\n', d).strip(' \n.,;:*')
    d = d.strip()
    if len(d) < 15:
        cname = {"funny": "funny jokes, memes and comedy", "health": "health, fitness and wellness tips"}.get(cat, cat)
        ctry = "" if country in ("International", "") else f" from {country}"
        return f"Join this {cat} WhatsApp group{ctry} to enjoy {cname} with active members. Chat, share and have fun with the community every day."
    return d

DROP_CODES = {
    'IkcNyqOeDIa4Z5Jf0boxnV': 'scam-xauusd-credential-harvest',
    'Bd8DimSMgKHKA8LzeABPGN': 'sax-name',
    'H6lWlNl2AtVIJpgAffyQXx': 'adult-hot-video',
    'CYEAO8o6nIBEIwJQomgsFI': 'adult-video-call-service-girls',
    'FJ2f95IpRbpGz2E6HpXv9Z': 'adult-18plus-marker',
    'GonNGeoj2uADnwz9291Ipn': 'scam-forex-account-manager',
    'HRXuJJK5agJITpoqnfalfO': 'adult-enlargement-spam',
    'CpLiBl6OIsHAGoQL7JJKGf': 'adult-emoji-big-offers',
    'FvQQCwAaFm35a6RwAJMzHj': 'adult-emoji-bikini-group',
    'DpnHxustDtK2FOHO5XV00O': 'porn-star-fan-group',
    'EfWutg0ZYYO6h19Pvwt8uJ': 'adult-non-veg-slang',
    'EdNAGDW7DHr9MTyyjkoL7N': 'adult-sinhala-vael-porn-paradise',
}

out = []
dropped = []
for x in live:
    if x['code'] in DROP_CODES:
        dropped.append((DROP_CODES[x['code']], x['code'])); continue
    d = sanitize_desc(x.get('description', ''), x['category'], x['country'])
    out.append({"name": x['name'], "category": x['category'], "country": x['country'],
                "description": d, "invite": x['invite'], "image": ""})

dest = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/team14-p5-gjl-funny-health.json'
with open(dest, 'w', encoding='utf-8') as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
    f.write('\n')
print(f"WROTE {len(out)} items, dropped {len(dropped)} -> {dest}")
