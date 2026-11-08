"""TEAM16: verify candidate codes via og:title with keep-alive session; build final files."""
import re, json, html, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

TDIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team16'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
ISO = {'Global': 'International', 'India': 'IN', 'Pakistan': 'PK', 'Spain': 'ES',
       'United States': 'US', 'Ghana': 'GH', 'Egypt': 'EG', 'Morocco': 'MA'}
CATMAP = {'Animation': 'Entertainment', 'Business': 'Business', 'Cryptocurrency': 'Crypto',
          'Earning': 'Finance', 'Education': 'Education', 'Finance': 'Finance',
          'Football': 'Sports', 'Friendship': 'Friendship', 'Gaming': 'Gaming',
          'Movies': 'Movies', 'Uncategorized': 'Other'}
COUNTRY_WORD = {'International': 'international', 'IN': 'Indian', 'PK': 'Pakistani',
                'ES': 'Spanish', 'US': 'American', 'GH': 'Ghanaian', 'EG': 'Egyptian',
                'MA': 'Moroccan'}

STOP = {'flag': False}

def make_session():
    s = requests.Session(); s.headers.update(UA); return s

def check(code):
    if STOP['flag']: return code, 'stopped', ''
    s = make_session()
    try:
        r = s.get('https://chat.whatsapp.com/' + code, timeout=50)
        if r.status_code == 429:
            STOP['flag'] = True; return code, 'rate-limited', ''
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return code, ('verified' if title else 'dead'), title
    except Exception as e:
        return code, 'transport', type(e).__name__
    finally:
        s.close()

def describe(name, site_cat, iso, site_desc):
    cw = COUNTRY_WORD.get(iso, 'global')
    catw = site_cat.lower()
    base = site_desc.strip()
    if len(base) > 140: base = base[:137].rsplit(' ', 1)[0] + '...'
    d = 'A %s %s WhatsApp group%s: %s' % (cw, catw,
        ' for members around the world' if iso == 'International' else ' community',
        base if base else 'members chat, share updates and connect daily')
    d = re.sub(r'\s+', ' ', d).strip()
    if 'groupwhat' in d.lower() or 'http' in d.lower():
        d = 'A %s %s WhatsApp group where members connect daily, share updates, tips and ideas.' % (cw, catw)
    return d

def main():
    cands = json.load(open(TDIR + '/_t16_cands.json'))
    print('to verify:', len(cands), flush=True)
    results = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, c['code']): c for c in cands}
        n = 0
        for f in as_completed(futs):
            code, status, title = f.result()
            results[code] = {'status': status, 'title': title}
            n += 1
            if STOP['flag']:
                print('RATE LIMITED - stopping', flush=True); break
            if n % 20 == 0:
                v = sum(1 for r in results.values() if r['status'] == 'verified')
                print('%d/%d verified=%d' % (n, len(cands), v), flush=True)
    v = sum(1 for r in results.values() if r['status'] == 'verified')
    print('FINAL checked=%d verified=%d stopped=%s' % (len(results), v, STOP['flag']), flush=True)
    json.dump(results, open(TDIR + '/_t16_verify.json', 'w'))

    verified, pending = [], []
    seen_codes = set()
    for c in cands:
        code = c['code']
        if code in seen_codes: continue
        seen_codes.add(code)
        st = results.get(code, {}).get('status', 'missing')
        title = results.get(code, {}).get('title', '')
        r = c['rec']
        name = (r.get('name') or '').strip() or title
        if not name: continue
        site_cat = r.get('category', {}).get('name', '') or 'Uncategorized'
        iso = ISO.get(r.get('country', {}).get('name', ''), 'International')
        img = (r.get('image_url') or '').strip()
        if not (img.startswith('https://pps.whatsapp.net') or img.startswith('https://mmg.whatsapp.net')
                or img.startswith('https://static.whatsapp.net')):
            img = ''
        item = {'name': name[:120], 'category': CATMAP.get(site_cat, 'Other'), 'country': iso,
                'description': describe(name, CATMAP.get(site_cat, 'Other'), iso, r.get('description') or ''),
                'invite': 'https://chat.whatsapp.com/' + code, 'image': img}
        if st == 'verified':
            verified.append(item)
        elif st in ('transport', 'rate-limited', 'stopped', 'missing'):
            item['note'] = 'transport failure' if st in ('transport', 'missing') else 'rate-limited'
            pending.append(item)
    json.dump(verified, open(TDIR + '/team16-groupwhat.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(TDIR + '/team16-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    print('verified=%d pending=%d' % (len(verified), len(pending)), flush=True)

if __name__ == '__main__':
    main()
