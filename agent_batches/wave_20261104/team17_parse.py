"""team17: groupor.link category-page SSR card parser."""
import re, html

ARTICLE_RE = re.compile(r'<article class="rounded-sm border.*?</article>', re.S)
HREF_CODE_RE = re.compile(r'/group/invite/whatsapp/([A-Za-z0-9]{20,24})')
H3_RE = re.compile(r'<h3>(.*?)</h3>', re.S)
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
INVITE_RE = re.compile(r'chat\.whatsapp\.com/invite/([A-Za-z0-9]{20,24})')
DESC_RE = re.compile(r'<p class="mt-3 line-clamp-2[^"]*"[^>]*>(.*?)</p>', re.S)
BADGE_RE = re.compile(r'</svg>([^<]+)</span>')

COUNTRY_MAP = {
    "United States": "US", "USA": "US", "India": "IN", "Pakistan": "PK",
    "United Kingdom": "GB", "UK": "GB", "Nigeria": "NG", "Indonesia": "ID",
    "Egypt": "EG", "Brazil": "BR", "Bangladesh": "BD", "Philippines": "PH",
    "Vietnam": "VN", "Thailand": "TH", "Malaysia": "MY", "Singapore": "SG",
    "South Africa": "ZA", "Kenya": "KE", "Ghana": "GH", "Uganda": "UG",
    "Saudi Arabia": "SA", "UAE": "AE", "United Arab Emirates": "AE",
    "Canada": "CA", "Australia": "AU", "Germany": "DE", "France": "FR",
    "Italy": "IT", "Spain": "ES", "Netherlands": "NL", "Turkey": "TR",
    "Qatar": "QA", "Kuwait": "KW", "Oman": "OM", "Bahrain": "BH",
    "Sri Lanka": "LK", "Nepal": "NP", "Myanmar": "MM", "Ethiopia": "ET",
    "Tanzania": "TZ", "Mexico": "MX", "Argentina": "AR", "Colombia": "CO",
    "Peru": "PE", "Chile": "CL", "Portugal": "PT", "Greece": "GR",
    "Poland": "PL", "Romania": "RO", "Ukraine": "UA", "Russia": "RU",
    "China": "CN", "Japan": "JP", "South Korea": "KR", "Taiwan": "TW",
    "Hong Kong": "HK", "New Zealand": "NZ", "Ireland": "IE", "Sweden": "SE",
    "Norway": "NO", "Denmark": "DK", "Finland": "FI", "Belgium": "BE",
    "Switzerland": "CH", "Austria": "AT", "Morocco": "MA", "Algeria": "DZ",
    "Tunisia": "TN", "Jordan": "JO", "Lebanon": "LB", "Iraq": "IQ",
    "Iran": "IR", "Afghanistan": "AF", "Uzbekistan": "UZ", "Kazakhstan": "KZ",
    "Zimbabwe": "ZW", "Zambia": "ZM", "Cameroon": "CM", "Senegal": "SN",
    "Ivory Coast": "CI", "Mali": "ML", "DR Congo": "CD", "Rwanda": "RW",
    "Malawi": "MW", "Botswana": "BW", "Namibia": "NA", "Mauritius": "MU",
    "Maldives": "MV", "Fiji": "FJ", "Papua New Guinea": "PG", "Israel": "IL",
    "Palestine": "PS", "Yemen": "YE", "Syria": "SY", "Sudan": "SD",
    "Somalia": "SO", "Libya": "LY", "Mauritania": "MR", "Niger": "NE",
    "Burkina Faso": "BF", "Chad": "TD", "Gabon": "GA", "Congo": "CG",
    "Angola": "AO", "Mozambique": "MZ", "Madagascar": "MG", "Seychelles": "SC", "Togo": "TG",
    "SriLanka": "LK",
}

def country_to_iso(name):
    n = html.unescape(name).strip()
    if n in COUNTRY_MAP:
        return COUNTRY_MAP[n]
    # try title-case match
    return COUNTRY_MAP.get(n.title(), None)

def parse_category(html_text):
    """Return list of dicts: name, country_iso, category_badge, description, code, image_url."""
    out = []
    for m in ARTICLE_RE.finditer(html_text):
        art = m.group(0)
        h3 = H3_RE.search(art)
        href = HREF_CODE_RE.search(art)
        if not h3 or not href:
            continue
        name = html.unescape(h3.group(1)).strip()
        code = href.group(1)
        badges = [html.unescape(b).strip() for b in BADGE_RE.findall(art)]
        # badges: [category, country, language] typically
        cat_badge = badges[0] if badges else ""
        country_badge = badges[1] if len(badges) > 1 else ""
        d = DESC_RE.search(art)
        desc_html = d.group(1) if d else ""
        desc_text = html.unescape(re.sub(r'<[^>]+>', ' ', desc_html))
        desc_text = re.sub(r'\\n', ' ', desc_text)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
        # strip the invite URL from description
        desc_text = re.sub(r'https?://chat\.whatsapp\.com/\S+', '', desc_text)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
        img_m = re.search(r'src="https://wsrv\.nl/\?url=([^"&]+)', art)
        img = ""
        if img_m:
            raw = html.unescape(img_m.group(1))
            raw = re.sub(r'&amp;', '&', raw)
            from urllib.parse import unquote
            img = unquote(raw)
        out.append({
            "name": name, "country_badge": country_badge,
            "country_iso": country_to_iso(country_badge) or "International",
            "category_badge": cat_badge, "description": desc_text,
            "code": code, "image": img,
        })
        # extra codes embedded in the description text (spam cross-posts) —
        # harvested separately; name falls back to og:title on verify.
        # chat.whatsapp.com/invite/ codes are CHANNELS — excluded.
        invite_codes = set(INVITE_RE.findall(desc_html))
        for cm in CODE_RE.finditer(desc_html):
            xc = cm.group(1)
            if xc != code and xc not in invite_codes:
                out.append({
                    "name": name, "country_badge": country_badge,
                    "country_iso": country_to_iso(country_badge) or "International",
                    "category_badge": cat_badge, "description": desc_text,
                    "code": xc, "image": img, "extra": True,
                })
    return out

if __name__ == "__main__":
    t = open("team17_probe_home.html").read()
    recs = parse_category(t)
    print("parsed", len(recs))
    for r in recs[:5]:
        print(r["code"], "|", r["name"][:60], "|", r["country_iso"], "|", r["category_badge"])
    # country badges not mapped
    unmapped = sorted(set(r["country_badge"] for r in recs if r["country_iso"] == "International"))
    print("unmapped countries:", unmapped[:30])
