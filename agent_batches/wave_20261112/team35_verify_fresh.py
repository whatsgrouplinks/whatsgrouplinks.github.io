import json, time, sys
sys.path.insert(0, ".")
from team35_verify import check

PRE_DROP = {
 "HzDnHRm7AXk4vIxlTVgBx9": "listing name 'WhatsApp group link adult' - adult/porn group",
 "I0dw4oL00D37D1gAyHexdA": "listing name 'WhatsApp group Aunty' - desi aunty sexual-content group",
 "Dmod5JgezT41oDDFd6vz3L": "listing name 'Pakistan leaked Video WhatsApp group links' - leaked-video porn",
 "FCovP6jEPeWAZfZNeVo0dM": "listing name 'WhatsApp join group 18+' - 18+ sexual group",
 "BEXEViUjuEZDrnrmIbLzMP": "listing name 'Pakistani WhatsApp sexy group community' - sexual content",
 "BRPiBfbYotm3HGCgF1FcE8": "listing name 'Pakistani WhatsApp sexy group community' - sexual content",
 "LmKcttmdcCzDzfqVTsvJcR": "listing name 'Pakistani WhatsApp sexy group community' - sexual content",
 "DrhPtk5b7Sq8HE8eoCyDVK": "listing name 'Pakistani WhatsApp sexy group community' - sexual content",
 "DSQnzTptzcl8aTty4DfgSR": "listing name 'Pakistani WhatsApp sexy group community' - sexual content",
 "D959Ymn0360CSqmMkz0HHl": "listing name 'Leaked viral video WhatsApp group' - leaked-video porn",
 "IQfccLQOC6o8EOFye3ZLcC": "listing name 'Leaked Videos WhatsApp Group Links' - leaked-video porn",
}
rows = [json.loads(l) for l in open("team35_fresh.jsonl")]
todo = [r for r in rows if r["code"] not in PRE_DROP]
print(f"fresh={len(rows)} pre-dropped={len(PRE_DROP)} to-verify={len(todo)}")
results = []
with open("team35_verify_progress.jsonl", "w") as f:
    for i, r in enumerate(todo):
        status, http, title = check(r["code"])
        if status == "transport":
            time.sleep(15)
            status, http, title = check(r["code"])
        rec = {**r, "status": status, "http": http, "og_title": title}
        results.append(rec)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
        print(f"[{i+1}/{len(todo)}] {r['code']} {status} {http} {title[:60]}")
        time.sleep(1.5)
json.dump({"pre_dropped": PRE_DROP}, open("team35_predrop.json", "w"), ensure_ascii=False)
live = [r for r in results if r["status"] == "live"]
dead = [r for r in results if r["status"] == "dead"]
pend = [r for r in results if r["status"] == "transport"]
print(f"LIVE={len(live)} DEAD={len(dead)} PENDING={len(pend)}")
