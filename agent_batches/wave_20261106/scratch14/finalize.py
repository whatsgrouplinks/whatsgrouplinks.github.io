#!/usr/bin/env python3
"""team14 final sanitize: read combined VERIFIED_JSON from saved exec output,
drop XAUUSD credential-harvest + 'sax' group, strip phones/URLs from descriptions,
print one chunk of the final verified JSON array (indent=1) for muse.write.
Usage: finalize.py <chunk 0..2>  -- prints CHUNK_START/CHUNK_END wrapped content.
Also prints a summary to stderr.
"""
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
print(f"SUMMARY kept={len(out)} dropped={dropped}", file=sys.stderr)
n = len(out)
chunks = [out[0:90], out[90:180], out[180:]]
chunk = int(sys.argv[1])
print(f"CHUNK {chunk} of 3, items {len(chunks[chunk])}")
print("CHUNK_START")
# raw items only (no array brackets) for muse.write stitching
print(",\n".join(json.dumps(it, ensure_ascii=False, indent=1) for it in chunks[chunk]))
print("CHUNK_END")
