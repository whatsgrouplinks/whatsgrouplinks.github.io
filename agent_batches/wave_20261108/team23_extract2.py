#!/usr/bin/env python3
"""Team 23: bs4-based extraction of (name, code, format, section) from listicle pages."""
import re, json, time, html
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

PAGES = [
    ("whatstele-pakistani", "https://whatstele.com/whatsapp/group-links/pakistani/"),
    ("wahublink-usa", "https://wahublink.com/usa-whatsapp-group-links/"),
    ("77links-islamic", "https://77links.com/islamic-whatsapp-group-links/"),
    ("whatsgroup-in", "https://www.whatsgroup.in/"),
    ("joinwagroupnow-kerala", "https://joinwagroupnow.com/kerala-whatsapp-group-links/"),
    ("eduwealthhub-usa-girls", "https://talk.eduwealthhub.com/usa-girls-whatsapp-mobile-numbers-list-2026/"),
    ("dostizone-girls", "https://dostizone.vercel.app/Girl-Whatsapp-group-links.html"),
    ("grouplink-malayalam-islamic", "http://grouplink.com.in/malayalam-islamic-whatsapp-group-links/"),
    ("77links-quran", "https://77links.com/quran-whatsapp-group-links/"),
    ("whatstele-yoga", "https://whatstele.com/whatsapp/group-links/yoga/"),
    ("grouplink-international", "https://grouplink.com.in/1300-international-whatsapp-group-link/"),
    ("wahublink-home", "https://wahublink.com/"),
]

JOIN_WORDS = re.compile(r"\b(join|join now|join group|click here|click|link|➛|►|✔|✅)\b", re.I)
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})\b")

def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def name_for(a):
    """Walk up ancestors; take the closest ancestor text that yields a plausible name."""
    link_text = clean(a.get_text(" ", strip=True))
    node = a
    for _ in range(5):
        node = node.parent
        if node is None or node.name in ("body", "html", "[document]"):
            break
        txt = clean(node.get_text(" ", strip=True))
        # remove the link's own text
        if link_text:
            txt = txt.replace(link_text, " ")
        txt = JOIN_WORDS.sub(" ", txt)
        txt = re.sub(r"\s+", " ", txt).strip(" -–—•|:·»«›‹")
        # strip trailing/leading junk chars
        if 2 <= len(txt) <= 90 and not txt.lower().startswith(("vid-", "has-background", "wp-element")):
            return txt
        if len(txt) > 90:
            # maybe name is at the start before other content; take first chunk
            head = txt[:90]
            if len(head) >= 2:
                return head.strip(" -–—•|:")
    return ""

def section_for(a):
    """Nearest preceding heading text."""
    h = a.find_previous(["h1", "h2", "h3", "h4"])
    return clean(h.get_text(" ", strip=True)) if h else ""

all_rows = []
for label, url in PAGES:
    try:
        r = requests.get(url, headers=UA, timeout=60)
        print(f"{label}: HTTP {r.status_code} len={len(r.text)}", flush=True)
        if r.status_code != 200:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        n_direct = n_invite = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            m = CODE_RE.search(href)
            if not m:
                continue
            code = m.group(1)
            fmt = "invite" if "/invite/" in href else "direct"
            if fmt == "direct":
                n_direct += 1
            else:
                n_invite += 1
            name = name_for(a)
            sec = section_for(a)
            all_rows.append({"page": label, "name": name, "code": code,
                             "format": fmt, "section": sec[:80]})
        print(f"  -> direct={n_direct} invite={n_invite}", flush=True)
        time.sleep(1)
    except Exception as e:
        print(f"{label}: ERROR {e}", flush=True)

MANUAL = [
    ("Sarita Desai Yoga Wellness Community", "GGse7SbF05IFh0R3FRgXTS", "manual-yoga-shorts", "Health"),
    ("Heal Your Anxiety Support Circle", "HuhGLLS7MqhET6V4ZhmsgS", "manual-meetup-anxiety", "Health"),
    ("Group WA Berbagi Ayat Quran", "CAPbqrZsJfCIWonembhZ54", "manual-quran-share", "Islamic"),
    ("Free Quranic Class", "ELUk73AuX4eGp3KMMVm2z0", "manual-quran-class", "Islamic"),
    ("Rotary Book Club Mumbai SOBO", "DWcZw00QrJjCW4JZNmfpri", "manual-rotary-book", "Community & Social"),
    ("Rotary Wine Appreciation Club", "HCTQ2cUgMcd6Lr5fR6gK9c", "manual-rotary-wine", "Community & Social"),
    ("Rotary Trekking Club", "HdpxwxCUoZi9KqeMaWv2Xh", "manual-rotary-trek", "Travel"),
    ("Rotary Golf Club", "Cpf4py9iwFoGzxn1R3f6W6", "manual-rotary-golf", "Sports"),
    ("Rotary Holistic Health Hub", "JDfElnueTavFNbmBOXMXJR", "manual-rotary-health", "Health"),
    ("Online Yoga Business Accelerator Group", "ITqRDqHGevG3gcVV3YVLr3", "manual-yoga-biz", "Health"),
    ("Yoga Instructors Community Group", "GlPJQSrCqzY2jRC88FLg7U", "manual-yoga-instructors", "Health"),
]
for name, code, page, sec in MANUAL:
    all_rows.append({"page": page, "name": name, "code": code, "format": "direct", "section": sec})

with open("/tmp/team23_raw2.json", "w") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=1)
uniq = {}
for r in all_rows:
    uniq.setdefault((r["code"], r["format"]), r)
print("TOTAL rows:", len(all_rows), "UNIQUE (code,format):", len(uniq))
print("empty names:", sum(1 for r in all_rows if not r["name"].strip()))
