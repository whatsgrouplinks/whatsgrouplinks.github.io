#!/usr/bin/env python3
"""Filter groupssor API fresh codes to South Asia + pre-screen hard porn/betting/airdrop."""
import json, re

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
fresh = json.load(open(f"{WD}/team23_groupssor_fresh.json"))

SA = {"IN", "PK", "BD", "LK", "NP"}
PORN = re.compile(r"(?i)\b(sex|porn|xxx|xx\b|nude|nudes|bhabhi\s*sex|video\s*call\s*girl|phone\s*sex|live\s*sex|hot\s*girl|sexy|fuck|desi\s*mom|gujarati.*sex|rekha.*sex|priya.*sex|pooja.*sex|punjabi.*sex|college.*sex|adult|erotic|boobs|pussy|dick|blowjob|masturbat|webcam\s*sex|escort|call\s*girl|sexting|leak\s*video|viral\s*leak|cp\s*video|child)\b")
BET = re.compile(r"(?i)\b(satta|1xbet|1x\s*bet|betting|casino|slot|aviator|tigrinho|fortune\s*tiger|sinais|plataformas\s*pagantes|wjbet|khaiwal|10\s*ka\s*9[05]0|10\s*ke\s*9[05]0)\b")
SCAM = re.compile(r"(?i)\b(airdrop|free\s*money|binance\s*millionaire|double\s*your|earn\s*\$\d|investment\s*platform|forex\s*signals?.*free|gold\s*trading\s*edge|treasure\s*nft)\b")

kept, excluded = {}, []
for code, d in fresh.items():
    name = (d.get("name") or "").strip()
    country = d.get("country") or ""
    reason = None
    if country not in SA:
        reason = f"non-SA country {country}"
    elif PORN.search(name):
        reason = "porn/xxx by directory name"
    elif BET.search(name):
        reason = "betting/casino by directory name"
    elif SCAM.search(name):
        reason = "crypto-airdrop/free-money scam by directory name"
    if reason:
        excluded.append({"code": code, "name": name, "country": country, "reason": reason, "source": "groupssor.com API"})
    else:
        kept[code] = d

print("SA kept:", len(kept), "excluded:", len(excluded))
for c, d in kept.items():
    print("KEEP", c, "|", d.get("name"), "|", d.get("category"), "|", d.get("country"))
json.dump(kept, open(f"{WD}/team23_groupssor_sa.json", "w"), ensure_ascii=False, indent=1)
json.dump(excluded, open(f"{WD}/team23_groupssor_excluded.json", "w"), ensure_ascii=False, indent=1)
