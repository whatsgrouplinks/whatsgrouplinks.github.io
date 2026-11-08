#!/usr/bin/env python3
"""Wave 20261106 coordinator validation. Reads every canonical team file,
checks schema/dedupe/union/regex/blocked-content, cross-team overlaps.
Writes validation_report.json (chunked) + prints summary."""
import json, os, re, glob, sys

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106")
CATS = set(json.load(open(os.path.join(WAVE, "categories.json"))))
UNION = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
INV_RE = re.compile(r"^https://chat\.whatsapp\.com/(invite/)?[A-Za-z0-9]{22}$")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")
PORN = re.compile(r"porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob", re.I)
ADULT_EMOJI = ["\U0001f970", "\U0001f346", "\U0001f351", "\U0001f4a6", "\U0001f445", "\U0001f444", "\U0001f48b", "\U0001f51e"]

def code_of(inv):
    m = CODE_RE.search(inv or "")
    return m.group(1) if m else None

def load(p):
    with open(p) as f:
        return json.load(f)

# canonical verified files: teamNN-<slice>.json, excluding -pending/-leads and coordinator inputs
all_team = sorted(glob.glob(os.path.join(WAVE, "team*.json")))
verified_files, pending_files, leads_files = [], [], []
for p in all_team:
    b = os.path.basename(p)
    if "-pending.json" in b:
        pending_files.append(p)
    elif "-leads.json" in b:
        leads_files.append(p)
    else:
        verified_files.append(p)

report = {"verified": {}, "pending": {}, "leads": {}, "cross_team": {}, "issues": []}
seen = {}  # code -> first team file
total_v = total_p = total_l = 0
overlap_pairs = []

for p in verified_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["verified"][b] = rec
        continue
    if isinstance(d, dict):
        # some teams wrote dicts; normalize to list of values
        items = list(d.values())
        rec["warnings"].append("file is a dict, normalized to values")
    elif isinstance(d, list):
        items = d
    else:
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["verified"][b] = rec
        continue
    rec["count"] = len(items)
    total_v += len(items)
    local = {}
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            rec["errors"].append(f"item {i}: not an object")
            continue
        for k in ("name", "category", "country", "description", "invite", "image"):
            if k not in e:
                rec["errors"].append(f"item {i}: missing key {k}")
        inv = e.get("invite", "")
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
                overlap_pairs.append((c, seen[c], b))
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
            rec["warnings"].append(f"item {i}: PORN-REGEX hit in name/desc: {e.get('name')!r}")
        if any(em in txt for em in ADULT_EMOJI):
            rec["warnings"].append(f"item {i}: adult emoji in name/desc: {e.get('name')!r}")
        for f in ("name", "description"):
            v = str(e.get(f, ""))
            if "http" in v or "groupjoin" in v.lower() or "grupbul" in v.lower() or "whatsappkanali" in v.lower() or "groupssor" in v.lower():
                rec["warnings"].append(f"item {i}: possible source ref in {f}: {v[:80]!r}")
        if re.search(r"\d{7,}", str(e.get("name", ""))):
            rec["warnings"].append(f"item {i}: possible phone number in name: {e.get('name')!r}")
    report["verified"][b] = rec

for p in pending_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["pending"][b] = rec
        continue
    items = list(d.values()) if isinstance(d, dict) else (d if isinstance(d, list) else None)
    if items is None:
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["pending"][b] = rec
        continue
    rec["count"] = len(items)
    total_p += len(items)
    local = set()
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            rec["errors"].append(f"item {i}: not an object")
            continue
        c = e.get("code") or code_of(e.get("invite", ""))
        if not c or not re.fullmatch(r"[A-Za-z0-9]{22}", c or ""):
            rec["errors"].append(f"item {i}: bad code {c!r}")
        if c in local:
            rec["errors"].append(f"item {i}: dup code in-file {c}")
        local.add(c)
        if c in UNION:
            rec["warnings"].append(f"item {i}: code in dedupe union {c}")
    report["pending"][b] = rec

for p in leads_files:
    b = os.path.basename(p)
    rec = {"file": b, "count": 0, "errors": [], "warnings": []}
    try:
        d = load(p)
    except Exception as e:
        rec["errors"].append(f"UNPARSEABLE: {e}")
        report["leads"][b] = rec
        continue
    items = d if isinstance(d, list) else None
    if items is None:
        rec["errors"].append(f"unexpected top-level type {type(d).__name__}")
        report["leads"][b] = rec
        continue
    rec["count"] = len(items)
    total_l += len(items)
    for i, e in enumerate(items):
        if not isinstance(e, dict) or not e.get("url"):
            rec["errors"].append(f"item {i}: bad lead {e!r}")
    report["leads"][b] = rec

report["cross_team"] = {
    "unique_verified_codes": len(seen),
    "overlap_count": len(overlap_pairs),
    "overlaps": [{"code": c, "first": a, "dup_in": b} for c, a, b in overlap_pairs[:200]],
}
report["totals"] = {"verified_file_sum": total_v, "unique_verified": len(seen),
                    "pending_total": total_p, "leads_total": total_l,
                    "verified_files": len(verified_files), "pending_files": len(pending_files),
                    "leads_files": len(leads_files)}

# stray files check
for p in sorted(glob.glob(os.path.join(WAVE, "*"))):
    b = os.path.basename(p)
    if b.startswith("team") and b.endswith(".json") and b not in [os.path.basename(x) for x in verified_files + pending_files + leads_files]:
        report["issues"].append(f"unclassified team file: {b} size={os.path.getsize(p)}")
    if os.path.getsize(p) == 0:
        report["issues"].append(f"ZERO-BYTE file: {b}")

with open(os.path.join(WAVE, "validation_report.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)

print("VERIFIED files:", len(verified_files), "file-sum:", total_v, "unique:", len(seen), "overlaps:", len(overlap_pairs))
print("PENDING total:", total_p, "files:", len(pending_files))
print("LEADS total:", total_l, "files:", len(leads_files))
print("--- per-file verified counts ---")
for b, r in sorted(report["verified"].items()):
    flag = f" ERRORS={len(r['errors'])}" if r["errors"] else ""
    warn = f" warnings={len(r['warnings'])}" if r["warnings"] else ""
    print(f"{b}: {r['count']}{flag}{warn}")
print("--- errors detail ---")
for b, r in sorted(report["verified"].items()):
    for e in r["errors"][:10]:
        print(b, "::", e)
print("--- pending/leads errors ---")
for sec in ("pending", "leads"):
    for b, r in sorted(report[sec].items()):
        for e in r["errors"][:5]:
            print(sec, b, "::", e)
print("--- overlaps (first 20) ---")
for o in report["cross_team"]["overlaps"][:20]:
    print(o)
print("--- issues ---")
for i in report["issues"]:
    print(i)
print("--- warnings sample (porn/adult-emoji/source-ref, max 40) ---")
n = 0
for b, r in sorted(report["verified"].items()):
    for w in r["warnings"]:
        if "PORN" in w or "adult emoji" in w or "source ref" in w or "phone" in w:
            print(b, "::", w)
            n += 1
            if n >= 40:
                break
    if n >= 40:
        break
