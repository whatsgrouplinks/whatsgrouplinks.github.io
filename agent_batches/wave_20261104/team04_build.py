#!/usr/bin/env python3
"""Team04 build: details.json -> candidates -> dedupe/filter/verify -> output files."""
import json, re, html, os, sys

SCR = "team04_scratch"

# ---------- mappings ----------
CAT_MAP = {
    "ترفيه": "Entertainment", "دردشة": "Friendship", "تعارف": "Friendship",
    "صداقة": "Friendship", "رياضة": "Sports", "كرة القدم": "Sports",
    "تعليم": "Education", "دراسة": "Education", "وظائف": "Jobs",
    "أخبار": "News", "دين": "Islamic", "ديني": "Islamic", "إسلامي": "Islamic",
    "قرآن": "Islamic", "أعمال": "Business", "تجارة": "Business", "تسويق": "Business",
    "مال": "Finance", "اقتصاد": "Finance", "كريبتو": "Crypto",
    "صحة": "Health", "تقنية": "Technology", "تكنولوجيا": "Technology",
    "طعام": "Food", "طبخ": "Food", "سفر": "Travel", "سياحة": "Travel",
    "موسيقى": "Music", "أفلام": "Movies", "مسلسلات": "Movies",
    "ألعاب": "Gaming", "قيمنق": "Gaming", "سيارات": "Other",
    "عقارات": "Business", "موضة": "Other", "فن": "Entertainment",
    "ثقافة": "Education", "شعر": "Entertainment", "أدب": "Entertainment",
    "زواج": "Friendship", "عائلة": "Community", "مجتمع": "Community",
    "عام": "Community", "أخرى": "Other", "منوعات": "Entertainment",
    "ضحك": "Funny", "نكت": "Funny", "فكاهة": "Funny",
    "بنات": "Girls", "شباب": "Friendship", "+18": "Friendship",
    "تسوق": "Buy-Sell", "مشاهير": "Entertainment",
    "اقتباسات": "Other", "حالات": "Entertainment", "صور": "Entertainment",
    "تصميم": "Technology", "برمجة": "Technology", "لغات": "Education",
    "انجليزي": "Education", "طب": "Health", "رياضة ولياقة": "Sports",
    "حيوانات": "Pets", "طبيعة": "Travel", "أطفال": "Community",
}
COUNTRY_MAP = {
    "مصر": "EG", "السعودية": "SA", "المغرب": "MA", "الجزائر": "DZ",
    "تونس": "TN", "العراق": "IQ", "الأردن": "JO", "الإمارات": "AE",
    "فلسطين": "PS", "سوريا": "SY", "لبنان": "LB", "اليمن": "YE",
    "ليبيا": "LY", "السودان": "SD", "الكويت": "KW", "قطر": "QA",
    "البحرين": "BH", "عمان": "OM", "موريتانيا": "MR", "الصومال": "SO",
    "جيبوتي": "DJ", "تركيا": "TR", "باكستان": "PK", "الهند": "IN",
    "إندونيسيا": "ID", "ماليزيا": "MY", "ألمانيا": "DE", "فرنسا": "FR",
    "إسبانيا": "ES", "إيطاليا": "IT", "بريطانيا": "GB", "المملكة المتحدة": "GB",
    "الولايات المتحدة": "US", "أمريكا": "US", "كندا": "CA", "البرازيل": "BR",
    "نيجيريا": "NG", "كينيا": "KE", "غانا": "GH", "أوغندا": "UG",
    "تشاد": "TD", "النيجر": "NE", "مالي": "ML", "السنغال": "SN",
    "أثيوبيا": "ET", "تنزانيا": "TZ", "جنوب أفريقيا": "ZA",
    "الأرجنتين": "AR", "أستراليا": "AU", "النمسا": "AT", "بلجيكا": "BE",
    "سريلانكا": "LK", "النرويج": "NO", "أوغندا": "UG", "بوتان": "BT",
    "دولي": "International",
}
COUNTRY_EN = {
    "EG": "Egypt", "SA": "Saudi Arabia", "MA": "Morocco", "DZ": "Algeria",
    "TN": "Tunisia", "IQ": "Iraq", "JO": "Jordan", "AE": "UAE",
    "PS": "Palestine", "SY": "Syria", "LB": "Lebanon", "YE": "Yemen",
    "LY": "Libya", "SD": "Sudan", "KW": "Kuwait", "QA": "Qatar",
    "BH": "Bahrain", "OM": "Oman", "MR": "Mauritania", "SO": "Somalia",
    "DJ": "Djibouti", "TR": "Turkey", "PK": "Pakistan", "IN": "India",
    "ID": "Indonesia", "MY": "Malaysia", "DE": "Germany", "FR": "France",
    "ES": "Spain", "IT": "Italy", "GB": "UK", "US": "USA", "CA": "Canada",
    "BR": "Brazil", "NG": "Nigeria", "KE": "Kenya", "GH": "Ghana",
    "UG": "Uganda", "TD": "Chad", "NE": "Niger", "ML": "Mali", "SN": "Senegal",
    "ET": "Ethiopia", "TZ": "Tanzania", "ZA": "South Africa", "AR": "Argentina",
    "AU": "Australia", "AT": "Austria", "BE": "Belgium", "LK": "Sri Lanka",
    "NO": "Norway", "BT": "Bhutan",
}

# Arabic topic keywords -> English phrase fragments for descriptions
TOPIC_EN = [
    ("كرة القدم", "football"), ("كوره", "football"), ("رياضة", "sports"),
    ("وظائف", "job openings"), ("وظايف", "job openings"), ("توظيف", "recruitment"),
    ("شغل", "work opportunities"), ("قرآن", "Quran recitation"), ("دين", "Islamic teachings"),
    ("إسلام", "Islam"), ("أذكار", "daily dhikr"), ("حديث", "hadith"),
    ("طبخ", "cooking and recipes"), ("وصفات", "recipes"), ("أكل", "food"),
    ("دراسة", "study help"), ("مذاكرة", "exam preparation"), ("تعليم", "learning"),
    ("انجليزي", "English learning"), ("لغة", "language learning"),
    ("تجارة", "business and trade"), ("تسويق", "marketing"), ("بيع", "buying and selling"),
    ("عقارات", "real estate"), ("سيارات", "cars"), ("أخبار", "latest news"),
    ("خبر عاجل", "breaking news"), ("طقس", "weather"), ("صحة", "health tips"),
    ("طب", "medical advice"), ("تخسيس", "weight loss"), ("ريجيم", "diet plans"),
    ("تقنية", "tech news"), ("برمجة", "programming"), ("ذكاء اصطناعي", "artificial intelligence"),
    ("سفر", "travel"), ("سياحة", "tourism"), ("هجرة", "immigration"),
    ("زواج", "marriage matchmaking"), ("خطوبة", "engagement"), ("تعارف", "making new friends"),
    ("صداقة", "friendship"), ("دردشة", "chatting"), ("شات", "chat"),
    ("بنات", "girls community"), ("شباب", "youth hangout"),
    ("أفلام", "movies"), ("مسلسلات", "TV series"), ("أنمي", "anime"),
    ("أغاني", "music"), ("موسيقى", "music"), ("شعر", "poetry"),
    ("قصص", "stories"), ("روايات", "novels"), ("نكت", "jokes and humor"),
    ("ضحك", "funny content"), ("ميمز", "memes"), ("ألعاب", "gaming"),
    ("ببجي", "PUBG"), ("فري فاير", "Free Fire"), ("بلايستيشن", "PlayStation"),
    ("كريبتو", "cryptocurrency"), ("تداول", "trading"), ("فوركس", "forex"),
    ("ربح", "earning online"), ("استثمار", "investment"),
    ("عروض", "deals and offers"), ("خصومات", "discounts"), ("تسوق", "shopping"),
    ("موضة", "fashion"), ("مكياج", "makeup"), ("جمال", "beauty tips"),
    ("ديكور", "home decor"), ("تصوير", "photography"), ("تصميم", "design"),
    ("حيوانات", "pets and animals"), ("قطط", "cats"), ("طبيعة", "nature"),
    ("زراعة", "farming"), ("صيد", "fishing"), ("حالات واتس", "WhatsApp statuses"),
    ("اقتباسات", "quotes"), ("حكم", "wisdom quotes"), ("أدعية", "duas"),
    ("رمضان", "Ramadan"), ("عيد", "Eid celebrations"),
    ("جامعة", "university students"), ("مدرسة", "school students"),
    ("معلمين", "teachers"), ("أطباء", "doctors"), ("مهندسين", "engineers"),
    ("مغتربين", "expats abroad"), ("جالية", "community abroad"),
]
CAT_DESC = {
    "Entertainment": "entertainment", "Friendship": "friendship and social chat",
    "Sports": "sports", "Education": "education and learning", "Jobs": "jobs and careers",
    "News": "news updates", "Islamic": "Islamic content", "Business": "business",
    "Finance": "finance", "Buy-Sell": "buying and selling", "Health": "health and wellness",
    "Community": "community chat", "Technology": "technology", "Crypto": "crypto",
    "Travel": "travel", "Music": "music", "Movies": "movies and shows",
    "Food": "food and cooking", "Pets": "pets", "Funny": "fun and humor",
    "Girls": "girls community", "Regional": "regional chat", "Other": "general chat",
}

PORN_RES = [
    (r'\bporn\w*\b', 'porn'), (r'\bxxx\b', 'xxx'), (r'\bnude\w*\b', 'nude'),
    ('sex video', 'sex video'), (r'\bescort\w*\b', 'escort'),
    ('call girl', 'call girl'), (r'\bf+u+c+k+\w*\b', 'fuck'),
    (r'\bdick\w*\b', 'dick'), (r'\bpuss\w*\b', 'pussy'),
    (r'\bboob\w*\b', 'boobs'), (r'\banal\b', 'anal'), (r'\bbokep\b', 'bokep'),
    ('نيك', 'نيك'), ('سكس', 'سكس'),
    ('مزا دينے', 'مزا دینے'), ('مزہ دینے', 'مزہ دینے'),
    ('🥵', '🥵'), ('🍆', '🍆'), ('🍑', '🍑'), ('🔞', '🔞'),
    ('💦', '💦'), ('👅', '👅'), ('👄', '👄'), ('💋', '💋'), ('🫦', '🫦'),
    ('ورعان', 'ورعان'),
    ('سالب', 'سالب'), ('فحل', 'فحل'), ('فحول', 'فحول'),
]
SCAM_RES = [(r'\bsatta\b', 'satta'), (r'\bmatka\b', 'matka'), (r'\bhyip\b', 'hyip'),
            ('money mule', 'money mule'), ('paypal receiver', 'paypal receiver'),
            ('loader', 'loader'), (r'\bdumps\b', 'dumps'), (r'\bcvv\b', 'cvv'),
            (r'\bcarding\b', 'carding')]
MINOR_RES = [(r'\b1[1-4]teen\b', 'teen'), ('underage', 'underage'), ('قاصر', 'قاصر')]

def _hit(patterns, text):
    t = text.lower()
    for pat, label in patterns:
        if pat.startswith('\\b') or pat.startswith('('):
            if re.search(pat, t):
                return label
        else:
            if pat.lower() in t:
                return label
    return None

def drop_reason(text):
    r = _hit(PORN_RES, text)
    if r:
        return f"porn:{r}"
    r = _hit(SCAM_RES, text)
    if r:
        return f"scam:{r}"
    r = _hit(MINOR_RES, text)
    if r:
        return f"minor:{r}"
    return None

def map_cat(ar):
    ar = (ar or "").strip()
    if ar in CAT_MAP:
        return CAT_MAP[ar]
    for k, v in CAT_MAP.items():
        if k and k in ar:
            return v
    return "Other"

def map_country(ar):
    ar = (ar or "").strip()
    if ar in COUNTRY_MAP:
        return COUNTRY_MAP[ar]
    for k, v in COUNTRY_MAP.items():
        if k and k in ar:
            return v
    return "International"

def clean_name(name):
    # h1 names are already clean; og:title fallback needs boilerplate stripping
    n = name or ""
    n = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', n)  # zero-width chars
    n = re.sub(r'\s*[|｜]\s*GroupChatConnect\s*$', '', n)
    n = re.sub(r'\s*[|｜]\s*[^|｜]*$', '', n)  # " | <category>" suffix
    m = re.match(r'^\s*مجموعة\s+(.*?)\s+على واتساب\s*$', n)
    if m:
        n = m.group(1)
    m = re.match(r'^\s*مجموعة\s+(.*?)\s+على تلغرام\s*$', n)
    if m:
        n = m.group(1)
    n = re.sub(r'\s+', ' ', n).strip()
    n = re.sub(r'\s*[|｜]\s*$', '', n).strip()  # dangling pipe
    return n[:120] if n else ""

def topics_en(name):
    found = []
    for ar, en in TOPIC_EN:
        if ar in name and en not in found:
            found.append(en)
    return found[:3]

SECOND_SENTENCES = [
    "Members chat daily, share updates and connect with people who share the same interests.",
    "Join the conversation, share ideas and meet new people every day.",
    "A lively place to exchange messages, media and ideas with fellow members.",
    "Connect with members, take part in discussions and stay updated.",
]

def build_description(name_ar, cat, country, seed_id):
    topics = topics_en(name_ar)
    c_en = COUNTRY_EN.get(country, "international")
    cat_phrase = CAT_DESC.get(cat, "general chat")
    if country == "International":
        loc = "from around the world"
    else:
        loc = f"in {c_en}"
    if topics:
        t = ", ".join(topics)
        d1 = f"A WhatsApp {cat_phrase} group {loc} focused on {t}."
    else:
        d1 = f"A WhatsApp {cat_phrase} group {loc}."
    d2 = SECOND_SENTENCES[int(seed_id) % len(SECOND_SENTENCES)]
    return d1 + " " + d2

def main():
    details = json.load(open(f"{SCR}/details.json"))
    union = set(json.load(open("dedupe_union.json")))
    print("union codes:", len(union), "details:", len(details))
    cands, nodata, tg_skip, seen_codes = [], 0, 0, set()
    dup_union = dup_self = 0
    for d in details:
        code = d.get("go_code")
        if d.get("is_telegram"):
            tg_skip += 1
            continue
        if not code:
            nodata += 1
            continue
        if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code):
            nodata += 1
            continue
        if code in union:
            dup_union += 1
            continue
        if code in seen_codes:
            dup_self += 1
            continue
        seen_codes.add(code)
        cands.append(d)
    print(f"candidates: {len(cands)} nodata/bad: {nodata} telegram_skipped: {tg_skip} dup_union: {dup_union} dup_self: {dup_self}")

    items, pending, drops = [], [], {"porn": 0, "scam": 0, "minor": 0}
    for d in cands:
        name = clean_name(d.get("name", ""))
        blob = f"{name} {d.get('desc_ar','')}"
        dr = drop_reason(blob)
        if dr:
            kind = dr.split(":")[0]
            drops[kind] = drops.get(kind, 0) + 1
            continue
        cat = map_cat(d.get("cat_ar", ""))
        country = map_country(d.get("country_ar", ""))
        desc = build_description(d.get("name", ""), cat, country, d["id"])
        base = {
            "name": name or f"WhatsApp Group {d['id']}",
            "category": cat,
            "country": country,
            "description": desc,
            "invite": f"https://chat.whatsapp.com/{d['go_code']}",
            "image": "",
        }
        # verification happens separately; keep code for the verify step
        base["_code"] = d["go_code"]
        base["_id"] = d["id"]
        items.append(base)
    print("kept:", len(items), "drops:", drops)
    json.dump(items, open(f"{SCR}/candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(drops, open(f"{SCR}/drops.json", "w"), indent=1)

if __name__ == "__main__":
    main()
