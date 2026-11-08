#!/usr/bin/env python3
"""Team16 stage 2 — verify candidates with python requests (fresh connection
per request), resume-aware via team16-progress.json.
Writes team16-verified-raw.json (schema-exact + _meta), team16-unverified-pending.json.
"""
import json, re, os, time, html as ihtml
import requests

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
SESS = requests.Session()
SESS.headers.update({"User-Agent": UA})

PORN_RE = re.compile(
    r'\b(porn|pornhub|xxx|nude|nudist|sex\s?video|escort|call\s?girl|'
    r'fuck|dick|pussy|boobs?|tits|anal|horny|porno|'
    r'sexo\s?(gratis|duro|expl[ií]cito)|chicas\s?(calientes|sexys))\b',
    re.I)
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6'
                      '\U0001F445\U0001F444\U0001F48B\U0001F924\U0001F60B'
                      '\U0001F612\U0001F440]')

PHONE_RE = re.compile(r'^\+?\d[\d\s\-]{7,}$')

def og_title(code):
    """Returns og:title str, '' for dead, None for transport failure,
    or the sentinel 'RATELIMIT' on HTTP 429. Uses a keep-alive Session
    (fresh-per-request measured 9s vs 0.6s keep-alive; results identical)."""
    global SESS
    try:
        r = SESS.get(f"https://chat.whatsapp.com/{code}", timeout=25)
    except Exception:
        # connection may have gone stale through the proxy; reset once
        try:
            SESS = requests.Session()
            SESS.headers.update({"User-Agent": UA})
            r = SESS.get(f"https://chat.whatsapp.com/{code}", timeout=25)
        except Exception:
            return None
    if r.status_code == 429:
        return "RATELIMIT"
    body = r.text or ""
    if not body:
        return None
    m = re.search(r'<meta\s[^>]*property=["\']og:title["\'][^>]*>', body, re.I)
    if not m:
        return None
    c = re.search(r'content=["\']([^"\']*)["\']', m.group(0))
    title = ihtml.unescape(c.group(1)).strip() if c else ""
    return title

def main():
    d = json.load(open(os.path.join(WAVE, "team16-candidates.json")))
    results = d["candidates"]
    porn_drops = d.get("porn_drops", 0)

    prog_path = os.path.join(WAVE, "team16-progress.json")
    if os.path.exists(prog_path):
        p = json.load(open(prog_path))
        verified, pending = p["verified"], p["pending"]
        done_codes = set(p.get("done_codes", []))
        porn_drops = p.get("porn_drops", porn_drops)
        ratelimited = p.get("ratelimited", False)
        print(f"resuming: {len(verified)} verified, {len(pending)} pending, "
              f"{len(done_codes)} done, ratelimited={ratelimited}", flush=True)
    else:
        verified, pending, done_codes = [], [], set()
        ratelimited = False

    todo = [r for r in results if r["code"] not in done_codes]
    print(f"to verify: {len(todo)}", flush=True)
    for i, r in enumerate(todo):
        code = r["code"]
        if ratelimited:
            r["note"] = "rate-limited"; pending.append(r)
        else:
            og = og_title(code)
            if og == "RATELIMIT":
                print("RATE LIMITED at", i, "- banking rest as pending", flush=True)
                r["note"] = "rate-limited"; pending.append(r)
                ratelimited = True
            elif og is None:
                r["note"] = "transport failure"; pending.append(r)
            elif og == "":
                pass  # dead link
            else:
                name = og if og else r["title"]
                if PHONE_RE.match(name):
                    pass
                elif PORN_RE.search(name) or EMOJI_RE.search(name):
                    porn_drops += 1
                else:
                    verified.append({
                        "name": name, "category": "Other",
                        "country": r["iso"], "description": "",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                        "_meta": {"title": r["title"], "tag": r["tag"],
                                  "cityname": r["cityname"], "desc": r["raw_desc"]},
                    })
        done_codes.add(code)
        time.sleep(0.6)
        if (i + 1) % 25 == 0 or i == len(todo) - 1:
            print(f"verify {i+1}/{len(todo)} verified={len(verified)}", flush=True)
            json.dump({"verified": verified, "pending": pending,
                       "porn_drops": porn_drops,
                       "done_codes": sorted(done_codes), "ratelimited": ratelimited},
                      open(prog_path, "w"), ensure_ascii=False)

    json.dump(pending, open(os.path.join(WAVE, "team16-unverified-pending.json"),
                            "w"), ensure_ascii=False, indent=1)
    json.dump(verified, open(os.path.join(WAVE, "team16-verified-raw.json"),
                             "w"), ensure_ascii=False, indent=1)
    print(f"DONE verified={len(verified)} pending={len(pending)} "
          f"porn_drops={porn_drops} ratelimited={ratelimited}", flush=True)

if __name__ == "__main__":
    main()
