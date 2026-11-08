#!/usr/bin/env python3
"""Build merge-ready clean outputs for wave 20261107.
- verified_clean: deduped first-team-wins (team-number order), 6 keys only.
- provenance, excluded (cross-team dups), pending_all, pending_bad, leads_all.
Defensive re-checks: porn word-boundary regex, adult emoji (task set only),
phone PII, URL in description, union leak, invite regex, canonical category.
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

def load(p):
    with open(p) as f:
        return json.load(f)

def code_of(inv):
    m = CODE_RE.search(inv or "")
    return m.group(1) if m else None

def team_no(basename):
    m = re.match(r"team(\d+)", basename)
    return int(m.group(1)) if m else 99

vfiles = sorted([p for p in glob.glob(os.path.join(WAVE, "team*.json"))
                 if "-pending.json" not in p and "-leads.json" not in p
                 and "unverified-candidates" not in p],
                key=lambda p: (team_no(os.path.basename(p)), os.path.basename(p)))
clean, prov, seen = [], {}, set()
excluded = []
for p in vfiles:
    b = os.path.basename(p)
    d = load(p)
    items = list(d.values()) if isinstance(d, dict) else d
    for e in items:
        c = code_of(e.get("invite", ""))
        if not c:
            excluded.append({"code": None, "team": b, "name": e.get("name"), "reason": "no extractable 22-char code"})
            continue
        if c in seen:
            excluded.append({"code": c, "team": b, "name": e.get("name"),
                             "reason": f"cross-team duplicate, first in {prov[c]}"})
            continue
        seen.add(c)
        txt = f"{e.get('name','')} {e.get('description','')}"
        reason = None
        if not INV_RE.match(e.get("invite","")): reason = "bad invite regex"
        elif c in UNION: reason = "code in dedupe union"
        elif e.get("category") not in CATS: reason = f"bad category {e.get('category')!r}"
        elif PORN.search(txt): reason = "porn-regex hit"
        elif any(em in txt for em in ADULT_EMOJI): reason = "adult emoji"
        elif re.search(r"\d{7,}", str(e.get("name",""))): reason = "possible phone number in name"
        elif "http" in str(e.get("description","")) or "www." in str(e.get("description","")): reason = "URL in description"
        elif not str(e.get("name","")).strip(): reason = "empty name"
        if reason:
            excluded.append({"code": c, "team": b, "name": e.get("name"), "reason": reason})
            continue
        clean.append({k: e[k] for k in ("name","category","country","description","invite","image")})
        prov[c] = b

with open(os.path.join(WAVE, "wave_20261107_verified_clean.json"), "w") as f:
    json.dump(clean, f, ensure_ascii=False)
with open(os.path.join(WAVE, "wave_20261107_verified_clean_provenance.json"), "w") as f:
    json.dump(prov, f, indent=1)
with open(os.path.join(WAVE, "wave_20261107_excluded.json"), "w") as f:
    json.dump(excluded, f, indent=1, ensure_ascii=False)

# pending: dedupe, drop bad/union/verified-superseded codes
pfiles = sorted(glob.glob(os.path.join(WAVE, "team*-pending.json")),
                key=lambda p: (team_no(os.path.basename(p)), os.path.basename(p)))
pend, pseen, bad = [], set(), []
for p in pfiles:
    b = os.path.basename(p)
    d = load(p)
    items = list(d.values()) if isinstance(d, dict) else d
    for e in items:
        c = e.get("code") or code_of(e.get("invite",""))
        if not c or not re.fullmatch(r"[A-Za-z0-9]{22}", c or ""):
            bad.append({"file": b, "entry": e}); continue
        if c in UNION:
            bad.append({"file": b, "entry": e, "reason": "code in dedupe union"}); continue
        if c in seen:
            bad.append({"file": b, "entry": e, "reason": f"already verified by {prov[c]}"}); continue
        if c in pseen:
            continue
        pseen.add(c)
        txt = f"{e.get('name','')} {e.get('description','')}"
        if PORN.search(txt) or any(em in txt for em in ADULT_EMOJI):
            bad.append({"file": b, "entry": e, "reason": "blocked content in pending"}); continue
        pend.append({k: e.get(k, "") for k in ("name","category","country","description","invite","image")})
with open(os.path.join(WAVE, "wave_20261107_pending_all.json"), "w") as f:
    json.dump(pend, f, ensure_ascii=False)
with open(os.path.join(WAVE, "wave_20261107_pending_bad.json"), "w") as f:
    json.dump(bad, f, indent=1, ensure_ascii=False)

# leads: dedupe by URL, drop empty + leaked invite URLs
lfiles = sorted(glob.glob(os.path.join(WAVE, "team*-leads.json")),
                key=lambda p: (team_no(os.path.basename(p)), os.path.basename(p)))
leads, lseen, ldropped = [], set(), []
for p in lfiles:
    b = os.path.basename(p)
    d = load(p)
    for e in (d if isinstance(d, list) else []):
        u = (e.get("url") or "").strip()
        if not u:
            ldropped.append({"file": b, "entry": e, "reason": "empty url"}); continue
        if "chat.whatsapp.com" in u:
            ldropped.append({"file": b, "entry": e, "reason": "invite URL leaked into leads"}); continue
        if u in lseen:
            continue
        lseen.add(u)
        leads.append({"url": u, "what": e.get("what","") or e.get("note",""), "source_team": b})
with open(os.path.join(WAVE, "wave_20261107_leads_all.json"), "w") as f:
    json.dump(leads, f, ensure_ascii=False)
with open(os.path.join(WAVE, "wave_20261107_leads_dropped.json"), "w") as f:
    json.dump(ldropped, f, indent=1, ensure_ascii=False)

print("clean verified:", len(clean))
print("excluded:", len(excluded))
print("pending_all:", len(pend), "pending_bad:", len(bad))
print("leads_all unique URLs:", len(leads), "leads_dropped:", len(ldropped))
print("provenance entries:", len(prov))
# per-team kept counts
from collections import Counter
print("kept per team:", dict(sorted(Counter(prov.values()).items())))
