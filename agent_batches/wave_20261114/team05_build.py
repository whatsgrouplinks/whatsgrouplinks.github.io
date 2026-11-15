"""Screen verified-live records, build candidates/pending/leads/summary.
Usage: team05_build.py"""
import json, re, os
from collections import Counter

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'

BET = re.compile(r'1xbet|linebet|melbet|mellbet|ميل بيت|bet365|betano|betway|mostbet|parimatch|xbet|مراهن|قمار|كازينو|سلوت|tigrinho|fortune.?tiger|sinais|plataformas pagantes|wjbet|casino|slots?|betting|aposta', re.I)
AIRDROP = re.compile(r'airdrop|ايردروب|خيارات ثنائية|binary option|opções binárias|opcoes binarias', re.I)
PORN = re.compile(r'xnxx|xxx|porn|onlyfans|🔞|اباح|نيك|كسم|شرموط|boquete|punheta|pelada', re.I)
PHONE = re.compile(r'\+?\d[\d\s\-]{9,}\d')

def porn_hit(text):
    if PORN.search(text):
        return True
    # 'سكس' (sex) as a word, but NOT inside 'الجنسيات' (nationalities)
    t = text.replace('الجنسيات', '').replace('جنسيات', '').replace('الجنسية', '').replace('جنسية', '')
    if 'سكس' in t:
        return True
    # 'جنس' standalone (not جنسية/جنسيات)
    if re.search(r'جنس(?!ية|يات)', t):
        return True
    return False

def clean_name(n):
    n = (n or '').strip()
    n = n.strip('"').strip("'").strip('«»').strip()
    n = re.sub(r'\s+', ' ', n)
    return n

def screen(rec):
    """Returns (keep, reason)."""
    name = rec.get('name', '')
    og = rec.get('og_title', '')
    text = f'{name} {og}'
    if BET.search(text):
        return False, 'betting/casino signals (1xbet/Linebet/Mellbet/casino)'
    if AIRDROP.search(text):
        return False, 'crypto-airdrop / binary-options scam signals'
    if porn_hit(text):
        return False, 'hard porn/xxx signals in live title'
    return True, ''

def build_name(rec):
    name = clean_name(rec.get('name', ''))
    og = clean_name(rec.get('og_title', ''))
    if (not name) or name.rstrip().endswith('…'):
        name = og
    # strip phone numbers (personal info) from the display name
    name = PHONE.sub('', name).strip()
    name = re.sub(r'\s+', ' ', name).strip(' -–—')
    return name

def main():
    main_state = json.load(open(os.path.join(WAVE, 'team05_verified_p61_160.json.state.json'), encoding='utf-8'))
    records = list(main_state.values())
    label_path = os.path.join(WAVE, 'team05_verified_labels.json')
    label_records = []
    if os.path.exists(label_path):
        label_records = json.load(open(label_path, encoding='utf-8'))
        # only label-only codes (main already covers the 9 overlaps)
        main_codes = {r['code'] for r in records}
        label_records = [r for r in label_records if r['code'] not in main_codes]
        records += label_records

    live = [r for r in records if r['status'] == 'live']
    dead = [r for r in records if r['status'] == 'dead']
    pending = [r for r in records if r['status'] == 'pending']

    candidates, excluded, flagged = [], [], []
    seen_codes = set()
    for r in live:
        code = r['code']
        if code in seen_codes:
            continue
        seen_codes.add(code)
        keep, reason = screen(r)
        if not keep:
            excluded.append({'code': code, 'name': r.get('name', ''), 'og_title': r.get('og_title', ''), 'reason': reason})
            continue
        name = build_name(r)
        if not name:
            excluded.append({'code': code, 'name': r.get('name', ''), 'og_title': r.get('og_title', ''), 'reason': 'no usable name (personal info only)'})
            continue
        cat = r.get('category') or 'Community & Social'
        country = r.get('country') or ''
        desc = f"Join {name}, an active WhatsApp group for {cat.lower()}."
        if country:
            desc += f" Based in {country}."
        desc += " Connect with members, share updates and join the conversation."
        candidates.append({
            'name': name,
            'category': cat,
            'country': country,
            'description': desc,
            'invite': f'https://chat.whatsapp.com/{code}',
        })
        # flag investment/MLM-flavoured keeps for coordinator review
        if re.search(r'dxn|استثمر|تداول|فوركس|اربح|مليون دولار|affiliate|أرباح', f"{r.get('name','')} {r.get('og_title','')}", re.I):
            flagged.append({'code': code, 'name': name, 'og_title': r.get('og_title', ''), 'note': 'investment/affiliate-flavoured; kept (not on hard drop list) — coordinator review'})

    # leads: merge both batches, dedupe by URL
    leads = []
    seen_u = set()
    for fn in ('team05_leads_p61_160.json', 'team05_leads_labels.json'):
        p = os.path.join(WAVE, fn)
        if os.path.exists(p):
            for l in json.load(open(p, encoding='utf-8')):
                if l['url'] in seen_u:
                    continue
                seen_u.add(l['url'])
                leads.append(l)

    pending_out = [{'code': r['code'], 'reason': r.get('verify_reason', '') or 'pending verification', 'name': r.get('name', '')} for r in pending]

    with open(os.path.join(WAVE, 'team05-candidates.json'), 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, 'team05-pending.json'), 'w', encoding='utf-8') as f:
        json.dump(pending_out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, 'team05-leads.json'), 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, 'team05-excluded.json'), 'w', encoding='utf-8') as f:
        json.dump(excluded, f, ensure_ascii=False, indent=1)

    cats = Counter(c['category'] for c in candidates)
    ctrs = Counter(c['country'] for c in candidates)
    print(f'live={len(live)} dead={len(dead)} pending={len(pending)}')
    print(f'candidates={len(candidates)} excluded={len(excluded)} flagged={len(flagged)} leads={len(leads)}')
    print('categories:', dict(cats))
    print('countries:', dict(ctrs))
    print('flagged:', json.dumps(flagged, ensure_ascii=False)[:1500])

if __name__ == '__main__':
    main()
