#!/usr/bin/env python3
"""Wave 20261114 Part A consolidation (coordinator).
Inputs: wave_20261113/team*-candidates.json (825 items, 656 unique codes),
        wave_20261112/team01-stream-verified.json (377 items),
        wave_20261113/team01-summary.json (excluded list w/ live-title reasons),
        coordinator spot-verification: wave_20261114/coordinator_spot_verify.json
        .existing_codes.json (union, 119,266)
Rules applied:
 - drop 12 contested codes (team01 excluded on live og:title; team32/team05
   re-added them without screening) — spot-verified 12/12, titles match.
 - drop 7 casino/slots codes team05 kept (spot-verified live titles +
   one description revealing 'slot Tiger'); keep 1 flagged coupons group
   (negated 'NAO E GRUPO DE APOSTAS').
 - drop all stream-file codes already in the union (162) + team01's 43
   content/dead exclusions (31 not re-mined anywhere; 12 = contested).
 - cross-team dedupe: prefer team01 copy, then lowest team number.
Outputs: partA_clean.json, partA_excluded.json, partA_report.json
"""
import json, glob, os, collections

BASE = "/home/hatch/workspace/whatsapp-groups-site"
W13 = f"{BASE}/agent_batches/wave_20261113"
W12 = f"{BASE}/agent_batches/wave_20261112"
W14 = f"{BASE}/agent_batches/wave_20261114"

def code(inv):
    return inv.rstrip("/").split("/")[-1]

union = set(json.load(open(f"{BASE}/.existing_codes.json")))

CONTESTED = {
    "B946Y1yIg5AEOcMqgUO3Ox": "investment/broker money-making scheme (live title 'ULTIMATEBROKER MONEY MAKING PLATFORM')",
    "Csopw2EvxtiKKqUQqZM7xl": "betting tips (live title 'JW TIPS FREE')",
    "EGCKrvzt3Nq5JnsVKlI6Tx": "'leaked videos' group (live title 'Videos vazado')",
    "EmGgfrPNWSWB4wjPlnBSi1": "sexualized 'Hot Viral video' (live title)",
    "Fu2xzLH9EisDq7x4VmVYaT": "sexualized 'Baddies' with tongue/lips emoji (live title)",
    "HMif2lSTJhGAHEyO9d06zt": "betting tips group (stored name 'Esportes da Sorte - Tips'; live title is meaningless 'A')",
    "J0hBoywknE86GcSpKWO754": "explicit 18+ videos (live title 'Hot videos18')",
    "JEBd4Lb3h5A4sM6ewq76pr": "group closed (live title 'GRUPO ENCERRADO')",
    "JqlWadz7x1ZJM0PkDfoE6k": "porn/sexual 'Grupo de sacanagem' (live title)",
    "K6O64hjoeX3II7ZdDXjZYe": "betting (live title 'Dicas e apostas esportivas')",
    "KhXj8RYbOqnLikUft3PrNJ": "sexualized 'Only Girls' with biting-lip emoji (live title)",
    "LwwGKw8BzZW9KKbwMnetCI": "money-doubling scam (live title 'PIX INFINITO')",
}
CASINO_TEAM05 = {
    "I3BHBegFrp80rshSi3bJNi": "slots/casino (live title 'SLOT DO MARIO')",
    "FdX8dhBUX9u3yUjHA6yoyk": "betting (live title 'BET NETWORK')",
    "K7GLDAb3MB47gA0VxwnNxc": "slots/casino (live title 'SLOTS DA SORTE')",
    "Hdm6R4YF4s04tPzOp120Jo": "slots/casino (live title 'Ronaldo galan slots pagano muito')",
    "HaCZIssURNE0zn3uNXhqKZ": "Tigrinho-variant casino (live title 'Trigre ganhos altos')",
    "IH48Tm3GwYgGXQWLgFVvke": "slots/casino (live title 'GGSLOTS 2')",
    "Cw03HFIMlRNGVoxvhxNTJF": "Fortune Tiger slots (description: 'grupo slot Tiger')",
}

# --- load wave13 candidates, cross-team dedupe (team01 first, then lowest team no.)
team_files = sorted(glob.glob(f"{W13}/team*-candidates.json"),
                    key=lambda p: int(os.path.basename(p).split("-")[0][4:]))
best = {}   # code -> (team, item)
dup_instances = 0
raw_total = 0
for f in team_files:
    team = os.path.basename(f).split("-")[0]
    for item in json.load(open(f)):
        raw_total += 1
        c = code(item["invite"])
        if c in best:
            dup_instances += 1
            continue
        best[c] = (team, item)
print(f"wave13 raw={raw_total} unique={len(best)} dup_instances={dup_instances}")

excluded = []  # {code, reason, source, name}
clean = []
for c, (team, item) in best.items():
    if c in CONTESTED:
        excluded.append({"code": c, "reason": "contested: team01 excluded on live og:title; team32/team05 re-added unscreened — " + CONTESTED[c],
                         "source": team, "name": item.get("name", "")})
    elif c in CASINO_TEAM05:
        excluded.append({"code": c, "reason": "casino/slots (coordinator spot-verified live title) — " + CASINO_TEAM05[c],
                         "source": team, "name": item.get("name", "")})
    elif c in union:
        excluded.append({"code": c, "reason": "already in .existing_codes.json union",
                         "source": team, "name": item.get("name", "")})
    else:
        clean.append(item)

# --- stream file: account for every code (must be 0 unaccounted)
stream = json.load(open(f"{W12}/team01-stream-verified.json"))
t01sum = json.load(open(f"{W13}/team01-summary.json"))
t01_excl = {e["code"]: e["reason"] for e in t01sum.get("excluded", [])}
stream_codes = {code(i["invite"]) for i in stream}
wave13_codes = set(best)
stream_accounted = {"in_wave13_clean": 0, "in_wave13_excluded": 0, "team01_excluded_only": 0, "unaccounted": []}
for c in stream_codes:
    if c in wave13_codes:
        if any(e["code"] == c for e in excluded):
            stream_accounted["in_wave13_excluded"] += 1
        else:
            stream_accounted["in_wave13_clean"] += 1
    elif c in t01_excl:
        stream_accounted["team01_excluded_only"] += 1
        if c not in union:
            excluded.append({"code": c, "reason": "team01 stream re-verification exclusion — " + t01_excl[c],
                             "source": "team01-stream", "name": next((i.get("name", "") for i in stream if code(i["invite"]) == c), "")})
    else:
        stream_accounted["unaccounted"].append(c)
# union-dup stream codes that never appeared in wave13 candidates (team01 dropped them)
for c in stream_codes:
    if c in union and c not in wave13_codes and c not in {e["code"] for e in excluded}:
        excluded.append({"code": c, "reason": "already in .existing_codes.json union (stream file, dropped by team01 re-verification)",
                         "source": "team01-stream", "name": next((i.get("name", "") for i in stream if code(i["invite"]) == c), "")})
print("stream accounting:", stream_accounted)

# --- schema validation on clean set
errors = []
seen = set()
for item in clean:
    c = code(item["invite"])
    if c in seen:
        errors.append(f"dup code {c}")
    seen.add(c)
    for k in ("name", "category", "country", "description", "invite"):
        if k not in item or not isinstance(item[k], str):
            errors.append(f"{c}: missing/non-string {k}")
    if not item.get("name", "").strip():
        errors.append(f"{c}: empty name")
    if item.get("invite", "") != "https://chat.whatsapp.com/" + c:
        errors.append(f"{c}: invite mismatch")
    if c in union:
        errors.append(f"{c}: UNION LEAK")
    cc = item.get("country", "")
    if cc and (len(cc) != 2 or not cc.isalpha() or cc != cc.upper()):
        errors.append(f"{c}: bad country {cc!r}")

json.dump(clean, open(f"{W14}/partA_clean.json", "w"), indent=1, ensure_ascii=False)
json.dump(excluded, open(f"{W14}/partA_excluded.json", "w"), indent=1, ensure_ascii=False)
report = {
    "wave13_raw_items": raw_total,
    "wave13_unique_codes": len(best),
    "wave13_cross_team_dup_instances": dup_instances,
    "wave13_in_union": sum(1 for c in best if c in union),
    "contested_excluded": len(CONTESTED),
    "casino_team05_excluded": len(CASINO_TEAM05),
    "partA_clean": len(clean),
    "partA_excluded_total": len(excluded),
    "stream_total": len(stream),
    "stream_accounting": stream_accounted,
    "schema_errors": errors,
    "union_leaks_in_clean": sum(1 for it in clean if code(it["invite"]) in union),
}
json.dump(report, open(f"{W14}/partA_report.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(report, indent=1))
