# TEAM 01 — wave 20261114, tglinkhub resume: banking/screening pass.
# Screens live og:titles from team01-verify-results.jsonl with the inherited
# bank_team03 screens + hard_screen_team03 patterns + the task's casino/
# slots/betting-signal screen (wave-20261113 team05 kept casino groups, so
# live titles are screened carefully here). Builds the four team01 outputs.
import json, re, html as H, collections

W14 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
W12 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
RAW = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
BASE = '/home/hatch/workspace/whatsapp-groups-site/'

res = [json.loads(l) for l in open(f'{W14}team01-verify-results.jsonl')]
todo = json.load(open(f'{W14}team01-todo.json'))
controls = json.load(open(f'{W14}team01-controls.json'))['controls']
recs = json.load(open(f'{RAW}tg_code_recs.json'))
src2 = json.load(open(f'{RAW}tg_code2src.json'))
for _c, _v in src2.items():
    if _c not in recs and _v:
        _link, _title = _v[0]
        recs[_c] = {'name': '', 'section': '', 'post_title': _title,
                    'post_link': _link, 'slug': _link.rstrip('/').split('/')[-1],
                    'post_cats': []}
union = set(json.load(open(f'{BASE}.existing_codes.json')))

live = [r for r in res if r['status'] == 'live']
dead = [r for r in res if r['status'] == 'dead']
pend = [r for r in res if r['status'] == 'pending']
print(f"checked={len(res)} live={len(live)} dead={len(dead)} pending={len(pend)}")

# --- screens (bank_team03 + hard_screen_team03 + casino) ---
NEG = re.compile(r'[^.!?\n]*\b(no|not allowed|prohibited|strictly no|no\s+allowed)\b[^.!?\n]*(porn|xxx|sex|nude|adult|18\+|hot\s+video)[^.!?\n]*[.!?\n]?', re.I)
def strip_negations(t):
    return NEG.sub(' ', t or '')
ADULT = re.compile(r'🔞|🥵|🍆|👙|se+x|hookup|escort|porn|x{3,}|xnxx|xxnx|\bpussy\b|seksi|boobs|navel|panty|\bbra\b|shagger|leak|nude|\bcum\b|randi|muth|puku|dengutha|molai|iduppu|nsfw|hotness|f[u_]+ck|naughty america|18\+\s*(hot|adult|sex|video|porn)|hot\s+(girls?|bhabhi|aunty|video|actress|bollywood)|chuchi|\blund\b|chut|\bchoot\b|\bgaand\b|bhosda', re.I)
SCAM = re.compile(r'b-?love|forsage|shey[iy]|holiverse|meta[\s\-]?whale|paypal loader|bitfinex|counterfeit|crypto.?doubling|carding|double (your|the) (money|investment|usdt|trx|btc)|airdrop|money\s*drop|binary\s*option|free\s+money', re.I)
PHONE = re.compile(r'(\+?\d[\d\s\-/]{8,}\d)')
NUMFRAG = re.compile(r'^[\d\s\-/\+]{5,}$')  # name of only digits/separators, e.g. '6/1/18+91' (phone fragment, no group identity)
BETTING = re.compile(r'match\s*fix|fix\s*report|\bfix\b.*\bipl\b|\bipl\b.*\bfix\b|real\s*bet|\bbetting\b|tipper|toss[^A-Za-z]{0,12}(report|killer|kings)|match\s*report|1xbet|opportunit\w*\s+paris', re.I)
RICHSCHEME = re.compile(r'ficar rico|way to get rich|make \d+k with|millionaire blueprint|\d+k-\d+k monthly', re.I)
HACKED = re.compile(r'\bhacked\b|virus in group|virus.*attacking', re.I)
GIRLSNUM = re.compile(r'(girls?|aunty|bhabhi|women|ladies)\s*(numbers?|number|num)', re.I)
CASINO = re.compile(r'tigrinho|fortune\s*(tiger|ox|rabbit|mouse|dragon)|sinais|plataforma[s]?\s*pagante[s]?|wjbet|bet365|cassin[oa]|casino|\bslots?\b|roleta|aviator|\bmines\b|aposta[s]?|\bbet\b|banca|saque|green\s*red|vip\s*sinais|jogo\s*do\s*tigrinho', re.I)
HARD = [
    (re.compile(r'call.?girls?|call.?boys?|escort|onlyfans', re.I), 'call-girl/escort/OnlyFans service'),
    (re.compile(r'\bbhabhi\b', re.I), 'Desi bhabhi'),
    (re.compile(r'auntys?\b', re.I), 'aunty video-call/sex-service genre'),
    (re.compile(r'\bhorny\b|\bxvideos\b|xnxx|brazzers|hentai|putaria|pundai|soothu|\bpenis\b|pussy|\bdick\b|\bcock\b|boobs|tites', re.I), 'explicit sexual content'),
    (re.compile(r'\bsexy\b|\bsaxy\b', re.I), 'sexy/saxy sexualised title'),
    (re.compile(r'paid\s+(girl|call|service|vc|video|tamil|telugu)|paid\s+\w*\s*girl|\bgirl\b.*\bpaid\b|\bpaid\b.*\bservice\b', re.I), 'paid girl/service'),
    (re.compile(r'video.?call|vidio|vid\s*call|\bvc\b', re.I), 'video-call sex service'),
    (re.compile(r'\bitem\b', re.I), 'item-girl sexualised trope'),
    (re.compile(r'18\s*\+\s*(xvideo|pics?|video|vidio|call|aunty|bhabhi|hot|ullu|sexy|adult)', re.I), '18+ sexual group'),
    (re.compile(r'susu|sus[uú]|नहाती|मूत', re.I), 'voyeur/bathing-urination sexualised title'),
    (re.compile(r'naughty\s+(girl|ladies|vid|call|teen)|teens?\s+(vid|call)', re.I), 'naughty/teen video-call sexual content'),
    (re.compile(r'\bgirl\b.*(💋|👅|💦)', re.I), 'girls + sexual emojis'),
]

def category_for(r, name=''):
    text = ((r.get('post_title') or '') + ' ' + r.get('slug', '') + ' ' +
            (' '.join(r.get('post_cats') or [])) + ' ' + name).lower()
    if any(k in text for k in ['forex', 'trading', 'share market', 'stock market']): return 'Finance'
    if any(k in text for k in ['amazon', 'deals', 'shopping', 'offers', 'discount', 'flipkart']): return 'Buy Sell'
    if 'attari' in text or 'الحمد' in text: return 'Islamic'
    if 'job' in text: return 'Jobs'
    if any(k in text for k in ['education', 'upsc', 'ssc', 'ibps', 'railway', 'nda', 'study', 'exam', 'college', 'school', 'gk', 'general knowledge', 'university', 'scholarship']): return 'Education'
    if any(k in text for k in ['islam', 'quran', 'muslim', 'allah', 'naat', 'madrasa']): return 'Islamic'
    if any(k in text for k in ['sport', 'ipl', 'cricket', 'football', 'kabaddi', 'hockey']): return 'Sports'
    if 'news' in text: return 'News'
    if any(k in text for k in ['business', 'digital marketing', 'marketing', 'entrepreneur']): return 'Business'
    if any(k in text for k in ['gaming', 'pubg', 'free fire', 'clash']): return 'Gaming'
    if any(k in text for k in ['movie', 'movies', 'status', 'song', 'music', 'actress', 'actor', 'entertainment', 'video']): return 'Entertainment'
    if any(k in text for k in ['health', 'fitness', 'doctor', 'medical']): return 'Health'
    if any(k in text for k in ['funny', 'joke', 'meme', 'comedy']): return 'Funny'
    if any(k in text for k in ['buy', 'sell', 'shopping', 'market']): return 'Buy Sell'
    if any(k in text for k in ['finance', 'forex', 'crypto', 'trading', 'share market', 'stock']): return 'Finance'
    if any(k in text for k in ['tech', 'technology', 'computer', 'software']): return 'Technology'
    return 'Community & Social'

def country_for(r):
    text = ((r.get('post_title') or '') + ' ' + r.get('slug', '')).lower()
    m = {'portugal': 'PT', 'malaya': 'MY', 'karnataka': 'IN', 'tamil': 'IN', 'telugu': 'IN',
         'kannada': 'IN', 'kerala': 'IN', 'malayalam': 'IN', 'hindi': 'IN', 'delhi': 'IN',
         'rajasthan': 'IN', 'indian': 'IN', 'india': 'IN', 'bhojpuri': 'IN', 'marathi': 'IN',
         'gujarati': 'IN', 'punjabi': 'IN', 'bengali': 'IN', 'urdu': 'PK', 'pakistani': 'PK',
         'pakistan': 'PK', 'south-africa': 'ZA', 'canada': 'CA', 'uk-': 'GB', 'usa': 'US',
         'america': 'US', 'dubai': 'AE', 'uae': 'AE', 'ghana': 'GH', 'tanzania': 'TZ',
         'indonesia': 'ID', 'brazil': 'BR', 'sri-lanka': 'LK', 'bangladesh': 'BD',
         'nepal': 'NP', 'nigeria': 'NG', 'kenya': 'KE', 'australia': 'AU', 'germany': 'DE',
         'france': 'FR', 'spain': 'ES', 'italy': 'IT', 'turkey': 'TR', 'saudi': 'SA',
         'qatar': 'QA', 'kuwait': 'KW', 'oman': 'OM', 'bahrain': 'BH'}
    for k, v in m.items():
        if k in text: return v
    return ''

CATDESC = {
    'Entertainment': 'An entertainment group for sharing videos, movies, songs and fun updates with members.',
    'Jobs': 'A jobs group sharing vacancies, walk-in alerts and career updates for members.',
    'Education': 'An education group for study material, exam preparation and learning resources.',
    'Islamic': 'An Islamic group for religious reminders, Quranic learning and faith discussions.',
    'Sports': 'A sports group for match updates, scores and discussion among fans.',
    'Community & Social': 'A community group for chatting, meeting new people and sharing everyday updates.',
    'Finance': 'A finance group for market updates, trading discussion and money tips.',
    'Funny': 'A fun group for jokes, memes and light-hearted entertainment.',
    'Buy Sell': 'A buy and sell group for deals, offers and marketplace listings.',
    'Health': 'A health group for wellness tips, fitness and healthy living discussion.',
    'News': 'A news group sharing daily headlines and current-affairs updates.',
    'Gaming': 'A gaming group for players to chat, share tips and team up for games.',
    'Technology': 'A technology group for tech news, tips and discussion.',
    'Business': 'A business group for entrepreneurs, marketing ideas and networking.',
    'Crypto': 'A crypto group for cryptocurrency news, discussion and market updates.',
    'Scholarship': 'A scholarship group sharing funding opportunities and application guidance.',
    'Freelance': 'A freelance group for gig work, clients and freelancing tips.',
    'Travel': 'A travel group for trip ideas, destinations and travel discussion.',
    'Poetry': 'A poetry group for sharing poems, verses and literary discussion.',
    'Cooking': 'A cooking group for recipes, food tips and kitchen discussion.',
    'Earning': 'An online earning group for legit ways to earn money online.',
    'Real Estate': 'A real estate group for property listings, buying and selling.',
}

items, exclusions, flagged = [], [], []
for r in live:
    code = r['code']; og = (r.get('og_title') or '').strip()
    rec = recs.get(code, {})
    name = H.unescape(re.sub(r'\s+', ' ', og)).strip() or rec.get('name', '')
    check = strip_negations(og)
    name_clean = strip_negations(name)
    drop = None
    if ADULT.search(check) or ADULT.search(name_clean):
        drop = 'adult-sexual signal in og:title/name: ' + og
    elif SCAM.search(check) or SCAM.search(name):
        drop = 'scam signal in og:title/name: ' + og
    elif CASINO.search(check) or CASINO.search(name):
        drop = 'casino/slots/betting-signal group: ' + og
    elif BETTING.search(check):
        drop = 'betting/match-fixing tipster group: ' + og
    elif RICHSCHEME.search(check):
        drop = 'get-rich-scheme title: ' + og
    elif HACKED.search(check):
        drop = 'hacked/virus warning in title; unusable group: ' + og
    elif GIRLSNUM.search(check):
        drop = 'shares girls phone numbers (personal info): ' + og
    elif PHONE.search(name) or NUMFRAG.match(name.strip()):
        drop = 'name looks like a phone number/personal info: ' + og
    else:
        for rx, why in HARD:
            if rx.search(check) or rx.search(name_clean):
                drop = 'hard-screen DROP: ' + why + ': ' + og
                break
    if drop:
        exclusions.append({'code': code, 'reason': drop})
        if code == '3EvZx578PQ6EwZtEdNnpnP':
            flagged.append({'code': code, 'og_title': og,
                            'note': 'ADJUDICATION FLAG: dropped as phone-number fragment '
                                    '(directory name and og:title are both just "6/1/18+91"); '
                                    'no group identity to bank honestly. If the coordinator '
                                    'judges it a date/code rather than a phone fragment, it '
                                    'could be banked as Business/Community & Social, but it '
                                    'was NOT banked here.'})
        continue
    cat = category_for(rec, name); ctry = country_for(rec)
    base = CATDESC.get(cat, 'A community group for chatting and sharing updates with members.')
    desc = f'Join {name}, an active WhatsApp group for {cat.lower()}. ' + base[0].lower() + base[1:]
    items.append({'name': name[:100], 'category': cat, 'country': ctry,
                  'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})

# dedupe banked items by code + against union (defensive; todo already excluded union)
seen, uniq = set(), []
for it in items:
    c = it['invite'].rsplit('/', 1)[-1]
    if c in seen or c in union: continue
    seen.add(c); uniq.append(it)
items = uniq

pend_items = []
for r in pend:
    rec = recs.get(r['code'], {})
    pend_items.append({'name': (rec.get('name') or ''), 'category': '', 'country': '',
                       'description': '', 'invite': 'https://chat.whatsapp.com/' + r['code'],
                       'reason': r.get('reason', 'transport failure')})
# leads: codes still unverified after this run = transport pendings only (none).
# The 999 recs-not-fresh codes never verified are ALL in the union -> skipped
# per task, NOT banked as leads (each link once, ever).
leads = [p['invite'].rsplit('/', 1)[-1] for p in pend_items]

dupes = [{'code': c, 'reason': 'duplicate of existing groups.json code (in .existing_codes.json union)'}
         for c in todo['pending_dupes']]

json.dump(items, open(f'{W14}team01-candidates.json', 'w'), ensure_ascii=False, indent=1)
json.dump(leads, open(f'{W14}team01-leads.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pend_items, open(f'{W14}team01-pending.json', 'w'), ensure_ascii=False, indent=1)

# counts for the summary: full-pool derivation
done_all = {}
for p in (f'{RAW}verify2_results.jsonl',
          '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/verify2_results_20261111.jsonl',
          f'{W12}verify2_results_20261112.jsonl'):
    for line in open(p):
        d = json.loads(line); done_all[d['code']] = d
f12 = [json.loads(l) for l in open(f'{W12}verify2_results_20261112.jsonl')]
summary = {
    'team': 'team01',
    'slice': 'tglinkhub resume — verify2_results_20261112.jsonl remainder + never-verified non-union codes',
    'sources': [
        'agent_batches/wave_20261112/verify2_results_20261112.jsonl (11,587 lines)',
        'agent_batches/wave_20261110/team32_raw/verify2_results.jsonl (Nov 10)',
        'agent_batches/wave_20261111/verify2_results_20261111.jsonl (Nov 11)',
        'agent_batches/wave_20261110/team32_raw/tg_fresh_codes.json + tg_code_recs.json + tg_code2src.json + tg_name_exclusions.json',
        'agent_batches/wave_20261112/team03-tglinkhub-summary.json (team03 prior work)',
        'agent_batches/wave_20261113/team04-summary.json (team04 re-verified the 62 pending)',
        '.existing_codes.json (union, 119,266 codes)',
    ],
    'controls': controls,
    'counts': {
        'raw_pool_fresh_codes': 13147,
        'in_verify2_20261112_file': len(f12),
        'in_verify2_20261112_live': sum(1 for r in f12 if r['status'] == 'live'),
        'in_verify2_20261112_dead': sum(1 for r in f12 if r['status'] == 'dead'),
        'in_verify2_20261112_undecided': sum(1 for r in f12 if r['status'] not in ('live', 'dead')),
        'pool_decided_across_all_3_verify2_files': len(done_all),
        'pool_live_across_all_3': sum(1 for v in done_all.values() if v['status'] == 'live'),
        'pool_dead_across_all_3': sum(1 for v in done_all.values() if v['status'] == 'dead'),
        'pool_pending_across_all_3': sum(1 for v in done_all.values() if v['status'] == 'pending'),
        'raw_this_run': len(res),
        'verified_live_this_run': len(live),
        'dead_this_run': len(dead),
        'pending_this_run': len(pend),
        'dupes_skipped_no_fetch': len(dupes),
        'verified_candidates_banked': len(items),
        'excluded_live': len(exclusions),
        'leads': len(leads),
    },
    'verified': len(items),
    'dead': len(dead),
    'dupes': len(dupes),
    'pending': len(pend_items),
    'leads': len(leads),
    'excluded': exclusions,
    'dupes_list': dupes,
    'flagged_for_adjudication': flagged,
    'resume': 'Nothing remains undecided in this slice. The 13,147-code keep pool is now fully decided: live 6,764 (6,763 from the 3 verify2 files + 1 pending re-verified live here, excluded), dead 6,380 (6,322 + 58 pending re-verified dead here), union dupes 3 (not fetched) = 13,147. Plus the 6 never-verified non-union codes: live 4 (all excluded), dead 2. Pending 0. Next run: re-derive from the 3 verify2 files + current union; do NOT re-fetch decided codes. Note: 999 tg_code_recs codes never verified are ALL in the union (skipped per dedupe rule); 3,887 recs-not-in-fresh codes are all in the union. If the coordinator wants those re-examined, that needs a union-snapshot decision, not a re-verify.',
    'notes': [
        'CONTROLS PASSED in-run: live KrDwdK8EIkB6vgauHg5M7N -> og:title exactly "JAY - PHP & Python Full Stack Developer" (http 200); fabricated ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title, dead (http 200).',
        'SLICE-SIZE DISCREPANCY (honest): the assigned "~2,394 unverified invite codes" matches NO derivable count. Recomputed: verify2_20261112 file = 11,587 decided rows, 0 undecided; full fresh pool 13,147 decided across Nov10+Nov11+Nov12 except exactly the 62 pending codes (3 union dupes + 59 verified here). Closest counts to 2,394: live-not-in-union across all 3 files = 2,144; f12-live-not-in-union = 1,990; live-not-in-union + pending-not-in-union = 2,203. This run verified the true undecided remainder (65 codes: 59 pending + 6 never-verified non-union) and banked 0 candidates because all 5 live hits were drops.',
        'INDEPENDENT RE-CHECK of wave_20261113 team04: team04 reported the 59 pending as 58 dead + 1 live-excluded (KrlclnHLTF92zoufKilMdh). This run independently re-fetched all 59 with spaced retries and got the IDENTICAL outcome: 58 dead (empty og:title after 3 attempts), 1 live with the same og:title (Hindi bhabhi/aunty bathing/urination voyeur content), excluded here too.',
        'The 6 never-verified non-union codes are the 7 tg_name_exclusions codes minus the 1 already in the union (KilgsNKL3aBEZGMvPYrK26, "Airdrop International"). Of the 6: 4 live (2 carding, 1 Forsage, 1 phone fragment) — all excluded; 2 dead (Free Crypto Airdrop, Amazon Airdrop).',
        'No HTTP 429 and no transport failures in this run (0 pending); persistent per-thread requests.Session held up for all 65 fetches + 2 controls (479s total).',
        'Casino/slots screen applied to every live title (tigrinho/fortune tiger/sinais/plataformas pagantes/WJBET/cassino/slots/bet): 0 casino hits among the 5 live — the 5 were porn-voyeur / carding / Forsage / phone-fragment drops.',
        'groups.json NOT edited, generate.py NOT run, no deploy. Only team01-* outputs written in wave_20261114 dir.',
    ],
}
json.dump(summary, open(f'{W14}team01-summary.json', 'w'), ensure_ascii=False, indent=1)
print('candidates:', len(items), 'excluded:', len(exclusions), 'pending:', len(pend_items), 'leads:', len(leads))
for e in exclusions: print('EXCLUDED', e)
for d in dupes: print('DUPE', d)
