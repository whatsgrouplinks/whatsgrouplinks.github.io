import re, json, time, sys, os
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

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
    'البيع والشراء': 'Buy & Sell',
    'الصداقة': 'Friendship',
}

def fetch_page(sess, p):
    url = 'https://www.groupslinks.com/' if p == 1 else f'https://www.groupslinks.com/page/{p}/'
    for i in range(3):
        try:
            r = sess.get(url, timeout=60)
            if r.status_code == 200:
                return r.text
            print(f'page {p} HTTP {r.status_code}', flush=True)
        except Exception as e:
            print(f'page {p} ERR {e}', flush=True)
        time.sleep(5)
    return None

def parse(h):
    out = []
    for c in re.findall(r'<article class="grplink-wa-related-card">(.*?)</article>', h, re.S):
        m = re.search(r'href="https://www\.groupslinks\.com/groups/([^/]+)/"', c)
        t = re.search(r'grplink-wa-related-card__title">([^<]+)</span>', c)
        co = re.search(r'badge--country">([^<]+)</span>', c)
        tp = re.search(r'badge--topic">([^<]+)</span>', c)
        inv = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', c)
        out.append({
            'detail': m.group(1) if m else '',
            'name': (t.group(1).strip() if t else ''),
            'country_ar': (co.group(1).strip() if co else ''),
            'topic_ar': (tp.group(1).strip() if tp else ''),
            'code': (inv.group(1) if inv else ''),
        })
    return out

def main():
    start, end = int(sys.argv[1]), int(sys.argv[2])
    sess = requests.Session()
    sess.headers.update(UA)
    allc = []
    out_path = os.path.join(WAVE, f'team15_cards_p{start}_{end}.json')
    failed = []
    for p in range(start, end + 1):
        h = fetch_page(sess, p)
        if not h:
            failed.append(p)
            print(f'FAIL page {p}', flush=True)
            continue
        cards = parse(h)
        print(f'page {p}: {len(cards)} cards, codes={sum(1 for c in cards if c["code"])}', flush=True)
        for c in cards:
            c['page'] = p
        allc += cards
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(allc, f, ensure_ascii=False, indent=1)
        time.sleep(1.5)
    print('TOTAL', len(allc), 'failed pages:', failed, flush=True)
    with open(os.path.join(WAVE, 'team15_mined.jsonl'), 'a', encoding='utf-8') as f:
        for c in allc:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
