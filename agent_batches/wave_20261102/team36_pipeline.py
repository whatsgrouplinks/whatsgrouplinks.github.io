#!/usr/bin/env python3
"""Team36 listicle scrape pipeline: extract, dedupe, curl-verify, bank."""
import json, re, html as h, subprocess, time, sys

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261102"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CODE_RE = r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"

PAGES = [
    # (file, page_url, category, country_fn)
    ("/tmp/whatgroupscom_cricket-whatsapp-group-links_.html",
     "https://whatgroups.com/cricket-whatsapp-group-links/", "Sports", "wg"),
    ("/tmp/wagro.html",
     "https://wagrouplinks.net/cricket-whatsapp-group-links/", "Sports", "fixed-International"),
    ("/tmp/newgrouplinkspk_cricket-whatsapp-group-links_.html",
     "https://newgrouplinks.pk/cricket-whatsapp-group-links/", "Sports", "ngl"),
    ("/tmp/whgroupslink_pakistan-jobs-whatsapp-group-links_.html",
     "https://whgroups.link/pakistan-jobs-whatsapp-group-links/", "Jobs", "fixed-PK"),
    ("/tmp/sandbox.html",
     "https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/", "Business", "sb"),
]

def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return h.unescape(s).strip()

def headings(html):
    hs = []
    for m in re.finditer(r"<h[123][^>]*>(.*?)</h[123]>", html, re.S | re.I):
        hs.append((m.start(), strip_tags(m.group(1))))
    return hs

def heading_for(hs, pos):
    cur = ""
    for p, t in hs:
        if p < pos:
            cur = t
        else:
            break
    return cur

def country_from_heading(kind, hd, name):
    hd = (hd or "").lower()
    nm = (name or "").lower()
    if kind == "wg":
        if "indian" in hd or "india" in hd: return "IN"
        if "pakistan" in hd: return "PK"
        if "austral" in hd: return "AU"
        if "sri lank" in hd: return "LK"
        return "International"
    if kind == "ngl":
        if "pakistani" in hd: return "PK"
        return "International"
    if kind == "sb":
        if "united states" in hd or "u.s" in hd: return "US"
        if "canada" in hd: return "CA"
        return "International"
    return "International"

def parse_page(path, cat, kind):
    html = open(path, encoding="utf-8", errors="ignore").read()
    hs = headings(html)
    out = []
    seen_local = set()
    # generic table pattern: <td>NAME</td><td>...<a href="chat.whatsapp.com/CODE"
    for m in re.finditer(
        r"<td[^>]*>([^<]{1,140})</td>\s*<td[^>]*>.*?<a\s+href=\"https?://" + CODE_RE + r"\"",
        html, re.S | re.I):
        name, code = m.group(1), m.group(2)
        # skip header cells
        nl = name.strip().lower()
        if nl in ("group name", "groups name", "links", "join link", "current group name",
                  "potentially useful for", "verification", "invite"):
            continue
        name = h.unescape(name).strip()
        hd = heading_for(hs, m.start())
        out.append((name, code, hd))
    # sandbox 4-col table: name, desc, verification, invite
    for m in re.finditer(
        r"<tr>\s*<td>([^<]{1,140})</td>\s*<td>([^<]{0,300})</td>\s*<td>[^<]{0,200}</td>\s*<td><a\s+href=\"https?://" + CODE_RE + r"\"",
        html, re.S | re.I):
        name, desc_hint, code = m.group(1), m.group(2), m.group(3)
        if name.strip().lower() in ("current group name",): continue
        hd = heading_for(hs, m.start())
        out.append((h.unescape(name).strip(), code, hd + " | " + h.unescape(desc_hint).strip()))
    # whgroups card pattern
    for m in re.finditer(
        r"<div[^>]*font-weight:700[^>]*>([^<]{1,140})</div>\s*<p[^>]*>([^<]{0,400})</p>\s*<p><a\s+href=\"https?://" + CODE_RE + r"\"",
        html, re.S | re.I):
        name, desc_hint, code = m.group(1), m.group(2), m.group(3)
        hd = heading_for(hs, m.start())
        out.append((h.unescape(name).strip(), code, hd + " | " + h.unescape(desc_hint).strip()))
    # newgrouplinks card pattern: <p ...>NAME</p></div><div><div><a href="code"
    for m in re.finditer(
        r"<p[^>]*>([^<]{1,140})</p></div>\s*<div[^>]*>\s*<div[^>]*><a[^>]*href=\"https?://" + CODE_RE + r"\"",
        html, re.S | re.I):
        name, code = m.group(1), m.group(2)
        hd = heading_for(hs, m.start())
        out.append((h.unescape(name).strip(), code, hd))
    # dedupe by code within page (keep first)
    uniq = []
    for name, code, hd in out:
        if code not in seen_local:
            seen_local.add(code)
            uniq.append((name, code, hd))
    return uniq

def verify(code):
    """returns (http_code, og_title) ; raises RuntimeError on transport failure"""
    url = "https://chat.whatsapp.com/" + code
    p = subprocess.run(
        ["curl", "-sL", "--max-time", "25", "-A", UA, "-o", "/tmp/team36_w.html",
         "-w", "%{http_code}", url],
        capture_output=True, text=True, timeout=40)
    if p.returncode != 0:
        raise RuntimeError("curl exit %d" % p.returncode)
    http_code = p.stdout.strip()
    if http_code in ("000", ""):
        raise RuntimeError("no response")
    html = open("/tmp/team36_w.html", encoding="utf-8", errors="ignore").read()
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html, re.S | re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', html, re.S | re.I)
    title = h.unescape(m.group(1)).strip() if m else ""
    return http_code, title

PORN = ["porn", "pornhub", "xxx", "nude", "sex video", "escort", "call girl",
        "fuck", "dick", "pussy", "boobs", "anal"]
PORN_EMOJI = ["\U0001F975", "\U0001F346", "\U0001F351", "\U0001F51E", "\U0001F4A6", "\U0001F445", "\U0001F444", "\U0001F48B"]

def porn_hit(text):
    t = (text or "").lower()
    if any(w in t for w in PORN): return True
    if any(e in (text or "") for e in PORN_EMOJI): return True
    return False

CAT_WORDS = {"Sports": ("cricket fans", "match"), "Jobs": ("job seekers", "vacancies"),
             "Business": ("entrepreneurs", "business owners")}

def make_desc(name, cat, country):
    cname = {"IN": "India", "PK": "Pakistan", "AU": "Australia", "LK": "Sri Lanka",
             "US": "the United States", "CA": "Canada"}.get(country, "around the world")
    if cat == "Sports":
        return (f"A {cat} group for cricket fans in {cname} sharing live match updates, scores and fan discussions. "
                "Follow tournaments, teams and match-day chat with fellow cricket lovers.")
    if cat == "Jobs":
        return (f"A {cat} group for job seekers in {cname} with daily vacancy alerts and hiring updates. "
                "Share openings, exam news and career tips with other applicants.")
    if cat == "Business":
        return (f"A {cat} group for entrepreneurs and professionals in {cname} exchanging ideas, contacts and opportunities. "
                "Network with founders, marketers and small-business owners.")
    return f"A {cat} community for members in {cname}. Chat, share updates and connect around shared interests."

def main():
    union = set(json.load(open(WAVE + "/dedupe_union.json")))
    cands = []
    seen = set()
    for path, url, cat, kind in PAGES:
        rows = parse_page(path, cat, kind)
        new_rows = 0
        for name, code, hd in rows:
            if code in union or code in seen:
                continue
            seen.add(code)
            if kind.startswith("fixed-"):
                country = kind.split("-")[1]
            else:
                country = country_from_heading(kind, hd, name)
            cands.append({"src_name": name, "code": code, "cat": cat, "country": country,
                          "hint": hd, "src": url})
            new_rows += 1
        print(f"{url}: {len(rows)} extracted, {new_rows} survive union+in-batch dedupe", flush=True)

    verified, pending, porn_drops = [], [], 0
    rate_limited = False
    for i, c in enumerate(cands):
        try:
            http_code, title = verify(c["code"])
        except RuntimeError as e:
            pending.append({**c, "note": "transport failure", "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""})
            time.sleep(0.7)
            continue
        if http_code == "429":
            rate_limited = True
            print("HTTP 429 hit at index %d — stopping" % i, flush=True)
            break
        time.sleep(0.7)
        if not title:
            continue  # dead
        name = c["src_name"]
        if not name or name.strip().lower() in ("link", "join", "click here", "view invite"):
            name = title
        if porn_hit(name) or porn_hit(title):
            porn_drops += 1
            continue
        # guard: name must not be URL / personal info-ish
        name = name.strip()
        if not name or name.startswith("http"):
            name = title.strip()
        item = {"name": name, "category": c["cat"], "country": c["country"],
                "description": make_desc(name, c["cat"], c["country"]),
                "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""}
        verified.append(item)
        print(f"[{i+1}/{len(cands)}] LIVE: {name[:50]} ({c['country']}/{c['cat']})", flush=True)

    if rate_limited:
        # bank remaining as rate-limited pending (resume point = first unprocessed index)
        for c in cands[i:]:
            pending.append({**{k: v for k, v in c.items() if k in ("src_name","code","cat","country","src","hint")},
                            "note": "rate-limited", "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""})

    json.dump(verified, open(WAVE + "/team36-new-listicles.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + "/team36-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print(f"VERIFIED={len(verified)} PENDING={len(pending)} PORN_DROPS={porn_drops} RATE_LIMITED={rate_limited}", flush=True)

if __name__ == "__main__":
    main()
