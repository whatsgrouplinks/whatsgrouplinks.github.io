#!/usr/bin/env python3
"""Team36 phase 2: more listicles -> append verified to team36-new-listicles.json"""
import json, re, html as h, time, sys
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261102")
import team36_pipeline as P

WAVE = P.WAVE
T36 = "/tmp/t36b/"

def strip_tags(s):
    return h.unescape(re.sub(r"<[^>]+>", " ", s)).strip()

def headings(html):
    hs = []
    for m in re.finditer(r"<h[123][^>]*>(.*?)</h[123]>", html, re.S | re.I):
        t = strip_tags(m.group(1))
        if t: hs.append((m.start(), t))
    return hs

def heading_for(hs, pos):
    cur = ""
    for p, t in hs:
        if p < pos: cur = t
        else: break
    return cur

PLAIN = r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"  # plain group links only, NO invite/

def parse_generic(path, cat_fn, ctry_fn, patterns, exclude_invite=True):
    html = open(path, encoding="utf-8", errors="ignore").read()
    hs = headings(html)
    out, seen = [], set()
    for pat in patterns:
        for m in re.finditer(pat, html, re.S | re.I):
            name, code = m.group(1), m.group(2)
            name = h.unescape(name).strip()
            hd = heading_for(hs, m.start())
            if code in seen: continue
            seen.add(code)
            nl = name.strip().lower()
            if nl in ("group name", "groups name", "current group name"): continue
            out.append((name, code, cat_fn(hd, name), ctry_fn(hd, name), hd))
    return out

def name_ctry(hd, name):
    t = (name or "").lower()
    if "pakistan" in t or "\U0001f1f5\U0001f1f0" in t or "lahore" in t or "karachi" in t or "punjab" in t or "sindh" in t or "baloch" in t or "peshawar" in t: return "PK"
    if "india" in t or "indian" in t or "kerala" in t or "tamil" in t or "malayalam" in t or "mumbai" in t or "delhi" in t: return "IN"
    if "bangladesh" in t or "bengali" in t: return "BD"
    if "sri lank" in t: return "LK"
    if "nigeria" in t: return "NG"
    if "usa" in t or "america" in t: return "US"
    if "uk" in t or "britain" in t: return "GB"
    return "International"

CATMAP = [
    ("islamic", "Islamic"), ("dawatelslami", "Islamic"), ("dawateislami", "Islamic"),
    ("quran", "Islamic"), ("naat", "Islamic"),
    ("cricket", "Sports"), ("ipl", "Sports"), ("football", "Sports"), ("soccer", "Sports"),
    ("sport", "Sports"), ("psl", "Sports"),
    ("job", "Jobs"), ("earn money", "Finance"), ("make money", "Finance"),
    ("pubg", "Gaming"), ("bgmi", "Gaming"), ("free fire", "Gaming"), ("gaming", "Gaming"),
    ("ludo", "Gaming"), ("efootball", "Sports"), ("pes", "Sports"),
    ("study", "Education"), ("education", "Education"), ("english learning", "Education"),
    ("course", "Education"), ("class", "Education"), ("exam", "Education"),
    ("news", "News"),
    ("girls", "Girls"), ("boys", "Friendship"), ("friendship", "Friendship"),
    ("romantic", "Friendship"), ("dating", "Friendship"),
    ("funny", "Funny"), ("meme", "Funny"),
    ("movie", "Movies"), ("bollywood", "Movies"), ("film", "Movies"), ("netflix", "Movies"),
    ("music", "Music"), ("tiktok", "Entertainment"), ("youtube", "Entertainment"),
    ("entertainment", "Entertainment"), ("anime", "Entertainment"), ("cartoon", "Entertainment"),
    ("status", "Entertainment"), ("shayari", "Other"), ("poetry", "Other"),
    ("buy and sell", "Buy-Sell"), ("shopping", "Buy-Sell"), ("offer", "Buy-Sell"),
    ("business", "Business"), ("digital marketing", "Business"), ("marketing", "Business"),
    ("crypto", "Crypto"), ("forex", "Crypto"), ("trading", "Finance"),
    ("technology", "Technology"), ("tech", "Technology"),
    ("health", "Health"), ("cooking", "Food"), ("food", "Food"),
    ("fashion", "Other"), ("sub4sub", "Other"), ("travel", "Travel"),
]
CTRYMAP = [("usa", "US"), ("america", "US"), ("indian", "IN"), ("india", "IN"),
           ("tamil", "IN"), ("malayalam", "IN"), ("kerala", "IN"), ("goa", "IN"),
           ("pakistani", "PK"), ("pakistan", "PK"), ("baloch", "PK"),
           ("uk", "GB"), ("canada", "CA"), ("arab", "International"),
           ("international", "International")]

def mega_map(hd):
    hdl = (hd or "").lower()
    cat, ctry = "Other", "International"
    for kw, c in CATMAP:
        if kw in hdl: cat = c; break
    for kw, c in CTRYMAP:
        if kw in hdl: ctry = c; break
    return cat, ctry

def main():
    union = set(json.load(open(WAVE + "/dedupe_union.json")))
    # also exclude phase-1 verified + pending codes
    for fn in ("team36-new-listicles.json", "team36-unverified-pending.json"):
        try:
            for it in json.load(open(WAVE + "/" + fn)):
                inv = it.get("invite", "")
                m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})", inv)
                if m: union.add(m.group(1))
        except FileNotFoundError:
            pass
    seen = set()
    cands = []

    # 1. groupda islamic listicle
    rows = parse_generic(
        T36 + "groupdacom_spiritual_best-islamic-whatsapp-group-link-2022.html",
        lambda hd, nm: "Islamic",
        lambda hd, nm: name_ctry(hd, nm),
        [r"<li>([^<]{1,160}?)\s*(?:&#8212;|&#8211;|—|–|-)\s*-?\s*<a\s+href=\"https?://" + PLAIN + r"\""])
    # 2. wagrouplinks messi
    rows += parse_generic(
        T36 + "wagrouplinksnet_lionel-messi-fans-whatsapp-group-links.html",
        lambda hd, nm: "Sports",
        lambda hd, nm: name_ctry(hd, nm),
        [r"<td[^>]*>([^<]{1,140})</td>\s*<td[^>]*>\s*(?:<strong>)?<a\s+href=\"https?://" + PLAIN + r"\""])
    # 3. wahublink sports
    rows += parse_generic(
        T36 + "wahublinkcom_sports-whatsapp-group-links.html",
        lambda hd, nm: "Sports",
        lambda hd, nm: name_ctry(hd, nm),
        [r"<tr><td>([^<]{1,140})</td><td><a\s+href=\"https?://" + PLAIN + r"\""])
    # 4. whtspgrouplink argentina (plain codes only)
    rows += parse_generic(
        T36 + "whtspgrouplinkcom_argentina-fans-kerala-whatsapp-group-links.html",
        lambda hd, nm: "Sports",
        lambda hd, nm: "IN",
        [r"<li>([^<]{1,160}?)\s*(?:&#8211;|&#8212;|–|—)\s*(?:&nbsp;)?\s*<a\s+href=\"https?://" + PLAIN + r"\""])
    # 5. whatsgroupslinkspk mega page
    rows += parse_generic(
        T36 + "whatsgroupslinkspkcom.html",
        lambda hd, nm: mega_map(hd)[0],
        lambda hd, nm: mega_map(hd)[1] if mega_map(hd)[1] != "International" else name_ctry(hd, nm),
        [r"<li[^>]*>\s*<span[^>]*>([^<]{1,160}?)\s*[–—-]\s*<a\s+href=\"https?://" + PLAIN + r"\""])

    for name, code, cat, ctry, hd in rows:
        if code in union or code in seen: continue
        seen.add(code)
        cands.append({"src_name": name, "code": code, "cat": cat, "country": ctry, "hint": hd[:120]})
    print(f"phase2 candidates after dedupe: {len(cands)}", flush=True)

    verified = json.load(open(WAVE + "/team36-new-listicles.json"))
    pending = json.load(open(WAVE + "/team36-unverified-pending.json"))
    porn_drops = 0
    rate_limited = False
    i = -1
    for i, c in enumerate(cands):
        try:
            http_code, title = P.verify(c["code"])
        except RuntimeError:
            pending.append({"name": c["src_name"], "category": c["cat"], "country": c["country"],
                            "description": "", "invite": "https://chat.whatsapp.com/" + c["code"],
                            "image": "", "note": "transport failure"})
            time.sleep(0.7); continue
        if http_code == "429":
            rate_limited = True
            print("HTTP 429 at index %d — stopping" % i, flush=True)
            break
        time.sleep(0.7)
        if not title: continue
        name = c["src_name"]
        if not name or name.strip().lower() in ("link", "join", "click here", "view invite", "join now", "join link", "join group"):
            name = title
        if P.porn_hit(name) or P.porn_hit(title):
            porn_drops += 1; continue
        name = name.strip()
        if not name or name.startswith("http"): name = title.strip()
        if not name: continue
        desc = P.make_desc(name, c["cat"], c["country"])
        verified.append({"name": name, "category": c["cat"], "country": c["country"],
                         "description": desc,
                         "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""})
        if len(verified) % 10 == 0:
            print(f"[{i+1}/{len(cands)}] verified total={len(verified)} latest={name[:45]}", flush=True)

    if rate_limited:
        for c in cands[i:]:
            pending.append({"name": c["src_name"], "category": c["cat"], "country": c["country"],
                            "description": "", "invite": "https://chat.whatsapp.com/" + c["code"],
                            "image": "", "note": "rate-limited"})

    # final in-batch dedupe by invite
    seen_inv, final = set(), []
    for it in verified:
        if it["invite"] not in seen_inv:
            seen_inv.add(it["invite"]); final.append(it)
    json.dump(final, open(WAVE + "/team36-new-listicles.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + "/team36-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print(f"PHASE2 DONE: verified={len(final)} pending={len(pending)} porn_drops={porn_drops} rate_limited={rate_limited}", flush=True)

if __name__ == "__main__":
    main()
