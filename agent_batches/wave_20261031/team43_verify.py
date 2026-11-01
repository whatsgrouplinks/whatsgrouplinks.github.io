#!/usr/bin/env python3
"""team43 verification: dedupe + og:title verify + porn filter -> JSON outputs."""
import json, re, subprocess, time, html, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
UNION = set(x.strip() for x in open('/tmp/team43_union.txt') if x.strip())
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

PORN = re.compile(r'pornhub|porn\b|xxx|nude|escort|call\s*girl|sex\s*video|\bfuck\b|\bdick\b|pussy|boobs|\banal\b|xnxx|xvideo|adulti?18|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)

def og_title(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(
            ["curl","-sL","--max-time","25","-A",UA,"-w","\n%{http_code}","--compressed",url],
            capture_output=True, text=True, timeout=40)
        body = p.stdout
        if "\n429" in body[-8:]:
            return ("RATE_LIMIT", None)
        m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', body)
        if not m:
            m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', body)
        if m:
            t = html.unescape(m.group(1)).strip()
            return ("OK", t)
        return ("OK", "")
    except Exception:
        return ("TRANSPORT", None)

def run(candidates, batch_name):
    """candidates: list of (name, code, country). Appends verified to team43-sports-fresh.json."""
    out_path = os.path.join(BASE, "team43-sports-fresh.json")
    pend_path = os.path.join(BASE, "team43-unverified-pending.json")
    seen = set()
    if os.path.exists(out_path):
        for it in json.load(open(out_path)):
            m = re.search(r'([A-Za-z0-9]{22})', it.get('invite',''))
            if m: seen.add(m.group(1))
    pend = json.load(open(pend_path)) if os.path.exists(pend_path) else []
    pend_codes = set(re.search(r'([A-Za-z0-9]{22})', p['invite']).group(1) for p in pend)
    verified, pending, dropped = 0, 0, 0
    for name, code, country in candidates:
        if code in UNION or code in seen or code in pend_codes:
            continue
        res, title = og_title(code)
        if res == "RATE_LIMIT":
            note = f"rate-limited at {batch_name}; resume here"
            pend.append({"name": name, "category": "Sports", "description": f"Sports fans group on WhatsApp ({country}).", "image": "",
                         "invite": f"https://chat.whatsapp.com/{code}", "country": country, "note": note})
            pending += 1
            break
        if res == "TRANSPORT":
            pend.append({"name": name, "category": "Sports", "description": f"Sports fans group on WhatsApp ({country}).", "image": "",
                         "invite": f"https://chat.whatsapp.com/{code}", "country": country, "note": "transport failure; retry next wave"})
            pending += 1
            time.sleep(0.8); continue
        if not title:
            dropped += 1; time.sleep(0.6); continue
        if PORN.search(name) or PORN.search(title):
            dropped += 1; time.sleep(0.6); continue
        gname = re.sub(r'\s+', ' ', title)[:120]
        item = {"name": gname, "category": "Sports",
                "description": f"Join {gname} on WhatsApp - a sports fan community for cricket and football fans ({country}) with match updates and live discussions.",
                "image": "", "invite": f"https://chat.whatsapp.com/{code}", "country": country}
        # rewrite description keyword-rich without repeating name verbatim twice
        item["description"] = f"Sports WhatsApp group ({country}) for fans - match updates, live scores, team discussions and fan chat."
        arr = json.load(open(out_path)) if os.path.exists(out_path) else []
        arr.append(item)
        json.dump(arr, open(out_path, 'w'), ensure_ascii=False, indent=1)
        seen.add(code)
        verified += 1
        time.sleep(0.8)
    json.dump(pend, open(pend_path, 'w'), ensure_ascii=False, indent=1)
    print(f"{batch_name}: verified={verified} pending={pending} dropped(dead/porn)={dropped}")
    return verified, pending

if __name__ == "__main__":
    # candidates json file passed as arg1
    cands = json.load(open(sys.argv[1]))
    run([(c['name'], c['code'], c.get('country','XX')) for c in cands], sys.argv[2] if len(sys.argv)>2 else "batch")
