import json, re, html as htmllib

cands = {c["code"]: c for c in json.load(open("team24_fresh_candidates.json"))}
ver = json.load(open("team24_verify_raw.json"))
print("verify records:", len(ver))
live_codes = [k for k,v in ver.items() if v["status"]=="live"]
dead_codes = [k for k,v in ver.items() if v["status"]=="dead"]
trans_codes = [k for k,v in ver.items() if v["status"]=="transport"]
unchecked = [k for k in cands if k not in ver]
print(f"live={len(live_codes)} dead={len(dead_codes)} transport={len(trans_codes)} unchecked={len(unchecked)}")

# final name/category/country/description overrides for live items
META = {
"EZ5KdR165IlCMyZDFtpo4r": ("CLEANERS GOLD COAST","Jobs","AU","A jobs group for cleaners on the Gold Coast, sharing cleaning work and vacancies in Australia."),
"FyLYGHxQg2b2mRDChG2GJr": ("Brisbane 2026/2027 Brazil","Jobs","AU","A group for Brazilians in Brisbane sharing jobs and plans for 2026 and 2027."),
"HOljtjdsI47GWN22PRuaol": ("Trabajos en Adelaide","Jobs","AU","A Spanish-language group sharing job openings and work opportunities in Adelaide."),
"GGEhVNv27JPKxHr2q6rYLC": ("DOAÇÕES de Adelaide","Jobs","AU","A donations group for people in Adelaide, sharing help and donated items within the community."),
"HuURLEIAaLR14JG1gzmpsA": ("Loo for a job-ADELAIDE","Jobs","AU","A group sharing job leads and openings around Adelaide."),
"Lo6eso4EOViFpqTa5chTRB": ("Brasileiros em Gold Coast","Jobs","AU","A group for Brazilians living on the Gold Coast to connect and share local updates and jobs."),
"J19Qld4aI5mAqfgpyu0QgM": ("AVB BRASIL - Acrelândia","Jobs","BR","A Brazil jobs group sharing vacancies and work opportunities in Acrelândia."),
"BzCOH7Amt3yKPc1KRZxpPA": ("Divulga Vagas Brasil","Jobs","BR","A group sharing job vacancies across Brazil."),
"JZvufr66n6Q0Bx1c1rBE94": ("CPG4 VAGAS E NOTICIAS","Jobs","BR","A group sharing job vacancies and news updates in Brazil."),
"CQ4dSXp431b52xVrgOkmXs": ("CPG3 Vagas e Noticias","Jobs","BR","A group sharing job vacancies and news updates in Brazil."),
"6QNyiERYHm2J5IvEngMJah": ("Grupo RH Brasilia Goiania","Jobs","BR","A recruitment and jobs group for Brasília and Goiânia, sharing vacancies and hiring updates."),
"DVSHWE5CSny3IHMdreNnmk": ("SAM VIDAMBU MOTIVATION 8","Community & Social","International","A motivational group sharing encouragement and success quotes."),
"HIcrLkFA5PHD6iE5586iJ1": ("Stay Lit Circle","Community & Social","International","A motivational community sharing positive quotes and encouragement."),
"ElmgRHHQ9wk59Jy8hLMDSj": ("GESTO Speak Up & Rise Up Buddies","Community & Social","International","A motivational group where members share talks and encouragement to speak up and rise up."),
"IeenRdE5ybmIvwGAtuwGVW": ("Quotes for you","Community & Social","International","A group sharing daily quotes for inspiration and motivation."),
"2Idh1tNOe6y9mgORaEVxSz": ("Motivational & Self Develop Group","Community & Social","International","A group for motivation and self-development, sharing tips and encouragement."),
"GAimGuHWceT88DXdQ0CicI": ("MOTIVATION is HERE","Community & Social","International","A motivational group sharing inspiring messages and encouragement."),
"KfGtmuKikYo1rBeBjIGrgD": ("Motivation For Success","Community & Social","International","A motivational group sharing quotes and ideas for success."),
"Isrc5lcvPwnHne9CR9gkOh": ("Motivational Quotes 1","Community & Social","International","A motivational quotes group sharing daily inspiration."),
"Lqp5FhL1sUwIIYUUwSmAB2": ("Calgary Motivational Group","Community & Social","CA","A motivational group based in Calgary sharing encouragement and positive messages."),
"ERBlUVUEItKHuPqV66WQtP": ("News Today Palau","News","PW","A Palau news group sharing daily news updates."),
"EHUXcXmZ5FeFGmy99FlHSf": ("Culture Clothing Store","Buy Sell","PW","A clothing store group sharing cultural clothing and new stock."),
"IUIwpEIACoFBkARTuaquze": ("WASSCE 2026 Learning Platform","Education","SL","A study group for WASSCE 2026 learners sharing lessons and exam preparation."),
"D4mVohGDEdp2C9gBsVf9l0": ("Solapur Maharashtra Friends","Community & Social","IN","A friends group for people from Solapur, Maharashtra to chat and connect."),
}
ADULT = re.compile(r'🔞|🥵|sexy|hookup|escort|porn|xxx|18\+|nude|call girls|desi bhabhi', re.I)
SCAM = re.compile(r'b-?love|forsage|shey|airdrop|paypal loader|bitfinex|counterfeit|crypto.?doubling|carding|double (your|the) money|earn.{0,20}2x', re.I)

verified, exclusions = [], []
for code in live_codes:
    name, cat, country, desc = META[code]
    og = htmllib.unescape(ver[code].get("og_title","") or "")
    c = cands[code]
    if ADULT.search(name) or ADULT.search(og) or SCAM.search(name) or SCAM.search(og):
        exclusions.append({"code": code, "reason": f"adult/scam signal in name/og:title: {name!r} / {og!r}"})
        continue
    verified.append({"name": name, "category": cat, "country": country,
                     "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
print("verified kept:", len(verified), "excluded:", len(exclusions))

# pending: transport codes (attempted, no HTTP status) + unchecked codes (never attempted - throttling stall)
PEND_META = {
"FN9zH2RN31032Ycv9y4eKR": ("XAUUSD SCALPING MASTER","Finance","International","A trading group sharing XAUUSD scalping signals and market updates."),
"Hjeck49eZsu3k3QmY0If7I": ("Trade With Ai","Finance","International","A trading group sharing AI-assisted trading ideas and market updates."),
"EBzKkFCvi01EOFMxtDpreV": ("TRUEMAX Traders","Finance","International","A traders group sharing market updates and trading discussion."),
"IGa2WwYKdD67tt4fnZjwww": ("Stock Market","Finance","International","A stock market group sharing market news and discussion."),
"EeI2EVMcoHE4qBHKttflHA": ("Equity","Finance","International","An equity markets group sharing news and discussion."),
"JqSCbwY486HLP1EB8cxKke": ("Swing Trading","Finance","International","A swing trading group sharing market ideas and discussion."),
"G6iuCsQLpPw4O9kRMopMWZ": ("Abroad jobs South Indian","Jobs","International","A group sharing abroad job opportunities for South Indian job seekers."),
"CZMuehOdUJ20N7hNer7gfx": ("GK Manpower International Requirements","Jobs","International","A manpower group sharing international job requirements."),
"DRLjaHdHh5w2c03ZUtIo0v": ("ABROAD JOB WALA 4","Jobs","International","A group sharing abroad job openings and updates."),
"H9LTbkC34L5989l4xuHTb5": ("Singapore Free Job Visa","Jobs","SG","A group sharing Singapore job openings and free visa job updates."),
"FzF8gpujVhXCTeXTe50y6P": ("Free jobs in europe group","Jobs","International","A group sharing free job openings in Europe."),
"F1cw4R2sf8KLj9rxNQhgrQ": ("Abroad Jobs 3","Jobs","International","A group sharing abroad job openings and updates."),
"9cr4ESYIFog7Sk6sWaLO0C": ("Target IAS Vision Group Chat","Education","IN","A study group for IAS aspirants sharing target-based preparation and updates."),
"H4pSJdaTGpyAm6Lsyqkvp6": ("ONE MISSION@IAS","Education","IN","A study group for IAS aspirants sharing preparation material and motivation."),
}
pending = []
for code in trans_codes:
    name, cat, country, desc = PEND_META[code]
    pending.append({"name": name, "category": cat, "country": country, "description": desc,
                    "invite": f"https://chat.whatsapp.com/{code}",
                    "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts (WhatsApp throttling)"})
for code in unchecked:
    name, cat, country, desc = PEND_META[code]
    pending.append({"name": name, "category": cat, "country": country, "description": desc,
                    "invite": f"https://chat.whatsapp.com/{code}",
                    "reason": "not verified in this run: verifier stopped early after chat.whatsapp.com stopped returning HTTP status to curl (throttling); re-check needed"})
print("pending:", len(pending))

# leads: post-sitemap URLs NOT mined this run
sitemap = json.load(open("team24_sitemap_urls.json"))
mined = set()
for c in json.load(open("team24_candidates_v2.json")):
    mined.add(c["source_file"].replace(".html",""))
slug2url = {u.rstrip('/').split('/')[-1]: u for u,d in sitemap}
leads = [{"url": u, "lastmod": d} for u,d in sitemap if u.rstrip('/').split('/')[-1] not in mined]
print("leads:", len(leads), "of", len(sitemap), "sitemap posts")

sources = sorted({cands[c]["source"] for c in live_codes} | {cands[c]["source"] for c in dead_codes} | {cands[c]["source"] for c in trans_codes})
sources.append("https://whtspgrouplink.com/")
sources = sorted(set(sources))

json.dump(verified, open("team24-whtspgrouplink.json","w"), indent=1, ensure_ascii=False)
json.dump(pending, open("team24-whtspgrouplink-pending.json","w"), indent=1, ensure_ascii=False)
json.dump(leads, open("team24-whtspgrouplink-leads.json","w"), indent=1, ensure_ascii=False)
summary = {
  "team": 24,
  "slice": "whtspgrouplink.com",
  "sources": sources,
  "verified": len(verified),
  "pending": len(pending),
  "leads": len(leads),
  "dead": len(dead_codes),
  "exclusions": exclusions,
  "resume": "Mined 31 pages (30 freshest post-sitemap pages by lastmod + homepage). 710 unique invite codes extracted; 53 fresh vs the 108,364-code union. Verified 24 live, 15 dead (HTTP 200 + empty og:title after retries), 5 transport-pending (no HTTP status after 3 attempts), 9 fresh codes left unverified because chat.whatsapp.com stopped answering curl mid-run. Next run: re-check the 14 pending codes first, then mine the 473 unmined post-sitemap listing pages in team24-whtspgrouplink-leads.json.",
  "notes": "Site is slow (~7-30s/page) and its gzip responses truncate at 192KB via this transport; identity encoding worked and all group lists sit before ~135KB so truncation lost no groups. WhatsApp curl checks throttle hard after ~35-40 checks: 4 codes first recorded as transport later re-verified LIVE on a spaced sequential re-check, so transport-pending codes are likely partly live. No live item triggered adult/scam screens; trading/scalping groups found fresh (XAUUSD, Trade With Ai, TRUEMAX, Stock Market, Equity, Swing Trading) all landed dead or transport-pending, none banked as verified. og:titles were HTML-entity encoded and often emoji/stylised; directory names used for final names where clearer. Union measured 108,364 codes (.existing_codes.json already contains all groups.json codes)."
}
json.dump(summary, open("team24-whtspgrouplink-summary.json","w"), indent=1, ensure_ascii=False)
print("WROTE all 4 files")
print("sources:", len(sources))
