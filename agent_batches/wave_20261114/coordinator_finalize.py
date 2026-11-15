#!/usr/bin/env python3
"""Wave 20261114 FINALIZE (coordinator).
- Removes 4 final-screen drops from wave_20261114_clean.json (2164 -> 2160).
- Re-runs keyword + de-spaced screens; re-validates schema.
- Builds wave_20261114_pending_all.json, wave_20261114_leads_all.json,
  wave_20261114_excluded.json (Part A + all team excluded lists + drops).
- Writes finalize_report.json + manifest_table.json (per-team table).
"""
import json, glob, os, re, unicodedata, collections

BASE = "/home/hatch/workspace/whatsapp-groups-site"
W14 = f"{BASE}/agent_batches/wave_20261114"

def code_of(inv):
    return inv.rstrip("/").split("/")[-1]

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def despace(s):
    # collapse "G H O S T B E T" style spaced letters
    return re.sub(r"(?<=[a-z])\s+(?=[a-z](\s|$))", "", s)

union = set(json.load(open(f"{BASE}/.existing_codes.json")))
clean = json.load(open(f"{W14}/wave_20261114_clean.json"))
stage1_excl = json.load(open(f"{W14}/_merge_excluded_stage1.json"))

FINAL_DROPS = {
    "J3piQqaXAdhA5wPKetGVMw": "final screen: 'Exemplo' — directory test listing, no real group identity (coordinator; team09 flagged, found in Part A clean)",
    "CtQAkW75l298Pq4g5gREm9": "final screen: description is Chinese casino-houses + roulette promo ('BAU E ROLETA DE 100 VEM FATURAR') (coordinator; Part A item)",
    "CbZlXX0nQNH3lfFhDwX1aa": "final screen: 'Pagol.bet Insiders' — betting-site promo group (coordinator; Part A item)",
    "CKzkMugEOJp6dT1ZQ38BTz": "final screen: 'Forsage' — crypto-pyramid scam group (coordinator; team30 item)",
}
excluded = list(stage1_excl)
excl_codes = {e["code"] for e in excluded}
final_clean = []
for item in clean:
    c = code_of(item["invite"])
    if c in FINAL_DROPS:
        excluded.append({"code": c, "reason": FINAL_DROPS[c], "source": "coordinator-final-screen",
                         "name": item.get("name", "")})
        excl_codes.add(c)
    else:
        final_clean.append(item)
print(f"clean after final drops: {len(final_clean)} (removed {len(clean)-len(final_clean)})")

# --- screens on final clean ---
PORN = [r"porn", r"\bxxx\b", r"onlyfans", r"\bnudes?\b", r"sacanagem", r"putaria",
        r"vazad[oa]", r"leak(ed|s)?\s*(video|photo|vid)", r"hot\s*(video|girl|babe)",
        r"chudai", r"figurinhas?\s*18", r"cabare", r"no sigilo", r"\bbaddies\b",
        r"sex\s*(video|chat|call|girl)", r"سكس", r"porno", r"videos?\s*18\+?",
        r"18\+\s*(video|sticker|figurinha)", r"nekopoi"]
SCAM = [r"tigrinho", r"fortune\s*tiger", r"\bsinais\b", r"plataformas?\s*pagantes",
        r"\bwjbet\b", r"\bslots?\b", r"\bcassino\b", r"\bcasino\b", r"\bbetting\b",
        r"\baposta", r"\bpalpite", r"pix\s*infinito", r"money\s*doubling",
        r"money\s*making\s*platform", r"ultimatebroker", r"binary\s*option",
        r"crypto\s*airdrop", r"free\s*money", r"carding", r"forsage",
        r"\bsatta\b", r"\bmatka\b", r"\bkhaiwal\b", r"guaranteed\s*investment",
        r"\b1xbet\b", r"linebet", r"mellbet", r"melbet", r"roleta", r"\bbet365\b",
        r"\bbet\b", r"\bbets\b", r"lucky\s*101", r"darazzmall"]
hits, despaced_hits = [], []
for item in final_clean:
    txt = norm(item.get("name", "") + " | " + item.get("description", ""))
    for pat in PORN + SCAM:
        if re.search(pat, txt):
            hits.append({"code": code_of(item["invite"]), "name": item.get("name", ""), "pattern": pat})
            break
    txt2 = despace(txt)
    for pat in [r"bet", r"slots?", r"casino", r"cassino", r"porn", r"xxx"]:
        if re.search(pat, txt2) and not any(h["code"] == code_of(item["invite"]) for h in hits):
            despaced_hits.append({"code": code_of(item["invite"]), "name": item.get("name", ""), "pattern": "despaced:" + pat})
            break
print("screen hits on final clean:", hits)
print("de-spaced extra hits:", despaced_hits)

# --- schema validation ---
errors = []
seen = set()
clean_codes = set()
for item in final_clean:
    c = code_of(item["invite"])
    if c in seen: errors.append(f"dup code {c}")
    seen.add(c); clean_codes.add(c)
    for k in ("name", "category", "country", "description", "invite"):
        if k not in item or not isinstance(item[k], str): errors.append(f"{c}: missing/non-string {k}")
    if not item.get("name", "").strip(): errors.append(f"{c}: empty name")
    if not item.get("description", "").strip(): errors.append(f"{c}: empty description")
    if item.get("invite", "") != "https://chat.whatsapp.com/" + c: errors.append(f"{c}: invite mismatch")
    if c in union: errors.append(f"{c}: UNION LEAK")
    cc = item.get("country", "")
    if cc and (len(cc) != 2 or not cc.isalpha() or cc != cc.upper()): errors.append(f"{c}: bad country {cc!r}")
print("schema errors:", errors)

# --- pending_all ---
def pending_path(tag):
    p = f"{W14}/{tag}-pending.json"
    return p if os.path.exists(p) else f"{W14}/{tag}/{tag}-pending.json"
pending, pend_seen, pend_dropped = [], set(), collections.Counter()
for n in range(1, 31):
    tag = f"team{n:02d}"
    for e in json.load(open(pending_path(tag))):
        if isinstance(e, dict):
            c = e.get("code") or (code_of(e["invite"]) if e.get("invite") else None)
            if not c:
                continue
            rec = {"code": c, "reason": e.get("reason", ""), "team": tag}
            for k in ("name", "listing", "source", "invite"):
                if e.get(k): rec[k] = e[k]
        elif isinstance(e, str):
            c = e.strip()
            rec = {"code": c, "reason": "", "team": tag}
        else:
            continue
        if c in pend_seen:
            pend_dropped["dup_across_teams"] += 1; continue
        if c in clean_codes:
            pend_dropped["already_in_clean"] += 1; continue
        if c in union:
            pend_dropped["in_union"] += 1; continue
        if c in excl_codes:
            pend_dropped["already_excluded"] += 1; continue
        pend_seen.add(c); pending.append(rec)
print(f"pending_all: {len(pending)} (dropped {dict(pend_dropped)})")

# --- leads_all ---
def leads_path(tag):
    p = f"{W14}/{tag}-leads.json"
    return p if os.path.exists(p) else f"{W14}/{tag}/{tag}-leads.json"
def lead_key(e):
    if isinstance(e, str): return ("s", e.strip())
    if isinstance(e, dict):
        for k in ("value", "detail_url", "url"):
            if e.get(k): return ("u", str(e[k]).strip())
        if e.get("invite"): return ("c", code_of(e["invite"]))
        if e.get("code"): return ("c", e["code"])
        return ("j", json.dumps(e, sort_keys=True, ensure_ascii=False))
    return ("j", json.dumps(e, sort_keys=True, ensure_ascii=False))
leads, lead_seen, lead_dropped = [], set(), collections.Counter()
for n in range(1, 31):
    tag = f"team{n:02d}"
    for e in json.load(open(leads_path(tag))):
        k = lead_key(e)
        if k in lead_seen:
            lead_dropped["dup_across_teams"] += 1; continue
        if k[0] == "c":
            if k[1] in clean_codes:
                lead_dropped["code_already_in_clean"] += 1; continue
            if k[1] in union:
                lead_dropped["code_in_union"] += 1; continue
            if k[1] in excl_codes:
                lead_dropped["code_already_excluded"] += 1; continue
        lead_seen.add(k); leads.append(e)
print(f"leads_all: {len(leads)} (dropped {dict(lead_dropped)})")

# --- excluded final: stage1 + team summaries + extra files + final drops (already in) ---
def add_excl(code, reason, source, name=""):
    if not code or code in excl_codes:
        return False
    excluded.append({"code": code, "reason": reason, "source": source, "name": name})
    excl_codes.add(code)
    return True
n_added = 0
for f in sorted(glob.glob(f"{W14}/team*-summary.json")):
    tag = os.path.basename(f).split("-")[0]
    s = json.load(open(f))
    ex = s.get("excluded")
    if isinstance(ex, list):
        for e in ex:
            if isinstance(e, dict) and e.get("code"):
                if add_excl(e["code"], e.get("reason", ""), tag, e.get("name", "") or e.get("og_title", "")):
                    n_added += 1
# extra excluded files
for f in sorted(glob.glob(f"{W14}/team*-excluded.json") + glob.glob(f"{W14}/team*-exclusions.json")):
    tag = os.path.basename(f).split("-")[0]
    for e in json.load(open(f)):
        if isinstance(e, dict) and e.get("code"):
            if add_excl(e["code"], e.get("reason", ""), tag, e.get("name", "") or e.get("og_title", "")):
                n_added += 1
print(f"excluded: stage1 {len(stage1_excl)} + summaries/files {n_added} + final drops in stage1? -> total {len(excluded)}")

json.dump(final_clean, open(f"{W14}/wave_20261114_clean.json", "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(f"{W14}/wave_20261114_pending_all.json", "w"), indent=1, ensure_ascii=False)
json.dump(leads, open(f"{W14}/wave_20261114_leads_all.json", "w"), indent=1, ensure_ascii=False)
json.dump(excluded, open(f"{W14}/wave_20261114_excluded.json", "w"), indent=1, ensure_ascii=False)
report = {
    "clean_total": len(final_clean),
    "pending_total": len(pending),
    "pending_dropped": dict(pend_dropped),
    "leads_total": len(leads),
    "leads_dropped": dict(lead_dropped),
    "excluded_total": len(excluded),
    "final_drops": list(FINAL_DROPS.keys()),
    "screen_hits_final": hits,
    "despaced_hits_final": despaced_hits,
    "schema_errors": errors,
    "union_leaks": sum(1 for it in final_clean if code_of(it["invite"]) in union),
}
json.dump(report, open(f"{W14}/finalize_report.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(report, indent=1))
os.remove(f"{W14}/_merge_excluded_stage1.json")
print("DONE")
