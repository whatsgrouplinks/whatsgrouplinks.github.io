import re, pickle, requests, json, html, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
OG_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.I)

# hard-rule exclusions: drugs, satta, pump-signal/scam crypto
EXCLUDE = {
 'EeZikmMnZ2B3LRgrNffcA9': 'drugs (meth plug)',
 'HlCzzR1JwD48acLN1mf7KZ': 'satta/gambling (SURE SHOT VIP SASI)',
 'Kjn6kELpbGi1wiNChWHRk3': 'crypto pump signals (scam)',
 'EY2iqRdP0yqGSfyVKwETee': 'crypto pump signals (scam)',
 'C14wQt4eG4q94I90O62J1A': 'VIP crypto signals (scam)',
 'KxCwoAMg8Zh2E1Z018E8Qd': 'crypto signals (scam)',
 'Jf9mjRezspQ1eCTAuE1PaW': 'crypto buy/sell signals (scam)',
 'B9kd2RJhhLELbhVQyXPvhm': "crypto tech signals (scam)",
}

pairs = json.load(open('candidates_named.json'))
# add search-extracted codes
pairs.update({
 'HNZlVa0lTQYLsRDGB4H6CY': ['North America Offer Holder WhatsApp Group 2026', 'qub.ac.uk'],
 'GuUBKpzlUnmEXBRmAHiW5j': ['UYDMUN 2026 Model UN community', 'mymun.com'],
 'GULbpIhspRXI1DgoZjXN7w': ['Crocheting at Yale', 'oiss.yale.edu'],
 'GZDTEHLOCYiCkmmjme8Sgm': ['Prism Club - Weill Cornell', 'gradschool.weill.cornell.edu'],
 'G5RNZPuGUKnKn2VMBBDQNw': ['Rice Business Student Association for Professionals', 'jones.campusgroups.com'],
 'H7RLfktgUNZ90lRJsTuiBA': ['Psychology Club - Edinburg', 'unis10.com'],
})

def check(code):
    s = requests.Session()
    s.mount('https://', HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=Retry(total=1, backoff_factor=1)))
    try:
        r = s.get(f'https://chat.whatsapp.com/{code}', headers=UA, timeout=55)
        m = OG_RE.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return (code, 'ok' if title else 'dead', title)
    except Exception as e:
        return (code, 'transport', repr(e)[:80])

results = {}
codes = [c for c in pairs if c not in EXCLUDE]
with ThreadPoolExecutor(max_workers=10) as ex:
    for code, status, title in ex.map(check, codes):
        results[code] = {'status': status, 'og_title': title, 'src_name': pairs[code][0], 'src': pairs[code][1]}
        print(code, status, '|', title[:60], flush=True)

import sys
sys.stdout.write(json.dumps(results))
sys.stdout.write('\n')
ok = sum(1 for v in results.values() if v['status']=='ok')
dead = sum(1 for v in results.values() if v['status']=='dead')
tr = sum(1 for v in results.values() if v['status']=='transport')
print(f'VERIFIED={ok} DEAD={dead} TRANSPORT={tr} EXCLUDED={len(EXCLUDE)}', file=sys.stderr, flush=True)
