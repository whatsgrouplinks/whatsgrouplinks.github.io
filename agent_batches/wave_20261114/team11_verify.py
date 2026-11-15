#!/usr/bin/env python3
"""TEAM11 wave 20261114: groupsinvite.link 61 JS-gated pages.
Route that cracked it: site's own WP API GET /wp-json/custom/v2/groups
returns the full catalog; group_id == invite code (proven: 2280/2281
entries with a chat.whatsapp.com invite_link match group_id
case-insensitively; the 1 mismatch is a junk group_id '1567').
All 61 slugs matched API entries by group_id.lower(); invite_link is
'' for all 61 (hence rules pages say 'Link Unavailable').
Dedupe vs .existing_codes.json + groups.json: 43 dupes, 18 fresh.
This script verifies ONLY the 18 fresh codes, one keep-alive
requests.Session, browser UA, 60s timeout, og:title live signal,
empty -> 2 spaced retries before dead, 429/transport -> pending.
"""
import json, re, time, html, os
import requests

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
OG = re.compile(r'property="og:title" content="([^"]*)"')

FRESH = [
    # (code, api_name, api_category, api_country)
    ("0029VaJWsaMAYlULoYIUnD22", "Work From Home", "Career/Jobs/Freelancing", "India"),
    ("4nCNG2BYLR70QlGeAGtCzZ", "IPL Match Discussion \U0001f601\U0001f601\U0001f601\U0001f61a", "Sports/Games/Fantasy", "India"),
    ("B6uxJy5pp0fEUJ4LkbM5Cc", "Only It Job Pune", "Career/Jobs/Freelancing", "India"),
    ("Bc5Ramr13vz3meu4lqhr7Z", "Bitcoin Baba Store", "Shopping/Deals/Coupons", "India"),
    ("BlcpctfO7jnI9OrOvdjdWG", "Kerala job vacancy daily updates", "Career/Jobs/Freelancing", "India"),
    ("C2RHr7EdTPGF6oAu3QSGTx", "Free fire Id sale \U0001f4a5\U0001f534", "Sports/Games/Fantasy", "India"),
    ("DPrgxnFcOiJBPkdK5hTkSC", "ROMANCE MAHOOL \U0001f525", "Entertainment/Comedy/Fun", "Pakistan"),
    ("HiiBmwzdLRX3wYRkKmtH02", "Free computer course", "Education/Study/Learning", "India"),
    ("Hn5zWuXP3iTHp3jgxd32J6", "Jobs in Delhi NCR", "Career/Jobs/Freelancing", "India"),
    ("I2qi4pYi90o27GFy6kGPuR", "Bussiness Idea & Offers", "Business/Startup/Earn Money", "India"),
    ("IvtF7H1wXySHN1evwMZg7w", "\u2708\ufe0fMAJESTIC TRAVELS \U0001f6ec(5)", "Travel/Adventure/Road Trips", "India"),
    ("JlLmucQHRrYIelIJIr0SL3", "Job opportunities", "Career/Jobs/Freelancing", "India"),
    ("JN9z7LGePy8Ff0nfvbpdwK", "Free video editing course (43)", "Education/Study/Learning", "Pakistan"),
    ("JpzvITtZBvPHoz2cq3yQpv", "WINNING OF DREAM 11", "Sports/Games/Fantasy", "India"),
    ("JXfEvKS2TSYE8Q3fYnzF0i", "The Travel Square", "Travel/Adventure/Road Trips", "India"),
    ("KkGoSIxFLXF7Jeq7v4Oj6g", "Pharma medicine Jobs Pakistan", "Career/Jobs/Freelancing", "Pakistan"),
    ("L8jU3jB428dEBxf0fzFrSu", "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930 \u0936\u093f\u0915\u094d\u0937\u0915 \u092a\u0945\u0928\u0932 151", "Education/Study/Learning", "India"),
    ("LP7D0oGrxraLaId5PrezVD", "Free earning & verified airdrops \U0001f4af\u2714\ufe0f", "Crypto/Blockchain/Web3", "Pakistan"),
]

def og_title(session, code):
    """Returns (status, og_title_or_None, http_code). status in live/empty/transport/ratelimited."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = session.get(url, timeout=60)
    except requests.RequestException as e:
        return ("transport", None, str(e))
    if r.status_code == 429:
        return ("ratelimited", None, 429)
    if r.status_code != 200:
        return ("transport", None, r.status_code)
    m = OG.search(r.text)
    title = html.unescape(m.group(1)).strip() if m else ""
    if title:
        return ("live", title, 200)
    return ("empty", None, 200)

def main():
    s = requests.Session()
    s.headers.update(UA)
    # CONTROLS FIRST
    st, title, _ = og_title(s, "KrDwdK8EIkB6vgauHg5M7N")
    print(f"CONTROL live: status={st} og:title={title!r}", flush=True)
    assert st == "live" and title == "JAY - PHP & Python Full Stack Developer", "LIVE CONTROL FAILED"
    st, title, _ = og_title(s, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    print(f"CONTROL fabricated: status={st} og:title={title!r}", flush=True)
    assert st == "empty", "FABRICATED CONTROL FAILED"
    print("CONTROLS PASS", flush=True)

    ckpt = os.path.join(WD, "team11_verify_ckpt.jsonl")
    done = {}
    if os.path.exists(ckpt):
        for line in open(ckpt):
            try:
                r = json.loads(line)
                done[r["code"]] = r
            except Exception:
                pass
    results = []
    for code, name, cat, country in FRESH:
        if code in done:
            results.append(done[code])
            print(f"SKIP (ckpt) {code}", flush=True)
            continue
        attempts = []
        final = None
        for attempt in range(3):
            st, title, http = og_title(s, code)
            attempts.append({"attempt": attempt + 1, "status": st, "og_title": title, "http": http})
            print(f"  {code} attempt {attempt+1}: {st} {title!r}", flush=True)
            if st == "live":
                final = "live"
                break
            if st in ("transport", "ratelimited"):
                final = "pending"
                break
            # empty -> spaced retry
            if attempt < 2:
                time.sleep(25)
        if final is None:
            final = "dead"
        rec = {"code": code, "api_name": name, "api_category": cat, "api_country": country,
               "verdict": final, "og_title": attempts[-1].get("og_title") if final == "live" else None,
               "attempts": attempts}
        # 0029Va special: if chat link dead, check channel URL before calling it dead
        if code.startswith("0029Va") and final == "dead":
            try:
                r = s.get(f"https://www.whatsapp.com/channel/{code}", timeout=60)
                m = OG.search(r.text)
                ch_title = html.unescape(m.group(1)).strip() if m else ""
                rec["channel_check"] = {"http": r.status_code, "og_title": ch_title, "len": len(r.text)}
                print(f"  channel check {code}: http={r.status_code} og:title={ch_title!r}", flush=True)
                if ch_title:
                    rec["verdict"] = "channel"
            except Exception as e:
                rec["channel_check"] = {"error": str(e)}
        results.append(rec)
        with open(ckpt, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        time.sleep(4)
    json.dump(results, open(os.path.join(WD, "team11_verify.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("VERIFY DONE:", Counter(r["verdict"] for r in results), flush=True)
    for r in results:
        print(f"  {r['verdict']:7s} {r['code']} og={r.get('og_title')!r} api={r['api_name'][:50]!r}", flush=True)

if __name__ == "__main__":
    main()
