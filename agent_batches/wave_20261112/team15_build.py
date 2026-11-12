import re, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team15_mine import COUNTRY, TOPIC

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
UNION = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))

ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
PORN_WORDS = [r'\bporn\b', r'\bporno\b', r'\bxxx\b', r'\bbokep\b', r'\bsex\b', r'\bsexy\b',
              r'\berotic\b', r'\bswinger\b', r'\bcornudo', r'\bpajas\b', r'\bmorbo\b',
              r'\bplay\s*boy\b', r'\bincel\b', r'xnxx', r'xvideos', r'\bsexo\b',
              r'\bsexuales\b', r'\bcaliente\b', r'\bcall.?girl', r'\bescort\b', r'\bhentai\b',
              r'\bhookup\b', r'brazzers', r'جنس', r'إباح', r'سكس', r'نيك', r'ممحون', r'شرموط',
              r'18\+.*(?:sex|porn|سكس)', r'(?:sex|porn|سكس).*18\+']
SCAM_RES = [r'\bforsage\b', r'\bholiverse\b', r'meta[\s\-]?whale\b', r'\bb-?love\b']
BET_SCAM = [r'1xbet', r'\bfixed\s+match', r'vip\s+bet\s*tips', r'free\s+vip\s+bet', r'\bbetway\b',
            r'betting.*promo', r'رهان']
TRADING_SCAM = [r'ارباح يومية من التداول', r'daily profit.*trad', r'ارباح.*تداول.*ذكاء',
                r'crypto.?airdrop', r'binary.?option', r'خيار ثنائي', r'paid.?hack',
                r'VENDA DE XIT', r'ai.?trading.*profit', r'ارباح.*ذكاء الاصطناعي']
NEG_PAT = re.compile(r'(?i)(no|not|never|don\'t|do not|prohib|forbid|ممنوع|لا\s|عدم|يمنع|proibido|sem|não pode)[^.\n]{0,60}(porn|xxx|sex|🍆|🍑|💦|👅|🔞|سكس|إباح)', re.S)

def strip_negated(text):
    sents = re.split(r'(?<=[.!؟\n])\s+', text)
    return ' '.join(s for s in sents if not NEG_PAT.search(s))

def screen(name, og):
    text = (name + ' ' + og).strip()
    t2 = strip_negated(text)
    for e in ADULT_EMOJI:
        if e in name or e in og:
            return 'adult-emoji ' + e
    low = t2.lower()
    for p in SCAM_RES:
        if re.search(p, low): return 'scam ' + p
    for p in PORN_WORDS:
        if re.search(p, low): return 'porn-keyword ' + p
    for p in BET_SCAM:
        if re.search(p, low): return 'betting-scam ' + p
    for p in TRADING_SCAM:
        if re.search(p, low): return 'trading/airdrop-scam ' + p
    return None

def build(verified_path, tag):
    res = json.load(open(verified_path, encoding='utf-8'))
    kept, pending, excl = [], [], []
    seen = set()
    dup_in_run = 0
    for r in res:
        code = r['code']
        if r['status'] == 'pending':
            pending.append({'name': r['name'], 'code': code,
                            'invite': 'https://chat.whatsapp.com/' + code,
                            'reason': 'transport failure after retries: ' + (r.get('og_title') or ''),
                            'page': r.get('page')})
            continue
        if r['status'] != 'live':
            continue
        if code in seen:
            dup_in_run += 1
            continue
        seen.add(code)
        name = r['name'].strip() or r['og_title'].strip()
        reason = screen(name, r['og_title'])
        if reason:
            excl.append({'code': code, 'name': name, 'og_title': r['og_title'], 'reason': reason})
            continue
        cc = COUNTRY.get(r['country_ar'], '')
        cat = TOPIC.get(r['topic_ar'], 'Community & Social')
        kept.append({
            'name': name,
            'category': cat,
            'country': cc,
            'description': f"Join {name}, a WhatsApp group listed under {cat}." + (f" Country: {cc}." if cc else ""),
            'invite': 'https://chat.whatsapp.com/' + code,
        })
    json.dump(kept, open(os.path.join(WAVE, f'team15-groupslinks-candidates-{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, f'team15-groupslinks-pending-{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(excl, open(os.path.join(WAVE, f'team15-exclusions-{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{tag}: kept={len(kept)} pending={len(pending)} excluded={len(excl)} dup_in_run={dup_in_run}')
    return kept, pending, excl

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
