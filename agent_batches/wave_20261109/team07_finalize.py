#!/usr/bin/env python3
"""Team07 phase 5: build candidates / pending / leads / summary from verify results."""
import json, re, os, html
from collections import Counter

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
ALLOWED = ["Gaming", "Education", "Online Earning", "Community & Social", "Business",
           "Friendship", "Finance", "Buy Sell", "Islamic", "Entertainment", "Jobs",
           "Technology", "Funny", "Sports", "Health", "News"]

recs = {r["code"]: r for r in json.load(open(os.path.join(WAVE, "team07_screened.json")))}
verify = {}
for line in open(os.path.join(WAVE, "team07_verify.jsonl"), encoding="utf-8"):
    try:
        v = json.loads(line)
        verify[v["code"]] = v
    except Exception:
        pass
# retries file (if present) overrides
rp = os.path.join(WAVE, "team07_verify_retry.jsonl")
if os.path.exists(rp):
    for line in open(rp, encoding="utf-8"):
        try:
            v = json.loads(line)
            if v.get("og_title"):
                verify[v["code"]] = v
            else:
                # keep latest attempt record
                verify[v["code"]] = v
        except Exception:
            pass

PROHIB = re.compile(r"[^.!?\n]*(?:na karein|not allowed|prohibit|no (?:porn|sex|adult|nude|xxx)|don't share|do not share|strictly prohibited|forbidden)[^.!?\n]*[.!?\n]?", re.I)
DROP_PATTERNS = [
    (r"\bporn\b", "porn"), (r"\bpr0n\b", "porn"), (r"\bxxx\b", "xxx"), (r"\bx+xx\b", "xxx"),
    (r"\bs3x\b", "sex"), (r"\bsex\b", "sex"), (r"s\*x", "sex"),
    (r"sexting", "sexting"), (r"sex chat", "sex chat"), (r"sex video", "sex video"),
    (r"\bhookup\b", "hookup"), (r"hook up", "hookup"),
    (r"\bescort\b", "escort"), (r"cam ?girl", "cam-girl"), (r"\bsexy\b", "sexy"),
    (r"video call.{0,15}girl", "cam-girl"), (r"\bhorny\b", "horny"),
    (r"\bnudes?\b", "nudes"), (r"onlyfans", "onlyfans"),
    (r"adult video", "adult video"), (r"adult group", "adult group"),
    (r"masturbat", "masturbation"), (r"friends with benefits", "fwb"),
    (r"b-?love", "b-love scam"), (r"forsage", "forsage scam"), (r"\bsheyi\b", "sheyi scam"),
    (r"free money", "free-money scam"), (r"double your (money|investment)", "doubling scam"),
    (r"claim (your )?free", "free-claim scam"), (r"\bairdrop\b.{0,30}(free|earn|claim)", "airdrop scam"),
]
DROP_RE = [(re.compile(p, re.I), label) for p, label in DROP_PATTERNS]

def clean_name(s):
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]

PHONE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")

candidates, pending, dead_list = [], [], []
drop_reasons = Counter()
for code, r in recs.items():
    v = verify.get(code)
    if not v:
        pending.append({"code": code, "reason": "not checked (verifier incomplete)", "name": r.get("name", ""), "src": r.get("src", "")})
        continue
    if v.get("transport_error") or v.get("http") == "000":
        pending.append({"code": code, "reason": f"transport failure http={v.get('http')}", "name": r.get("name", ""), "src": r.get("src", "")})
        continue
    if v.get("http") != "200":
        dead_list.append(code)
        continue
    title = clean_name(v.get("og_title", ""))
    if not title:
        dead_list.append(code)  # ambiguous, retries still empty
        continue
    name = title or clean_name(r.get("name", ""))
    desc = clean_name(r.get("description", "")) or clean_name(v.get("og_desc", ""))
    if desc in ("WhatsApp Group Invite", ""):
        desc = ""
    # screen on og:title + listing name/desc
    text = f"{title} {r.get('name','')} {r.get('description','')} {v.get('og_desc','')}"
    hit = None
    for rx, label in DROP_RE:
        if rx.search(PROHIB.sub(" ", text)):
            hit = label
            break
    if hit:
        drop_reasons[hit] += 1
        dead_list.append(code)
        continue
    if PHONE.search(name) or PHONE.search(desc):
        # strip phone numbers from description; drop if name is a phone number
        desc = PHONE.sub("", desc).strip()
        if PHONE.fullmatch(name.strip()):
            drop_reasons["phone-in-name"] += 1
            dead_list.append(code)
            continue
    if not name:
        name = "WhatsApp Group"
    if not desc:
        desc = f"Join this {r.get('category','Community & Social')} WhatsApp group to connect, share and chat with members."
    cat = r.get("category") if r.get("category") in ALLOWED else "Community & Social"
    candidates.append({"name": name, "category": cat, "country": (r.get("country") or "IN")[:2].upper(),
                       "description": desc[:300], "invite": f"https://chat.whatsapp.com/{code}"})

print(f"candidates={len(candidates)} pending={len(pending)} dead/screen-dropped={len(dead_list)}")
print("post-verify drops:", dict(drop_reasons))
print("by category:", dict(Counter(c["category"] for c in candidates)))
json.dump(candidates, open(os.path.join(WAVE, "team07-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(WAVE, "team07-pending.json"), "w"), indent=1, ensure_ascii=False)

# ---- leads ----
raw = json.load(open(os.path.join(WAVE, "team07_leads_raw.json")))
leads_in = json.load(open(os.path.join(WAVE, "leads_slice_07.json")))
lead_list = []
def add_lead(url, source, note):
    lead_list.append({"url": url, "source": source, "note": note})
for u in raw["appgrouplink"]:
    add_lead(u, "appgrouplink post-sitemap", "listing post from sitemap — fetch for invites")
for u in raw["groupizo"]:
    add_lead(u, "groupizo sitemap-groups-12", "group page from sitemap — fetch for invite")
for u in raw["grupbul"]:
    add_lead(u, "grupbul detail page", "NEEDS-BROWSER-LEG — invite behind /redirect interstitial")
for u in raw["igrupos_nocode"]:
    add_lead(u, "igrupos detail page", "NEEDS-BROWSER-LEG — no invite code in fetched HTML")
for e in leads_in:
    if "groupda.com" in e["url"]:
        add_lead(e["url"], "groupda.com (slice 07)", "NEEDS-BROWSER-LEG — Cloudflare 403 via curl; text fetch yields no invite codes")
# dedupe leads by url
seen = set(); uniq = []
for l in lead_list:
    if l["url"] not in seen:
        seen.add(l["url"]); uniq.append(l)
json.dump(uniq, open(os.path.join(WAVE, "team07-leads.json"), "w"), indent=1, ensure_ascii=False)
print(f"leads={len(uniq)}")

summary = {
    "team": "07",
    "slice": "leads_slice_07.json (184 listing URLs)",
    "sources": dict(Counter(e["source"] for e in leads_in)),
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(uniq),
    "dead": len(dead_list),
    "notes": [
        "groupda.com: all 38 post URLs + category sitemap returned Cloudflare 403 via curl; browser text fetch yields no invite codes — banked as NEEDS-BROWSER-LEG leads.",
        "groupsinvite: 2 category pages initially 000, refetched OK (200) before extraction.",
        "groupjoin.link adult-tagged pages (Adult/Sexchat/Sexting/Sex-vc/Naughty/Horny/Masturbation/Friends-with-benefits) screened out at name/description stage; og:title re-screened post-verify incl. leetspeak (s3x).",
        "ongrupos invite codes come from /grupo/<code> detail URLs; titles taken from card headings.",
        "groupsinvite invite codes come from /group/link/<code>/ card URLs with name/category/country/description from the card.",
        "igrupos detail pages fetched via curl (254 IDs, 145 yielded codes); 108 detail pages with no code banked as leads.",
        "grupbul invite behind /redirect interstitial — 32 detail pages banked as leads.",
        "WhatsApp verify: HTTP 200 with empty og:title treated as AMBIGUOUS per spec; ONE full retry round over all 1,821 ambiguous codes (spaced apart from pass 1) recovered 0 titles, plus 2 manual spaced re-checks also stayed empty — still-empty marked dead. (Spec allows up to 2 retry rounds; the second was not run because the retry round recovered zero of 1,821 and manual spaced re-checks were also stable-empty.)",
        "Betting groups kept per spec; girls/friendship groups kept.",
    ],
}
json.dump(summary, open(os.path.join(WAVE, "team07-summary.json"), "w"), indent=1, ensure_ascii=False)
print("summary written")
