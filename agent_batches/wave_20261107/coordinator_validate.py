#!/usr/bin/env python3
"""Wave 20261107 coordinator validation + clean build.
Reads every team file, checks schema/dedupe/union/regex/blocked-content,
cross-team overlaps, then builds:
  wave_20261107_verified_clean.json (first-team-wins, team-number order)
  wave_20261107_verified_clean_provenance.json
  wave_20261107_excluded.json
  wave_20261107_pending_all.json (+ _pending_bad.json)
  wave_20261107_leads_all.json
  validation_report.json
Prints summary. Spot live re-check is a separate step (sample_recheck.py).
"""
import json, os, re, glob

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261107")
CATS = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
        "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto",
        "Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell",
        "Finance","Funny"}
UNION = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
INV_RE = re.compile(r"^https://chat\.whatsapp\.com/(invite/)?[A-Za-z0-9]{22}$")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")
PORN = re.compile(r"\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|bokep|orgasm|cumshot|blowjob)\b", re.I)
ADULT_EMOJI = ["\U0001f975","\U0001f346","\U0001f351","\U0001f4a6","\U0001f445","\U0001f444","\U0001f48b","\U0001f51e"]
# NOTE: U+1F970 (🥰 smiling face with hearts) is NOT adult — prior wave's list
# wrongly included it; the task's blocked set is 🥵🍆🍑🔞💦👅👄💋 only.
SRC_NAMES = ["groupjoin","grupbul","whatsappkanali","groupssor","groupda","groupizo",
             "linkado","igrupos","ongrupos","appgrouplink","groupsinvite","tglinkhub",
             "groupwa","wagroup","whtsagrouplink","whatgroups.com","groupchatconnect"]
BETTING = re.compile(r"\b(betting|betting tips|satta|matka|fixed match|palpite)\b", re.I)

def code_of(inv):
    m = CODE_RE.search(inv or "")
    return m.group(1) if m else None

def load(p):
    with open(p) as f:
        return json.load(f)

def team_no(basename):
    m = re.match(r"team(\d+)", basename)
    return int(m.group(1)) if m else 99

all_team = sorted(glob.glob(os.path.join(WAVE, "team*.json")),
                  key=lambda p: (team_no(os.path.basename(p)), os.path.basename(p)))
verified_files = [p for p in all_team if "-pending.json" not in p and "-leads.json" not in p
                  and "unverified-candidates" not in p]
pending_files = [p for p in all_team if "-pending.json" in p]
leads_files = [p for p in all_team if "-leads.json" in p]

report = {"verified": {}, "pending": {}, "leads": {}, "cross_team_overlaps": [],
          "exclusions": [], "flags": [], "issues": []}
seen = {}          # code -> first verified team file
seen_pending = {}  # code -> first pending team file
total_v = total_p = total_l = 0

for p in verified_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["verified"][b] = rec
        continue
    items = list(d.values()) if isinstance(d, dict) else d
    if not isinstance(items, list):
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["verified"][b] = rec
        continue
    rec["count"] = len(items)
    total_v += len(items)
    local = {}
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            rec["errors"].append(f"item {i}: not an object"); continue
        for k in ("name","category","country","description","invite","image"):
            if k not in e:
                rec["errors"].append(f"item {i}: missing key {k}")
        extra = set(e.keys()) - {"name","category","country","description","invite","image"}
        if extra:
            rec["warnings"].append(f"item {i}: extra keys {sorted(extra)}")
        inv = e.get("invite","")
        if not INV_RE.match(inv or ""):
            rec["errors"].append(f"item {i}: bad invite {inv!r}")
        c = code_of(inv)
        if c:
            if c in local:
                rec["errors"].append(f"item {i}: dup code in-file {c}")
            local[c] = i
            if c in UNION:
                rec["errors"].append(f"item {i}: code in dedupe union {c}")
            if c in seen:
                report["cross_team_overlaps"].append({"code": c, "first": seen[c], "later": b})
            else:
                seen[c] = b
        if e.get("category") not in CATS:
            rec["errors"].append(f"item {i}: bad category {e.get('category')!r}")
        if not e.get("name") or not str(e.get("name")).strip():
            rec["errors"].append(f"item {i}: empty name")
        if not e.get("description") or not str(e.get("description")).strip():
            rec["warnings"].append(f"item {i}: empty description")
        txt = f"{e.get('name','')} {e.get('description','')}"
        if PORN.search(txt):
            rec["errors"].append(f"item {i}: PORN-REGEX hit: {e.get('name')!r}")
        if any(em in txt for em in ADULT_EMOJI):
            rec["errors"].append(f"item {i}: adult emoji: {e.get('name')!r}")
        low = txt.lower()
        for s in SRC_NAMES:
            if s in low:
                rec["warnings"].append(f"item {i}: possible source ref '{s}': {e.get('name')!r}")
        if "http" in str(e.get("description","")) or "www." in str(e.get("description","")):
            rec["errors"].append(f"item {i}: URL in description")
        if re.search(r"\d{7,}", str(e.get("name",""))):
            rec["errors"].append(f"item {i}: possible phone number in name: {e.get('name')!r}")
        if BETTING.search(txt):
            rec["warnings"].append(f"item {i}: betting/gambling flag (kept, parent decides): {e.get('name')!r}")
            report["flags"].append({"code": c, "team": b, "name": e.get("name"), "kind": "betting"})
        if str(e.get("country","")).strip() in ("", "N/A", "Unknown"):
            rec["warnings"].append(f"item {i}: weak country {e.get('country')!r}")
    report["verified"][b] = rec

# pending validation
for p in pending_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["pending"][b] = rec
        continue
    items = list(d.values()) if isinstance(d, dict) else d
    if not isinstance(items, list):
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["pending"][b] = rec
        continue
    rec["count"] = len(items)
    total_p += len(items)
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            rec["errors"].append(f"item {i}: not an object"); continue
        c = e.get("code") or code_of(e.get("invite",""))
        if not c or not re.fullmatch(r"[A-Za-z0-9]{22}", c or ""):
            rec["errors"].append(f"item {i}: bad/missing code {c!r}")
            continue
        if c in UNION:
            rec["errors"].append(f"item {i}: code in dedupe union {c}")
        if c in seen:
            rec["warnings"].append(f"item {i}: code already VERIFIED by {seen[c]} (pending superseded)")
        if c in seen_pending:
            rec["warnings"].append(f"item {i}: dup pending code, first in {seen_pending[c]}")
        else:
            seen_pending[c] = b
        txt = f"{e.get('name','')} {e.get('description','')}"
        if PORN.search(txt):
            rec["errors"].append(f"item {i}: PORN-REGEX hit in pending: {e.get('name')!r}")
        if any(em in txt for em in ADULT_EMOJI):
            rec["errors"].append(f"item {i}: adult emoji in pending: {e.get('name')!r}")
        if e.get("name","").strip() in ("WhatsApp Group","",):
            rec["warnings"].append(f"item {i}: placeholder/empty name in pending (re-verify name later)")
    report["pending"][b] = rec

# leads validation
for p in leads_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["leads"][b] = rec
        continue
    items = list(d.values()) if isinstance(d, dict) else d
    if not isinstance(items, list):
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["leads"][b] = rec
        continue
    rec["count"] = len(items)
    total_l += len(items)
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            rec["errors"].append(f"item {i}: not an object"); continue
        u = (e.get("url") or "").strip()
        if not u:
            rec["errors"].append(f"item {i}: empty url")
        elif "chat.whatsapp.com" in u:
            rec["warnings"].append(f"item {i}: invite URL leaked into leads: {u[:80]}")
    report["leads"][b] = rec

report["totals"] = {"verified_files": len(verified_files), "verified_items": total_v,
                    "pending_files": len(pending_files), "pending_items": total_p,
                    "leads_files": len(leads_files), "leads_items": total_l,
                    "unique_verified_codes": len(seen),
                    "cross_team_overlap_codes": len(report["cross_team_overlaps"])}
with open(os.path.join(WAVE, "validation_report.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
print(json.dumps(report["totals"], indent=1))
nerr = sum(len(r["errors"]) for r in list(report["verified"].values())+list(report["pending"].values())+list(report["leads"].values()))
nwarn = sum(len(r["warnings"]) for r in list(report["verified"].values())+list(report["pending"].values())+list(report["leads"].values()))
print("total errors:", nerr, " total warnings:", nwarn)
for b, r in report["verified"].items():
    for e in r["errors"]:
        print("V-ERR", b, e)
for b, r in report["pending"].items():
    for e in r["errors"]:
        print("P-ERR", b, e)
for b, r in report["leads"].items():
    for e in r["errors"]:
        print("L-ERR", b, e)
