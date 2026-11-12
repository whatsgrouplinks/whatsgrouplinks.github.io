#!/usr/bin/env python3
"""TEAM22 groupssor API newest poll — resume after 2026-11-11T06:21:18.305Z."""
import json, re, time, sys
from pathlib import Path
import requests

WAVE = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112")
BUILD = Path("/home/hatch/workspace/whatsapp-groups-site")
API = "https://groupssor-api.blog-99n.workers.dev/api/groups"
CUTOFF = "2026-11-11T06:21:18.305Z"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

CATMAP = {
    "education": "Education", "entertainment": "Entertainment", "jobs": "Jobs",
    "community": "Community & Social", "social": "Community & Social",
    "sports": "Sports", "funny": "Funny", "humor": "Funny", "islamic": "Islamic",
    "health": "Health", "finance": "Finance", "news": "News",
    "buy": "Buy & Sell", "sell": "Buy & Sell", "friendship": "Friendship",
    "friends": "Friendship", "gaming": "Gaming", "technology": "Technology",
    "tech": "Technology", "business": "Business", "cooking": "Cooking",
    "crypto": "Crypto", "real estate": "Real Estate", "poetry": "Poetry",
    "dating": "Friendship", "music": "Entertainment", "movies": "Entertainment",
    "chat": "Community & Social", "study": "Education",
}

def cat_for(raw):
    r = (raw or "").strip().lower()
    if r in CATMAP: return CATMAP[r]
    for k, v in CATMAP.items():
        if k in r: return v
    return "Community & Social"

def extract_code(link):
    m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]{10,})", link or "")
    return m.group(1) if m else ""

# --- poll API ---
s = requests.Session()
s.headers.update(UA)
r = s.get(API, timeout=90)
print("API status", r.status_code, "len", len(r.text), flush=True)
r.raise_for_status()
entries = r.json()
if isinstance(entries, dict):
    entries = entries.get("groups") or entries.get("data") or []
print("entries:", len(entries), flush=True)
(entries_path := WAVE / "team22_api_raw.json").write_text(json.dumps(entries, ensure_ascii=False))
newest = max((e.get("createdAt", "") for e in entries), default="")
oldest = min((e.get("createdAt", "") for e in entries), default="")
print("window newest:", newest, "oldest:", oldest, flush=True)
fresh = [e for e in entries if e.get("createdAt", "") > CUTOFF]
fresh.sort(key=lambda e: e.get("createdAt", ""))
print("fresh >", CUTOFF, ":", len(fresh), flush=True)
for e in fresh:
    print("  FRESH", e.get("createdAt"), e.get("platform"), repr(e.get("name")), e.get("category"), e.get("country"), e.get("inviteLink"), flush=True)

# --- dedupe union ---
union = set(json.load(open(BUILD / ".existing_codes.json")))
print("union size:", len(union), flush=True)

# --- controls ---
def og_title(html):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html or "", re.I)
    if m: return m.group(1)
    m = re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', html or "", re.I)
    return m.group(1) if m else ""

def og_desc(html):
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html or "", re.I)
    return m.group(1) if m else ""

def check(code):
    """Returns (status, title, desc): status live/dead/pending.
    LIVE = non-empty og:title ONLY. og:description is the generic string
    'WhatsApp Group Invite' on BOTH live and dead pages, so it cannot be
    used as a fallback (verified 2026-11-12: fabricated code returned
    og:title='' with og:description='WhatsApp Group Invite')."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        resp = s.get(url, timeout=75)
        html = resp.text
        t, d = og_title(html), og_desc(html)
        if t.strip():
            return "live", t, d
        return "dead", t, d
    except Exception as ex:
        print("  transport fail", code, type(ex).__name__, ex, flush=True)
        return "pending", "", ""

# control live: pick a code from groups.json
groups = json.load(open(BUILD / "groups.json"))
ctrl_live = None
for g in groups:
    c = extract_code(g.get("invite", ""))
    if c:
        ctrl_live = c
        break
print("control live code:", ctrl_live, flush=True)
st, t, d = check(ctrl_live)
print("CONTROL live ->", st, repr(t), flush=True)
assert st == "live", "CONTROL LIVE FAILED"
st2, t2, d2 = check("ZZZZZZZZZZZZZZZZZZZZZZ")
print("CONTROL fabricated ->", st2, repr(t2), flush=True)
assert st2 == "dead", "CONTROL FABRICATED FAILED"

# --- screen ---
PORN = re.compile(r"\b(xxx|porn|porno|hentai|call.?girl|escort|brazzers|hookup|sexe|baise|sex(ual)?\s*(home|group|chat|video)?|desi bhabhi|18\+\s*(sex|porn|xxx|nude|hot))\b", re.I)
SCAM = re.compile(r"(airdrop|crypto.?airdrop|binary.?option|paid.?hack|venda de xit|betting|daily.?profit|ai.?trading|invest.{0,20}profit|double.{0,10}(money|cash)|contribute and gain|10 to pack 100k)", re.I)
NEGATED = re.compile(r"(no porn|porn not allowed|proibido.*porn|sem porn|não pode.*porn|nao pode.*porn|pornografia.*proibid|proibido pornografia|sem pornografia)", re.I)

def screen(name, desc, tags=""):
    text = f"{name} {desc} {tags}"
    if NEGATED.search(text):
        return None  # negated prohibition — keep
    if PORN.search(text):
        return "porn/xxx explicit content"
    if SCAM.search(text):
        return "scam pattern"
    return None

candidates, pending, leads, exclusions = [], [], [], []
seen = set()
for e in fresh:
    if e.get("platform", "").lower() != "whatsapp":
        exclusions.append({"code": "", "reason": f"{e.get('platform')} platform, not WhatsApp — '{e.get('name')}' ({e.get('category')}), created {e.get('createdAt')}"})
        continue
    code = extract_code(e.get("inviteLink", ""))
    if not code:
        exclusions.append({"code": "", "reason": f"No WhatsApp invite code in link '{e.get('inviteLink')}' — '{e.get('name')}', created {e.get('createdAt')}"})
        continue
    if code in union or code in seen:
        exclusions.append({"code": code, "reason": f"Already in existing-codes union — '{e.get('name')}', created {e.get('createdAt')}"})
        continue
    seen.add(code)
    name = (e.get("name") or "").strip()
    desc_raw = (e.get("description") or "").strip()
    reason = screen(name, desc_raw, " ".join(e.get("tags") or []))
    if reason:
        exclusions.append({"code": code, "reason": f"{reason} — '{name}' ({e.get('category')}), created {e.get('createdAt')}; dropped on sight, not verified"})
        continue
    st, t, d = check(code)
    time.sleep(1)
    if st == "pending":
        pending.append({"name": name or t, "category": cat_for(e.get("category")), "country": (e.get("country") or "")[:2].upper(), "description": f"Join {name or t}, ...", "invite": f"https://chat.whatsapp.com/{code}"})
        continue
    if st == "dead":
        # spaced retry once before calling dead
        time.sleep(5)
        st2, t2, d2 = check(code)
        if st2 == "pending":
            pending.append({"name": name or t2, "category": cat_for(e.get("category")), "country": (e.get("country") or "")[:2].upper(), "description": f"Join {name or t2}, ...", "invite": f"https://chat.whatsapp.com/{code}"})
            continue
        if st2 == "live":
            st, t, d = st2, t2, d2
        else:
            exclusions.append({"code": code, "reason": f"Dead — empty og:title/og:description on two checks — '{name}', created {e.get('createdAt')}"})
            continue
    # live
    final_name = name or t.strip()
    country = (e.get("country") or "")[:2].upper()
    if len(country) != 2 or not country.isalpha():
        country = ""
    desc = f"Join {final_name}, " + (desc_raw.replace("\n", " ").strip()[:160] if desc_raw else "a WhatsApp group.")
    candidates.append({"name": final_name, "category": cat_for(e.get("category")), "country": country, "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
    print("  LIVE", code, repr(final_name), flush=True)

# leads: none from API-only slice (no listing-page URLs mined)
(WAVE / "team22-groupssor-candidates.json").write_text(json.dumps(candidates, indent=1, ensure_ascii=False))
(WAVE / "team22-groupssor-pending.json").write_text(json.dumps(pending, indent=1, ensure_ascii=False))
(WAVE / "team22-groupssor-leads.json").write_text(json.dumps(leads, indent=1, ensure_ascii=False))
summary = {
    "team": 22,
    "slice": "groupssor API newest poll",
    "sources": [API],
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len([x for x in exclusions if x["reason"].startswith("Dead")]),
    "fresh_entries": len(fresh),
    "api_window": {"newest": newest, "oldest": oldest, "total_returned": len(entries)},
    "exclusions": exclusions,
    "resume": f"Next poll: only entries with createdAt newer than {newest} (newest entry this run). API returns a fixed latest-500; this run's window was {oldest} to {newest}. Cutoff used this run: {CUTOFF}.",
    "notes": "Controls passed: known-live code from groups.json showed og:title; fabricated code showed empty og:title. NOTE: og:description is the generic string 'WhatsApp Group Invite' on both live and dead pages, so LIVE = non-empty og:title ONLY (og:description must NOT be used as fallback). Transport failures go to pending, never counted dead/live.",
}
(WAVE / "team22-groupssor-summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
print(json.dumps(summary, indent=1, ensure_ascii=False))
