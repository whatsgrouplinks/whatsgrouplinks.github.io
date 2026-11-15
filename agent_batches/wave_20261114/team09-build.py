import json, re
WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
res=json.load(open(f"{WAVE}/team09-verify-results.json"))
assert len(res)==80, len(res)

CATMAP={"Amizade":"Community & Social","Namoro":"Community & Social","Links":"Community & Social",
        "Religião":"Community & Social","Comprar e venda":"Buy Sell","Dinheiro":"Finance",
        "Trabalho":"Jobs","Tecnologia":"Technology","Esportes":"Sports","Games":"Gaming"}

# decisions: code -> (verdict, reason) ; verdict in keep/exclude ; dead handled by status
EXCLUDE={
 "BQSo4FsUIqTAvfmQiEJ4mA":("betting: live title 'CAMBISTA RAFAEL' (bookmaker/tout); dir desc betting tips"),
 "BXkhIXYcySlBBU59StsbVL":("betting: live title 'Aposta Esportivas #1'"),
 "BcI9w95fxnE8jyl4HzYKr7":("betting: live title 'Apostas esportivas'"),
 "C1EDmo22BI2I3jkHINI81x":("betting: live title '4X4 APOSTADO WAVE'"),
 "CUvraq7w2ZM5E4Cu5D9Mw6":("betting/lottery tips: live title 'Renda Extra' but group desc is lotofacil lottery-betting tips ('segredo da lotofacil', results on all your bets)"),
 "Cb4ZY4EJlwf24ENsk4PVXO":("PIX investment scheme: group desc asks for R$10 'investimento' via PIX to a personal email address"),
 "CrUYaN0ExzoDx1ue3HAfBA":("sexual content: live title 'Fas do Richard G.' is clean but group desc explicitly permits sending nudes ('PODE MNDR NUDES SE QUISER')"),
 "DGSc0KMwKOdKC1BMR77Nex":("earn-money referral scheme + phone-like numeric code as group name ('Kwai176551729'); desc 'grupo pra ganhar dinheiro com kwai'"),
 "DKEpXIogwuU8RcARJNXvpg":("sexual content: live title 'Fas do Richard G.' is clean but group desc says 'ROLA PUTARIA TOTAL' (explicit sex)"),
 "DWjJTUZyCH2L3tPHzxOHYI":("porn leaks: live title 'VIDEOS VAZADOS' (leaked videos)"),
 "DoEJCTwrjge3vyxl0pIbfZ":("betting: live title 'FUT PRE E LIVE' (football pre-match/live betting); dir 'CORNER BETS', desc corner-betting group"),
 "DqdpfejPMcS8YC8fU2cuG4":("betting tips: live title 'Dicas Free' (free tips); dir 'Sportbet Brasil Cambista', desc sports-betting group"),
 "E8O4xkaJtIoKevRUotDdw8":("betting: live title 'X1 apostado'"),
 "EKNoEAD9b91EDfasD5131L":("betting: live title 'Aposta 24H FF'"),
 "EhK6KhlZbAjL55mL1P1HEF":("betting: live title 'Aposta Esportivas #2'"),
 "EwtvI083nDRJXjjTrG9A8g":("porn: live title 'Kawaii' is clean but group desc regulates posting pornographic videos"),
 "F0x4AfhzPlG0WxGFHma66l":("hard porn/xxx: live title 'DIARIO DO XXX'"),
 "FS78GVLCklI5Wf3oNd63nX":("betting: live title 'Lidertoppp Free G&g'; desc 'grupo de apostas'"),
 "FV7rX4uB4OiDzHQc6pKkox":("betting: live title 'SUPERBETS88 TIPS E APOSTA'"),
 "FuBKONlfp2E0GHbdo3YVTD":("betting: live title 'APOSTAS DO LUK | 10%'"),
 "FwH1GABvjAR5XehCDG9fo9":("betting: live title 'Sorte esportiva - sua aposta aki' (your bet here)"),
 "G1a4FBi97EyJNmtKJ0lbe8":("no usable name: live title and directory name are only the emoji"),
 "GFqgjUHbo011D2zdKbg047":("betting promo: live title 'Ganhe 5 reais de Bonus' (win R$5 bonus); dir 'Apostas Free'"),
 "GORA4rfaLZI4VdQSoUEilF":("earn-money referral scheme + phone-like numeric code in name ('Kwai236332278 dinheiro')"),
 "GVDl3sdswUF5Jh33oydwHf":("betting: live title '5 - BETS CARTOLAO'"),
 "GWczr4W0GKKH39A8FPqZBo":("betting: live title 'APOSTA 24HRS @WILL'"),
 "GeG6FCcFKCYKtDSMOqhd5a":("betting: paid betting league on Cartola per desc ('LIGA APOSTADA NO CARTOLA', R$3 per team)"),
 "GhpUY3vGFEd9pfHUdneENX":("betting signals: live title 'Palpites Zero Grau' (palpites = betting predictions)"),
 "GnSt94nmjgDLPtmO7cIXFX":("betting: live title '4 - BETS CARTOLAO'"),
 "GvBsn0kLtjGF7jAm15OM8K":("earn-money referral scheme: 'Cadastros Novos KWAI VIP' (Kwai signup recruitment for money)"),
 "HgjodQUE4md3Rwl2zRuJF7":("betting: live title 'GALAXY APOSTAS GP-1'"),
 "Ho1XYfqQxJ91PcdPXd4ijQ":("sexual content: live title 'Pau no cu' is explicit sexual slang; desc invites ages 13+ into a sexual group"),
 "INVcmZVPuheAJXwmQlw1z6":("betting: live title 'FAMILIA vL apostaaas'"),
 "J1mCBWkQBiYKAaQycB3SZ7":("betting: live title '4X4 ALEMAO/ apostado'"),
 "JGGeEo9rYNHI4jZOulGxxf":("betting: live title '3 - BETS CARTOLAO'"),
 "JP3zyiEZL2K5HkEnZwX2DZ":("betting: live title 'Banca ilha bet'"),
 "JVAmYNlbTXzEzFbBykfzx6":("betting: live title 'BANCA DO ELTONBETS88'"),
 "JgOljnheVuNCAeVt7xJIN9":("betting: live title 'GORILA APOSTAS - 10%'"),
 "K08Hb1Zcm62D8dcBG8eTD8":("betting: 'Geração Milionária' group is a ColorWiz gambling group per desc ('APOSTA LUCRATIVA #COLORWIZ')"),
 "K7JacPSLgnb2vHtoZQPzf9":("betting signals: live title 'Gavião. Palpites free'; dir 'BET365 - SINAIS'"),
 "KfLXQ12PUm0Ht0XOevPxK1":("earn-money scheme: 'Kwai golds 2.000.000 =200' (trading Kwai virtual currency for cash)"),
 "KmZIXCLB3dwIWEDNkh8Lel":("betting: live title 'Apostas esportivas gp#13'"),
 "LIgMCJbsFpcBSOfEjyh909":("betting signals: live title 'Placarbets palpite'; desc football predictions + betting"),
}
KEEP={
 "EmO6JC91mCa9ZKHJXvJFC1":"restored false positive: group rules explicitly ban pornography ('NADA DE PORNOGRAFIA'); live title 'PAPO DE VISAO $2' kept but flagged - hustle-talk name with $2, borderline money theme",
 "FyWIxmqzHNjAVAJA7LsERO":"restored false positive: live title reads 'NOVAS AMIZADE' (new friendship); friendship allowed",
 "I7ML3IEg1boJDYvN0cLXm7":"restored false positive: group rules ban pornography; live title is farm/truck implements, buy-sell group",
 "IM4OcOcf9yHE1PSf5obv64":"restored false positive: group rules ban nude photos; religious greeting group",
 "IWRqKhn92ATJlqpcYAjUqB":"restored false positive: group rules ban nudes/links; live title 'Ganhe dinheiro em casa' kept but flagged - generic earn-money name, no scam signal in title",
 "Ic5aOLb3TfC046EAoF15Yb":"restored false positive: group rules ban porn content; evangelical group",
 "J3piQqaXAdhA5wPKetGVMw":"kept but flagged: live title 'Exemplo' (Example) - placeholder-sounding name, looks like a directory test listing; live and clean",
 "J9mPZdv2lyJCoPfQdgd1h4":"restored false positive: group rules ban pornography; follower-exchange group",
 "JNrqVYzcnM59V7nkUnqrxQ":"restored false positive: group rules ban pornography; promotion/divulgation group",
 "K24x2AkliINJTfLW5qbLcI":"restored false positive: group rules ban sending porn ('Manda porno' forbidden); stylized 'novas amizades' (new friendships)",
 "L23GzabfhdO2g75WkxzWCL":"restored false positive: group rules ban pornography; mutual-help group; flagged - money-face emoji and renda-extra theme in desc",
}
live=[v for v in res.values() if v["status"]=="live"]
dead=[v for v in res.values() if v["status"]=="dead"]
pend=[v for v in res.values() if v["status"]=="pending"]
assert len(live)==54 and len(dead)==26 and len(pend)==0
assert set(EXCLUDE)|set(KEEP)=={v["code"] for v in live}, (set(EXCLUDE)^set(KEEP), {v["code"] for v in live})
assert not (set(EXCLUDE)&set(KEEP))
# candidates from KEEP, name = live og:title (verified current name), whitespace collapsed
cands=[]
for code, note in KEEP.items():
    v=res[code]
    name=re.sub(r"\s+"," ", v["og_title"]).strip()
    cat=CATMAP[v["cat_raw"]]
    cands.append({"name":name,"category":cat,"country":"BR",
        "description":f"Join {name}, an active WhatsApp group for {cat.lower()}. Chat with members, share updates and connect.",
        "invite":f"https://chat.whatsapp.com/{code}"})
cands.sort(key=lambda c: c["invite"])
# sanity: no source name/link, no emails/phones in any output field
for c in cands:
    assert "linkado" not in (c["name"]+c["description"]).lower()
    assert "@" not in c["name"] and "@" not in c["description"]
    assert c["category"] in ["Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell","Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto","Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"]
    assert re.match(r"^https://chat\.whatsapp\.com/[A-Za-z0-9_-]+$", c["invite"])
assert len({c["invite"] for c in cands})==len(cands)==11
excluded=[{"code":code,"reason":EXCLUDE[code],"og_title":res[code]["og_title"]} for code in sorted(EXCLUDE)]
json.dump(cands, open(f"{WAVE}/team09-candidates.json","w"), ensure_ascii=False, indent=1)
json.dump([], open(f"{WAVE}/team09-leads.json","w"))
json.dump([], open(f"{WAVE}/team09-pending.json","w"))
summary={
 "team":"team09",
 "slice":"team02-extracted.jsonl (wave_20261112) remainder reconciliation - codes never verified anywhere",
 "sources":["wave_20261112/team02-extracted.jsonl","wave_20261112/team02-awaiting-verification.json",
   "wave_20261113/team02-summary.json + team02-candidates.json","wave_20261113/team03-summary.json + team03-candidates.json",
   "wave_20261112/team02-verify-state.json","wave_20261112/team02-leads-slice2-summary.json (exclusions + candidates)",
   ".existing_codes.json (union, 119266 codes)"],
 "controls":{"live":"KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (LIVE)",
   "fabricated":"ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title (dead)",
   "method":"one requests.Session, browser User-Agent, 60s timeout, empty og:title retried 3x spaced before dead; HTTP 429/transport -> pending"},
 "counts":{"raw_extracted_lines":3603,"raw_unique_codes":3601,"no_code_entries":3,
   "verified_this_run":80,"live":54,"dead":26,"pending":0,
   "candidates":11,"excluded_live":43,"leads":0,
   "dupes_vs_union_in_remainder":77},
 "reconciliation":{
   "extracted_unique_codes":3601,
   "in_awaiting_file":2160,
   "awaiting_verified_by_wave13_team02":1080,
   "awaiting_verified_by_wave13_team03":1080,
   "awaiting_unverified":0,
   "in_wave12_verify_state_not_in_awaiting":1284,
   "wave12_verify_state_live":528,"wave12_verify_state_dead":756,
   "never_verified_anywhere":157,
   "never_verified_of_which_union_dupes":77,
   "never_verified_of_which_non_union_to_verify":80,
   "note":"The 80 to-verify codes are EXACTLY the 80 wave_20261112 slice2 exclusions sitting in the uncovered set (set equality checked): wave12 pre-screened them on directory name/desc without a live check. This run live-verified all 80 and re-screened on the LIVE og:title (+ group description text for borderline cases). 26 dead, 43 live-but-excluded, 11 restored as candidates. No wave13-verified code was re-verified. Wave12 verify-state 'live' entries were NOT re-verified (out of scope); see flags.",
   "wave13_team02_counts_check":"2 verified + 611 dupes + 462 dead + 5 excluded = 1080 = raw",
   "wave13_team03_counts_check":"0 verified + 643 dupes + 433 dead + 4 excluded = 1080 = raw"},
 "excluded":excluded,
 "dead_codes":[v["code"] for v in sorted(dead, key=lambda x: x["code"])],
 "flags":[
   "Restored 10 false positives + 1 placeholder keep = 11 candidates; each restore is backed by the group's own rules text banning porn/nudes (negated-prohibition) or a clean live title (friendship/religion/buy-sell).",
   "Live og:title often differs from the directory name - 2 codes (CrUYaN0ExzoDx1ue3HAfBA, DKEpXIogwuU8RcARJNXvpg) share live title 'Fas do Richard G.' but their group descriptions are sexual (nudes allowed / 'putaria total'), so both were EXCLUDED on description evidence, not the clean title.",
   "Ho1XYfqQxJ91PcdPXd4ijQ ('Pau no cu'): explicit sexual live title AND its description invites ages 13+ - excluded; worst item in the slice.",
   "Kwai referral groups (4): DGSc0KMwKOdKC1BMR77Nex, GORA4rfaLZI4VdQSoUEilF, GvBsn0kLtjGF7jAm15OM8K, KfLXQ12PUm0Ht0XOevPxK1 excluded as earn-money referral/free-money schemes (+ bare phone-like numeric code names on the first two). Judgment call - coordinator may restore if referral groups are wanted.",
   "BmkCPrwgaqk7515rbN8kE1 ('Tudo estudado', desc says 'ND de PORNOGRAFIA' - negated prohibition) would have been a restore candidate but the link is DEAD, so no restore was possible.",
   "J3piQqaXAdhA5wPKetGVMw kept as 'Exemplo' (Technology): live and clean, but the name/desc ('hello appstore') look like a directory test listing - coordinator may drop it.",
   "Borderline keeps flagged in candidates notes above: EmO6JC91mCa9ZKHJXvJFC1 ('PAPO DE VISAO $2'), IWRqKhn92ATJlqpcYAjUqB ('Ganhe dinheiro em casa'), L23GzabfhdO2g75WkxzWCL ('VAMOS NOS AJUDAR', money emoji).",
   "OBSERVATION (not re-verified, out of scope): wave12 team02-verify-state.json marks 1787 codes 'live', many with empty og:'' (e.g. first entries BnfNh3lujd2FCYrXcJa8Nh, Ht6lvqqIubo30cpr8HbyZg). An empty og:title would be dead under this wave's hard rule, so those live verdicts rest on a weaker/unknown signal. Only 3 of the 528 live remainder codes became slice2 candidates (rest were union/already-merged dupes), so exposure is limited to already-merged codes - but the coordinator may want a spot re-check of verify-state live-with-empty-og codes before trusting them.",
   "No source name/link and no personal info stored in any output file; descriptions are generated from name/category/country only."],
 "resume_point":"COMPLETE - all 80 remainder codes verified (54 live / 26 dead / 0 pending); outputs team09-candidates.json (11), team09-leads.json ([]), team09-pending.json ([]), team09-summary.json. No resume needed. Raw verification log: team09-verify-results.json (80 entries with og_title + wave12 reason).",
 "files":{"candidates":"team09-candidates.json","leads":"team09-leads.json","pending":"team09-pending.json",
   "verify_log":"team09-verify-results.json","verify_list":"team09-verify-list.json","script":"team09-verify.py"}
}
json.dump(summary, open(f"{WAVE}/team09-summary.json","w"), ensure_ascii=False, indent=1)
print("candidates:", len(cands))
for c in cands: print(" ", c["name"], "|", c["category"], "|", c["invite"])
print("excluded:", len(excluded), "dead:", len(dead), "pending:", len(pend))
print("OK")
