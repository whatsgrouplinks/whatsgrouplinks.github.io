#!/usr/bin/env python3
"""Team 06 phase 2: verify 780 extracted codes against chat.whatsapp.com.
Rules: max 3 parallel, >=0.5s between dispatches, timeout 25s, retry once on
200-empty-og:title or transport error. 200-empty after retry = dead (dropped).
Transport error after retry = pending. Live = 200 + non-empty, non-generic og:title.
Checkpoints every 40 results to team06-scratch-verify.json."""
import json, re, html, time, requests, threading, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

data = json.load(open(BASE / 'team06-scratch-extract.json'))
extracted = data['extracted']

ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
BLOCK_WORDS = ['porn', 'xxx', 'sex video', 'sex group', 'escort', 'call girl', 'callgirl',
               'bitfinexinvests', 'paypal loader', 'counterfeit', 'fake currency', 'fake money',
               'money mule', 'adult video', '18+ video', 'desi sex', 'bhabhi sex', 'xxx video',
               'onlyfans', 'nude', 'hot girls sex',
               'bokep', 'bokeh', 'xnxx', 'xvideos', 'pornhub', 'xhamster', 'redtube',
               'camgirl', 'cam girl', 'nude pics', 'porn video', 'leaked video', 'leak video',
               'mms video', 'sexy video', 'sexy girls', 'desi bhabhi', 'hot sexy', 'pornstar',
               'sex chat', 'phone sex', 'live sex', 'video call sex']
SCAM_PHRASES = ['bitfinex', 'paypal loader', 'counterfeit']

def blocked(name, title):
    t = (name + ' ' + title).lower()
    if any(e in (name + ' ' + title) for e in ADULT_EMOJI):
        return True
    return any(w in t for w in BLOCK_WORDS)

# ---- category / country mapping from page slug ----
CAT_RULES = [
    ('ielts', 'Education'), ('duolingo', 'Education'), ('iti-', 'Education'),
    ('college', 'Education'), ('study-', 'Education'), ('-study', 'Education'),
    ('education', 'Education'), ('scholarship', 'Scholarship'),
    ('job', 'Jobs'), ('driver', 'Jobs'),
    ('cricket', 'Sports'), ('sports', 'Sports'),
    ('crypto', 'Crypto'), ('forex', 'Finance'), ('trading', 'Finance'),
    ('share-market', 'Finance'), ('islamic', 'Islamic'),
    ('movie', 'Entertainment'), ('anime', 'Entertainment'), ('drama', 'Entertainment'),
    ('audition', 'Entertainment'), ('celebrity', 'Entertainment'), ('fan-club', 'Entertainment'),
    ('k-pop', 'Entertainment'), ('k-drama', 'Entertainment'), ('youtube', 'Entertainment'),
    ('bollywood', 'Entertainment'), ('modeling', 'Entertainment'), ('creative', 'Entertainment'),
    ('art-', 'Entertainment'), ('photography', 'Entertainment'),
    ('gaming', 'Gaming'), ('girls', 'Friendship'), ('boys', 'Friendship'),
    ('friendship', 'Friendship'), ('dating', 'Friendship'), ('gay-', 'Friendship'),
    ('real-estate', 'Real Estate'), ('earn-money', 'Online Earning'),
    ('affiliate-marketing', 'Online Earning'), ('dropshipping', 'Online Earning'),
    ('freelancer', 'Freelance'), ('web-developer', 'Technology'),
    ('technology', 'Technology'), ('seo-', 'Technology'), ('photo-editing', 'Technology'),
    ('photoshop', 'Technology'), ('innovative', 'Technology'), ('designers', 'Technology'),
    ('digital-marketing', 'Business'), ('sales-and-marketing', 'Business'),
    ('lead-generation', 'Business'), ('event-management', 'Business'),
    ('agriculture', 'Business'), ('business', 'Business'),
    ('amazon-deals', 'Buy & Sell'), ('wholesale', 'Buy & Sell'), ('reseller', 'Buy & Sell'),
    ('shopping', 'Buy & Sell'), ('diamond-buyers', 'Buy & Sell'),
    ('weight-loss', 'Health'), ('fitness', 'Health'), ('beauty-parlour', 'Health'),
    ('news', 'News'), ('newspaper', 'News'), ('bjp', 'News'),
    ('urdu-poetry', 'Poetry'), ('poetry', 'Poetry'),
    ('travel', 'Travel'), ('funny', 'Funny'), ('motivational', 'Community & Social'),
    ('lifestyle', 'Community & Social'),
]
COUNTRY_RULES = [
    ('uttar-pradesh', 'IN'), ('bangalore', 'IN'), ('assam', 'IN'), ('indian-', 'IN'),
    ('tamil', 'IN'), ('kannada', 'IN'), ('malayalam', 'IN'), ('gujarati', 'IN'),
    ('pakistani', 'PK'), ('bangladesh', 'BD'), ('sri-lanka', 'LK'), ('afghanistan', 'AF'),
    ('london', 'GB'), ('uk-', 'GB'), ('-uk', 'GB'), ('usa', 'US'), ('new-york', 'US'),
    ('california', 'US'), ('las-vegas', 'US'), ('canada', 'CA'), ('qatar', 'QA'),
    ('kuwait', 'KW'), ('saudi-arabia', 'SA'), ('oman', 'OM'), ('dubai', 'AE'),
    ('bahamas', 'BS'), ('kenya', 'KE'), ('uganda', 'UG'), ('south-africa', 'ZA'),
    ('zimbabwe', 'ZW'), ('tanzania', 'TZ'), ('romania', 'RO'), ('nigeria', 'NG'),
    ('hong-kong', 'HK'), ('italy', 'IT'), ('france', 'FR'), ('paris', 'FR'),
    ('brazil', 'BR'), ('germany', 'DE'), ('poland', 'PL'), ('europe', 'International'),
    ('k-pop', 'KR'), ('k-drama', 'KR'), ('spanish', 'ES'),
]
VALID_CATS = {'Education', 'Jobs', 'Entertainment', 'Islamic', 'News', 'Sports', 'Technology',
              'Health', 'Business', 'Gaming', 'Friendship', 'Community & Social', 'Online Earning',
              'Crypto', 'Cooking', 'Poetry', 'Travel', 'Scholarship', 'Freelance', 'Real Estate',
              'Buy & Sell', 'Finance', 'Funny'}

def map_cat(slug, name):
    s = slug.lower()
    for k, c in CAT_RULES:
        if k in s:
            return c
    n = name.lower()
    if 'job' in n: return 'Jobs'
    if 'cricket' in n or 'football' in n: return 'Sports'
    if 'crypto' in n or 'bitcoin' in n: return 'Crypto'
    if 'islamic' in n or 'quran' in n: return 'Islamic'
    if 'poetry' in n or 'shayari' in n: return 'Poetry'
    if 'earn' in n or 'earning' in n: return 'Online Earning'
    if 'news' in n: return 'News'
    if 'study' in n or 'exam' in n or 'ielts' in n: return 'Education'
    if 'funny' in n or 'joke' in n or 'meme' in n: return 'Funny'
    if 'movie' in n or 'music' in n or 'song' in n: return 'Entertainment'
    if 'cook' in n or 'recipe' in n: return 'Cooking'
    if 'game' in n or 'gaming' in n or 'pubg' in n or 'free fire' in n: return 'Gaming'
    if 'friend' in n or 'girls' in n or 'boys' in n: return 'Friendship'
    if 'travel' in n: return 'Travel'
    if 'health' in n or 'fitness' in n: return 'Health'
    if 'shop' in n or 'buy' in n or 'sell' in n: return 'Buy & Sell'
    return 'Community & Social'

def map_country(slug):
    s = slug.lower()
    for k, c in COUNTRY_RULES:
        if k in s:
            return c
    return 'International'

def slug_of(page):
    return page.rstrip('/').split('/')[-1]

GENERIC_TITLES = {'whatsapp group', 'join this group on whatsapp', 'whatsapp', ''}

def fetch_title(code):
    """Returns (status, og_title or None, is_channel, error_kind). Uses curl (requests stalls on chat.whatsapp.com)."""
    url = f'https://chat.whatsapp.com/{code}'
    for attempt in range(2):
        try:
            p = subprocess.run(['curl', '-s', '-A', UA['User-Agent'], '--max-time', '25',
                                '-w', '\n%{http_code}', url],
                               capture_output=True, text=True, timeout=40)
            out = p.stdout
            lines = out.rsplit('\n', 1)
            try:
                status = int(lines[1].strip())
            except Exception:
                status = 0
            body = lines[0] if len(lines) > 1 else out
            if status != 200:
                if attempt == 0:
                    time.sleep(8)
                    continue
                return (status, None, False, 'transport' if (status == 0 or status == 429 or status >= 500) else 'http')
            m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
            title = html.unescape(m.group(1)).strip() if m else ''
            title = re.sub(r'\s+', ' ', title)
            if not title:
                if attempt == 0:
                    time.sleep(8)
                    continue
                return (200, '', False, 'empty')
            is_channel = ('Follow this channel' in body) or ('whatsapp.com/channel/' in body)
            return (200, title, is_channel, None)
        except Exception:
            if attempt == 0:
                time.sleep(3)
                continue
            return (0, None, False, 'transport')
    return (0, None, False, 'transport')

# pre-filter blocked by listing name
todo, preblocked = [], 0
for e in extracted:
    if blocked(e['name'], ''):
        preblocked += 1
        continue
    todo.append(e)
print(f'to verify: {len(todo)} (pre-blocked by listing name: {preblocked})', flush=True)

verified, pending, dead_codes = [], [], []
dead = blocked_live = channels = 0
import sys
SKIP = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if SKIP:
    # restore prior checkpoint results, then continue after the skipped prefix
    prior = json.load(open(BASE / 'team06-scratch-verify.json'))
    verified.extend(prior['verified']); pending.extend(prior['pending'])
    dead_codes.extend(prior.get('dead_codes', []))
    dead = prior.get('dead', 0); blocked_live = prior.get('blocked_live', 0); channels = prior.get('channels', 0)
    todo = todo[SKIP:]
    print(f'RESUME: restored {len(verified)} verified, {len(pending)} pending, {dead} dead; {len(todo)} left to check', flush=True)
lock = threading.Lock()
last_dispatch = [0.0]

def work(e):
    global dead, blocked_live, channels
    with lock:
        gap = 0.7 - (time.time() - last_dispatch[0])
        if gap > 0:
            time.sleep(gap)
        last_dispatch[0] = time.time()
    status, title, is_channel, err = fetch_title(e['code'])
    rec = None
    with lock:
        if status == 200 and title and title.lower() not in GENERIC_TITLES:
            if is_channel:
                channels += 1
                return
            if blocked(e['name'], title):
                blocked_live += 1
                return
            name = title if title else e['name']
            name = re.sub(r'\s+', ' ', name).strip()
            if not name or len(name) > 120:
                name = e['name'] or 'WhatsApp Group'
            slug = slug_of(e['page'])
            cat = map_cat(slug, name)
            country = map_country(slug)
            desc = f'Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay active in the group.'
            verified.append({'name': name, 'category': cat, 'country': country,
                             'description': desc,
                             'invite': f"https://chat.whatsapp.com/{e['code']}", 'image': ''})
        elif err == 'transport':
            pending.append({'name': e['name'] or 'WhatsApp Group',
                            'category': map_cat(slug_of(e['page']), e['name']),
                            'country': map_country(slug_of(e['page'])),
                            'description': f"Join {e['name'] or 'this group'}, a WhatsApp group listed under {map_cat(slug_of(e['page']), e['name'])}.",
                            'invite': f"https://chat.whatsapp.com/{e['code']}", 'image': '',
                            'reason': 'transport'})
        else:
            dead += 1
            dead_codes.append(e['code'])

def save_checkpoint():
    with lock:
        json.dump({'verified': verified, 'pending': pending, 'dead_codes': dead_codes,
                   'dead': dead, 'blocked_live': blocked_live, 'channels': channels},
                  open(BASE / 'team06-scratch-verify.json', 'w'), indent=1)

with ThreadPoolExecutor(max_workers=3) as ex:
    futs = [ex.submit(work, e) for e in todo]
    done = 0
    for f in futs:
        f.result()
        done += 1
        if done % 25 == 0:
            save_checkpoint()
            print(f'{done}/{len(todo)} checked — verified {len(verified)}, pending {len(pending)}, dead {dead}', flush=True)
save_checkpoint()
print(f'DONE verified={len(verified)} pending={len(pending)} dead={dead} blocked_live={blocked_live} channels={channels} preblocked={preblocked}')
