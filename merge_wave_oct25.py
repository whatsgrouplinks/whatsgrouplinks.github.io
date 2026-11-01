#!/usr/bin/env python3
"""Merge agent-scraped WhatsApp groups into groups.json with dedupe + porn filter.
Usage: python3 merge_agent_batches_oct23.py <out1.json> <out2.json> ...
Outputs merge stats; backs up groups.json first."""
import json, re, os, sys, pickle, shutil, time

SITE = os.path.dirname(os.path.abspath(__file__))
GROUPS = os.path.join(SITE, 'groups.json')
CODES_JSON = os.path.join(SITE, '.existing_codes.json')
CODES_PKL = os.path.join(SITE, 'dedup_codes.pkl')

VALID_CATS = {'Education','Jobs','Entertainment','Islamic','News','Sports','Technology',
              'Health','Business','Gaming','Friendship','Community & Social','Online Earning',
              'Crypto','Cooking','Poetry','Travel','Scholarship','Freelance','Real Estate',
              'Buy & Sell'}
# alias -> canonical (handles scrapes with lowercase/messy categories)
ALIASES = {
    'education':'Education','jobs':'Jobs','job':'Jobs','entertainment':'Entertainment',
    'fun':'Entertainment','islamic':'Islamic','islam':'Islamic','news':'News',
    'sports':'Sports','sport':'Sports','technology':'Technology','tech':'Technology',
    'health':'Health','business':'Business','gaming':'Gaming','games':'Gaming',
    'friendship':'Friendship','friends':'Friendship','community & social':'Community & Social',
    'community':'Community & Social','social':'Community & Social','online earning':'Online Earning',
    'earning':'Online Earning','crypto':'Crypto','cooking':'Cooking','food':'Cooking',
    'poetry':'Poetry','shayari':'Poetry','travel':'Travel','scholarship':'Scholarship',
    'freelance':'Freelance','real estate':'Real Estate','buy & sell':'Buy & Sell',
    'buysell':'Buy & Sell','buy sell':'Buy & Sell','general':'Community & Social',
}

PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')

def code_of(invite):
    m = CODE_RE.search(invite or '')
    return m.group(1) if m else None

def canon_cat(c):
    if not c:
        return 'Community & Social'
    c = str(c).strip()
    if c in VALID_CATS:
        return c
    return ALIASES.get(c.lower(), 'Community & Social')

def clean_name(n):
    n = (n or '').strip()
    n = re.sub(r'\s+', ' ', n)
    return n[:120]

def main():
    files = sys.argv[1:]
    if not files:
        print("usage: merge_agent_batches_oct23.py <batch json files...>")
        sys.exit(1)

    with open(GROUPS) as f:
        groups = json.load(f)
    with open(CODES_JSON) as f:
        codes = set(json.load(f))

    stats = {'candidates':0,'added':0,'dup':0,'porn':0,'bad':0}
    new_groups = []
    batch_codes = set()
    for fp in files:
        if not os.path.exists(fp):
            print(f"SKIP missing: {fp}")
            continue
        with open(fp) as f:
            items = json.load(f)
        for g in items:
            stats['candidates'] += 1
            name = clean_name(g.get('name'))
            invite = (g.get('invite') or '').strip()
            code = code_of(invite)
            if not name or not code:
                stats['bad'] += 1
                continue
            if code in codes or code in batch_codes:
                stats['dup'] += 1
                continue
            text = f"{name} {g.get('description','')} {g.get('category','')}"
            if PORN_RE.search(text):
                stats['porn'] += 1
                continue
            cat = canon_cat(g.get('category'))
            img = (g.get('image') or '').strip()
            country = (g.get('country') or '').strip()
            raw_desc = re.sub(r'\s+', ' ', (g.get('description') or '').strip())[:300]
            if not raw_desc or 'http' in raw_desc or 'www.' in raw_desc:
                raw_desc = f"Join {name}, a WhatsApp group listed under {cat}."
            new_groups.append({
                'name': name,
                'category': cat,
                'description': raw_desc,
                'image': img,
                'invite': f"https://chat.whatsapp.com/{code}",
                'country': country,
            })
            batch_codes.add(code)

    if not new_groups:
        print("No new groups to merge.", stats)
        return

    old_total = len(groups)
    backup = GROUPS + f".backup-merge-20261025-{time.strftime('%H%M')}"
    shutil.copy2(GROUPS, backup)
    groups.extend(new_groups)
    with open(GROUPS, 'w') as f:
        json.dump(groups, f, ensure_ascii=False)
    codes |= batch_codes
    with open(CODES_JSON, 'w') as f:
        json.dump(sorted(codes), f)
    try:
        with open(CODES_PKL, 'wb') as f:
            pickle.dump(codes, f)
    except Exception as e:
        print(f"pickle update failed: {e}")
    stats['added'] = len(new_groups)
    print(f"MERGED: {old_total} -> {len(groups)} (+{len(new_groups)})")
    print(stats)
    print(f"backup: {backup}")

if __name__ == '__main__':
    main()
