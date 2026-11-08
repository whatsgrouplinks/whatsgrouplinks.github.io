#!/usr/bin/env python3
"""Team09 wave20261108: verify groupda candidates live via curl + og:title.
Rules: max 3 parallel, >=0.6s between check starts; 200 + non-empty
non-generic og:title = live; 200-empty retried once after a pause, then dead;
transport errors / 429 / 5xx -> pending (reason transport). Dead -> dropped.
Name prefers the live og:title (the true group name).
"""
import json, os, re, subprocess, time, html as ihtml
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
CANDS = os.path.join(WAVE, 'team09_gd_candidates.json')

UA1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
UA2 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
GENERIC_TITLES = {'whatsapp group', 'join this group on whatsapp', 'whatsapp'}
BAD_NAME = re.compile(r'porn|xxx|bokep|escort|call[\s\-]?girl|nude|sex\s*(video|group|chat)|desi49|kambi|18\s*\+|adult', re.I)
SCAM = re.compile(r'bitfinex|paypal[\s\-]?loader|money[\s\-]?mule|counterfeit|fake\s*(currency|note|money)|double\s+your\s+money', re.I)

COUNTRY_NAME = {'PK': 'Pakistan', 'IN': 'India', 'ID': 'Indonesia', 'NG': 'Nigeria',
                'LK': 'Sri Lanka', 'BD': 'Bangladesh', 'US': 'the United States',
                'GB': 'the United Kingdom', 'MY': 'Malaysia', 'SA': 'Saudi Arabia',
                'AE': 'the UAE', 'GH': 'Ghana', 'UG': 'Uganda', 'KE': 'Kenya',
                'ZA': 'South Africa', 'NP': 'Nepal'}

_last = [0.0]
_lock = Lock()

def fetch_og(code, ua):
    url = 'https://chat.whatsapp.com/' + code
    with _lock:
        wait = 0.6 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
    try:
        r = subprocess.run(['curl', '-sS', '-A', ua, '--max-time', '30',
                            '-o', '/tmp/gd_wa.html', '-w', '%{http_code}', url],
                           capture_output=True, text=True, timeout=40)
        http = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    except Exception:
        return None, None
    if http != 200:
        return http, None
    try:
        txt = open('/tmp/gd_wa.html', encoding='utf-8', errors='ignore').read()
    except Exception:
        return http, None
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', txt)
    if not m:
        return http, ''
    return http, ihtml.unescape(m.group(1)).strip()

def check(cand):
    code = cand['invite'].split('/')[-1]
    http, title = fetch_og(code, UA1)
    if http is None or http in (429, 500, 502, 503, 504, 0):
        time.sleep(5)
        http2, title2 = fetch_og(code, UA2)
        if http2 is None or http2 in (429, 500, 502, 503, 504, 0):
            return ('pending', cand, 'transport')
        http, title = http2, title2
    if http != 200:
        return ('dead', cand, f'http{http}')
    if not title:
        time.sleep(5)
        http, title = fetch_og(code, UA2)
        if http != 200 or not title:
            return ('dead', cand, 'empty-og-title-after-retry')
    if title.lower() in GENERIC_TITLES:
        return ('dead', cand, 'generic-title')
    return ('live', cand, title)

def blocked(name, title):
    s = (name or '') + ' ' + (title or '')
    if any(e in s for e in ADULT_EMOJI):
        return 'adult-emoji'
    if BAD_NAME.search(s):
        return 'porn-adult'
    if SCAM.search(s):
        return 'scam'
    return None

def main():
    cands = json.load(open(CANDS))
    print('candidates to verify:', len(cands))
    verified, pending, dropped = [], [], []
    with ThreadPoolExecutor(max_workers=3) as ex:
        for status, cand, info in ex.map(check, cands):
            name = cand['name']
            if status == 'live':
                title = info
                reason = blocked(name, title)
                if reason:
                    dropped.append((cand['invite'], reason, name, title))
                    print(f"DROP {reason}: {name} | og:{title}")
                    continue
                final_name = title if len(title) >= 3 else name
                country = cand.get('country') or 'International'
                cat = cand['category']
                if country == 'International':
                    desc = f"Join {final_name}, a WhatsApp group listed under {cat}."
                else:
                    desc = (f"Join {final_name}, a WhatsApp group listed under {cat} "
                            f"from {COUNTRY_NAME.get(country, country)}.")
                verified.append({'name': final_name, 'category': cat, 'country': country,
                                 'description': desc,
                                 'invite': cand['invite'], 'image': ''})
                print(f"LIVE {final_name} [{cat}/{country}] {cand['invite']}")
            elif status == 'pending':
                pending.append({**{k: cand[k] for k in ('name', 'category', 'country')},
                                'description': f"Join {cand['name']}, a WhatsApp group listed under {cand['category']}.",
                                'invite': cand['invite'], 'image': '', 'reason': 'transport'})
                print(f"PENDING {cand['invite']} ({info})")
            else:
                dropped.append((cand['invite'], info, name, ''))
                print(f"DEAD {info}: {name} {cand['invite']}")
    # final dedupe by code (keep first)
    seen, out = set(), []
    for g in verified:
        code = g['invite'].split('/')[-1]
        if code in seen:
            continue
        seen.add(code)
        out.append(g)
    with open(os.path.join(WAVE, 'team09-groupda.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    with open(os.path.join(WAVE, 'team09-groupda-pending.json'), 'w', encoding='utf-8') as f:
        json.dump(pending, f, indent=1, ensure_ascii=False)
    print(f"VERIFIED={len(out)} PENDING={len(pending)} DROPPED={len(dropped)}")
    with open(os.path.join(WAVE, 'team09_gd_dropped.json'), 'w', encoding='utf-8') as f:
        json.dump([{'invite': d[0], 'reason': d[1], 'name': d[2], 'og_title': d[3]} for d in dropped],
                  f, indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
