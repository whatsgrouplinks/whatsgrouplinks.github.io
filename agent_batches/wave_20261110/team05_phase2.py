import json, re, os, subprocess, time, html
from concurrent.futures import ThreadPoolExecutor
import threading

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ---------- load existing union ----------
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
g = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
pat = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)')
for x in g:
    m = pat.search(x.get('invite', ''))
    if m:
        existing.add(m.group(1))
print("union size:", len(existing), flush=True)

codes = json.load(open(f"{WD}/team05_phase1_codes.json"))
print("unique extracted codes:", len(codes), flush=True)

# ---------- screening ----------
ADULT_RE = re.compile(r'(\U0001F51E|\U0001F975|sexy|hookup|escort|\bporn\b|xxx|\b18\+|adult|\bnude\b|\bsex\b|hot\s*girls?|call\s*girls?|bhabhi\s*hot)', re.I)
SCAM_RE = re.compile(r'(b[-\s]?love|forsage|shey(i|y)|airdrop|paypal\s*loader|bitfinex|counterfeit|carding|money\s*doubling|double\s*(your|the)\s*(money|bitcoin|crypto)|crypto\s*doubling|double\s*income)', re.I)

def screen(text):
    if not text:
        return None
    if ADULT_RE.search(text):
        return "adult-sexual signal in directory name/title"
    if SCAM_RE.search(text):
        return "scam/phishing signal in directory name/title"
    return None

# ---------- category / country inference ----------
CAT_RULES = [
    (r'job|career|employment|vacanc|hiring', 'Jobs'),
    (r'islam|quran|muslim|madrasa|naat|spiritual', 'Islamic'),
    (r'ipl|cricket|football|soccer|fans|fifa|rcb|blasters|liverpool|kerala.*portugal', 'Sports'),
    (r'stock|share.?market|trading|invest|forex|nft|crypto|option', 'Finance'),
    (r'student|school|college|university|learning|english|spanish|ias|exam|study|education|medical|pharma|seo', 'Education'),
    (r'news', 'News'),
    (r'movie|drama|poetry|entertainment|song|music|funny|comedy|meme|shayari|status', 'Entertainment'),
    (r'pubg|gaming|game', 'Gaming'),
    (r'tech|digital|marketing|affiliate|youtube|sub4sub', 'Technology'),
    (r'business|real.?estate|shopping|buy.?sell|sell|fashion|watch|temu', 'Buy Sell'),
    (r'health|yoga|weight.?loss|skin.?doctor|fitness', 'Health'),
    (r'friend|girl|boy|community|social|indian|pakistani|tamil|malayalam|punjabi|korean|russian|turkey|usa|uk\b|country', 'Community & Social'),
]
COUNTRY_RULES = [
    (r'\bindia\b|indian|gurgaon|karnataka|kerala|kolkata|tamil|punjabi|rajasthan|surat|solapur|trichy|vizag|ncr|delhi|uppcl', 'IN'),
    (r'pakistan|pakistani', 'PK'),
    (r'\busa\b|american', 'US'),
    (r'\buk\b|british|london', 'GB'),
    (r'\buae\b|dubai', 'AE'),
    (r'ksa|saudi', 'SA'),
    (r'nigeria', 'NG'),
    (r'sri.?lanka', 'LK'),
    (r'bangladesh', 'BD'),
    (r'nepal', 'NP'),
    (r'morocco', 'MA'),
    (r'namibia', 'NA'),
    (r'lesotho', 'LS'),
    (r'laos', 'LA'),
    (r'lithuania', 'LT'),
    (r'ukraine', 'UA'),
    (r'uruguay', 'UY'),
    (r'turkey|turkish', 'TR'),
    (r'martinique', 'MQ'),
    (r'san.?marino', 'SM'),
    (r'sierra.?leone', 'SL'),
    (r'spain|spanish', 'ES'),
    (r'russia', 'RU'),
]
TOPIC = {
    'Jobs': 'job openings and career opportunities',
    'Education': 'learning and study resources',
    'Islamic': 'Islamic reminders, learning and community',
    'Sports': 'sports news, scores and fan discussions',
    'Finance': 'market news, trading ideas and investment discussion',
    'News': 'daily news and current affairs',
    'Entertainment': 'movies, videos and entertainment',
    'Gaming': 'gaming news, tips and gameplay discussion',
    'Technology': 'technology news, tips and discussion',
    'Business': 'business ideas, deals and networking',
    'Buy Sell': 'buying, selling and deals',
    'Health': 'health tips, fitness and wellbeing',
    'Funny': 'funny videos, memes and light entertainment',
    'Community & Social': 'chatting, friendship and community discussion',
}

def infer(page_url, dir_name):
    hay = (page_url + ' ' + (dir_name or '')).lower()
    cat = 'Community & Social'
    for rx, c in CAT_RULES:
        if re.search(rx, hay):
            cat = c
            break
    country = 'International'
    for rx, cc in COUNTRY_RULES:
        if re.search(rx, hay):
            country = cc
            break
    return cat, country

def clean_name(raw, fallback):
    s = html.unescape(raw or '')
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s*\|\s*WhatsApp.*$', '', s, flags=re.I)
    s = re.sub(r'\s*-\s*WhatsApp Group.*$', '', s, flags=re.I)
    s = re.sub(r'^(join|join now|join group)\s*', '', s, flags=re.I)
    s = s.strip(' -–—|•·:').strip()
    if len(s) < 3:
        s = fallback or ''
    return s[:100].strip()

def make_desc(name, cat):
    topic = TOPIC.get(cat, 'chatting and community discussion')
    return (f"Join {name}, a WhatsApp group for {topic}. "
            f"Members share updates, chat and connect with others who enjoy the same interests.")

# ---------- dedupe + prescreen ----------
fresh = []
exclusions = []
dup = 0
for c in codes:
    code = c['code']
    if code in existing:
        dup += 1
        continue
    reason = screen(c.get('dir_name') or '')
    if reason:
        exclusions.append({"code": code, "reason": reason})
        continue
    fresh.append(c)
print(f"dupes in union: {dup}, prescreen exclusions: {len(exclusions)}, fresh to verify: {len(fresh)}", flush=True)
json.dump(fresh, open(f"{WD}/team05_to_verify.json", "w"), indent=1)

# ---------- verify with curl ----------
lock = threading.Lock()
last = [0.0]

def curl_once(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "15",
                            "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=20)
    except Exception as e:
        return None, None, f"curl error: {str(e)[:80]}"
    out = p.stdout
    if not out:
        return None, None, "empty curl response (no HTTP status)"
    lines = out.rsplit("\n", 1)
    body, status = lines[0], lines[1].strip()
    if not status.isdigit():
        return None, None, "no HTTP status in curl output"
    status = int(status)
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', body, re.I)
    title = html.unescape(m.group(1)).strip() if m else ""
    return status, title, None

def verify(item):
    code = item['code']
    with lock:
        dt = time.time() - last[0]
        if dt < 0.5:
            time.sleep(0.5 - dt)
        last[0] = time.time()
    status, title, err = curl_once(code)
    if err is not None:
        return ('pending', item, None, err)
    if status in (429, 503):
        return ('pending', item, None, f"HTTP {status} (rate-limit/server busy)")
    if status != 200:
        return ('dead', item, None, f"HTTP {status}")
    if title:
        return ('live', item, title, None)
    # empty og:title: 2 spaced retries
    for _ in range(2):
        time.sleep(3)
        status2, title2, err2 = curl_once(code)
        if err2 is not None:
            return ('pending', item, None, err2)
        if status2 != 200:
            return ('dead', item, None, f"HTTP {status2} on retry")
        if title2:
            return ('live', item, title2, None)
    return ('dead', item, None, "empty og:title after 2 retries")

verified, pending, dead = [], [], []
excl2 = []
n = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for outcome, item, title, note in ex.map(verify, fresh):
        n += 1
        if n % 100 == 0:
            print(f"verified {n}/{len(fresh)} live={len(verified)} pending={len(pending)} dead={len(dead)}", flush=True)
        if outcome == 'live':
            # screen og:title too
            reason = screen(title)
            if reason:
                excl2.append({"code": item['code'], "reason": f"{reason} (og:title: {title[:60]})"})
                continue
            name = clean_name(title, item.get('dir_name') or '')
            if not name:
                dead.append(item['code'])
                continue
            cat, country = infer(item['page'], item.get('dir_name') or '')
            verified.append({
                "name": name,
                "category": cat,
                "country": country,
                "description": make_desc(name, cat),
                "invite": f"https://chat.whatsapp.com/{item['code']}",
            })
        elif outcome == 'pending':
            cat, country = infer(item['page'], item.get('dir_name') or '')
            name = clean_name(item.get('dir_name') or '', '')
            pending.append({
                "name": name or "WhatsApp Group",
                "category": cat,
                "country": country,
                "description": make_desc(name or "this group", cat),
                "invite": f"https://chat.whatsapp.com/{item['code']}",
                "reason": note,
            })
        else:
            dead.append(item['code'])

print(f"DONE live={len(verified)} pending={len(pending)} dead={len(dead)} og-exclusions={len(excl2)}", flush=True)
exclusions.extend(excl2)
json.dump(verified, open(f"{WD}/team05-leads-slice5.json", "w"), indent=1)
json.dump(pending, open(f"{WD}/team05-leads-slice5-pending.json", "w"), indent=1)

# ---------- leads file ----------
disc = json.load(open(f"{WD}/team05_phase1_discovered.json"))
input_urls = {e['url'].rstrip('/') for e in json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_05.json"))}
leads_out = []
for u in disc:
    if u in input_urls:
        continue
    if '/category/' in u and 'imagesplatform' in u:
        continue
    if 'favicon' in u or 'submit-your' in u:
        continue
    from urllib.parse import urlparse as _up
    src = _up(u).netloc
    leads_out.append({"url": u, "source": src})
json.dump(leads_out, open(f"{WD}/team05-leads-slice5-leads.json", "w"), indent=1)
print("leads:", len(leads_out), flush=True)

summary = {
    "team": 5,
    "slice": "leads slice 5",
    "sources": sorted({c.get('source') for c in codes if c.get('source')}),
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads_out),
    "dead": len(dead),
    "exclusions": exclusions,
    "resume": "Resume: wave_20261109 leads_slice_05.json (184 listing pages); 125 fetched OK on first pass, 59 retried (see team05_phase1_retry.log). Fresh codes verified with curl against chat.whatsapp.com (HTTP 200 + non-empty og:title). Pending items are transport/rate-limit only and need re-verification; dead = non-200 or empty og:title after 2 retries.",
    "notes": f"Extracted {len(codes)} unique invite codes from 184 listing pages; {dup} already in the 108,364-code union; {len(fresh)} fresh candidates verified. Prescreen+og:title exclusions: {len(exclusions)} (adult/scam signals). Discovered {len(leads_out)} new listing-page URLs for future waves.",
}
json.dump(summary, open(f"{WD}/team05-leads-slice5-summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1)[:1500], flush=True)
