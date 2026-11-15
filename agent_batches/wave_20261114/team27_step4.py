#!/usr/bin/env python3
"""team27 step4: verify 27 fresh codes (one session), og:title = real name, screen content."""
import requests, re, json, html, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
S = requests.Session(); S.headers.update(UA)

raw = json.load(open("team27-raw.json"))
fresh = raw["fresh"]

def og_title(code):
    """Returns (title or '', status, error)."""
    last = ""
    for attempt in range(3):
        try:
            r = S.get(f"https://chat.whatsapp.com/{code}", timeout=75)
            if r.status_code == 429:
                return "", 429, "HTTP 429"
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            t = html.unescape(m.group(1)).strip() if m else ""
            if t:
                return t, r.status_code, ""
            last = t
            time.sleep(6)
        except Exception as e:
            return "", 0, f"transport: {type(e).__name__}"
    return last, 200, ""

BAD = re.compile(r"(?i)\b(xxx|porn|sex\s*video|nude|desi\s*aunty|bhabhi\s*sex|hot\s*girl\s*sex|erotic|onlyfans|escort|call\s*girl)\b|airdrop|binary\s*option|free\s*money|double\s*your\s*money|tigrinho|fortune\s*tiger|sinais|plataformas?\s*pagantes|wjbet|casino|slots?\s*bet|betting\s*signal|aviator\s*signal|1xbet|stake\.com")
# negated-prohibition / false-positive guards handled by manual review below

cands, dead, excluded, pending = [], [], [], []
for f in fresh:
    title, status, err = og_title(f["code"])
    time.sleep(2)
    if err:
        pending.append({"code": f["code"], "reason": err, "name": f["name"],
                        "category": f["category"], "source_page": f["source_page"]})
        print(f"PENDING {f['code']} {err}"); continue
    if not title:
        dead.append({"code": f["code"], "reason": "empty og:title after 3 attempts",
                     "name": f["name"], "category": f["category"], "source_page": f["source_page"]})
        print(f"DEAD {f['code']}"); continue
    if title.lower() in ("whatsapp group invite", "whatsapp group", "invite"):
        dead.append({"code": f["code"], "reason": f"generic og:title {title!r}",
                     "name": f["name"], "category": f["category"], "source_page": f["source_page"]})
        print(f"DEAD-generic {f['code']} {title!r}"); continue
    # content screen on live title + listed name
    hay = f"{title} {f['name']}"
    if BAD.search(hay):
        excluded.append({"code": f["code"], "reason": f"content screen: {title!r}",
                         "name": f["name"], "category": f["category"], "source_page": f["source_page"]})
        print(f"EXCLUDED {f['code']} {title!r}"); continue
    name = title
    cat = f["category"].lower()
    desc = f"Join {name}, an active WhatsApp group for {cat}."
    if f["country"]:
        desc += f" Connect with members from {f['country']} and stay updated."
    else:
        desc += " Connect with members and stay updated."
    cands.append({"name": name, "category": f["category"], "country": f["country"],
                  "description": desc, "invite": f"https://chat.whatsapp.com/{f['code']}"})
    print(f"LIVE {f['code']} {title!r}")

json.dump(cands, open("team27-candidates.json", "w"), indent=1, ensure_ascii=False)
json.dump([], open("team27-leads.json", "w"))
json.dump(pending, open("team27-pending.json", "w"), indent=1, ensure_ascii=False)
json.dump({"dead": dead, "excluded": excluded}, open("team27-verify-detail.json", "w"), indent=1, ensure_ascii=False)
print(f"live={len(cands)} dead={len(dead)} excluded={len(excluded)} pending={len(pending)}")
