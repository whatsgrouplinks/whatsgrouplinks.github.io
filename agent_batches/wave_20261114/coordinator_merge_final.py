#!/usr/bin/env python3
"""Wave 20261114 FINAL consolidation (coordinator).
Merges Part A clean (637) + all 30 Part B team candidate files into
wave_20261114_clean.json, plus pending_all / leads_all / excluded.json,
manifest data (manifest_table.json) and a validation report.
Dedupe order: union -> Part A clean -> Part A excluded -> cross-team.
Merge drops are coordinator adjudications (see MERGE_DROPS).
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

union = set(json.load(open(f"{BASE}/.existing_codes.json")))
partA_clean = json.load(open(f"{W14}/partA_clean.json"))
partA_excl = json.load(open(f"{W14}/partA_excluded.json"))
partA_clean_codes = {code_of(i["invite"]) for i in partA_clean}
partA_excl_codes = {e["code"] for e in partA_excl}

# --- coordinator adjudication drops (code -> reason) ---
MERGE_DROPS = {
    "C516urnVfHg4P6yjwbKcR2": "merge-drop: live og:title sexualized 'Chicas con senos' (team13 kept per doubt rule; dropped per wave13 team01 precedent on sexualized live titles)",
    "J3piQqaXAdhA5wPKetGVMw": "merge-drop: 'Exemplo' — directory test listing, no real group identity (team09 flagged)",
    "GT1ysM3lNwCA5GHPQeQtIy": "merge-drop: 'guaranteed investment' wording — guaranteed-returns investment pitch = free-money scam (team04 flagged)",
    "HIhIXMu1HjX7UojAK9W1w5": "merge-drop: 'GRUPO HACKEADO' — hacked-content group (team03 flagged; cf. wave14 team04 hacking-service exclusion)",
    "HSaFF1Gi3IF7gdcEEOawZN": "merge-drop: 'Lançamentos plataforma' — casino-platform promo phrasing in a casino-saturated linkado slice (team03 flagged)",
    "CkFWiYl4T29H7vTGUxfh0D": "merge-drop: bare 'Plataforma' in Finance in a casino-saturated linkado slice — casino-platform promo (team03 flagged)",
    "FfMen8t7ySDHpgbboLswIq": "merge-drop: bare 'Jogos' in Finance category — betting (team03 flagged)",
    "CxtLPVfzMwPAQnApYvRrDY": "merge-drop: 'GRUPO JOGOS' in Finance category — betting (team03 flagged)",
    "HYYdA8kMuje1irthS3ik17": "merge-drop: 'ÁGUIA PLAY' in Finance/Dinheiro category — casino-platform pattern (team03 flagged)",
    "KByTwCwllZdFZQxVfEjKq0": "merge-drop: 'Grupo hormonal' sexual euphemism — dropped by wave13 team11 and wave14 team06 under doubt-rule; team24's keep overruled (2 teams vs 1)",
}
# recategorization
RECATEGORIZE = {"JzWs9w4vi5F0VKkxMcbnxb": "Earning"}  # team27 Cointiply Business -> Earning

# --- load team candidates in team order (team22 lives in subdir) ---
team_cands = {}
for n in range(1, 31):
    tag = f"team{n:02d}"
    p = f"{W14}/{tag}-candidates.json"
    if not os.path.exists(p):
        p = f"{W14}/{tag}/{tag}-candidates.json"
    team_cands[tag] = json.load(open(p))
print("team candidate counts:", {t: len(v) for t, v in team_cands.items()})

clean = list(partA_clean)
clean_codes = set(partA_clean_codes)
stats = collections.Counter()
excluded = list(partA_excl)
excl_codes = set(partA_excl_codes)
per_team = {}
for tag in sorted(team_cands):
    items = team_cands[tag]
    kept = dup_union = dup_partA = dup_cross = dup_excl = dropped = 0
    for item in items:
        c = code_of(item["invite"])
        if c in union:
            dup_union += 1; stats["partB_union_dup"] += 1
            excluded.append({"code": c, "reason": "already in .existing_codes.json union (found in Part B re-check)",
                             "source": tag, "name": item.get("name", "")})
            excl_codes.add(c)
        elif c in partA_clean_codes:
            dup_partA += 1; stats["partB_partA_dup"] += 1
        elif c in partA_excl_codes:
            dup_excl += 1; stats["partB_partA_excluded"] += 1
            excluded.append({"code": c, "reason": "already excluded in Part A consolidation — " +
                             next(e["reason"] for e in partA_excl if e["code"] == c),
                             "source": tag, "name": item.get("name", "")})
        elif c in clean_codes:
            dup_cross += 1; stats["partB_cross_team_dup"] += 1
        elif c in MERGE_DROPS:
            dropped += 1; stats["merge_drops"] += 1
            excluded.append({"code": c, "reason": MERGE_DROPS[c], "source": tag, "name": item.get("name", "")})
            excl_codes.add(c)
        else:
            if c in RECATEGORIZE:
                item = dict(item); item["category"] = RECATEGORIZE[c]
                stats["recategorized"] += 1
            clean.append(item); clean_codes.add(c); kept += 1
    per_team[tag] = {"candidates_file": len(items), "kept": kept, "dup_union": dup_union,
                     "dup_partA_clean": dup_partA, "dup_partA_excluded": dup_excl,
                     "dup_cross_team": dup_cross, "merge_dropped": dropped}
    print(tag, per_team[tag])

print("clean total:", len(clean), "stats:", dict(stats))

# --- keyword screen over merged clean (report hits; do NOT auto-drop) ---
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
        r"\b1xbet\b", r"linebet", r"mellbet", r"melbet", r"blaze\s*(aposta|bet|slot)?",
        r"roleta", r"\bbet365\b", r"\bbet\b", r"\bbets\b", r"lucky\s*101",
        r"darazzmall", r"\bkwai\b.*referral|referral.*\bkwai\b"]
hits = []
for item in clean:
    txt = norm(item.get("name", "") + " | " + item.get("description", ""))
    for pat in PORN + SCAM:
        if re.search(pat, txt):
            hits.append({"code": code_of(item["invite"]), "name": item.get("name", ""),
                         "category": item.get("category", ""), "pattern": pat})
            break
print(f"KEYWORD SCREEN HITS on merged clean: {len(hits)}")
for h in hits:
    print("  HIT", h["code"], "|", h["name"][:70], "|", h["category"], "|", h["pattern"])

# --- schema validation ---
errors = []
seen = set()
for item in clean:
    c = code_of(item["invite"])
    if c in seen: errors.append(f"dup code {c}")
    seen.add(c)
    for k in ("name", "category", "country", "description", "invite"):
        if k not in item or not isinstance(item[k], str):
            errors.append(f"{c}: missing/non-string {k}")
    if not item.get("name", "").strip(): errors.append(f"{c}: empty name")
    if not item.get("description", "").strip(): errors.append(f"{c}: empty description")
    if item.get("invite", "") != "https://chat.whatsapp.com/" + c:
        errors.append(f"{c}: invite mismatch")
    if c in union: errors.append(f"{c}: UNION LEAK")
    cc = item.get("country", "")
    if cc and (len(cc) != 2 or not cc.isalpha() or cc != cc.upper()):
        errors.append(f"{c}: bad country {cc!r}")
print("SCHEMA ERRORS:", len(errors))
for e in errors[:20]: print("  ", e)

json.dump(clean, open(f"{W14}/wave_20261114_clean.json", "w"), indent=1, ensure_ascii=False)
json.dump({"per_team": per_team, "stats": dict(stats), "screen_hits": hits,
           "schema_errors": errors, "clean_total": len(clean)},
          open(f"{W14}/merge_report.json", "w"), indent=1, ensure_ascii=False)
# stash excluded-so-far for the pending/leads step
json.dump(excluded, open(f"{W14}/_merge_excluded_stage1.json", "w"), indent=1, ensure_ascii=False)
print("WROTE wave_20261114_clean.json:", len(clean))
