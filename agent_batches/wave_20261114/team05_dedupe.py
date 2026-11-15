"""Dedupe team05 mined cards vs union + within-team; emit fresh codes + leads."""
import json, re, html, os, sys

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
UNION = '/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'

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

def clean_name(n):
    n = html.unescape(n or '').strip()
    n = re.sub(r'\s+', ' ', n)
    return n

def main():
    cards_file = sys.argv[1]
    tag = sys.argv[2]
    cards = json.load(open(os.path.join(WAVE, cards_file), encoding='utf-8'))
    union = set(json.load(open(UNION, encoding='utf-8')))
    seen = set()
    fresh, leads, dup_union, dup_within = [], [], 0, 0
    for c in cards:
        name = clean_name(c.get('name', ''))
        code = (c.get('code') or '').strip()
        detail = c.get('detail') or ''
        if not code:
            if detail:
                leads.append({
                    'url': f'https://www.groupslinks.com/groups/{detail}/',
                    'name': name,
                    'country_ar': c.get('country_ar', ''),
                    'topic_ar': c.get('topic_ar', ''),
                    'page': c.get('page'),
                    'reason': 'listing has no invite code on the listing page; detail page may hold the code',
                })
            continue
        if code in union:
            dup_union += 1
            continue
        if code in seen:
            dup_within += 1
            continue
        seen.add(code)
        fresh.append({
            'code': code,
            'name': name,
            'country': COUNTRY.get((c.get('country_ar') or '').strip(), ''),
            'country_ar': c.get('country_ar', ''),
            'category': TOPIC.get((c.get('topic_ar') or '').strip(), 'Community & Social'),
            'topic_ar': c.get('topic_ar', ''),
            'page': c.get('page'),
            'detail': detail,
        })
    # dedupe leads by url
    seen_l = set(); uleads = []
    for l in leads:
        if l['url'] in seen_l:
            continue
        seen_l.add(l['url']); uleads.append(l)
    with open(os.path.join(WAVE, f'team05_fresh_{tag}.json'), 'w', encoding='utf-8') as f:
        json.dump(fresh, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, f'team05_leads_{tag}.json'), 'w', encoding='utf-8') as f:
        json.dump(uleads, f, ensure_ascii=False, indent=1)
    print(f'cards={len(cards)} fresh={len(fresh)} dup_union={dup_union} dup_within={dup_within} leads={len(uleads)}')

if __name__ == '__main__':
    main()
