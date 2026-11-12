#!/usr/bin/env python3
"""TEAM21 grupbul re-check: controls, Food/Chat category re-check, 3 pending codes, 2 redirects."""
import json, re, time, sys
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
S = requests.Session()
S.headers.update(UA)
LOG = open(WAVE + "team21-grupbul-progress.jsonl", "a", encoding="utf-8")

def log(rec):
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    LOG.write(json.dumps(rec, ensure_ascii=False) + "\n"); LOG.flush()
    print(json.dumps(rec, ensure_ascii=False), flush=True)

def og_title(html):
    if not html: return ""
    m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', html, re.I)
    if m: return m.group(1).strip()
    m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', html, re.I)
    return m.group(1).strip() if m else ""

def og_desc(html):
    if not html: return ""
    m = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)', html, re.I)
    return m.group(1).strip() if m else ""

def fetch(url, timeout=90):
    """Returns (http_status_or_'000', html_or_'', error)."""
    try:
        r = S.get(url, timeout=timeout, allow_redirects=True)
        return str(r.status_code), r.text, ""
    except requests.exceptions.Timeout:
        return "000", "", "timeout"
    except Exception as e:
        return "000", "", type(e).__name__ + ": " + str(e)[:120]

def verify_code(code, attempts=3, gap=45):
    """Spaced retries. LIVE if og:title non-empty on any attempt with HTTP 200."""
    results = []
    for i in range(attempts):
        if i: time.sleep(gap)
        http, html, err = fetch(f"https://chat.whatsapp.com/{code}", timeout=90)
        t = og_title(html); d = og_desc(html)
        rec = {"kind": "verify", "code": code, "attempt": i+1, "http": http, "og_title": t, "og_desc": d[:120], "err": err}
        log(rec); results.append(rec)
        if http == "200" and t:
            return "LIVE", t, results
        if http == "200" and not t:
            # confirmed dead only if a second 200 also empty? keep going per spec: spaced retry before dead
            pass
    # decide
    https = [r["http"] for r in results]
    if all(h == "200" for h in https):
        return "DEAD", "", results
    if any(h == "200" for h in https):
        return "PENDING", "", results
    return "PENDING", "", results

# ---------- CONTROLS ----------
print("== CONTROLS ==", flush=True)
ctrl_live = "KrDwdK8EIkB6vgauHg5M7N"   # from groups.json
ctrl_fake = "ZZZZZZZZZZZZZZZZZZZZZZ"
for label, code in [("control-live", ctrl_live), ("control-fake", ctrl_fake)]:
    http, html, err = fetch(f"https://chat.whatsapp.com/{code}", timeout=90)
    log({"kind": label, "code": code, "http": http, "og_title": og_title(html), "err": err, "len": len(html)})

# ---------- CATEGORY PAGES (one re-check each) ----------
print("== CATEGORY PAGES ==", flush=True)
cats = {
    "food_p1": "https://grupbul.com/en/category/whatsapp/53/food",
    "food_p2": "https://grupbul.com/en/category/whatsapp/53/food?page=2",
    "chat_p1": "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
    "chat_p2": "https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=2",
}
cat_res = {}
for key, url in cats.items():
    http, html, err = fetch(url, timeout=90)
    gids = sorted(set(re.findall(r'/group/(\d+)', html)))
    rec = {"kind": "category", "key": key, "url": url, "http": http, "len": len(html), "group_count": len(gids), "gids": gids, "err": err}
    log(rec); cat_res[key] = rec
    with open(WAVE + f"team21_{key}.html", "w", encoding="utf-8") as f: f.write(html)
    time.sleep(20)

# ---------- 3 PENDING CODES ----------
print("== PENDING CODES ==", flush=True)
pendings = [
    ("440817", "Tamil Jalsa", "ACtQYie1P32IceedwfPY9p"),
    ("865745", "Mumbaikar!", "I39fLwOHZ730XJ5glkcE82"),
    ("219135", "I Like India", "58IfJaAavCGId7CEz0vNJH"),
]
code_results = {}
for gid, name, code in pendings:
    verdict, title, results = verify_code(code, attempts=3, gap=45)
    code_results[code] = {"gid": gid, "name": name, "verdict": verdict, "og_title": title, "attempts": results}
    log({"kind": "code-verdict", "gid": gid, "name": name, "code": code, "verdict": verdict, "og_title": title})
    time.sleep(30)

# ---------- 2 REDIRECTS ----------
print("== REDIRECTS ==", flush=True)
redirects = [
    ("662627", "TIGER MAHARASTRA", "https://grupbul.com/redirect/662627/1325254"),
    ("400673", "Yaar Beli", "https://grupbul.com/redirect/400673/801346"),
]
redir_results = {}
for gid, name, url in redirects:
    got_code = None; attempts = []
    for i in range(3):
        if i: time.sleep(45)
        try:
            r = S.get(url, timeout=90, allow_redirects=False)
            loc = r.headers.get("Location", "")
            attempts.append({"attempt": i+1, "http": str(r.status_code), "location": loc[:200], "len": len(r.text)})
            log({"kind": "redirect", "gid": gid, "name": name, **attempts[-1]})
            m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,30})', loc)
            if m: got_code = m.group(1); break
            # also check body for invite link
            m2 = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,30})', r.text)
            if m2: got_code = m2.group(1); break
        except Exception as e:
            attempts.append({"attempt": i+1, "http": "000", "location": "", "err": type(e).__name__})
            log({"kind": "redirect", "gid": gid, "name": name, **attempts[-1]})
    redir_results[gid] = {"gid": gid, "name": name, "code": got_code, "attempts": attempts}
    # if code extracted, verify it
    if got_code:
        verdict, title, results = verify_code(got_code, attempts=3, gap=45)
        redir_results[gid]["verify"] = verdict; redir_results[gid]["og_title"] = title
        log({"kind": "redirect-code-verdict", "gid": gid, "name": name, "code": got_code, "verdict": verdict, "og_title": title})
    time.sleep(30)

json.dump({"categories": cat_res, "codes": code_results, "redirects": redir_results},
          open(WAVE + "team21-grupbul-raw-results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("DONE", flush=True)
