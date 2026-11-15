import requests, re, json, time, html
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})')

class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []  # (href, text)
        self._href = None
        self._text = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            d = dict(attrs)
            self._href = d.get('href', '')
            self._text = []
    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)
    def handle_endtag(self, tag):
        if tag == 'a' and self._href is not None:
            self.anchors.append((self._href, ''.join(self._text)))
            self._href = None

GENERIC = re.compile(r'^(join|join now|join group|click here|click to join|link|join link|tap to join|join chat|open|visit|go|join whatsapp group)[\s\W]*$', re.I)

def clean_name(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))
    s = re.sub(r'\s+', ' ', s).strip(' -|•·\u00a0')
    return s

def extract(page_html, url):
    out = {}  # code -> name
    # 1) table rows: <tr> ... code ... </tr> -> name = text before the link cell
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', page_html, re.S | re.I):
        m = CODE_RE.search(tr)
        if not m:
            continue
        code = m.group(1)
        text = clean_name(tr)
        # remove generic join tokens
        text = re.sub(r'\b(join now|join group|join|click here|click to join)\b', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip(' -|•')
        if len(text) > 120:
            text = text[:120]
        if code not in out or (out[code] in ('', None) and text):
            out[code] = text
    # 2) list items
    for li in re.findall(r'<li[^>]*>(.*?)</li>', page_html, re.S | re.I):
        m = CODE_RE.search(li)
        if not m:
            continue
        code = m.group(1)
        if code in out and out[code]:
            continue
        text = clean_name(li)
        text = re.sub(r'\b(join now|join group|join|click here|click to join)\b', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip(' -|•')
        if len(text) > 120:
            text = text[:120]
        out.setdefault(code, text)
    # 3) anchors: text may be the group name
    p = AnchorParser()
    try:
        p.feed(page_html)
    except Exception:
        pass
    for href, text in p.anchors:
        m = CODE_RE.search(href or '')
        if not m:
            continue
        code = m.group(1)
        t = clean_name(text)
        if code not in out or not out[code]:
            out[code] = t if not GENERIC.match(t or '') else ''
        elif GENERIC.match(t or ''):
            pass
        elif not out[code] and t:
            out[code] = t
    # 4) any remaining bare codes
    for code in CODE_RE.findall(page_html):
        out.setdefault(code, '')
    return out

SOURCES = [
    ("grouplinks-arsenal", "https://grouplinks.co.uk/arsenal-whatsapp-group-links/"),
    ("grouplinks-chelsea", "https://grouplinks.co.uk/chelsea-whatsapp-group-links/"),
    ("grouplinks-liverpool", "https://grouplinks.co.uk/liverpool-whatsapp-group-links/"),
    ("grouplinks-manutd", "https://grouplinks.co.uk/manchester-united-whatsapp-group-links/"),
    ("grouplinks-premier-league", "https://grouplinks.co.uk/premier-league-whatsapp-group-links/"),
    ("grouplinks-glasgow", "https://grouplinks.co.uk/glasgow-whatsapp-group-links/"),
    ("grouplinks-london", "https://grouplinks.co.uk/london-whatsapp-group-links/"),
    ("grouplinks-manchester", "https://grouplinks.co.uk/manchester-whatsapp-group-links/"),
    ("grouplinks-students", "https://grouplinks.co.uk/students-whatsapp-group-links/"),
    ("grouplinks-uk-education", "https://grouplinks.co.uk/uk-education-whatsapp-groups/"),
    ("grouplinks-uk-student-community", "https://grouplinks.co.uk/uk-student-community-whatsapp-group-links/"),
    ("grouplinks-freelancing", "https://grouplinks.co.uk/freelancing-whatsapp-group-links/"),
    ("grouplinks-gaming", "https://grouplinks.co.uk/gaming-whatsapp-group-links/"),
    ("grouplinks-movies", "https://grouplinks.co.uk/movies-whatsapp-group-links/"),
    ("grouplinks-online-earning", "https://grouplinks.co.uk/online-earning-whatsapp-group-links/"),
    ("grouplinks-islamic", "https://grouplinks.co.uk/islamic-whatsapp-group-links/"),
    ("grouplinks-indian-uk", "https://grouplinks.co.uk/indian-whatsapp-group-links-uk/"),
    ("grouplinks-pakistani-uk", "https://grouplinks.co.uk/pakistani-whatsapp-group-links-uk/"),
    ("grouplinks-uk", "https://grouplinks.co.uk/uk-whatsapp-group-links/"),
    ("grouplinks-all", "https://grouplinks.co.uk/all-whatsapp-groups/"),
    ("whatsappgroupslinkss-business", "https://whatsappgroupslinkss.com/business-whatsapp-group-links/"),
    ("activesociallinks", "https://activesocilalinks.com/"),
    ("whtsagroupslinks-home", "https://www.whtsagroupslinks.com/"),
    ("wagroupnest", "https://wagroupnest.com/"),
    ("grouplink-pakistani", "https://grouplink.com.in/explore-the-active-pakistani-whatsapp-group-links-right-here/"),
    ("grouplink-india-study", "https://grouplink.com.in/all-india-study-whatsapp-group-links/"),
    ("grouplink-malayalam-islamic", "http://grouplink.com.in/malayalam-islamic-whatsapp-group-links/"),
    ("grouplink-central-govt", "http://grouplink.com.in/join-now-central-government-whatsapp-group-links/"),
    ("whtsagrouplinks-pakistani", "https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/"),
    ("whtsgrouplink-home", "https://whtsgrouplink.com"),
    ("bestdelhi-du", "https://www.bestdelhi.in/delhi-university-whatsapp-group-link/"),
    ("whtspgrouplink-ghana-shs", "https://whtspgrouplink.com/ghana-shs-whatsapp-group-links/"),
    ("wemakescholars-ms-us", "https://www.wemakescholars.com/blog/whatsapp-group-for-ms-in-us-fall"),
    ("grouplinksforyou-dubai", "https://www.grouplinksforyou.com/2023/04/dubai-whatsapp-group-links.html"),
    ("whatgroups-islamic", "https://whatgroups.com/islamic-whatsapp-group-link/"),
]

def main():
    s = requests.Session()
    all_items = {}  # code -> {name, sources:[...]}
    report = []
    for label, url in SOURCES:
        try:
            r = s.get(url, headers=UA, timeout=60)
            if r.status_code != 200:
                report.append({"url": url, "label": label, "codes_found": 0, "note": "HTTP %d" % r.status_code})
                print(label, "HTTP", r.status_code)
                continue
            if 'One moment, please' in r.text or 'cf-challenge' in r.text or 'challenges.cloudflare.com' in r.text:
                report.append({"url": url, "label": label, "codes_found": 0, "note": "Cloudflare JS challenge; banked as lead"})
                print(label, "CLOUDFLARE")
                continue
            found = extract(r.text, url)
            for code, name in found.items():
                if code not in all_items:
                    all_items[code] = {"code": code, "name": name, "sources": [label]}
                else:
                    if not all_items[code]["name"] and name:
                        all_items[code]["name"] = name
                    if label not in all_items[code]["sources"]:
                        all_items[code]["sources"].append(label)
            report.append({"url": url, "label": label, "codes_found": len(found), "note": ""})
            print(label, len(found), "codes")
        except Exception as e:
            report.append({"url": url, "label": label, "codes_found": 0, "note": "fetch error: %s: %s" % (type(e).__name__, str(e)[:100])})
            print(label, "ERROR", e)
        time.sleep(1)
    json.dump({"items": list(all_items.values()), "sources": report}, open("team28-mined.json", "w"), ensure_ascii=False, indent=1)
    print("TOTAL unique codes mined:", len(all_items))
    print("sources with 0 codes:", [x["label"] for x in report if x["codes_found"] == 0])

if __name__ == "__main__":
    main()
