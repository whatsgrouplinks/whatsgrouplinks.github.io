#!/usr/bin/env python3
"""Team33 pending-retry verification: team14 (groupjoin.link) + team25R (linkado.app)."""
import json, re, html, threading, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WORK = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
OG = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', re.I | re.S)
OG2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]*property=["\']og:title["\']', re.I | re.S)

PORN = re.compile(r'pornhub|xxx|nude|sex video|escort|call girl|fuck|dick|pussy|boobs|anal|\bbokep\b|\bporn\b|\bporno\b|\berotic\b|مزا دینے|مزہ دینے|🥵|🍆|🍑|🔞|💦|👅|👄|💋|📞.*(?:girl|escort)', re.I)

CATMAP = {
 'Money':'Finance','Entertainment':'Entertainment','Business':'Business','Comedy':'Funny',
 'Education':'Education','News & Politics':'News','Jobs':'Jobs','Online Shopping':'Buy-Sell',
 'Health':'Health','Friendship':'Friendship','Sports & Fitness':'Sports','Gaming':'Gaming',
 'Travel & Tourism':'Travel','Beauty & Fashion':'Other','Quotes':'Other','Flirting':'Friendship',
 'Love & Relationship':'Friendship','Pets & Animals':'Pets','Photography':'Other','Music':'Music',
 'Science & Technology':'Technology','Spiritual':'Other','Earn Money Online':'Finance',
 'Autos & Vehicles':'Other','Food & Recipes':'Food','Fan Club':'Entertainment','Other':'Other',
 'Advertising':'Business','Investment':'Finance','Comics':'Funny','Art & Design':'Other',
 'E':'Other','Deals & Offers':'Buy-Sell',
}
CNAMES = {'PK':'Pakistani','IN':'Indian','LK':'Sri Lankan','ID':'Indonesian','NG':'Nigerian',
 'MY':'Malaysian','BD':'Bangladeshi','US':'American','AE':'Emirati','CA':'Canadian','GB':'British',
 'UG':'Ugandan','JM':'Jamaican','MA':'Moroccan','BR':'Brazilian','AE':'Emirati','SA':'Saudi',
 'ZA':'South African','GH':'Ghanaian','KE':'Kenyan','TZ':'Tanzanian','PH':'Filipino','VN':'Vietnamese',
 'TH':'Thai','SG':'Singaporean','EG':'Egyptian','NP':'Nepali','AU':'Australian','DE':'German','FR':'French',
 'ES':'Spanish','IT':'Italian','NL':'Dutch','PT':'Portuguese','MX':'Mexican','AR':'Argentinian','CO':'Colombian'}
CWORDS = {'Sports':'sports fans','Gaming':'gamers','Jobs':'job seekers','Education':'learners',
 'Entertainment':'entertainment lovers','Friendship':'friends','News':'news followers','Islamic':'members',
 'Business':'entrepreneurs','Finance':'finance enthusiasts','Buy-Sell':'buyers and sellers',
 'Health':'health-conscious members','Community':'community members','Technology':'tech enthusiasts',
 'Crypto':'crypto enthusiasts','Travel':'travellers','Music':'music lovers','Movies':'movie fans',
 'Food':'food lovers','Pets':'pet lovers','Funny':'fun lovers','Girls':'members',
 'Regional':'community members','Other':'members'}

_local = threading.local()
_stop429 = threading.Event()
_lock = threading.Lock()

def get_session():
    s = getattr(_local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
        _local.s = s
    return s

def og_title(code):
    url = f'https://chat.whatsapp.com/{code}'
    for _ in range(2):
        if _stop429.is_set():
            return ('ratelimit', None)
        try:
            r = get_session().get(url, timeout=45, allow_redirects=True)
            if r.status_code == 429:
                _stop429.set(); return ('ratelimit', None)
            m = OG.search(r.text) or OG2.search(r.text)
            if not m:
                return ('dead', None)
            t = html.unescape(m.group(1)).strip()
            return ('live' if t else 'dead', t)
        except requests.RequestException:
            _local.s = None
            return ('transport', None)
    return ('transport', None)

def clean_title(t):
    t = re.sub(r'[^\x00-\x7F\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F\u00A0-\u024F]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()[:120]

def make_desc(name, cat, cc):
    nat = CNAMES.get(cc, 'international')
    who = CWORDS.get(cat, 'members')
    words = [w for w in re.findall(r'[A-Za-z\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F]{3,}', name) if len(w) > 2][:8]
    topic = ' '.join(words[:5]) if words else 'general chat'
    return (f"A {nat} WhatsApp group about {topic} where {who} connect and chat every day. "
            f"Active {cat.lower()} discussions, updates and friendly conversation in one lively group.")

def build_items():
    kept = json.load(open(WORK + '_team33_verify_input.json'))
    stats = json.load(open(WORK + '_team33_stats.json'))
    items = []
    for rec in kept:
        r = rec['record']
        items.append({'src': 'team14', 'code': r['code'], 'title': r.get('title') or '',
                      'cat_name': r.get('cat_name') or '', 'country': (r.get('country') or 'International')[:2],
                      'note': rec.get('note', '')})
    for rec in stats['t25']:
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', rec.get('invite', ''))
        items.append({'src': 'team25R', 'code': m.group(1), 'title': rec.get('name') or '',
                      'cat_name': rec.get('category') or '', 'country': (rec.get('country') or 'International')[:2],
                      'note': rec.get('note', ''), 'raw': rec})
    return items

def main():
    items = build_items()
    total = len(items)
    verified, pending, drops = [], [], {'porn': 0, 'dead': 0}
    done = [0]
    def work(it):
        if _stop429.is_set():
            return ('ratelimit', it, None)
        st, t = og_title(it['code'])
        return (st, it, t)
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = {ex.submit(work, it): it for it in items}
        for f in as_completed(futs):
            st, it, t = f.result()
            with _lock:
                done[0] += 1
                if done[0] % 500 == 0:
                    print(f'... {done[0]}/{total}', flush=True)
            if st == 'ratelimit':
                with _lock: pending.append({'code': it['code'], 'title': it['title'], 'note': 'rate-limited'})
                continue
            if st == 'transport':
                pending.append({'code': it['code'], 'title': it['title'], 'note': 'transport failure'})
                continue
            if st == 'dead':
                with _lock: drops['dead'] += 1
                continue
            # live
            name = clean_title(t or it['title'])
            if not name or PORN.search(name) or PORN.search(it['title']):
                with _lock: drops['porn'] += 1
                continue
            if it['src'] == 'team25R':
                cat = it['cat_name'] if it['cat_name'] in CWORDS else 'Other'
                cc = it['country']
                desc = it['raw'].get('description') or make_desc(name, cat, cc)
            else:
                cat = CATMAP.get(it['cat_name'], 'Other')
                cc = it['country'] if len(it['country']) == 2 and it['country'].isalpha() else 'International'
                desc = make_desc(name, cat, cc)
            with _lock:
                verified.append({'name': name, 'category': cat, 'country': cc,
                                 'description': desc,
                                 'invite': f'https://chat.whatsapp.com/{it["code"]}',
                                 'image': ''})
    # also handle untouched items if 429 stopped early
    print(f'verified={len(verified)} pending={len(pending)} dead={drops["dead"]} porn={drops["porn"]}', flush=True)
    json.dump(verified, open(WORK + 'team33-pending-retry.json', 'w'), ensure_ascii=False, indent=1)
    # pending: keep fuller records (schema + note)
    pend_out = []
    for p in pending:
        pend_out.append({'code': p['code'], 'title': p['title'], 'note': p['note'],
                         'invite': f'https://chat.whatsapp.com/{p["code"]}', 'image': ''})
    json.dump(pend_out, open(WORK + 'team33-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump({'verified': len(verified), 'pending': len(pending), 'dead': drops['dead'],
               'porn_title_drops': drops['porn']}, open(WORK + '_team33_result.json', 'w'))
    print('WROTE OUTPUT', flush=True)

main()
