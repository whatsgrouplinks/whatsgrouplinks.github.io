#!/usr/bin/env python3
"""Team 23: fetch listicle pages, extract (name, code) pairs."""
import re, sys, json, time, html
import requests

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

# Manual full-length codes found in search-result descriptions (listicle-adjacent)
MANUAL = [
    ("Sarita Desai Yoga Wellness Community", "GGse7SbF05IFh0R3FRgXTS", "manual-yoga-shorts"),
    ("Heal Your Anxiety Support Circle", "HuhGLLS7MqhET6V4ZhmsgS", "manual-meetup-anxiety"),
    ("Group WA Berbagi Ayat Quran", "CAPbqrZsJfCIWonembhZ54", "manual-quran-share"),
    ("Free Quranic Class", "ELUk73AuX4eGp3KMMVm2z0", "manual-quran-class"),
    ("Rotary Book Club Mumbai SOBO", "DWcZw00QrJjCW4JZNmfpri", "manual-rotary-book"),
    ("Rotary Wine Appreciation Club", "HCTQ2cUgMcd6Lr5fR6gK9c", "manual-rotary-wine"),
    ("Rotary Trekking Club", "HdpxwxCUoZi9KqeMaWv2Xh", "manual-rotary-trek"),
    ("Rotary Golf Club", "Cpf4py9iwFoGzxn1R3f6W6", "manual-rotary-golf"),
    ("Rotary Holistic Health Hub", "JDfElnueTavFNbmBOXMXJR", "manual-rotary-health"),
    ("Online Yoga Business Accelerator Group", "ITqRDqHGevG3gcVV3YVLr3", "manual-yoga-biz"),
    ("Yoga Instructors Community Group", "GlPJQSrCqzY2jRC88FLg7U", "manual-yoga-instructors"),
]

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})")

def clean_text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract(page_html):
    """Return list of (name, code). For each invite link, take text of enclosing <li>/<tr>/<p>."""
    out = []
    # split into blocks by <li, <tr, <p
    blocks = re.split(r"(?=<li[\s>]|<tr[\s>]|<p[\s>])", page_html, flags=re.I)
    for b in blocks:
        m = CODE_RE.search(b)
        if not m:
            continue
        code = m.group(1)
        # name = text before the link within block
        before = b[:m.start()]
        name = clean_text(before)
        # strip trailing junk like "Join", "Click Here", separators
        name = re.sub(r"(Join|Click Here|Join Now|Join Group)\s*$", "", name, flags=re.I).strip(" -–—•|:")
        # if name too long, take last 60 chars
        if len(name) > 80:
            name = name[-80:].strip()
        out.append((name, code))
    return out

all_rows = []
for label, url in PAGES:
    try:
        r = requests.get(url, headers=UA, timeout=60)
        print(f"{label}: HTTP {r.status_code} len={len(r.text)}", flush=True)
        if r.status_code != 200:
            continue
        rows = extract(r.text)
        print(f"  -> {len(rows)} invite anchors", flush=True)
        for name, code in rows:
            all_rows.append({"page": label, "name": name, "code": code})
        time.sleep(1)
    except Exception as e:
        print(f"{label}: ERROR {e}", flush=True)

with open("/tmp/team23_raw.json", "w") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=1)
for name, code, page in MANUAL:
    all_rows.append({"page": page, "name": name, "code": code})
with open("/tmp/team23_raw.json", "w") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=1)
print("TOTAL rows:", len(all_rows))
# unique codes
codes = {}
for r in all_rows:
    codes.setdefault(r["code"], r)
print("UNIQUE codes:", len(codes))
