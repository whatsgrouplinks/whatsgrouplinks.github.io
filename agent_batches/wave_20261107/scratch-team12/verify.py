#!/usr/bin/env python3
"""Team 12: verify harvested codes against chat.whatsapp.com og:title."""
import json, re, sys, time, html, requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261107/"
SCRATCH = WAVE + "scratch-team12/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
BLOCK_WORDS = ["porn", "xxx", "nudes", "nude", "sex video", "escort", "call girl", "randi",
               "fuck", "dick", "pussy", "boobs", "anal", "bokep", "onlyfans", "sexchat", "sexy video"]
BLOCK_EMOJI = ["🥵", "🍆", "🍑", "🔞", "💦", "👅", "👄", "💋"]
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{6,}\d")

union = set(json.load(open(WAVE + "dedupe_union.json")))

def og_meta(text, prop):
    # content="..." property="og:title" or property first
    m = re.search(r'<meta[^>]*property=["\']' + prop + r'["\'][^>]*content=["\']([^"\']*)["\']', text, re.I)
    if m:
        return html.unescape(m.group(1)).strip()
    m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']' + prop + r'["\']', text, re.I)
    if m:
        return html.unescape(m.group(1)).strip()
    return ""

def check(code):
    """Returns (status, og_title, og_image): status in live/dead/pending."""
    url = "https://chat.whatsapp.com/" + code
    last_exc = None
    for attempt in range(2):
        try:
            s = requests.Session() if attempt == 1 else requests.Session()
            r = s.get(url, headers=UA, timeout=20, allow_redirects=True)
            if r.status_code != 200:
                if attempt == 0:
                    time.sleep(2)
                    continue
                return ("pending", "", "")
            title = og_meta(r.text, "og:title")
            img = og_meta(r.text, "og:image")
            if title:
                return ("live", title, img)
            if attempt == 0:
                time.sleep(2)
                continue
            return ("dead", "", "")
        except Exception as e:
            last_exc = e
            if attempt == 0:
                time.sleep(2)
                continue
            return ("pending", "", "")
    return ("pending", "", "")

def clean_name(n):
    n = html.unescape(n or "").strip()
    return re.sub(r"\s+", " ", n)

BLOCK_RE = re.compile(r"\b(porn|xxx|nudes?|sex\s*video|escort|call\s*girl|randi|fuck|dick|pussy|boobs|anal|bokep|onlyfans|sexchat|sexy\s*video)\b", re.I)
def blocked(name, ogtitle=""):
    s = (name + " " + ogtitle)
    if BLOCK_RE.search(s):
        return True
    if any(e in (name + ogtitle) for e in BLOCK_EMOJI):
        return True
    return False

# inputs: pairs of (rawfile, country)
inputs = []
for arg in sys.argv[1:]:
    f, country = arg.split(":", 1)
    inputs.append((f, country))

cands = {}  # code -> record
for f, country in inputs:
    try:
        raw = json.load(open(SCRATCH + f))
    except Exception as e:
        print("skip", f, e, flush=True)
        continue
    for code, r in raw.items():
        if code in union or code in cands:
            continue
        name = clean_name(r.get("name", ""))
        if not name:
            continue
        if "whatsappkanali" in name.lower() or "linkado" in name.lower():
            continue
        if PHONE_RE.search(name):
            continue
        if blocked(name):
            print("BLOCKED name:", name, flush=True)
            continue
        cat = r.get("category", "Community & Social")
        cands[code] = {"name": name, "category": cat, "country": country,
                       "code": code, "src_desc": (r.get("desc", "") or "")[:200]}
print("candidates to verify:", len(cands), flush=True)

verified, pending = [], []
items = list(cands.items())
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(lambda kv: (kv[0], kv[1], check(kv[0])), items))
for code, rec, (status, ogtitle, ogimg) in results:
    if status == "live":
        # final name = live og:title (the true WhatsApp group name); fall back to listing name
        name = ogtitle.strip() if ogtitle and ogtitle.strip() else rec["name"]
        try:
            if any(ch in name for ch in "Ãð"):
                name = name.encode("latin-1").decode("utf-8")
        except Exception:
            pass
        name = re.sub(r"\s+", " ", name).strip()
        if not name or name.endswith("..."):
            print("DROP bad name:", repr(name), rec["invite"] if "invite" in rec else code, flush=True)
            continue
        if blocked(name, ogtitle):
            print("BLOCKED og:", name, "|", ogtitle, flush=True)
            continue
        cat = rec["category"]
        desc = f"Join the {name} WhatsApp group for {cat.lower()} discussions and updates."
        img = ogimg if "pps.whatsapp.net" in ogimg else ""
        verified.append({"name": name, "category": cat, "country": rec["country"],
                         "description": desc,
                         "invite": "https://chat.whatsapp.com/" + code,
                         "image": img})
    elif status == "pending":
        pending.append({"name": rec["name"], "category": rec["category"],
                        "country": rec["country"], "description": "",
                        "invite": "https://chat.whatsapp.com/" + code, "image": ""})
    # dead: dropped
print(f"VERIFIED {len(verified)} PENDING {len(pending)} DEAD {len(items)-len(verified)-len(pending)}", flush=True)
json.dump(verified, open(SCRATCH + "verified.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(SCRATCH + "pending.json", "w"), ensure_ascii=False, indent=1)
for v in verified:
    print("LIVE", v["invite"], v["name"], "|", v["category"], "|", v["country"], flush=True)
for p in pending:
    print("PEND", p["invite"], p["name"], flush=True)
