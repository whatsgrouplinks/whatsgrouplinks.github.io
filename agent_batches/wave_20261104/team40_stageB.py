#!/usr/bin/env python3
"""Team40 stage B: verify candidates via og:title (keep-alive session)."""
import re, os, json, html, requests
from concurrent.futures import ThreadPoolExecutor

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
PORN = ['porn', 'pornhub', 'xxx', 'nude', 'sex video', 'escort', 'call girl', 'fuck', 'dick',
        'pussy', 'boobs', 'anal', 'bokep', 'vcs', '18+', '🔞', '🥵', '🍆', '🍑', '💦', '👅', '👄', '💋']
TITLE_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"')

cands = json.load(open(WD + '/team40_stageA.json'))
codes = list(cands.keys())
print('verifying', len(codes), flush=True)

def check(code):
    s = requests.Session(); s.headers.update(UA)
    try:
        r = s.get('https://chat.whatsapp.com/' + code, timeout=60)
        m = TITLE_RE.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return (code, title, None)
    except Exception as e:
        return (code, None, str(e)[:90])

results = []
with ThreadPoolExecutor(max_workers=12) as ex:
    for res in ex.map(check, codes):
        results.append(res)
        code, title, err = res
        if title:
            print('OK', code, title[:55], flush=True)
        elif err:
            print('TRANSPORT', code, err[:60], flush=True)
        else:
            print('DEAD', code, flush=True)

verified, pending = [], []
porn_drops = 0
for code, title, err in results:
    info = cands[code]
    if title:
        if any(p in title.lower() for p in PORN):
            porn_drops += 1
            print('PORN-DROP', code, title[:50], flush=True)
            continue
        combo = title.lower()
        cc = 'International'
        if 'pakistan' in combo or '🇵🇰' in title: cc = 'PK'
        elif 'india' in combo or '🇮🇳' in title: cc = 'IN'
        elif 'indonesia' in combo or '🇮🇩' in title: cc = 'ID'
        elif 'nigeria' in combo or '🇳🇬' in title: cc = 'NG'
        elif 'bangladesh' in combo or '🇧🇩' in title: cc = 'BD'
        elif 'brazil' in combo or '🇧🇷' in title: cc = 'BR'
        verified.append({"name": title, "category": "Gaming", "country": cc,
                         "description": f"Active {title} WhatsApp gaming group. Join {title} to chat with fellow gamers, find teammates, and share gameplay tips.",
                         "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
    elif err:
        pending.append({"name": info['name'] or title or 'Gaming group', "category": "Gaming",
                        "country": "International",
                        "description": "Gaming WhatsApp group pending liveness recheck.",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                        "note": "transport failure"})

json.dump(verified, open(WD + '/team40-gaming-residual.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(WD + '/team40-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
print(f'VERIFIED={len(verified)} PENDING={len(pending)} PORN_DROPS={porn_drops}', flush=True)
