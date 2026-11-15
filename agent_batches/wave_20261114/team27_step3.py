#!/usr/bin/env python3
"""team27 step3: retry failed pages with fresh session per page + backoff."""
import requests, re, json, html, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

FAILED = [
 ("https://wahublink.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://wahublink.com/online-shopping-whatsapp-group-links/", "Buy Sell", ""),
 ("https://wahublink.com/pakistani-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://wahublink.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://wagroupshub.com/entertainment-whatsapp-group-links/", "Entertainment", ""),
 ("https://wagroupshub.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://wagroupshub.com/online-shopping-whatsapp-group-links/", "Buy Sell", ""),
 ("https://wagroupshub.com/kerala-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://wagroupshub.com/sri-lanka-whatsapp-group-links/", "Community & Social", "LK"),
 ("https://wagroupshub.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://activewagroup.com/entertainment-whatsapp-group-links/", "Entertainment", ""),
 ("https://activewagroup.com/online-earning-whatsapp-group-links/", "Earning", ""),
 ("https://activewagroup.com/poetry-whatsapp-group-links/", "Poetry", ""),
 ("https://activewagroup.com/single-girls-whatsapp-group-links/", "Community & Social", ""),
 ("https://activewagroup.com/usa-whatsapp-group-links/", "Community & Social", "US"),
 ("https://activewagroup.com/tamil-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://activewagroup.com/kerala-whatsapp-group-links/", "Community & Social", "IN"),
 ("https://newgrouplinks.pk/karachi-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://newgrouplinks.pk/pakistani-whatsapp-group-links/", "Community & Social", "PK"),
 ("https://wagroupslink.com/pakistani-whatsapp-group-link/", "Community & Social", "PK"),
]

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
raw = json.load(open("team27-raw.json"))
seen = {f["code"] for f in raw["fresh"]}
tried = raw["tried"]

def clean(s):
    s = re.sub(r"<[^>]*$", " ", s)  # drop trailing partial tag
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"\s+", " ", s).strip(" |-\u2013\u2014")
    # drop leftover attribute junk
    s = re.sub(r'^(.*?(href|class|target|rel)=["\'][^"\']*["\']\s*)*', "", s)
    return s.strip(" |-\u2013\u2014\"'")

def extract(text):
    out = []
    for m in re.finditer(r"<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", text, re.S):
        out.append((clean(m.group(1)), m.group(2)))
    seen_c = {c for _, c in out}
    for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})', text):
        code = m.group(1)
        if code in seen_c: continue
        seg = text[max(0, m.start()-600):m.start()]
        seg = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", seg, flags=re.S)
        txt = clean(seg)
        # take last sentence-ish chunk, drop button/boilerplate words
        name = txt.split("Join")[-1].strip()
        words = [w for w in name.split() if not w.startswith(("kt-", "kb-", "wp-block"))]
        name = " ".join(words[-7:]) if words else ""
        out.append((name, code)); seen_c.add(code)
    return out

for url, cat, country in FAILED:
    pairs, status = [], None
    for attempt in range(3):
        try:
            s = requests.Session(); s.headers.update(UA)
            r = s.get(url, timeout=60)
            status = r.status_code
            if status == 200:
                pairs = extract(r.text)
            s.close()
            break
        except Exception as e:
            status = f"ERR {type(e).__name__}"
            time.sleep(8)
        time.sleep(4)
    fresh = 0
    for name, code in pairs:
        if code not in union and code not in seen:
            raw["fresh"].append({"name": name, "category": cat, "country": country,
                                 "code": code, "source_page": url})
            seen.add(code); fresh += 1
    tried.append({"url": url, "category": cat, "country": country, "status": status,
                  "codes_found": len(pairs), "fresh_vs_union": fresh, "retry": True})
    print(f"{status} {len(pairs):4d} fresh={fresh:3d} {url}", flush=True)
    time.sleep(4)

json.dump(raw, open("team27-raw.json", "w"), indent=1, ensure_ascii=False)
print("total fresh now:", len(raw["fresh"]))
