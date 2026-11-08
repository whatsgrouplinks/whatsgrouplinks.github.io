#!/usr/bin/env python3
"""Build merge-ready clean outputs for wave 20261106.
- verified_clean: deduped (first team wins, team-number order), schema 6 keys,
  exclusions removed (blocked emojis / phone-PII / borderline sexual names).
- provenance: code -> first team file.
- pending_all: deduped pending (bad 21-char code excluded).
- leads_all: deduped leads by URL.
Prints totals. Writes files incrementally (small writes)."""
import json, os, re, glob

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106")
CATS = set(json.load(open(os.path.join(WAVE, "categories.json"))))
UNION = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
INV_RE = re.compile(r"^https://chat\.whatsapp\.com/(invite/)?[A-Za-z0-9]{22}$")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")
BLOCKED_EMOJI = ["\U0001f346", "\U0001f351", "\U0001f4a6", "\U0001f445", "\U0001f444", "\U0001f48b", "\U0001f51e"]

# coordinator exclusions (code -> reason), derived from validation
EXCLUDE = {
    "KJZepzyDBYhBeYsAncBfxb": "blocked emoji 💋 in name (team14)",
    "D8dlZUexrBhG8euUffZH04": "blocked emoji 💦 in name (team14)",
    "Kh2vAF1lwia8JG4nsYJ7Ri": "blocked emoji 👅 in name (team14)",
    "EhAawChcZdx9hp67vo3gbA": "phone number in name = PII (team15)",
    "ErLrUe6zkGx9KelAWs16Cg": "phone number in name = PII (team15)",
    "G6L2P41O16V3dswTrwZmLz": "blocked emoji 💋 in name (team19)",
    "EMM6yx1z3db712G99kh2sM": "blocked emoji 🔞 in name (team19)",
    "JI8Son6NqGR4AP3HTED650": "blocked emoji 💋 in name (team23)",
    "LOGAaik2rdZEbHr1Xr88Lh": "blocked emoji 💋 in name (team27)",
    "HFZwMiBuuMmEaLLE5bX1EQ": "blocked emoji 💋 in name (team27)",
    "FONKiD1Ny6C3AYV6QmeVqf": "blocked emoji 💋 in name (team27)",
    "IkWEZYUsaeqEuVXsBSuoFp": "blocked emoji 💋 in name (team27)",
    "LEHtMMdY57b9koeVXNGr5Z": "blocked emoji 💦 in name (team35)",
    "Cet480NOxLs6fH0f7tV7wx": "blocked emoji 💋 in name (team35)",
    "IE4W5tFswkuLXKxUgUL2C8": "blocked emoji 💋 in name (team35)",
    "DNlyhn12f6fCq2cB7SfAIC": "borderline sexual name 'femboys - tomboys hornys' (team03, coordinator-excluded)",
    "G5PSXniy1OD4qzPjU0zjzX": "borderline sexual name 'FANTACIAS ESCONDIDAS' (team03, coordinator-excluded)",
}

def load(p):
    with open(p) as f:
        return json.load(f)

def code_of(inv):
    m = CODE_RE.search(inv or "")
    return m.group(1) if m else None

# verified files in team-number order
vfiles = sorted(
    [p for p in glob.glob(os.path.join(WAVE, "team*.json"))
     if "-pending.json" not in p and "-leads.json" not in p],
    key=lambda p: os.path.basename(p))
clean, prov, seen = [], {}, set()
excluded_used = []
for p in vfiles:
    b = os.path.basename(p)
    d = load(p)
    items = list(d.values()) if isinstance(d, dict) else d
    for e in items:
        c = code_of(e.get("invite", ""))
        if not c or c in seen:
            continue
        seen.add(c)
        if c in EXCLUDE:
            excluded_used.append({"code": c, "team": b, "name": e.get("name"), "reason": EXCLUDE[c]})
            continue
        assert INV_RE.match(e["invite"]) and e["category"] in CATS and c not in UNION
        clean.append({k: e[k] for k in ("name", "category", "country", "description", "invite", "image")})
        prov[c] = b

with open(os.path.join(WAVE, "wave_20261106_verified_clean.json"), "w") as f:
    json.dump(clean, f, ensure_ascii=False)
with open(os.path.join(WAVE, "wave_20261106_verified_clean_provenance.json"), "w") as f:
    json.dump(prov, f, indent=1)
with open(os.path.join(WAVE, "wave_20261106_excluded.json"), "w") as f:
    json.dump(excluded_used, f, indent=1, ensure_ascii=False)

# pending: dedupe, drop bad codes
pfiles = sorted(glob.glob(os.path.join(WAVE, "team*-pending.json")))
pend, pseen, bad = [], set(), []
for p in pfiles:
    d = load(p)
    items = list(d.values()) if isinstance(d, dict) else d
    for e in items:
        c = e.get("code") or code_of(e.get("invite", ""))
        if not c or not re.fullmatch(r"[A-Za-z0-9]{22}", c or ""):
            bad.append({"file": os.path.basename(p), "entry": e})
            continue
        if c in pseen:
            continue
        pseen.add(c)
        pend.append({"code": c, "name": e.get("name", ""), "category": e.get("category", ""),
                     "country": e.get("country", ""), "invite": e.get("invite", "")})
with open(os.path.join(WAVE, "wave_20261106_pending_all.json"), "w") as f:
    json.dump(pend, f, ensure_ascii=False)
with open(os.path.join(WAVE, "wave_20261106_pending_bad.json"), "w") as f:
    json.dump(bad, f, indent=1, ensure_ascii=False)

# leads: dedupe by URL
lfiles = sorted(glob.glob(os.path.join(WAVE, "team*-leads.json")))
leads, lseen = [], set()
for p in lfiles:
    d = load(p)
    for e in (d if isinstance(d, list) else []):
        u = (e.get("url") or "").strip()
        if not u or u in lseen:
            continue
        lseen.add(u)
        leads.append({"url": u, "note": e.get("note", "")})
with open(os.path.join(WAVE, "wave_20261106_leads_all.json"), "w") as f:
    json.dump(leads, f, ensure_ascii=False)

print("clean verified:", len(clean))
print("excluded:", len(excluded_used))
print("pending_all:", len(pend), "bad pending entries:", len(bad))
print("leads_all unique URLs:", len(leads))
print("provenance entries:", len(prov))
