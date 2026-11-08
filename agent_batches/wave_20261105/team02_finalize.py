import json, re, html
from collections import Counter

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
RESULTS = WAVE + '/team02-progress.jsonl'

with open('../wave_20261104/team14-unverified-pending.json') as f:
    pool = json.load(f)
slice_codes = pool['codes'][5892:]
with open(f'{WAVE}/dedupe_union.json') as f:
    union = set(json.load(f))
with open('/home/hatch/workspace/team28_work/candidates.json') as f:
    cand = json.load(f)
meta = {c['code']: c for c in cand}
preblocked = set(json.load(open(f'{WAVE}/team02_preblocked.json')))

results = {}
with open(RESULTS) as f:
    for line in f:
        r = json.loads(line)
        results[r['code']] = r

CATMAP = {
 'Education':'Education','Jobs':'Jobs','Business':'Business','Friendship':'Friendship',
 'News':'News','Islamic':'Islamic','Gaming':'Gaming','Entertainment':'Entertainment',
 'Technology':'Technology','Health':'Health','Buy-Sell':'Buy & Sell','Regional':'Community & Social',
 'Community':'Community & Social','Other':'Community & Social','Movies':'Entertainment',
 'Travel':'Travel & Tourism','Girls':'Friendship','Pets':'Community & Social',
 'Food':'Community & Social','Music':'Entertainment',
}
COUNTRY_WORDS = [
 ('Pakistan','PK'),('Pakistani','PK'),('India','IN'),('Indian','IN'),('Bangladesh','BD'),
 ('Bangladeshi','BD'),('Nepal','NP'),('Nepali','NP'),('Sri Lanka','LK'),('USA','US'),
 ('United States','US'),('America','US'),('American','US'),('United Kingdom','GB'),
 ('UK','GB'),('England','GB'),('London','GB'),('Canada','CA'),('Canadian','CA'),
 ('Australia','AU'),('Australian','AU'),('Dubai','AE'),('UAE','AE'),('Emirates','AE'),
 ('Saudi Arabia','SA'),('Saudi','SA'),('Nigeria','NG'),('Nigerian','NG'),('Kenya','KE'),
 ('Kenyan','KE'),('Ghana','GH'),('South Africa','ZA'),('Philippines','PH'),('Filipino','PH'),
 ('Indonesia','ID'),('Indonesian','ID'),('Malaysia','MY'),('Malaysian','MY'),('Turkey','TR'),
 ('Turkish','TR'),('Egypt','EG'),('Egyptian','EG'),('Morocco','MA'),('Moroccan','MA'),
 ('Germany','DE'),('German','DE'),('France','FR'),('French','FR'),('Italy','IT'),('Italian','IT'),
 ('Spain','ES'),('Spanish','ES'),('Brazil','BR'),('Brazilian','BR'),('Mexico','MX'),
 ('Mexican','MX'),('Russia','RU'),('Russian','RU'),('China','CN'),('Chinese','CN'),
 ('Japan','JP'),('Japanese','JP'),('Korea','KR'),('Korean','KR'),('Thailand','TH'),('Thai','TH'),
 ('Vietnam','VN'),('Singapore','SG'),('Afghanistan','AF'),('Afghan','AF'),('Iran','IR'),
 ('Iraq','IQ'),('Kuwait','KW'),('Qatar','QA'),('Oman','OM'),('Bahrain','BH'),('Jordan','JO'),
 ('Lebanon','LB'),('Yemen','YE'),('Sudan','SD'),('Ethiopia','ET'),('Uganda','UG'),
 ('Tanzania','TZ'),('Zambia','ZM'),('Zimbabwe','ZW'),('Malawi','MW'),('Mozambique','MZ'),
 ('Angola','AO'),('Cameroon','CM'),('Senegal','SN'),('Ivory Coast','CI'),("Côte d'Ivoire",'CI'),
 ('Netherlands','NL'),('Dutch','NL'),('Belgium','BE'),('Switzerland','CH'),('Austria','AT'),
 ('Sweden','SE'),('Norway','NO'),('Denmark','DK'),('Finland','FI'),('Poland','PL'),
 ('Portugal','PT'),('Greece','GR'),('Romania','RO'),('Ukraine','UA'),('Argentina','AR'),
 ('Chile','CL'),('Colombia','CO'),('Peru','PE'),('Venezuela','VE'),('New Zealand','NZ'),
]
BLOCK = [
 r'\bxxx\b', r'\bporn\b', r'porno', r'pornhub', r'xvideos', r'\bsex\s*videos?\b',
 r'\bsex\s*mms\b', r'\badult\s*videos?\b', r'\bnude\b', r'\bnaked\b', r'desi\s*sex',
 r'\bsex\s*chat\b', r'hot\s*sex', r'\bhyip\b', r'crypto\s*pump', r'pump\s*signal',
 r'double\s*(your\s*)?money', r'money\s*doubling', r'\bsatta\b', r'\bmatka\b', r'\bdrugs?\b',
 r'cocaine', r'heroin', r'counterfeit', r'\bscam\b', r'\bfraud\b', r'free\s*money',
 r'teen\s*sex', r'school\s*girl[s]?\s*sex', r'underage', r'minor\s*sex', r'child\s*sex',
 r'https?://', r'www\.', r'\.com\b', r'\.net\b', r'\d{10,}',
]
block_pat = re.compile('|'.join(BLOCK), re.I)

def clean_topic(post_title):
    t = re.sub(r'\s*Whatsapp Group Link\s*$', '', post_title, flags=re.I).strip()
    t = re.sub(r'\s+', ' ', t)
    return t

def detect_country(*texts):
    joined = ' ' + ' '.join(texts) + ' '
    for word, iso in COUNTRY_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', joined, re.I):
            return iso
    return 'International'

verified, pending, drops = [], [], []
drop_reasons = Counter()
for code in slice_codes:
    if code in union:
        drops.append({'code': code, 'reason': 'in-dedupe-union'})
        drop_reasons['in-dedupe-union'] += 1
        continue
    if code in preblocked:
        drops.append({'code': code, 'reason': 'content-block: satta (post_title)'})
        drop_reasons['content-block-satta'] += 1
        continue
    m = meta.get(code, {})
    pt = m.get('post_title', '')
    r = results.get(code)
    if r is None:
        pending.append({'code': code, 'name': clean_topic(pt) if pt else '', 'note': 'not-attempted: verifier did not reach this code'})
        continue
    if r['verdict'] != 'verified':
        pending.append({'code': code, 'name': clean_topic(pt) if pt else '', 'note': r['note']})
        continue
    title = re.sub(r'\s+', ' ', html.unescape(r['title']).strip())
    hit = block_pat.search(title) or block_pat.search(pt)
    if hit:
        drops.append({'code': code, 'reason': f"content-block: matched '{hit.group(0)}' in og:title/post_title"})
        drop_reasons['content-block-ogtitle'] += 1
        continue
    if re.search(r'@', title) and re.search(r'\.(com|net|org)\b', title, re.I):
        drops.append({'code': code, 'reason': 'content-block: name looks like email/url'})
        drop_reasons['content-block-urlname'] += 1
        continue
    topic = clean_topic(pt) or title
    cat = CATMAP.get(m.get('cat', ''), 'Community & Social')
    country = detect_country(pt, title)
    topic_l = topic.lower()
    desc = (f"Join the {topic} WhatsApp group to connect with members interested in {topic_l}. "
            f"Share updates, discussions, tips and daily posts with an active {cat.lower()} community.")
    verified.append({
        'name': title,
        'category': cat,
        'country': country,
        'description': desc,
        'invite': f'https://chat.whatsapp.com/{code}',
        'image': '',
    })

with open(f'{WAVE}/team02-groups1-pool-b.json', 'w') as f:
    json.dump(verified, f, ensure_ascii=False, indent=1)
with open(f'{WAVE}/team02-unverified-pending.json', 'w') as f:
    json.dump(pending, f, ensure_ascii=False, indent=1)
with open(f'{WAVE}/team02-leads.json', 'w') as f:
    json.dump([], f, ensure_ascii=False, indent=1)
with open(f'{WAVE}/team02_dropped.json', 'w') as f:
    json.dump(drops, f, ensure_ascii=False, indent=1)

print('slice total:', len(slice_codes))
print('attempted (verifier records):', len(results))
print('verified:', len(verified))
print('pending:', len(pending))
print('drops:', len(drops), dict(drop_reasons))
print('pending note breakdown:', Counter(p['note'] for p in pending).most_common(10))
print('verified categories:', Counter(v['category'] for v in verified).most_common(15))
print('verified countries:', Counter(v['country'] for v in verified).most_common(15))
print('sample verified:', json.dumps(verified[:2], ensure_ascii=False))
