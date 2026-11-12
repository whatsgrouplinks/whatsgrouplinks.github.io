"""Build the 4 output files from the current extraction + verify-state snapshots.
No network. Unverified candidates go to team02-awaiting-verification.json (not banked)."""
import json, os, sys, importlib.util
WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
spec=importlib.util.spec_from_file_location("tb", WAVE+"team02_build.py")
tb=importlib.util.module_from_spec(spec); spec.loader.exec_module(tb)
existing=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
slice_urls=json.load(open(WAVE+"leads_slice2.json"))
recs=[]
with open(WAVE+"team02-extracted.jsonl") as f:
    for line in f:
        try: recs.append(json.loads(line))
        except: pass
ok=[r for r in recs if 'error' not in r]
mined_urls={r["url"] for r in ok}
fetch_fail=[r["url"] for r in recs if 'error' in r]
state=json.load(open(WAVE+"team02-verify-state.json")) if os.path.exists(WAVE+"team02-verify-state.json") else {}
seen=set(); cands=[]; dup_existing=0; dup_within=0; no_code=0; exclusions=[]
for r in ok:
    codes=r.get("codes") or []
    if not codes: no_code+=1; continue
    for code in codes:
        if code in existing: dup_existing+=1; continue
        if code in seen: dup_within+=1; continue
        seen.add(code)
        name=tb.clean_name(r.get("name",""))
        if not name:
            exclusions.append({"code":code,"reason":"empty name after cleaning"}); continue
        cat=tb.CATMAP.get((r.get("cat_raw") or "").strip(), "Community & Social")
        reason=tb.screen(name, r.get("desc") or "")
        if reason:
            exclusions.append({"code":code,"reason":reason}); continue
        desc=f"Join the '{name}' WhatsApp group for {cat} — chat with members, share updates and connect."
        cands.append({"name":name,"category":cat,"country":"BR","description":desc[:200],
                      "invite":f"https://chat.whatsapp.com/{code}","_code":code})
verified=[]; pending=[]; awaiting=[]; dead=0
for c in cands:
    st=state.get(c["_code"],{}).get("status")
    cc={k:v for k,v in c.items() if k!="_code"}
    if st=="live": verified.append(cc)
    elif st=="pending":
        cc["reason"]="transport failure: no WhatsApp page after retries"; pending.append(cc)
    elif st=="dead": dead+=1
    else: awaiting.append(cc)
remaining=[u for u in slice_urls if u not in mined_urls]
json.dump(verified, open(WAVE+"team02-leads-slice2.json","w"), ensure_ascii=False, indent=1)
json.dump(pending, open(WAVE+"team02-leads-slice2-pending.json","w"), ensure_ascii=False, indent=1)
json.dump(remaining, open(WAVE+"team02-leads-slice2-leads.json","w"), ensure_ascii=False, indent=1)
json.dump(awaiting, open(WAVE+"team02-awaiting-verification.json","w"), ensure_ascii=False, indent=1)
summary={"team":"02","slice":"leads_slice2","sources":["linkado.app grupo pages"],
  "verified":len(verified),"pending":len(pending),"leads":len(remaining),"dead":dead,
  "dup_existing":dup_existing,"dup_within":dup_within,"no_code_listings":no_code,
  "fetch_fail_listings":len(fetch_fail),"awaiting_verification":len(awaiting),
  "exclusions":exclusions,
  "resume":f"mined {len(mined_urls)}/{len(slice_urls)} listing pages (checkpoint team02-extracted.jsonl, {len(recs)} records); verify-state has {len(state)} codes in team02-verify-state.json; {len(awaiting)} mined candidates await WhatsApp verification in team02-awaiting-verification.json; next unmined listing URLs in team02-leads-slice2-leads.json. To resume: re-run team02_mine2.py (skips mined URLs) then team02_build.py (reuses verify-state, verifies only new/pending codes).",
  "notes":"WhatsApp live-check = curl chat.whatsapp.com/<code>, LIVE iff HTTP 200 + non-empty og:title, one spaced retry on empty og; empty og after retry = DEAD; no WhatsApp page after retries = pending (transport failure). Early control test: 3 provably-bogus codes also returned HTTP 200 + empty og:title (correctly dead), while genuine listing codes DO return non-empty og:title when live (12 live in pilot of 60) — the rule discriminates. Do NOT re-check via browser.open on chat.whatsapp.com (403 upstream). Categories mapped from Portuguese linkado categories; country BR (Brazilian platform); descriptions generated from name/category. Screening strips negated-prohibition clauses (e.g. 'nao pode enviar pornografia', 'sem putaria', '🚫pornografia') before the porn/betting/crypto-airdrop screen, so rule-posting groups are kept."}
json.dump(summary, open(WAVE+"team02-leads-slice2-summary.json","w"), ensure_ascii=False, indent=1)
print(f"FINALIZE verified {len(verified)} pending {len(pending)} leads {len(remaining)} dead {dead} awaiting {len(awaiting)} mined {len(mined_urls)}/{len(slice_urls)} exclusions {len(exclusions)}")
