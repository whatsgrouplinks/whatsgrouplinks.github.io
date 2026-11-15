import re, json, html
from collections import Counter

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
COUNTRY = {
    'مصر': 'EG', 'اليمن': 'YE', 'السعودية': 'SA', 'المغرب': 'MA', 'سوريا': 'SY',
    'الأردن': 'JO', 'عُمان': 'OM', 'عمان': 'OM', 'العراق': 'IQ', 'الإمارات': 'AE',
    'الامارات': 'AE', 'الجزائر': 'DZ', 'لبنان': 'LB', 'تونس': 'TN', 'ليبيا': 'LY',
    'السودان': 'SD', 'تركيا': 'TR', 'قطر': 'QA', 'موريتانيا': 'MR', 'البحرين': 'BH',
    'الكويت': 'KW', 'فلسطين': 'PS', 'الصومال': 'SO', 'جيبوتي': 'DJ', 'جزر القمر': 'KM',
    'كل الدول': '',
}
TOPIC = {
    'مجتمع ودردشة عامة': 'Community & Social',
    'منوعات أخرى': 'Community & Social',
    'الإسلاميات والقرآن الكريم': 'Islamic',
    'الصحة والنمط الصحي': 'Health',
    'الترفيه والألعاب Gaming': 'Entertainment',
    'المال والأعمال والاستثمار': 'Business',
    'الوظائف والتعليم': 'Jobs',
    'المرأة والمنزل': 'Community & Social',
    'الهواية والفنون': 'Entertainment',
    'التكنولوجيا والمستقبل': 'Technology',
    'الرياضة': 'Sports',
    'الأخبار': 'News',
    'الطبخ': 'Cooking',
    'الشعر': 'Poetry',
    'التعليم': 'Education',
    'الضحك والفكاهة': 'Funny',
    'الألعاب': 'Gaming',
    'العملات الرقمية': 'Crypto',
    'العقارات': 'Real Estate',
    'البيع والشراء': 'Buy Sell',
    'الصداقة': 'Community & Social',
}

# Hard drops decided on LIVE og:title (manual review of all 216 live titles)
DROPS = {
    'InSz9fZXXEg0nE7rWbXGqh': 'live og:title "سكس ومتعه" — hard porn/sex content',
    'Kd8ESkXxznr3RfV02znbXJ': 'live og:title "مجموعة سكس" — hard porn/sex content',
    'CQHv7la2HXhEJOx57Va939': 'live og:title "الربح من 1Xbet" — betting (1xBet)',
    'K4PmmGzK7yNLWmAkPOSEZw': 'live og:title game-account hacking service with 18+ marker ("هكر ... اي حسبات ... 🔞") — paid hack',
    'F2WQtsGW6NZ8GZ1KwE5Aii': 'live og:title "اربح مع بوت alpha trader" — trading-bot profit promise ("free money" scam flavour)',
    'CjJFzZycvLsIBF99GPgFCu': 'live og:title "Nizar FX" with red/green signal emojis — binary-options/FX signal group',
}
# Kept but flagged for coordinator review (MLM/investment/earning flavour, per team15 precedent)
FLAG = {
    'E2nLCZufW0qKVSAxXWNFVN': 'crypto trading/investment group ("تداول في عملات الرقميه") — not an airdrop, kept',
    'G61GtCEzRBQIWAt9mm0nqU': 'USDT buy/sell group — P2P crypto exchange, kept',
    'FbbqqwAtch69o3GgXvyvr4': 'listing name "بوت ربح حقيقي" (real profit bot) but live og:title is benign social-media support — kept on live title',
    'FMcYMO9opvo3H0vDBgBt5r': 'generic "earn online" group — kept',
    'D6ESUB2nCkxA6bFGPbrbyT': 'earn-money via Sham Cash group — kept',
    'Kk5MzmawyYDE0WAWuM8nFM': '"Amplicloud" investment platform — kept',
    'GT1ysM3lNwCA5GHPQeQtIy': '"guaranteed investment" (اسثمار مضمون) wording — kept per team15 MLM precedent',
    'JcRdR9OkT8D6o9fumSzjtn': 'wealth-building pitch ("نصنع الثراء") — kept',
    'IzMdR4whuhUHLiLnnAxZ7Z': 'AI financial project pitch — kept',
    'ByUAqdvakZP5VwGidkFLMJ': 'DXN opportunity group — kept per team15 DXN precedent',
    'I5mU1GXwDnHDjahkKjzTVR': 'DXN/global-company opportunity group — kept per team15 DXN precedent',
    'Kcod0oqudlIHppmUvPPSHH': '"invest from home" pitch — kept',
}

def clean_name(r):
    name = html.unescape((r['name'] or '').strip())
    og = html.unescape((r['og_title'] or '').strip())
    # truncated listing name -> live title (team15 rule)
    if (not name) or name.endswith('…') or 'chat.whatsapp' in name or 'http' in name:
        return og
    # emoji-only live title but usable listing name -> listing name
    if og and not re.search(r'[A-Za-z\u0600-\u06FF0-9]', og):
        pass
    # strip directory disambiguation counter " <n>" at end
    name = re.sub(r' \d+$', '', name)
    return name

def main():
    allv = json.load(open(WAVE + 'team04_verified_p31_60.json', encoding='utf-8'))
    live = [r for r in allv if r['status'] == 'live']
    dead = [r for r in allv if r['status'] == 'dead-empty']
    pend = [r for r in allv if r['status'] == 'pending']
    cands, excl, flagged = [], [], []
    for r in live:
        code = r['code']
        if code in DROPS:
            excl.append({'code': code, 'name': r['name'], 'og_title': r['og_title'], 'reason': DROPS[code]})
            continue
        name = clean_name(r)
        cat = TOPIC.get(r['topic_ar'], 'Community & Social')
        cc = COUNTRY.get(r['country_ar'], '')
        desc = f"Join {name}, an active WhatsApp group for {cat.lower()}."
        if cc:
            desc += f" Country: {cc}."
        cands.append({'name': name, 'category': cat, 'country': cc,
                      'description': desc,
                      'invite': f"https://chat.whatsapp.com/{code}"})
        if code in FLAG:
            flagged.append({'code': code, 'name': name, 'og_title': r['og_title'], 'note': FLAG[code]})
    # sanity: no dup codes, all codes fresh
    assert len({c['invite'] for c in cands}) == len(cands)
    json.dump(cands, open(WAVE + 'team04-candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(excl, open(WAVE + 'team04-exclusions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(pend, open(WAVE + 'team04-pending.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # leads: no-code cards, unique detail URLs
    cards = json.load(open(WAVE + 'team04_cards_p31_60.json', encoding='utf-8'))
    leads, seen = [], set()
    for c in cards:
        if not c['code'] and c['detail'] and c['detail'] not in seen:
            seen.add(c['detail'])
            leads.append({'detail_url': f"https://www.groupslinks.com/groups/{c['detail']}/",
                          'page': c['page'], 'name': c['name'], 'reason': 'no invite code on listing card'})
    json.dump(leads, open(WAVE + 'team04-leads.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('live', len(live), 'kept', len(cands), 'excluded', len(excl), 'dead', len(dead), 'pending', len(pend), 'leads', len(leads))
    print('categories', Counter(c['category'] for c in cands))
    print('countries', Counter(c['country'] for c in cands))
    print('flagged', len(flagged))
    for f in flagged:
        print(' FLAG', f['code'], f['note'])
    for e in excl:
        print(' DROP', e['code'], e['reason'])
    # spot-check a few descriptions / names
    for c in cands[:5]:
        print(' CAND', c)

if __name__ == '__main__':
    main()
