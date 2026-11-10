#!/usr/bin/env python3
"""Team 03 wave 20261110: verify fresh codes, screen, build outputs.
Verify: curl chat.whatsapp.com/<code>, browser UA, max 3 parallel,
>=0.6s between check starts, 15s timeout. LIVE = 200 + non-empty og:title.
Empty og:title retried twice (30s, then 60s gaps). Transport failure
(curl rc!=0 / http 0 / no status) = PENDING. Adult-category groupjoin
rows are NEVER verified. Scam/adult-signal items are excluded, not banked.
"""
import json, re, subprocess, sys, time, html, threading
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110")
import team03_run as T
from concurrent.futures import ThreadPoolExecutor

BASE = T.BASE
UA = T.UA
fresh = json.load(open(f"{BASE}/team03-fresh.json"))
by_code = {r["code"]: r for r in fresh}

ADULT_RE = re.compile(r"🔞|🥵|sexy|hookup|escort|porn|xxx|nude|naked|onlyfans|cam[- ]?girl|camgirl|sex video|sex chat|desi (?:viral|video|sex)|hot (?:girl|video|bhabhi)", re.I)
SCAM_RE = re.compile(r"b[- ]?love|forsage|shey?i\b.*airdrop|airdrop.*shey?i|paypal loader|bitfinex|counterfeit (?:currency|money)|carding|crypto[- ]?doubling|double (?:your|the) (?:money|investment)|double your (?:income|profit)|free money", re.I)
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
SRC_RE = re.compile(r"(?i)\b(groupsinvite|groupchatconnect|groupsor|groupjoin|ongrupos|whatsapp group invite link|group/channel chat invite)\b")
PROHIB_RE = re.compile(r"[^.!?\n]*(not allowed|prohibit|na\s*karein|don'?t\s+share|do\s+not\s+share|no\s+porn|no\s+xxx|strictly\s+prohibited|not\s+share|allowed\s+nahi|mana\s+hai|DILARANG\s+SHARE[^.!?\n]*pronO|DILARANG\s+SPAM)[^.!?\n]*[.!?\n]?", re.I)

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()

def screen_text(name, og, desc):
    t = T.clean(f"{name} {og} {desc}")
    t2 = PROHIB_RE.sub(" ", t)
    m = SCAM_RE.search(t2)
    if m:
        return f"scam signal: {m.group(0)}"
    m = ADULT_RE.search(t2)
    if m:
        return f"adult-sexual signal: {m.group(0)}"
    return None

# ---- pre-verify exclusions (never verify these) ----
exclusions = []
to_verify = []
for r in fresh:
    code = r["code"]
    if r.get("source") == "groupjoin.link API" and (r.get("category_hint") or "") == "Adult":
        exclusions.append({"code": code, "reason": "groupjoin.link source-classified Adult category (nsfw=1) — never verified/banked per task rule",
                           "name": r.get("name", "")[:80], "source": r["source"]})
        continue
    hit = screen_text(r.get("name") or "", "", r.get("desc") or "")
    if hit:
        exclusions.append({"code": code, "reason": f"listing name/desc {hit}", "name": r.get("name", "")[:80], "source": r["source"]})
        continue
    to_verify.append(r)
print(f"fresh={len(fresh)} pre-excluded={len(exclusions)} to_verify={len(to_verify)}", flush=True)
json.dump(exclusions, open(f"{BASE}/team03-exclusions-stage1.json", "w"), ensure_ascii=False, indent=1)

# ---- verification ----
lock = threading.Lock()
last = [0.0]

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "15", "-A", UA,
                            "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=25)
        body = r.stdout or ""
        m = re.search(r"\n(\d{3})\s*$", body)
        http = int(m.group(1)) if m else 0
        body_only = body[:m.start()] if m else body
        og = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', body_only, re.I)
        if not og:
            og = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body_only, re.I)
        title = clean(og.group(1)) if og else ""
        return {"code": code, "http": http, "og_title": title, "curl_rc": r.returncode}
    except Exception as e:
        return {"code": code, "http": 0, "og_title": "", "curl_rc": -1, "error": str(e)[:100]}

def gated(code):
    with lock:
        gap = 0.6 - (time.time() - last[0])
        if gap > 0:
            time.sleep(gap)
        last[0] = time.time()
    return check(code)

codes = [r["code"] for r in to_verify]
results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(gated, codes):
        results[res["code"]] = res
        n = len(results)
        if n % 20 == 0:
            live = sum(1 for v in results.values() if v["http"] == 200 and v["og_title"])
            print(f"... pass1 {n}/{len(codes)} live-so-far={live}", flush=True)

for rnd, wait in ((1, 30), (2, 60)):
    amb = [c for c, v in results.items() if v["http"] == 200 and not v["og_title"]]
    if not amb:
        break
    print(f"retry round {rnd}: {len(amb)} ambiguous, sleeping {wait}s", flush=True)
    time.sleep(wait)
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(gated, amb):
            if res["og_title"]:
                results[res["code"]] = res
                print("  resolved live:", res["code"], repr(res["og_title"][:60]), flush=True)
            else:
                results[res["code"]] = res
    json.dump(results, open(f"{BASE}/team03-verify.json", "w"), indent=1)

json.dump(results, open(f"{BASE}/team03-verify.json", "w"), indent=1)
live = sum(1 for v in results.values() if v["http"] == 200 and v["og_title"])
amb = sum(1 for v in results.values() if v["http"] == 200 and not v["og_title"])
pend = sum(1 for v in results.values() if v["http"] == 0 or v.get("curl_rc", 0) not in (0,))
print(f"verify done: live={live} dead-empty={amb} transport-pending={pend} total={len(results)}", flush=True)

# ---- build candidates ----
def parse_gcc(desc):
    cat, ctry = "Community & Social", "International"
    m = re.search(r"ضمن تصنيف\s+(\S+)\s+من\s+(\S+)", desc or "")
    if m:
        cat = T.AR_CAT.get(m.group(1), "Community & Social")
        ctry = T.AR_COUNTRY.get(m.group(2), "International")
    return cat, ctry

JB_RE = re.compile(r"jb|jual|beli|store|shop|akun|top\s*up|rekber|japost", re.I)

def build_candidate(code, v, r):
    og = clean(v["og_title"])
    name = PHONE_RE.sub("", og).strip()
    name = re.sub(r"\s+", " ", name)
    desc_raw = clean(r.get("desc") or "")
    src = r.get("source", "")
    country, category = "International", "Community & Social"
    if src == "groupjoin.link API":
        country = (r.get("country_hint") or "International").upper()
        if len(country) != 2:
            country = "International"
        ch = r.get("category_hint") or ""
        blob = f"{r.get('name','')} {' '.join(r.get('tags') or [])} {ch}"
        if JB_RE.search(blob):
            category = "Buy Sell"
        elif ch in ("Gaming", "Sports & Fitness", "Business", "Money", "Online Shopping"):
            category = {"Gaming": "Gaming", "Sports & Fitness": "Sports", "Business": "Business",
                        "Money": "Finance", "Online Shopping": "Buy Sell"}[ch]
        else:
            category = T.infer_category(blob)
    elif src == "groupchatconnect.info":
        category, country = parse_gcc(desc_raw)
        if category == "Community & Social":
            category = T.infer_category(f"{r.get('name','')} {desc_raw}")
    elif src == "groupsinvite.link":
        country = r.get("country_hint") or "International"
        category = T.infer_category(f"{r.get('name','')} {' '.join(r.get('tags') or [])} {desc_raw}")
    elif src == "ongrupos.com":
        country = "BR"
        category = T.infer_category(f"{r.get('name','')} {desc_raw}")
    if category not in T.ALLOWED_CATS:
        category = "Community & Social"
    d = PROHIB_RE.sub(" ", desc_raw)
    d = SRC_RE.sub("", d)
    d = URL_RE.sub("", d)
    d = PHONE_RE.sub("", d)
    d = re.sub(r"Welcome to my whatsapp group[^.]*\.\s*Please join my whatsapp group\.?\s*", "", d, flags=re.I)
    d = re.sub(r"Follow this invite link to join[^.]*\.?\s*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip(" .")
    if len(d) < 25 or "Group/Channel Chat Invite" in d or "اكتشف أيضاً مجموعات مشابهة" in d:
        d = ""
    if not d:
        d = f"Join {name}, a WhatsApp group for {category.lower()} fans and members. Share updates, chat with others and stay connected with the community."
    sents = re.split(r"(?<=[.!?])\s+", d)
    d = " ".join(sents[:2])[:300].strip()
    return {"name": name, "category": category, "country": country,
            "description": d, "invite": f"https://chat.whatsapp.com/{code}"}

candidates, pending, dead = [], [], []
for code, v in results.items():
    r = by_code[code]
    og = clean(v.get("og_title") or "")
    if v.get("http") == 0 or v.get("curl_rc", 0) not in (0,):
        pending.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                        "reason": f"transport failure http={v.get('http')} curl_rc={v.get('curl_rc')}",
                        "source": r.get("source"), "listing_url": r.get("listing_url")})
        continue
    if v.get("http") != 200 or not og:
        dead.append(code)
        continue
    hit = screen_text(r.get("name") or "", og, r.get("desc") or "")
    if hit:
        exclusions.append({"code": code, "reason": f"og:title/name/desc {hit} (og_title={og[:80]})",
                           "name": r.get("name", "")[:80], "source": r.get("source")})
        continue
    if len(re.sub(r"[^\w]", "", og, flags=re.UNICODE)) < 2:
        exclusions.append({"code": code, "reason": "junk og:title", "name": og[:80], "source": r.get("source")})
        continue
    candidates.append(build_candidate(code, v, r))

# leads file
disc = json.load(open(f"{BASE}/team03-discovered-leads.json"))
leads_out = []
for l in disc:
    item = {"url": l["url"], "source": l["source"]}
    if "/channel/" in l["url"]:
        item["note"] = "channel-only page (WhatsApp/Telegram channel, no group invite)"
    elif l.get("note"):
        item["note"] = l["note"]
    leads_out.append(item)

json.dump(candidates, open(f"{BASE}/team03-leads-slice3.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{BASE}/team03-leads-slice3-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads_out, open(f"{BASE}/team03-leads-slice3-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(exclusions, open(f"{BASE}/team03-exclusions.json", "w"), ensure_ascii=False, indent=1)

raw = json.load(open(f"{BASE}/team03-raw.json"))
n_nocode = sum(1 for r in raw if not r.get("code"))
n_channel = sum(1 for r in raw if r.get("channel_only"))
summary = {
    "team": 3,
    "slice": "leads slice 3",
    "sources": ["groupsinvite.link (93 listings)", "groupchatconnect.info (63 listings)",
                "ongrupos.com (24 listings)", "groupjoin.link API (4 tag pages, 60 rows)"],
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads_out),
    "dead": len(dead),
    "exclusions": [{"code": e["code"], "reason": e["reason"]} for e in exclusions],
    "resume": "Slice complete. No resume needed: all 184 listings processed; 8 groupinvite detail fetches still failed after retries (codes unknown, listed in notes) and 9 GCC go.php groupe pages never resolved to a code — re-run those 17 listing URLs in a future wave.",
    "notes": (
        f"184 listings -> 240 records (60 groupjoin rows). Codes extracted: 188. Fresh vs dedupe union "
        f"(.existing_codes.json 108364 + groups.json 72742 codes, union 108364): 101 fresh, of which 8 "
        f"groupjoin Adult-category rows were never verified. Verified 93 codes: {len(candidates)} live, "
        f"{len(dead)} dead (HTTP 200 + empty og:title after 2 spaced retries), {len(pending)} transport-pending. "
        f"No-code records: {n_nocode} (16 channel-only GCC pages, 8 GI detail-fetch failures after retries, "
        f"9 GCC go.php failures, 5 GI rules pages with no join link, rest dup/unknown). "
        f"groupsinvite detail pages expose no invite; code lives on /group/rules/<slug>/. "
        f"ongrupos path segment IS the code; /join-group/<code> 301s to chat.whatsapp.com/<code>. "
        f"groupchatconnect /go/<token> token IS the code; go.php->join.php->groupsor flow did not resolve "
        f"in this run (join.php returned no groupsor redirect under curl). "
        f"Wave dir is shared with many teams hammering the same sites; fetches were slow/congested. "
        f"Low yield: slice is old listings, most invites revoked/expired."
    ),
}
json.dump(summary, open(f"{BASE}/team03-leads-slice3-summary.json", "w"), ensure_ascii=False, indent=1)
print("candidates:", len(candidates), flush=True)
for c in candidates:
    print(" -", c["category"], c["country"], "|", c["name"][:50], "|", c["invite"], flush=True)
print("excluded:", len(exclusions), "pending:", len(pending), "dead:", len(dead), "leads:", len(leads_out), flush=True)
