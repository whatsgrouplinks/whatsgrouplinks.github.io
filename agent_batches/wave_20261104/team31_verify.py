#!/usr/bin/env python3
"""Team31: verify chat.whatsapp.com codes via og:title (keep-alive session)."""
import json, re, sys, html
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.S | re.I)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.S | re.I)

def og_title(html_text):
    m = OG_RE.search(html_text) or OG_RE2.search(html_text)
    if not m: return ""
    return html.unescape(m.group(1)).strip()

def main():
    items = json.load(open(sys.argv[1]))  # [{"name":...,"category":...,"country":...,"description":...,"code":...}]
    union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/dedupe_union.json')))
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    verified, pending = [], []
    seen = set()
    for it in items:
        code = it["code"]
        if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code):
            print(f"SKIP bad code {code}"); continue
        if code in union or code in seen:
            print(f"SKIP dup {code}"); continue
        seen.add(code)
        url = f"https://chat.whatsapp.com/{code}"
        try:
            r = s.get(url, timeout=55)
            title = og_title(r.text)
            if title:
                it2 = {"name": title, "category": it["category"], "country": it["country"],
                       "description": it["description"], "invite": url, "image": ""}
                verified.append(it2)
                print(f"OK {code} -> {title[:60]}")
            else:
                print(f"DEAD(no og:title) {code} http={r.status_code}")
        except requests.exceptions.HTTPError as e:
            if getattr(e.response, 'status_code', None) == 429:
                print("RATE LIMITED 429 - stopping"); pending.append({**it, "invite": url, "note": "rate-limited"}); break
            pending.append({**it, "invite": url, "note": f"transport failure: {e}"}); s = requests.Session(); s.headers.update({"User-Agent": UA})
        except Exception as e:
            print(f"TRANSPORT {code}: {e}")
            pending.append({**it, "invite": url, "note": f"transport failure: {type(e).__name__}"})
            s = requests.Session(); s.headers.update({"User-Agent": UA})
    wd = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
    json.dump(verified, open(wd+'team31-meetup-eu-uk.json','w'), indent=1, ensure_ascii=False)
    json.dump(pending, open(wd+'team31-unverified-pending.json','w'), indent=1, ensure_ascii=False)
    print(f"VERIFIED={len(verified)} PENDING={len(pending)}")

if __name__ == "__main__":
    main()
