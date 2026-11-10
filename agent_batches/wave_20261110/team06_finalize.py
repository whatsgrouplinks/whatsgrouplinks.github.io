#!/usr/bin/env python3
"""TEAM 06 wave 20261110 slice 6: build the 4 output files from verify results."""
import json, re, os, html

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
ALLOWED_CATS = {"Entertainment", "Jobs", "Education", "Islamic", "Sports",
                "Community & Social", "Finance", "Funny", "Buy Sell", "Health",
                "News", "Gaming", "Technology", "Business"}

ver = json.load(open(os.path.join(BASE, "team06-verify.json")))
ext = {r["code"]: r for r in json.load(open(os.path.join(BASE, "team06-extracted.json")))}
leads_in = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_06.json"))
disc = json.load(open(os.path.join(BASE, "team06-discovered-leads.json")))

ADULT_RE = re.compile(r'(\U0001F51E|\U0001F975|\U0001F346|\U0001F351|\U0001F4A6|sexy|sexual|\bsex\b|porn|xxx|nude|naked|escort|hookup|erotic|call\s*girl|callgirl|adult|18\+|18 plus|hot\s*sex|viral leak|leak.{0,12}(video|videos|mms|scandal))', re.I)
SCAM_RE = re.compile(r'(b[\s\-]?love|blove|forsage|shey(i|y)\b|airdrop|paypal\s*loader|bitfinex|counterfeit\s*currency|carding|crypto[ -]?doubling|double\s*(your|the)\s*(money|bitcoin|btc|crypto|usdt)|money[ -]?doubling|double\s*income)', re.I)

def clean_name(n):
    if not n:
        return None
    n = html.unescape(n)
    n = re.sub(r'https?://\S+', '', n)
    n = re.sub(r'\s+', ' ', n).strip(" \t\r\n-–—:|·•\"'“”‘’")
    if len(n) < 2 or len(n) > 90:
        return None
    if not re.search(r'[A-Za-z]', n):
        return None
    if n.lower() in {"join group", "join", "whatsapp group", "whatsapp", ".", "group"}:
        return None
    return n

verified = []
exclusions = list(ver.get("exclusions_prescreen", []))
for code, r in ver["live"].items():
    rec = ext.get(code, {})
    title = clean_name(r.get("title"))
    listed = clean_name(rec.get("name"))
    # og:title is WhatsApp ground truth for the group name: prefer it when usable.
    # Fall back to the directory listing name only when og:title is junk/missing.
    name = title or listed
    if not name:
        exclusions.append({"code": code, "reason": "live but no usable name (og:title junk)"})
        continue
    if ADULT_RE.search(name) or ADULT_RE.search(title or ""):
        exclusions.append({"code": code, "reason": f"post-verify adult screen: name={name!r} og:title={title!r}"})
        continue
    if SCAM_RE.search(name) or SCAM_RE.search(title or ""):
        exclusions.append({"code": code, "reason": f"post-verify scam screen: name={name!r} og:title={title!r}"})
        continue
    cat = rec.get("category") or "Community & Social"
    if cat not in ALLOWED_CATS:
        cat = "Community & Social"
    country = rec.get("country") or "International"
    if not re.fullmatch(r'[A-Z]{2}', country or ""):
        country = "International"
    desc = f"Join {name}, a WhatsApp group to chat, share updates and connect with members."
    verified.append({"name": name, "category": cat, "country": country,
                     "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})

# dedupe verified by code (defensive)
seen = set()
uniq = []
for v in verified:
    c = v["invite"].rsplit("/", 1)[-1]
    if c in seen:
        continue
    seen.add(c)
    uniq.append(v)
verified = uniq

pending = [{"code": code, "invite": f"https://chat.whatsapp.com/{code}",
            "reason": (r.get("transport_error") or f"HTTP {r.get('http')} transport failure"),
            "http": r.get("http"), "attempts": 3}
           for code, r in ver["pending"].items()]

# leads: discovered listing URLs, minus input URLs
input_urls = {html.unescape(x["url"]) for x in leads_in}
leads_out = [d for d in disc if d["url"] not in input_urls]
seen_u = set()
ld = []
for d in leads_out:
    if d["url"] in seen_u:
        continue
    seen_u.add(d["url"])
    ld.append(d)
leads_out = ld

json.dump(verified, open(os.path.join(BASE, "team06-leads-slice6.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(BASE, "team06-leads-slice6-pending.json"), "w"), indent=1, ensure_ascii=False)
json.dump(leads_out, open(os.path.join(BASE, "team06-leads-slice6-leads.json"), "w"), indent=1, ensure_ascii=False)

from collections import Counter
srcs = sorted({html.unescape(x.get("source", "")) for x in leads_in if x.get("source")})
summary = {
    "team": 6,
    "slice": "leads slice 6",
    "sources": srcs,
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads_out),
    "dead": len(ver["dead"]),
    "exclusions": exclusions,
    "resume": "Wave 20261110 slice 6 complete. Re-fetched all 184 wave_20261109 slice-6 listing pages; fresh codes = extracted minus 108,365-code union (.existing_codes.json + groups.json invites). Verified live via curl og:title. Next wave: re-fetch team06-leads-slice6-leads.json discovered listing URLs plus the same 184 slice pages for newly added groups.",
    "notes": (
        f"Fetched 184 listing pages; extracted {len(ext)} unique invite codes; "
        f"fresh vs union: {len(ver['live']) + len(ver['dead']) + len(ver['pending'])} candidates verified "
        f"(live {len(ver['live'])}, dead {len(ver['dead'])} empty og:title after retries, pending {len(ver['pending'])} transport-only). "
        f"Post-verify screening dropped {len(exclusions) - len(ver.get('exclusions_prescreen', []))} live items; "
        f"prescreen dropped {len(ver.get('exclusions_prescreen', []))}. "
        f"Verified file holds {len(verified)} clean items. "
        f"Category/country inherited from listing page; descriptions are plain generic lines with no source name/link and no personal info. "
        f"Verification: curl browser UA, max 3 parallel, >=0.5s start spacing, 15s timeout; LIVE = HTTP 200 + non-empty og:title."
    ),
}
json.dump(summary, open(os.path.join(BASE, "team06-leads-slice6-summary.json"), "w"), indent=1, ensure_ascii=False)
print("verified:", len(verified), "pending:", len(pending), "leads:", len(leads_out),
      "dead:", len(ver["dead"]), "exclusions:", len(exclusions))
print("categories:", Counter(v["category"] for v in verified))
print("countries:", Counter(v["country"] for v in verified).most_common(10))
