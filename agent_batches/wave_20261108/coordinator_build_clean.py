#!/usr/bin/env python3
"""Coordinator merge/validation for WGL wave 20261108.
Reads all 24 team files in team-number order, dedupes (first-team-wins),
screens porn/adult-emoji/scam/PII, canonicalises categories, fills
descriptions, normalises /invite/ URLs, and writes:
  wave_20261108_verified_clean.json, wave_20261108_pending_all.json,
  wave_20261108_leads_all.json, wave_20261108_excluded.json,
  validation_report.json
Run from $HOME (wave dir contains inspect.py shadowing stdlib inspect).
"""
import json, re, os, unicodedata
from collections import Counter, defaultdict

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
UNION = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))

CANON = ["Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
         "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
         "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate",
         "Buy & Sell","Finance","Funny"]
ALIASES = {
    "buy-sell":"Buy & Sell","buysell":"Buy & Sell","buy sell":"Buy & Sell",
    "buy & sell":"Buy & Sell","movies":"Entertainment","movie":"Entertainment",
    "music":"Entertainment","religious":"Islamic","religion":"Islamic",
    "education":"Education","business":"Business","jobs":"Jobs","job":"Jobs",
    "sports":"Sports","sport":"Sports","news":"News","health":"Health",
    "technology":"Technology","tech":"Technology","gaming":"Gaming","games":"Gaming",
    "game":"Gaming","friendship":"Friendship","friends":"Friendship",
    "community":"Community & Social","community & social":"Community & Social",
    "online earning":"Online Earning","earning":"Online Earning","crypto":"Crypto",
    "cooking":"Cooking","food":"Cooking","poetry":"Poetry","shayari":"Poetry",
    "travel":"Travel","scholarship":"Scholarship","freelance":"Freelance",
    "real estate":"Real Estate","finance":"Finance","funny":"Funny","fun":"Funny",
    "islamic":"Islamic","islam":"Islamic","entertainment":"Entertainment",
    "shopping":"Buy & Sell","digital marketing":"Business","marketing":"Business",
}
ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
# porn tokens checked in NAME (word-ish); description-only hits are flagged, not dropped,
# except adult emoji which drops wherever found.
PORN_NAME_RES = [
    re.compile(r'\bporn\b', re.I), re.compile(r'\bxxx\b', re.I),
    re.compile(r'\bbokep\b', re.I), re.compile(r'\bhentai\b', re.I),
    re.compile(r'\bsex\b', re.I), re.compile(r'\bescort\b', re.I),
    re.compile(r'call[\s\-]?girl', re.I), re.compile(r'\bnude', re.I),
    re.compile(r'onlyfans', re.I), re.compile(r'\bcamgirl\b', re.I),
    re.compile(r'xvideos|xnxx|pornhub', re.I),
]
SCAM_NAME_RES = [
    re.compile(r'bitfinex', re.I), re.compile(r'paypal\s+(loader|receiver)', re.I),
    re.compile(r'counterfeit', re.I), re.compile(r'fake\s+currency', re.I),
    re.compile(r'\bcarding\b', re.I), re.compile(r'cc\s+seller', re.I),
    re.compile(r'\bforsage\b', re.I), re.compile(r'b[\s\-]?love', re.I),
    re.compile(r'vendas?\s+de\s+documentos', re.I), re.compile(r'cartel\s+dos\s+7', re.I),
    re.compile(r'virus[\s_\-]?data[\s_\-]?hack', re.I),
]
BETTING_RES = [
    re.compile(r'1xbet', re.I), re.compile(r'bet\s*tips?', re.I),
    re.compile(r'fixed\s+match', re.I), re.compile(r'sure\s+odds', re.I),
    re.compile(r'sporty\s+hero', re.I), re.compile(r'betway', re.I),
    re.compile(r'teen\s*patti', re.I),
]
PHONE_RE = re.compile(r'\d{7,}')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,30})')
X_RUN_RE = re.compile(r'^x{4,}$', re.I)

def deobfuscate(s):
    return unicodedata.normalize('NFKD', s or '')

def canon_cat(c):
    if not c: return None
    c = str(c).strip()
    if c in CANON: return c
    return ALIASES.get(c.lower())

def extract_code(invite):
    m = CODE_RE.search(invite or '')
    return m.group(1) if m else None

TEAMS = [
    (1,  'leads-harvest-a', 'leads slice 1 (idx 0-114)'),
    (2,  'leads-harvest-b', 'leads slice 2 (idx 115-229)'),
    (3,  'leads-harvest-c', 'leads slice 3 (idx 230-345)'),
    (4,  'leads-harvest-d', 'leads slice 4 (idx 346-460)'),
    (5,  'leads-harvest-e', 'leads slice 5 (idx 461-575)'),
    (6,  'leads-harvest-f', 'leads slice 6 (idx 576-691)'),
    (7,  'leads-harvest-g', 'leads slice 7 (idx 692-806)'),
    (8,  'leads-harvest-h', 'leads slice 8 (idx 807-922)'),
    (9,  'groupda', 'groupda.com AJAX/Wayback'),
    (10, 'groupssor-grupbul', 'groupssor API + grupbul'),
    (11, 'groupizo', 'groupizo.com sitemaps'),
    (12, 'igrupos-ongrupos', 'igrupos + ongrupos'),
    (13, 'appgrouplink-groupsinvite', 'appgrouplink + groupsinvite.link'),
    (14, 'groupjoin', 'groupjoin.link new tags'),
    (15, 'whatsappkanali-linkado', 'whatsappkanali + linkado.app'),
    (16, 'newdirs-global', 'new dirs — global/Mideast'),
    (17, 'newdirs-southasia', 'new dirs — South Asia'),
    (18, 'newdirs-africa', 'new dirs — Africa'),
    (19, 'newdirs-seasia', 'new dirs — SE Asia'),
    (20, 'listicles-study-jobs', 'listicles — Education/Jobs'),
    (21, 'listicles-sports-movies', 'listicles — Sports/Movies'),
    (22, 'listicles-crypto-earning', 'listicles — Crypto/Earning'),
    (23, 'listicles-islamic-community', 'listicles — Islamic/Community'),
    (24, 'latam-brazil', 'LatAm/Spanish + Brazil + Nov-6 leads'),
]

def load_json(path):
    with open(path) as f:
        d = json.load(f)
    assert isinstance(d, list), f'{path} is not a list'
    return d

clean, excluded, pending_all, leads_all = [], [], [], []
seen_clean, seen_pending, seen_leads = set(), set(), set()
per_team = {}
warnings, flags = [], []
schema_errors = 0
cat_fixes = Counter()

def screen(item, team_no):
    """Returns (drop_reason or None, flag or None). Screens name+description.
    Adult-emoji rule: strict on NAME; in DESCRIPTION, sentences that PROHIBIT
    adult content ("na karein", "not allowed", "no adult", "mana hai", ...)
    are stripped first (team13's Peace-group false-positive fix)."""
    name = item.get('name') or ''
    desc = item.get('description') or ''
    # strip prohibition sentences from description before emoji check
    desc_clean = re.sub(r'[^.\n]*(na karein|not allowed|no adult|mana hai|prohibited|'
                        r'don.t share|never share|not share|no porn|no sex)[^.\n]*',
                        '', desc, flags=re.I)
    text = f'{name} {desc_clean}'
    plain = deobfuscate(text)
    if any(e in name for e in ADULT_EMOJI) or any(e in desc_clean for e in ADULT_EMOJI):
        return ('adult-emoji', None)
    for rx in PORN_NAME_RES:
        if rx.search(deobfuscate(name)):
            return ('porn-keyword-in-name', None)
    for rx in SCAM_NAME_RES:
        if rx.search(deobfuscate(name)):
            return ('scam', None)
    if X_RUN_RE.match(name.strip()):
        return ('xxx-marker-name', None)
    if PHONE_RE.search(name):
        return ('phone-number-in-name', None)
    if name.strip().upper() == 'SHEYI LEGIT ONLINE UPDATE':
        return ('scam-airdrop-pitch (team05 drop vs team10 keep)', None)
    # flags (kept)
    flag = None
    for rx in BETTING_RES:
        if rx.search(deobfuscate(name)):
            flag = 'betting'; break
    if name.strip() in ('.', 'G', ''):
        flag = 'degenerate-name'
    if 'FUCK' in name.upper():
        flag = 'profanity'
    if 'HACK' in name.upper() and 'FREE FIRE' in name.upper():
        flag = 'cheat-sale'
    if '🫦' in name or '😈' in name:
        flag = 'borderline-emoji'
    if name.strip().upper().startswith('AUNTY'):
        flag = 'borderline-adult-name'
    if 'P0lnito' in name:
        flag = 'ambiguous-leet-name'
    return (None, flag)

for team_no, stem, slice_label in TEAMS:
    vpath = os.path.join(WAVE, f'team{team_no:02d}-{stem}.json')
    ppath = os.path.join(WAVE, f'team{team_no:02d}-{stem}-pending.json')
    lpath = os.path.join(WAVE, f'team{team_no:02d}-{stem}-leads.json')
    raw_v = load_json(vpath); raw_p = load_json(ppath); raw_l = load_json(lpath)
    kept = pend = leads = 0
    for item in raw_v:
        code = extract_code(item.get('invite', ''))
        if not code:
            schema_errors += 1
            excluded.append({'team': team_no, 'reason': 'bad-invite-format', 'item': item})
            continue
        if len(code) != 22:
            # keep only exact 22-char codes per schema; shorter/longer are bad format
            schema_errors += 1
            excluded.append({'team': team_no, 'reason': f'bad-code-length-{len(code)}', 'item': item})
            continue
        if code in UNION:
            excluded.append({'team': team_no, 'reason': 'union-dup', 'code': code,
                             'name': item.get('name')})
            continue
        if code in seen_clean:
            excluded.append({'team': team_no, 'reason': 'cross-team-dup', 'code': code,
                             'name': item.get('name')})
            continue
        drop, flag = screen(item, team_no)
        if drop:
            excluded.append({'team': team_no, 'reason': drop, 'code': code,
                             'name': item.get('name')})
            continue
        # canonicalise category
        cat = canon_cat(item.get('category'))
        if cat is None:
            cat_fixes[str(item.get('category'))] += 1
            cat = 'Community & Social'
            warnings.append(f"team{team_no:02d} {code}: unmapped category "
                            f"{item.get('category')!r} -> Community & Social")
        elif cat != item.get('category'):
            cat_fixes[f"{item.get('category')}->{cat}"] += 1
        name = (item.get('name') or '').strip()
        if not name:
            schema_errors += 1
            excluded.append({'team': team_no, 'reason': 'empty-name', 'code': code, 'item': item})
            continue
        desc = (item.get('description') or '').strip()
        if not desc:
            desc = (f"Join {name}, a WhatsApp group listed under {cat}. "
                    f"Connect with members and stay updated at this group's join screen.")
        country = (item.get('country') or '').strip() or 'International'
        if country != 'International':
            country = country.upper()
            if len(country) != 2:
                country = 'International'
        rec = {'name': name, 'category': cat, 'country': country,
               'description': desc,
               'invite': f'https://chat.whatsapp.com/{code}', 'image': ''}
        clean.append(rec)
        seen_clean.add(code)
        kept += 1
        if flag:
            flags.append({'code': code, 'team': team_no, 'flag': flag, 'name': name})
    for item in raw_p:
        code = extract_code(item.get('invite', ''))
        if not code or code in UNION or code in seen_clean or code in seen_pending:
            if code and code not in UNION and code not in seen_clean:
                excluded.append({'team': team_no, 'reason': 'pending-dup', 'code': code,
                                 'name': item.get('name')})
            continue
        drop, flag = screen(item, team_no)
        if drop:
            excluded.append({'team': team_no, 'reason': f'pending-{drop}', 'code': code,
                             'name': item.get('name')})
            continue
        cat = canon_cat(item.get('category')) or 'Community & Social'
        name = (item.get('name') or '').strip() or 'WhatsApp Group'
        desc = (item.get('description') or '').strip() or \
            f"Join {name}, a WhatsApp group listed under {cat}."
        country = (item.get('country') or '').strip() or 'International'
        if country != 'International':
            country = country.upper() if len(country) == 2 else 'International'
        pending_all.append({'name': name, 'category': cat, 'country': country,
                            'description': desc,
                            'invite': f'https://chat.whatsapp.com/{code}', 'image': '',
                            'reason': 'transport'})
        seen_pending.add(code)
        pend += 1
        if flag:
            flags.append({'code': code, 'team': team_no, 'flag': f'pending-{flag}',
                          'name': name})
    for item in raw_l:
        url = (item.get('url') or '').strip()
        if not url or 'chat.whatsapp.com' in url:
            if url:
                excluded.append({'team': team_no, 'reason': 'leads-invite-url-leak',
                                 'url': url})
            continue
        if url in seen_leads:
            continue
        seen_leads.add(url)
        leads_all.append({'url': url, 'source': item.get('source') or f'team{team_no:02d}'})
        leads += 1
    per_team[team_no] = {'slice': slice_label, 'verified_raw': len(raw_v),
                         'kept': kept, 'pending_raw': len(raw_p), 'pending_kept': pend,
                         'leads_raw': len(raw_l), 'leads_kept': leads}

def dump(name, data):
    with open(os.path.join(WAVE, name), 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

dump('wave_20261108_verified_clean.json', clean)
dump('wave_20261108_pending_all.json', pending_all)
dump('wave_20261108_leads_all.json', leads_all)
dump('wave_20261108_excluded.json', excluded)

report = {
    'baseline_groups_json': 69491,
    'dedupe_union_codes': len(UNION),
    'teams': 24,
    'verified_raw_total': sum(t['verified_raw'] for t in per_team.values()),
    'verified_clean_total': len(clean),
    'pending_raw_total': sum(t['pending_raw'] for t in per_team.values()),
    'pending_total': len(pending_all),
    'leads_raw_total': sum(t['leads_raw'] for t in per_team.values()),
    'leads_total': len(leads_all),
    'excluded_total': len(excluded),
    'excluded_by_reason': dict(Counter(e['reason'] for e in excluded)),
    'per_team': {str(k): v for k, v in per_team.items()},
    'schema_errors': schema_errors,
    'category_fixes': dict(cat_fixes),
    'flags': flags,
    'warnings': warnings,
}
dump('validation_report.json', report)
print(json.dumps({k: v for k, v in report.items() if k not in ('per_team', 'flags', 'warnings')}, indent=1))
print('PER-TEAM:')
for k, v in per_team.items():
    print(f"  team{k:02d} {v['slice'][:44]:44s} raw={v['verified_raw']:4d} kept={v['kept']:4d} "
          f"pend={v['pending_kept']:3d} leads={v['leads_kept']:3d}")
print('FLAGS:', len(flags))
for f in flags:
    print('  ', f)
