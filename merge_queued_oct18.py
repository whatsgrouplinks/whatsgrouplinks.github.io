#!/usr/bin/env python3
"""Phase 1A: Merge queued scraped team files -> dedupe -> porn-filter -> candidates.
No network. Output: queued_new_oct18.json + report.
"""
import json, glob, re, os, time

SITE = os.path.dirname(os.path.abspath(__file__))

def canon_code(invite):
    if not invite:
        return ''
    u = invite.strip()
    # take last path segment, drop query/fragment
    code = u.split('?')[0].split('#')[0].rstrip('/').split('/')[-1].strip()
    return code

def canon_invite(code):
    return f'https://chat.whatsapp.com/{code}'

# Python mirror of submit.html ADULT_RE (v4 Oct 18 ~14:55 PKT: girls groups ALLOWED per owner;
# v4 closes gaps found in live audit — suggestive-emoji adult patterns v3 missed)
ADULT_RE = re.compile(
    r'\b(porn|pornography|xxx|sex|sexy|nudes?|naked|escort|playboy|call[\s-]?girls?|'
    r'bhabhi|aunty|mms|'
    r'leak(?:ed|s)?[\s-]?videos?|viral[\s-]?videos?|'
    r'bedroom[\s-]?videos?|blue[\s-]?films?|adult[\s-]?videos?|'
    r'sex[\s-]?(videos?|chat)|sexy[\s-]?videos?|porn[\s-]?videos?|'
    r'xxx[\s-]?videos?|hot[\s-]?videos?|'
    r'massage[\s-]?girls?)\b|18\+|'
    r'🍆|videos?\W{0,5}🤤|🤤\W{0,5}videos?|only\s*girls?\W{0,5}[🥵🤤]|'
    r'leaks?\W{0,10}(paid|vip|premium|membership)|'
    r'(paid|vip|premium)\W{0,20}leaks?|leaks?\W{0,5}[🥵🤤🍆🍑👙]', re.I)
LEGIT_ADULT = re.compile(r'adult\s+(education|quran|class|course|learning)', re.I)
# Negation guard (v4.1): "no porn" / "don't send nudes" / "porn not allowed" is RULES
# text on legit groups — not adult content. Skip adult-pattern matches that are negated.
NEGATE_BEFORE_RE = re.compile(
    r"\b(no|not|never|without|against|banned?|prohibit\w*|free from)\b(?:\W+\w+){0,5}\W*$"
    r"|n['\u2019]?t(?:\W+\w+){0,5}\W*$", re.I)
NEGATE_AFTER_RE = re.compile(
    r"^\W*(?:\w+\W+){0,5}(not|never|banned?|prohibit\w*|didn['\u2019]?t|don['\u2019]?t|doesn['\u2019]?t|n['\u2019]?t|🚫|❌|⛔)"
    r"|^\W*(?:\w+\W+){0,5}(nhi|nahi|nahin)\b", re.I)

def is_adult(name, desc):
    t = f'{name or ""} {desc or ""}'
    if LEGIT_ADULT.search(t):
        return False
    for m in ADULT_RE.finditer(t):
        before = t[max(0, m.start() - 30):m.start()]
        after = t[m.end():m.end() + 60]
        if NEGATE_BEFORE_RE.search(before):
            continue
        if NEGATE_AFTER_RE.search(after):
            continue
        return True
    return False

CAT_MAP = {
    'education': 'Education',
    'business': 'Business',
    'buysell': 'Buy Sell', 'buy sell': 'Buy Sell',
    'buy/sell': 'Buy Sell',
    'games': 'Gaming', 'gaming': 'Gaming',
    'community': 'Community & Social',
    'community & social': 'Community & Social',
    'money/earning': 'Online Earning',
    'online earning': 'Online Earning',
    'business/advertising/marketing': 'Business',
    'finance': 'Finance',
    'jobs': 'Jobs',
    'entertainment': 'Entertainment',
    'friendship': 'Friendship',
    'islamic': 'Islamic',
    'news': 'News',
    'technology': 'Technology',
    'sports': 'Sports',
    'health': 'Health',
    'funny': 'Funny',
    'travel & tourism': 'Travel & Tourism',
    'shopping': 'Shopping',
    'social/friendship/community': 'Community & Social',
    'movies': 'Entertainment',
    'music': 'Entertainment',
    'study': 'Education',
    'crypto': 'Finance',
    'cryptocurrency': 'Finance',
    'trading': 'Finance',
    'earnings': 'Online Earning',
    'earning': 'Online Earning',
}

def norm_cat(c):
    c = (c or '').strip()
    if not c:
        return 'Community & Social'
    return CAT_MAP.get(c.lower(), c.title() if c == c.lower() else c)

def main():
    t0 = time.time()
    # existing codes
    existing = json.load(open(os.path.join(SITE, 'groups.json')))
    existing_codes = set()
    for g in existing:
        code = canon_code(g.get('invite', ''))
        if code:
            existing_codes.add(code)
    print(f'Existing groups: {len(existing)}, unique codes: {len(existing_codes)}', flush=True)

    seen = {}
    stats = {'files': 0, 'records': 0, 'no_code': 0, 'dup_in_queue': 0,
             'dup_existing': 0, 'adult': 0}
    for f in sorted(glob.glob(os.path.join(SITE, 'scraped', 'team*.json'))):
        stats['files'] += 1
        try:
            d = json.load(open(f))
        except Exception as e:
            print(f'  ERR {f}: {e}', flush=True); continue
        if isinstance(d, dict):
            d = d.get('groups', d.get('data', []))
        if not isinstance(d, list):
            continue
        for g in d:
            if not isinstance(g, dict):
                continue
            stats['records'] += 1
            code = canon_code(g.get('invite', ''))
            if not code or len(code) < 10:
                stats['no_code'] += 1
                continue
            if code in seen:
                stats['dup_in_queue'] += 1
                continue
            if code in existing_codes:
                stats['dup_existing'] += 1
                continue
            name = (g.get('name') or '').strip()
            desc = (g.get('description') or g.get('desc') or '').strip()
            if is_adult(name, desc):
                stats['adult'] += 1
                continue
            seen[code] = {
                'name': name or f'WhatsApp Group {code[:8]}',
                'category': norm_cat(g.get('category')),
                'description': desc,
                'image': (g.get('image') or '').strip(),
                'invite': canon_invite(code),
                'country': (g.get('country') or '').strip(),
            }

    cands = list(seen.values())
    out = os.path.join(SITE, 'queued_new_oct18.json')
    json.dump(cands, open(out, 'w'), ensure_ascii=False)
    print(f'\nFiles: {stats["files"]}, records: {stats["records"]}', flush=True)
    print(f'no_code: {stats["no_code"]}, dup_in_queue: {stats["dup_in_queue"]}, '
          f'dup_existing: {stats["dup_existing"]}, adult_filtered: {stats["adult"]}', flush=True)
    print(f'NEW CANDIDATES: {len(cands)} -> {out}', flush=True)
    print(f'Done in {time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    main()
