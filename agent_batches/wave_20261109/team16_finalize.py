import json, re, html as H

# --- load checks ---
c1 = json.load(open('team16_check1.json'))
c2 = json.load(open('team16_check2.json'))
c3 = json.load(open('team16_check3.json'))
tocheck = {i['code']: i for i in json.load(open('team16_tocheck.json'))}

live, dead, pending = {}, {}, {}
for code, meta in tocheck.items():
    titles = [c1.get(code,{}).get('og_title',''), c2.get(code,{}).get('og_title',''), c3.get(code,{}).get('og_title','')]
    https = [c1.get(code,{}).get('http',0), c2.get(code,{}).get('http',0), c3.get(code,{}).get('http',0)]
    title = next((t for t in titles if t.strip()), '')
    if title.strip():
        live[code] = title
    elif any(h == 0 for h in https) and not any(h == 200 for h in https):
        pending[code] = meta
    elif all(h == 200 for h in https) and not title.strip():
        dead[code] = meta
    elif any(h == 0 for h in https):
        # transport failed on some attempt but got HTTP 200 empty on others -> dead, not pending
        dead[code] = meta
    else:
        pending[code] = meta

print(f"live={len(live)} dead={len(dead)} pending={len(pending)}")

# --- screening ---
DROP = [
    # porn / sex / hookup / escort / cam
    'porn', 'xxx', 'sex', 'sexy', 'hookup', 'escort', 'cam girl', 'camgirl',
    'nude', 'erotic', 'adult video', 'hot girl', 'call girl', 'dating girls',
    'xxx video', 'porn video', 'sex video', 'sexy video', 'bhabhi', 'desi sex',
    # scams
    'b-love', 'blove', 'forsage', 'sheyi', 'free money', 'airdrop', 'crypto airdrop',
    'double your money', 'earn money free', 'investment double',
]
def strip_prohibitions(text):
    # remove sentences that prohibit adult content (rules), before screening
    sents = re.split(r'(?<=[.!?])\s+', text)
    keep = []
    for s in sents:
        low = s.lower()
        if any(p in low for p in ['na karein', 'not allowed', 'mana hai', 'prohibit', 'no adult', 'no porn', 'no sex', 'share na kare', 'allow nahi', 'not allow']):
            continue
        keep.append(s)
    return ' '.join(keep)

def screen(name, desc):
    hay = strip_prohibitions((name + ' ' + desc).lower())
    for d in DROP:
        if d in hay:
            return d
    return None

CATMAP = [
    ('pubg|bgmi|free fire|gaming|game|ludo|psl|ipl|fantasy|esports', 'Gaming'),
    ('study|education|exam|notes|english learn|gk|general knowledge|course|class|school|college|university|ielts|css|jobs? prep|test prep', 'Education'),
    ('earn money|earning|make money|online earning|daily earning|work from home|freelanc', 'Online Earning'),
    ('islam|islamic|quran|madani|ramadan|naat|dawat|muslim', 'Islamic'),
    ('job|jobs|government job|vacanc|hiring|career', 'Jobs'),
    ('cricket|football|sport|tennis|hockey', 'Sports'),
    ('news|headline|geo news|ary news|breaking', 'News'),
    ('movie|movies|drama|music|bollywood|entertain|tiktok|youtube|anime|cartoon|status|shayari|poetry', 'Entertainment'),
    ('funny|joke|meme|comedy', 'Funny'),
    ('buy|sell|shopping|offer|deal|market|olx|business', 'Buy Sell'),
    ('business|trading|forex|crypto|invest|marketing|digital marketing', 'Business'),
    ('girl|girls|friendship|friends|chat|romantic|love', 'Friendship'),
    ('health|fitness|medical|doctor', 'Health'),
    ('tech|technology|mobile|android|software|graphic design|programming', 'Technology'),
    ('finance|loan|bank|paytm', 'Finance'),
]
def categorize(section, name):
    hay = (section + ' ' + name).lower()
    for pat, cat in CATMAP:
        if re.search(pat, hay):
            return cat
    return 'Community & Social'

COUNTRYMAP = [
    ('indian|india|tamil|malayalam|kerala|goa|hindi|telugu|punjab', 'IN'),
    ('pakistan|pakistani|karachi|lahore|islamabad|balochistan|sindh|urdu|punjabi', 'PK'),
    ('usa|america|american|united states', 'US'),
    ('uk|britain|england|london', 'GB'),
    ('canada|canadian', 'CA'),
    ('dubai|uae|emirates', 'AE'),
    ('bangladesh|bengali', 'BD'),
    ('indonesia', 'ID'),
    ('brazil', 'BR'),
    ('arab|saudi', 'SA'),
]
def country(section, name):
    hay = (section + ' ' + name).lower()
    for pat, cc in COUNTRYMAP:
        if re.search(pat, hay):
            return cc
    return 'IN'

def clean_name(t):
    t = H.unescape(t or '')
    t = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]+', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' -–—:|•*~_')
    return t[:80] if t else 'WhatsApp Group'

candidates, screened_out = [], []
for code, title in live.items():
    meta = tocheck[code]
    name = clean_name(title) or clean_name(meta.get('name',''))
    desc_src = meta.get('name','')
    desc = f"A WhatsApp group for {name.lower()} fans and members to chat, share updates and stay connected." if len(name) > 3 else "An active WhatsApp community group to chat, share updates and connect with members."
    reason = screen(name, desc_src + ' ' + title)
    if reason:
        screened_out.append({'code': code, 'name': name, 'reason': reason, 'section': meta.get('section','')})
        continue
    cat = categorize(meta.get('section',''), name + ' ' + desc_src)
    cc = country(meta.get('section',''), name + ' ' + desc_src)
    candidates.append({
        'name': name,
        'category': cat,
        'country': cc,
        'description': desc[:200],
        'invite': f'https://chat.whatsapp.com/{code}',
    })

json.dump(candidates, open('team16-candidates.json','w'), indent=1, ensure_ascii=False)
json.dump([{'code': c, 'section': m.get('section',''), 'source': m.get('source',''), 'note': 'transport failed on all attempts (curl timeout/no response); not verified live or dead'} for c, m in pending.items()],
          open('team16-pending.json','w'), indent=1, ensure_ascii=False)
json.dump({'live': live, 'screened_out': screened_out}, open('team16_live_screen.json','w'), indent=1, ensure_ascii=False)
print('candidates:', len(candidates), 'screened_out:', len(screened_out), 'pending:', len(pending), 'dead:', len(dead))
for s in screened_out: print('SCREENED:', s)
for c in candidates: print('CAND:', c)
json.dump({'dead_count': len(dead), 'dead_codes': sorted(dead)}, open('team16_dead.json','w'), indent=1)
