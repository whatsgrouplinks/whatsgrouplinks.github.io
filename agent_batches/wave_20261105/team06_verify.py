#!/usr/bin/env python3
"""team06: re-verify Arabic pending codes (wave 20261104 team32) via og:title."""
import json, re, html, random, subprocess, threading, time, os
from concurrent.futures import ThreadPoolExecutor

BASE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
PENDING = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team32-unverified-pending.json'
UNION = os.path.join(BASE, 'dedupe_union.json')
PROGRESS = os.path.join(BASE, 'team06-progress.jsonl')
UA = 'Mozilla/5.0'

def code_of(inv):
    m = re.match(r'https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', inv or '')
    return m.group(1) if m else None

def fetch(code):
    """Returns (http_code, og_title or '', og_image or '', err)."""
    try:
        r = subprocess.run(
            ['curl', '-sL', '-A', UA, '--max-time', '20',
             '-w', '\n%{http_code}', f'https://chat.whatsapp.com/{code}'],
            capture_output=True, text=True, timeout=30)
        out = r.stdout
        lines = out.rsplit('\n', 1)
        http = lines[1].strip() if len(lines) > 1 else '000'
        body = lines[0] if len(lines) > 1 else out
        m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', body, re.I)
        if not m:
            m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', body, re.I)
        title = html.unescape(m.group(1)).strip() if m else ''
        im = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']*)', body, re.I)
        img = html.unescape(im.group(1)).replace('&amp;', '&').strip() if im else ''
        if img and not img.startswith('https://pps.whatsapp.net/'):
            img = ''
        return http, title, img, ''
    except Exception as e:
        return '000', '', '', str(e)[:80]

# ---------- content rules ----------
BLOCK_WORDS = [
    'xxx', 'porn', 'onlyfans', 'escort', 'nude', 'sex ', ' sex', 'sex:', '18+',
    'hyip', 'crypto pump', 'pump signal', 'satta', 'counterfeit', 'casino',
    'إباح', 'سكس', 'جنس', 'قاصر', 'underage', 'مخدرات', 'حشيش', 'قمار', 'كازينو',
    'ربح سريع', 'ارباح مضمونة', 'guaranteed profit', 'double your money',
    'teen sex', 'child sex', 'أطفال جنس',
]
URL_SIGNS = ['http', 'www.', '.com', '.net', '.org', '.io']
PHONE_RE = re.compile(r'\+?\d[\d\s\-]{8,}\d')
EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')

def blocked(title):
    t = ' ' + title.lower() + ' '
    for w in BLOCK_WORDS:
        if w in t:
            return f'blocked:{w.strip()}'
    for s in URL_SIGNS:
        if s in title.lower():
            return 'blocked:name-is-url'
    if PHONE_RE.search(title) or EMAIL_RE.search(title):
        return 'blocked:personal-info'
    return None

CAT_RULES = [
    ('Religion', ['قرآن', 'quran', 'qur\'an', 'islam', 'إسلام', 'اسلام', 'ديني', 'أذكار', 'اذكار', 'حديث', 'دعاء', 'رمضان', 'صلاة', 'سنة نبوية', 'مسجد']),
    ('Education', ['تعليم', 'مدرسة', 'جامعة', 'دراسة', 'دورة', 'كورس', 'learn', 'تعلم', 'لغة', 'english', 'ielts', 'لغات', 'تدريس', 'مذاكرة']),
    ('Jobs', ['وظائف', 'وظيفة', 'توظيف', 'شغل', 'jobs', 'hiring', 'employment', 'عمل في', 'فرص عمل']),
    ('News', ['أخبار', 'اخبار', 'news', 'عاجل', 'خبر عاجل']),
    ('Sports', ['رياضة', 'كرة', 'football', 'soccer', 'ريال', 'برشلونة', 'الهلال', 'النصر', 'الأهلي', 'الزمالك', 'sport', 'الدوري', 'كأس']),
    ('Entertainment', ['أفلام', 'افلام', 'مسلسل', 'فيلم', 'movies', 'series', 'netflix', 'أنمي', 'anime', 'سينما', 'مسلسلات']),
    ('Gaming', ['ألعاب', 'العاب', 'لعبة', 'pubg', 'ببجي', 'gaming', 'games', 'فري فاير', 'free fire', 'بلايستيشن']),
    ('Music', ['موسيقى', 'موسيقي', 'أغاني', 'اغاني', 'music', 'songs', 'طرب', 'أغنية']),
    ('Food & Cooking', ['طبخ', 'مطبخ', 'وصفات', 'أكل', 'اكل', 'food', 'recipes', 'cooking', 'حلويات']),
    ('Health & Fitness', ['صحة', 'صحه', 'علاج', 'دواء', 'health', 'fitness', 'رجيم', 'تخسيس', 'لياقة', 'طب بديل']),
    ('Real Estate', ['عقارات', 'عقار', 'شقق', 'real estate', 'فلل', 'أراضي']),
    ('Shopping', ['تسوق', 'بيع', 'شراء', 'سوق', 'shopping', 'market', 'تخفيضات', 'عروض']),
    ('Business', ['تجارة', 'استثمار', 'business', 'مشاريع', 'ريادة', 'تسويق', 'تداول', 'فوركس', 'forex']),
    ('Technology', ['تقنية', 'برمجة', 'تكنولوجيا', 'tech', 'programming', 'coding', 'ذكاء اصطناعي', 'كمبيوتر', 'حاسوب', 'انترنت']),
    ('Travel', ['سفر', 'سياحة', 'travel', 'tourism', 'رحلات', 'طيران']),
    ('Books & Literature', ['كتب', 'قراءة', 'روايات', 'books', 'reading', 'شعر', 'أدب', 'قصص']),
    ('Automotive', ['سيارات', 'سيارة', 'cars', 'دراجات', 'سيارات مستعملة']),
    ('Arts & Culture', ['فن', 'رسم', 'تصميم', 'art', 'poetry', 'ثقافة', 'خط عربي']),
    ('Friendship & Chat', ['زواج', 'تعارف', 'صداقة', 'دردشة', 'بنات', 'شباب', 'girls', 'friendship', 'dating', 'chat', 'تعارف بنات', 'سوالف']),
]
COUNTRY_RULES = [
    ('EG', ['مصر', 'egypt', 'القاهرة', 'cairo', 'الإسكندرية', 'alexandria', 'الجيزة', 'giza', 'مصري', 'مصرية']),
    ('SA', ['السعودية', 'saudi', 'الرياض', 'riyadh', 'جدة', 'jeddah', 'مكة', 'mecca', 'المدينة', 'medina', 'الدمام', 'dammam', 'سعودي', 'سعودية']),
    ('AE', ['الإمارات', 'emirates', 'دبي', 'dubai', 'أبوظبي', 'abu dhabi', 'الشارقة', 'sharjah', 'العين', 'عجمان', 'ajman', 'إماراتي']),
]
TOPIC = {
    'Religion': 'Quran, Islamic teachings and daily duas',
    'Education': 'learning, courses and study help',
    'Jobs': 'job openings and work opportunities',
    'News': 'breaking news and daily updates',
    'Sports': 'football, matches and sports news',
    'Entertainment': 'movies, series and entertainment',
    'Gaming': 'gaming, PUBG and online games',
    'Music': 'music and songs',
    'Food & Cooking': 'recipes, cooking and food',
    'Health & Fitness': 'health, fitness and wellbeing',
    'Real Estate': 'property, apartments and real estate',
    'Shopping': 'shopping, deals and offers',
    'Business': 'business, trade and marketing',
    'Technology': 'technology, programming and the internet',
    'Travel': 'travel, tourism and trips',
    'Books & Literature': 'books, reading and stories',
    'Automotive': 'cars and motoring',
    'Arts & Culture': 'art, design and culture',
    'Friendship & Chat': 'friendship, chatting and meeting new people',
    'Community': 'community chat and everyday conversation',
}

def classify(title):
    t = title.lower()
    cat = 'Community'
    for c, kws in CAT_RULES:
        if any(k.lower() in t for k in kws):
            cat = c; break
    country = 'International'
    for cc, kws in COUNTRY_RULES:
        if any(k.lower() in t for k in kws):
            country = cc; break
    return cat, country

def describe(name, cat, country):
    topic = TOPIC.get(cat, 'community chat and everyday conversation')
    place = {'EG': 'Egypt', 'SA': 'Saudi Arabia', 'AE': 'the UAE'}.get(country)
    if place:
        return (f"Join {name}, an Arabic WhatsApp group for {topic}. "
                f"Connect with members in {place} and across the Arab world to chat, share and stay updated on {topic}.")
    return (f"Join {name}, an Arabic WhatsApp group for {topic}. "
            f"Connect with Arabic-speaking members to chat, share and stay updated on {topic}.")

def main():
    union = set(json.load(open(UNION)))
    pending = json.load(open(PENDING))
    seen_codes = set()
    todo, skipped_union, dupes = [], 0, 0
    for r in pending:
        c = code_of(r.get('invite', ''))
        if not c:
            continue
        if c in seen_codes:
            dupes += 1; continue
        seen_codes.add(c)
        if c in union:
            skipped_union += 1; continue
        todo.append(c)
    print(f'total pending records={len(pending)} todo={len(todo)} skipped_union={skipped_union} dupes={dupes}', flush=True)

    done = []
    if os.path.exists(PROGRESS):
        for line in open(PROGRESS):
            try: done.append(json.loads(line))
            except Exception: pass
    done_codes = {d['code'] for d in done}
    todo = [c for c in todo if c not in done_codes]
    print(f'resuming: already done={len(done_codes)} remaining={len(todo)}', flush=True)

    lock = threading.Lock()
    backoff_until = [0.0]

    def work(code):
        for attempt in range(2):
            # global 429 backoff
            while True:
                with lock:
                    wait = backoff_until[0] - time.time()
                if wait <= 0: break
                time.sleep(min(wait, 30))
            time.sleep(random.uniform(0.5, 2.0))
            http, title, img, err = fetch(code)
            if http == '429':
                with lock:
                    backoff_until[0] = time.time() + 180
                if attempt == 0:
                    continue
                return {'code': code, 'status': 'pending', 'note': 'http-429'}
            if err:
                return {'code': code, 'status': 'pending', 'note': f'transport-error: {err}'}
            if http != '200':
                return {'code': code, 'status': 'pending', 'note': f'http-{http}'}
            if not title or title.lower() == 'whatsapp group invite':
                return {'code': code, 'status': 'pending', 'note': 'empty-og:title'}
            b = blocked(title)
            if b:
                return {'code': code, 'status': 'dropped', 'name': title, 'note': b}
            cat, country = classify(title)
            rec = {'name': title, 'category': cat, 'country': country,
                   'description': describe(title, cat, country),
                   'invite': f'https://chat.whatsapp.com/{code}', 'image': img}
            return {'code': code, 'status': 'verified', 'record': rec}
        return {'code': code, 'status': 'pending', 'note': 'http-429'}

    results = list(done)
    n = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(work, todo):
            results.append(res)
            n += 1
            with open(PROGRESS, 'a') as f:
                f.write(json.dumps(res, ensure_ascii=False) + '\n')
            if n % 100 == 0:
                v = sum(1 for r in results if r['status'] == 'verified')
                p = sum(1 for r in results if r['status'] == 'pending')
                d = sum(1 for r in results if r['status'] == 'dropped')
                print(f'progress {len(results)}/{len(pending)} verified={v} pending={p} dropped={d}', flush=True)

    verified = [r['record'] for r in results if r['status'] == 'verified']
    pend = [{'code': r['code'], **({'name': r['name']} if r.get('name') else {}), 'note': r['note']}
            for r in results if r['status'] == 'pending']
    drops = [{'code': r['code'], 'name': r.get('name', ''), 'note': r['note']}
             for r in results if r['status'] == 'dropped']
    json.dump(verified, open(os.path.join(BASE, 'team06-arabic.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(pend, open(os.path.join(BASE, 'team06-unverified-pending.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump([], open(os.path.join(BASE, 'team06-leads.json'), 'w'))
    import collections
    print('DONE verified=%d pending=%d dropped=%d skipped_union=%d' % (len(verified), len(pend), len(drops), skipped_union))
    print('pending reasons:', collections.Counter(r['note'] for r in pend))
    print('drop reasons:', collections.Counter(r['note'] for r in drops))
    print('categories:', collections.Counter(r['category'] for r in verified))
    print('countries:', collections.Counter(r['country'] for r in verified))

if __name__ == '__main__':
    main()
