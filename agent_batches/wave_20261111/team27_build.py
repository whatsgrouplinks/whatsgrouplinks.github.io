#!/usr/bin/env python3
"""Team27 wave 20261111: build verified/pending/exclusions from verification TSVs.
Names come from og:title first (html-unescaped), listing name as fallback.
Screens BOTH banked name and og:title for porn/scam markers."""
import json, re, os, sys, html, unicodedata

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
pool1 = json.load(open(os.path.join(WAVE, "team27_pool.json")))
pool2 = json.load(open(os.path.join(WAVE, "team27_pool2.json")))
pool = dict(pool1); pool.update(pool2)
if os.path.exists(os.path.join(WAVE, "team27_pool3.json")):
    pool.update(json.load(open(os.path.join(WAVE, "team27_pool3.json"))))
fkph = json.load(open(os.path.join(WAVE, "team27_fkph_names.json")))

# definitive results: v1 live/dead + v2 (v2 overrides v1 for re-checked codes)
res = {}
for fn in ("team27_verify.tsv", "team27_verify2.tsv"):
    p = os.path.join(WAVE, fn)
    if not os.path.exists(p):
        continue
    for line in open(p, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 4:
            res[f[0]] = (f[1], f[2], f[3])

ADULT_EMOJI = set("🍆🍑💦👅👄💋🔞🥵")
NEG_PAT = re.compile(r"[^.!?\n]{0,80}?(no|not|don't|dont|do not|never|dilarang|jangan|tidak|na\s*karein|na\s*karo|mana\s*hai|prohibit\w*|forbidden)[^.!?\n]{0,80}?", re.I)

def strip_negated(text):
    return NEG_PAT.sub(" ", text)

def has_adult_emoji(text):
    return any(e in strip_negated(text) for e in ADULT_EMOJI)

PORN_WORDS = [r"\bbokep\b", r"\bporn\b", r"\bxxx\b", r"xnxx", r"xvideos",
              r"pornhub", r"\bphone\s*sex\b",
              r"\bsex\s*(video|call|chat|group|18|free)\b", r"\b18\+\s*(video|sex|only|grup|group)\b",
              r"\bdesi\s*(leak|mms)\b", r"\bgirl[s]?\s*leak\b", r"\bviral\s*leak\b",
              r"\bonlyfans\b", r"\bsex\b.{0,10}\b18\b"]
SCAM_WORDS = [r"b-?love", r"forsage", r"shey[iy]", r"holiverse", r"meta-?whale",
              r"\bbinary\s*options?\b", r"\bolymp\s*trade\b", r"\bquotex\b",
              r"\byoutag\b", r"\busdt\s*flash\b", r"\bbtc\s*flash\b", r"\bcarding\b",
              r"\b1xbet\b", r"\bfixed\s*match\b", r"\bteen\s*patti\b.*\b(winning|trick)\b",
              r"\bairdrop\b.{0,30}\b(legit|free money|claim|earn)\b"]

def norm_name(s):
    s = html.unescape(s or "")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    # strip trailing member counts / junk from table extraction
    s = re.sub(r"\s+\d{1,4}$", "", s)
    return s

def clean_listing_name(s):
    s = norm_name(s)
    # drop any whatsapp URL fragments (e.g. truncated "hat.whatsapp.com/CODE" from a neighbouring link)
    s = re.sub(r"[\w.]*whatsapp\.com/\S*", " ", s, flags=re.I)
    s = re.sub(r"https?://\S*", "", s).strip(" |:;-")
    # drop leading table junk / comment artefacts
    s = re.sub(r"^(Hapus|Balasan|Balas|Anonim|[^A-Za-z0-9]{0,3}\s*)+", "", s)
    s = re.sub(r"\s+\d{1,4}$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def screen(name, title):
    """return exclusion reason or None"""
    for txt, label in ((title, "og:title"), (name, "name")):
        t = txt or ""
        if has_adult_emoji(t):
            return f"adult emoji in {label}"
        low = t.lower()
        for pat in PORN_WORDS:
            if re.search(pat, low):
                # 'sex' inside 'bisexual' is not porn (w09 precedent)
                if pat == r"\bsex\b.{0,10}\b18\b" and "bisexual" in low:
                    continue
                return f"porn/xxx keyword ({pat}) in {label}"
        for pat in SCAM_WORDS:
            if re.search(pat, low):
                return f"scam keyword ({pat}) in {label}"
    return None

CAT_KEYS = [
    (r"free\s*fire|pubg|mobile\s*legend|mabar|ff\b|gaming|game", "Gaming"),
    (r"youtuber|youtube|creator|monet", "Entertainment"),
    (r"cari\s*pacar|cari\s*jodoh|jomblo|jodoh|gebeth?an|teman|pacar|friend", "Friendship"),
    (r"job|lowongan|kerja|vacancy|hiring|career", "Jobs"),
    (r"quran|islam|muslim|kajian|tahfidz|sholat", "Islamic"),
    (r"crypto|bitcoin|btc|trading|forex|stock|invest", "Finance"),
    (r"kelompok|choir|handicraft|course|kelas|kuliah|student|mahasiswa|university|universiti|postgraduate|phd|master", "Education"),
    (r"news|berita|update\s*news", "News"),
    (r"health|sehat|doctor|nursing", "Health"),
    (r"cook|recipe|masak|baking", "Cooking"),
    (r"travel|backpack|nomad|tour", "Travel"),
    (r"scholarship|beasiswa", "Scholarship"),
    (r"movie|film|cinema|series|drama", "Entertainment"),
    (r"poetry|shayari|kavita", "Poetry"),
    (r"funny|meme|joke|humor|lawak", "Funny"),
    (r"buy|sell|jual|beli|market|shop|olshop", "Buy Sell"),
    (r"business|bisnis|reseller|entrepreneur", "Business"),
    (r"sport|cricket|football|badminton", "Sports"),
]

def categorize(name, src_cat):
    low = (name or "").lower()
    for pat, cat in CAT_KEYS:
        if re.search(pat, low):
            return cat
    return src_cat

def describe(name, cat, country):
    c = {"ID": "Indonesia", "MY": "Malaysia", "PH": "Philippines",
         "SG": "Singapore", "TH": "Thailand", "VN": "Vietnam"}.get(country, "")
    where = f" in {c}" if c else ""
    art = "an" if cat[0].lower() in "aeiou" else "a"
    return f"{name} — {art} {cat.lower()} WhatsApp group{where} for members to connect, chat and share updates."

verified, pending, exclusions = [], [], []
dead = 0
for code, item in sorted(pool.items()):
    http, title, note = res.get(code, ("?", "", "not-checked"))
    src_cat = item.get("category", "Community & Social")
    country = item.get("country", "")
    listing = clean_listing_name(item.get("name", ""))
    title_n = norm_name(title)
    if http == "0" or http == "?":
        # transport failure / not checked -> pending (keep listing name; no og:title yet)
        nm = listing or fkph.get(code, "")
        pending.append({"name": nm, "category": src_cat, "country": country,
                        "description": describe(nm, src_cat, country) if nm else "",
                        "invite": "https://chat.whatsapp.com/" + code,
                        "reason": "transport failure on verify (curl timeout/connection)" if http == "0" else "not checked (verifier incomplete)"})
        continue
    if http != "200" or not title_n:
        dead += 1
        continue
    # live: name = og:title; fallback listing/fkph name if generic
    name = title_n
    if name.lower() in ("whatsapp group", "whatsapp", "join whatsapp group", "group"):
        name = fkph.get(code, "") or listing
    if not name:
        exclusions.append({"code": code, "reason": "live but no usable name (generic og:title and empty listing name)"})
        continue
    reason = screen(name, title_n)
    if reason:
        exclusions.append({"code": code, "reason": reason})
        continue
    cat = categorize(name, src_cat)
    # country inference from name
    if not country:
        if re.search(r"\bsingapore\b|\bSG\b|🇸🇬", name):
            country = "SG"
        elif re.search(r"indonesia|🇮🇩", name, re.I):
            country = "ID"
        elif re.search(r"malaysia|🇲🇾", name, re.I):
            country = "MY"
        elif re.search(r"philippines|filipino|🇵🇭", name, re.I):
            country = "PH"
    desc = item.get("description", "") if item.get("source", "").startswith("gw_") else ""
    if desc:
        desc = html.unescape(desc).strip()
        if len(desc) > 200:
            desc = desc[:197] + "..."
    if not desc:
        desc = describe(name, cat, country)
    # fkph groups: cleaner description
    if code in fkph:
        desc = f"Student group for the FKPH Law Fair 2025 ({fkph[code]}) at Universitas Brawijaya, Indonesia."
        cat, country = "Education", "ID"
        name = title_n if title_n.lower() not in ("whatsapp group",) else fkph[code]
    verified.append({"name": name, "category": cat, "country": country,
                     "description": desc,
                     "invite": "https://chat.whatsapp.com/" + code})

verified.sort(key=lambda x: x["invite"])
pending.sort(key=lambda x: x["invite"])
json.dump(verified, open(os.path.join(WAVE, "team27-newdirs-seasia.json"), "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(WAVE, "team27-newdirs-seasia-pending.json"), "w"), ensure_ascii=False, indent=1)
json.dump(exclusions, open(os.path.join(WAVE, "team27_exclusions.json"), "w"), ensure_ascii=False, indent=1)
print(f"verified={len(verified)} pending={len(pending)} excluded={len(exclusions)} dead={dead} total-pool={len(pool)}")
print("categories:", {c: sum(1 for v in verified if v["category"] == c) for c in sorted(set(v['category'] for v in verified))})
print("countries:", {c: sum(1 for v in verified if v["country"] == c) for c in sorted(set(v['country'] for v in verified))})
