#!/usr/bin/env python3
"""TEAM 06 wave 20261110 slice 6: extract invite codes + names from fetched pages."""
import json, re, html, os, urllib.parse

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(BASE, "raw")
ALLOWED_CATS = ["Entertainment", "Jobs", "Education", "Islamic", "Sports",
                "Community & Social", "Finance", "Funny", "Buy Sell", "Health",
                "News", "Gaming", "Technology", "Business"]

leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_06.json"))
for i, l in enumerate(leads):
    l["url"] = html.unescape(l["url"])

KW_CAT = [
    ("gaming", "Gaming"), ("game", "Gaming"),
    ("bank-jobs", "Jobs"), ("jobs", "Jobs"), ("government", "Jobs"),
    ("visa", "Jobs"), ("career", "Jobs"), ("employment", "Jobs"),
    ("educational", "Education"), ("education", "Education"),
    ("general-knowledge", "Education"), ("css", "Education"),
    ("islamic", "Islamic"), ("sunni", "Islamic"), ("quran", "Islamic"),
    ("sports", "Sports"), ("cricket", "Sports"), ("football", "Sports"),
    ("breaking-news", "News"), ("news", "News"), ("national", "News"),
    ("business", "Business"), ("real-estate", "Business"),
    ("iphone-sell", "Buy Sell"), ("buy-sell", "Buy Sell"), ("sell", "Buy Sell"),
    ("social-media", "Entertainment"), ("entertainment", "Entertainment"),
    ("funny", "Funny"), ("jokes", "Funny"), ("comedy", "Funny"),
    ("health", "Health"), ("medical", "Health"),
    ("finance", "Finance"), ("forex", "Finance"), ("trading", "Finance"),
    ("money", "Finance"),
    ("technology", "Technology"), ("tech", "Technology"), ("gsm", "Technology"),
    ("food", "Community & Social"),
]
COUNTRY_KW = [("pakistan", "PK"), ("kenya", "KE"), ("tanzania", "TZ"),
              ("sri-lanka", "LK"), ("nepal", "NP"), ("bangladesh", "BD"),
              ("india", "IN"), ("nigeria", "NG"), ("ghana", "GH"),
              ("uganda", "UG"), ("ethiopia", "ET"), ("zambia", "ZM"),
              ("malaysia", "MY"), ("indonesia", "ID"), ("philippines", "PH"),
              ("turkey", "TR"), ("saudi", "SA"), ("uae", "AE"), ("dubai", "AE"),
              ("usa", "US"), ("america", "US"), ("uk", "GB"), ("london", "GB"),
              ("canada", "CA"), ("australia", "AU"), ("south-africa", "ZA")]

def cat_country_from_url(url, source):
    u = url.lower()
    m = re.search(r'/country/([a-z]{2})(?:[/?#]|$)', u)
    if m:
        country = m.group(1).upper()
    else:
        country = "International"
        for kw, cc in COUNTRY_KW:
            if kw in u:
                country = cc
                break
    cat = None
    if source == "www.groupjoin.link":
        m = re.search(r'/category/([^/?#]+)', url)
        if m:
            seg = urllib.parse.unquote(m.group(1)).replace("-", " ").strip()
            low = seg.lower()
            for kw, c in KW_CAT:
                if kw in low:
                    cat = c
                    break
            if cat is None:
                cat = "Community & Social"
    if cat is None:
        for kw, c in KW_CAT:
            if kw in u:
                cat = c
                break
    if cat is None:
        cat = "Community & Social"
    return cat, country

STOP_NAMES = {"join group", "join", "members", "member", "join now", "join whatsapp group",
              "whatsapp group", "whatsapp group link", "group link", "click here", "view group",
              "more", "read more", "advertisement", "share", "copy link", "add group",
              "submit", "search", "home", "login", "sign up", "register", "groups",
              "active", "online", "new", "latest", "trending"}

def clean_name(n):
    if not n:
        return None
    n = html.unescape(n)
    n = re.sub(r'\\u([0-9a-fA-F]{4})', lambda mm: chr(int(mm.group(1), 16)), n)
    n = n.replace('\\n', ' ').replace('\\"', '"').replace('\\\\', '\\')
    n = re.sub(r'\s+', ' ', n).strip(" \t\r\n-–—:|·•\"'“”‘’")
    n = re.sub(r'^(join|click|view)\s+', '', n, flags=re.I)
    if len(n) < 2 or len(n) > 90:
        return None
    if '<' in n or 'href' in n or 'http' in n:
        return None
    if n.lower() in STOP_NAMES:
        return None
    if re.fullmatch(r'[\d\W]+', n):
        return None
    # date-like / pure stats
    if re.fullmatch(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s*\d{2,4}', n, re.I):
        return None
    if re.fullmatch(r'\d[\d,\.]*', n):
        return None
    if re.fullmatch(r'[\d,\.]+\s*(members?|views?|subscribers?|online)?', n, re.I):
        return None
    if not re.search(r'[A-Za-z]', n):
        return None
    return n

def name_from_context(text_before):
    """text_before: plain text (tags stripped) preceding the invite link."""
    lines = [ln.strip() for ln in text_before.split("\n")]
    cands = []
    for ln in lines:
        c = clean_name(ln)
        if c:
            cands.append(c)
    if not cands:
        return None
    # prefer the candidate with most words (titles beat single category words), tie -> last
    best = max(cands, key=lambda c: (len(c.split()), len(c)))
    # but if the last candidate has >=2 words, prefer it (closest to link)
    last = cands[-1]
    if len(last.split()) >= 2:
        return last
    return best

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})')
TAG_RE = re.compile(r'<[^>]+>')

def strip_to_text(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</(p|div|li|tr|h[1-6]|td|article|section|a|button)>', '\n', s, flags=re.I)
    s = TAG_RE.sub(' ', s)
    s = html.unescape(s)
    return s

extracted = {}   # code -> record
page_stats = []
all_leads = {}   # url -> source/note

for i, l in enumerate(leads):
    url, source = l["url"], l.get("source", "")
    path = os.path.join(RAW, f"p{i}.html")
    if not os.path.exists(path):
        page_stats.append({"idx": i, "url": url, "codes": 0, "error": "no file"})
        continue
    s = open(path, encoding="utf-8", errors="ignore").read()
    cat, country = cat_country_from_url(url, source)
    is_adult_page = bool(re.search(r'/category/adult', url, re.I))

    # groupjoin JSON payload: group_title ... link pairing (with category/country/nsfw)
    gj = {}
    if "groupjoin" in source:
        for tm in re.finditer(r'group_title\\*":\\*"(.*?)\\*",\\*"group_img', s, re.S):
            seg_end = s.find('group_title', tm.end())
            seg = s[tm.end(): seg_end if seg_end != -1 else tm.end() + 9000]
            lm = re.search(r'\\"link\\":\\"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})', seg)
            if not lm:
                continue
            cm = re.search(r'\\"category_name\\":\\"([^"\\]*)', seg)
            im = re.search(r'\\"iso2\\":\\"([A-Za-z]{2})', seg)
            nm = re.search(r'\\"nsfw\\":(true|false)', seg)
            rm = re.search(r'\\"contentRating\\":(\d+)', seg)
            gcat = None
            if cm:
                raw = cm.group(1).strip()
                low = raw.lower()
                for kw, c in KW_CAT:
                    if kw in low:
                        gcat = c
                        break
                if gcat is None:
                    gcat = "Community & Social"
                if low == "adult":
                    gcat = "Adult"
            gj[lm.group(1)] = {
                "name": clean_name(tm.group(1)),
                "category": gcat,
                "country": im.group(1).upper() if im else None,
                "adult": (gcat == "Adult") or (nm and nm.group(1) == "true"),
            }

    n_here = 0
    for m in CODE_RE.finditer(s):
        code = m.group(1)
        if code in ("invite",):
            continue
        # drop channel links (they use /channel/, not matched here, but guard)
        start = max(0, m.start() - 4000)
        ctx_html = s[start:m.start()]
        ctx_html = re.sub(r'<[^>]*$', '', ctx_html)  # drop trailing partial tag
        ctx_text = strip_to_text(ctx_html)
        g = gj.get(code)
        name = (g["name"] if g else None) or name_from_context(ctx_text[-1200:])
        rec = extracted.get(code)
        if rec is None:
            extracted[code] = {"code": code, "name": name,
                               "category": (g["category"] if g and g.get("category") else cat),
                               "country": (g["country"] if g and g.get("country") else country),
                               "page": url, "source": source,
                               "adult_page": bool(is_adult_page or (g and g.get("adult")))}
            n_here += 1
        else:
            # upgrade name if missing or better (longer, more words)
            if not rec["name"] and name:
                rec["name"] = name
            elif name and rec["name"] and len(name.split()) > len(rec["name"].split()):
                rec["name"] = name
            if g:
                if g.get("category") and g["category"] != "Adult":
                    rec["category"] = g["category"]
                if g.get("country"):
                    rec["country"] = g["country"]
                if g.get("adult"):
                    rec["adult_page"] = True
    page_stats.append({"idx": i, "url": url, "codes": n_here})

    # discovered listing-page URLs on same domain (pagination/category/country/label/tag)
    for href in set(re.findall(r'href="([^"]+)"', s)):
        href = html.unescape(href).split("#")[0]
        if not href or href.startswith(("javascript:", "mailto:", "tel:")):
            continue
        full = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(full).netloc not in urllib.parse.urlparse(url).netloc:
            continue
        low = full.lower()
        if re.search(r'/(category|label|country|tag|search/label)/', low) or re.search(r'/page/\d+/?$', low) or re.search(r'[?&]page=\d+', low) or re.search(r'max-results=\d+', low):
            if full not in [x["url"] for x in leads]:
                all_leads.setdefault(full, {"url": full, "source": source,
                                            "note": "discovered listing/pagination link"})

json.dump([{"code": v["code"], "name": v["name"], "category": v["category"],
            "country": v["country"], "page": v["page"], "source": v["source"],
            "adult_page": v["adult_page"]} for v in extracted.values()],
          open(os.path.join(BASE, "team06-extracted.json"), "w"), indent=1)
json.dump(page_stats, open(os.path.join(BASE, "team06-page-stats.json"), "w"), indent=1)
json.dump(list(all_leads.values()), open(os.path.join(BASE, "team06-discovered-leads.json"), "w"), indent=1)
print("pages:", len(page_stats), "unique codes:", len(extracted))
print("pages with 0 codes:", sum(1 for p in page_stats if p["codes"] == 0))
print("codes with name:", sum(1 for v in extracted.values() if v["name"]))
print("discovered leads:", len(all_leads))
from collections import Counter
print(Counter(v["source"] for v in extracted.values()))
