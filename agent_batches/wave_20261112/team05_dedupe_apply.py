#!/usr/bin/env python3
"""TEAM05 apply — writes the reviewed clean pass into the final outputs:
 - team05-leads-slice4.json = proposed keeps (943)
 - team05-dedupe-removed.json = the 472 union-dup records (audit trail)
 - team05-casino-flagged.json = kept casino/slots signal-platform groups
   (no sports-betting markers; kept per the task's sports-only betting rule,
   flagged for the coordinator to adjudicate)
 - team05-leads-slice4-summary.json updated (verified count, merged
   exclusions deduped by code, added notes). Pending + leads files untouched.
"""
import json, re, os
from collections import Counter

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"

def code_of(v):
    return re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", v["invite"]).group(1)

def main():
    keeps = json.load(open(os.path.join(WAVE, "team05-proposed-keeps.json")))
    drops = json.load(open(os.path.join(WAVE, "team05-proposed-drops.json")))
    summ = json.load(open(os.path.join(WAVE, "team05-leads-slice4-summary.json")))
    ver_before = json.load(open(os.path.join(WAVE, "team05-leads-slice4.json")))

    # sanity: keeps + drops == previous verified file, disjoint by code
    assert len(keeps) + len(drops) == len(ver_before), (len(keeps), len(drops), len(ver_before))
    assert not (set(map(code_of, keeps)) & {d["code"] for d in drops})
    assert len({code_of(v) for v in keeps}) == len(keeps)

    # audit file: union-removed records (full items)
    union_codes = {d["code"] for d in drops if d["stage"] == "union-dedupe"}
    removed = [v for v in ver_before if code_of(v) in union_codes]
    with open(os.path.join(WAVE, "team05-dedupe-removed.json"), "w", encoding="utf-8") as f:
        json.dump(removed, f, ensure_ascii=False, indent=1)

    # casino/slots gray-zone flag file (kept, no sports markers)
    pat = re.compile(r"plataforma|slots?|tigrinho|fortune|cassino|casino|sinais|banca", re.I)
    flagged = [{"code": code_of(v), "name": v["name"],
                "reason": "kept: casino/slots signal-platform group, no sports-betting markers; coordinator to adjudicate"}
               for v in keeps if pat.search(v["name"] + " " + v["description"])]
    with open(os.path.join(WAVE, "team05-casino-flagged.json"), "w", encoding="utf-8") as f:
        json.dump(flagged, f, ensure_ascii=False, indent=1)

    # write final verified file
    with open(os.path.join(WAVE, "team05-leads-slice4.json"), "w", encoding="utf-8") as f:
        json.dump(keeps, f, ensure_ascii=False, indent=1)

    # merge exclusions (dedupe by code, keep first)
    ex_seen, ex_out = set(), []
    for e in summ["exclusions"]:
        if e["code"] not in ex_seen:
            ex_seen.add(e["code"]); ex_out.append(e)
    for d in drops:
        if d["code"] not in ex_seen:
            ex_seen.add(d["code"])
            ex_out.append({"code": d["code"], "reason": d["reason"]})
    summ["verified"] = len(keeps)
    summ["exclusions"] = ex_out
    summ["notes"] = summ["notes"] + [
        "TEAM05 clean pass (post-finalize): removed 472 codes already in groups.json/.existing_codes.json (Nov 11 10:49 union rebuild merged team04's items; inherited miner/finalize only dedupe at mine time, so carried-over team04 items were stripped here and saved to team05-dedupe-removed.json).",
        "TEAM05 clean pass: dropped 31 more by the task hard screen as proven by the Nov-11 coordinator's team04 exclusions — hentai (1), 18+ sticker/anything-goes/streaming groups (5), sports-betting promos/recruitment incl. palpites/apostas-esportivas/bilhetes/casa-de-aposta/lucro-garantido (25). 4 eFootball tournament/trading groups first flagged by the efootball rule were RESTORED (tournament/account-trading, not betting).",
        "Kept per task false-positive restores: negated-prohibition groups (PROIBIDO PORNOGRAFIA / sem porno / proibido:hentai rules) and 18+ age gates on non-porn groups (alcohol sales, dark/reality-video group). Note: the Nov-11 coordinator screen strips a narrower prohibition set, so it may drop ~5 of these rule-text groups at merge.",
        f"Casino/slots gray zone: {len(flagged)} kept groups are casino/slots signal-platform promos with no sports-betting markers (kept per the task's sports-only betting rule); listed in team05-casino-flagged.json for coordinator adjudication.",
        "Descriptions follow the inherited team04 script convention: the listing's own description text where present, else the 'Join <name>, ...' template. Categories 'Buy Sell'/'Online Earning' per the inherited script mapping (both in the coordinator CANON).",
        "VM rebooted ~08:18 UTC mid-verify of batch 18: 45 mined-but-unverified orphan codes were repaired by team05_repair_orphans.py (19 live, 26 dead, 0 pending) before the miner resumed; no listings were lost.",
        "Controls (06:55 UTC): known-live KrDwdK8EIkB6vgauHg5M7N showed og:title 'JAY - PHP & Python Full Stack Developer' (HTTP 200); fabricated ZZZZZZZZZZZZZZZZZZZZZZ showed empty og:title (HTTP 200).",
    ]
    with open(os.path.join(WAVE, "team05-leads-slice4-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=1)
    print(f"APPLIED verified={len(keeps)} removed_union={len(removed)} "
          f"screen_drops={len(drops)-len(removed)} exclusions_total={len(ex_out)} "
          f"casino_flagged={len(flagged)}")

if __name__ == "__main__":
    main()
