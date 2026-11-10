import json, re, unicodedata, collections

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
ALLOWED = ["Entertainment","Jobs","Education","Islamic","Sports","Community & Social",
           "Finance","Funny","Buy Sell","Health","News","Gaming","Technology","Business"]
CATMAP = {
 "entertainment":"Entertainment","jobs":"Jobs","education":"Education","islamic":"Islamic",
 "sports":"Sports","sports & fitness":"Sports","community":"Community & Social",
 "community & social":"Community & Social","finance":"Finance","money":"Finance",
 "earn money online":"Finance","funny":"Funny","comedy":"Funny","buy sell":"Buy Sell",
 "online shopping":"Buy Sell","health":"Health","news":"News","gaming":"Gaming",
 "technology":"Technology","science & technology":"Technology","business":"Business",
 "friendship":"Community & Social","pets & animals":"Community & Social",
 "flirting":"Community & Social","love & relationship":"Community & Social",
 "quotes":"Entertainment","advertising":"Business","comics":"Entertainment",
 "beauty & fashion":"Entertainment","fan club":"Entertainment","autos & vehicles":"Community & Social",
 "photography":"Entertainment",
}
COUNTRY_WORDS = {"pakistan":"PK","india":"IN","indian":"IN","bangladesh":"BD","usa":"US","america":"US",
 "united states":"US","uk":"GB","england":"GB","london":"GB","uae":"AE","dubai":"AE","canada":"CA",
 "australia":"AU","nigeria":"NG","kenya":"KE","ghana":"GH","nepal":"NP","sri lanka":"LK",
 "philippines":"PH","indonesia":"ID","malaysia":"MY","turkey":"TR","saudi":"SA","qatar":"QA",
 "kuwait":"KW","oman":"OM","bahrain":"BH","egypt":"EG","south africa":"ZA","germany":"DE",
 "france":"FR","italy":"IT","spain":"ES","portugal":"PT","brazil":"BR","mexico":"MX",
 "bangalore":"IN","delhi":"IN","gujarat":"IN","dehradun":"IN","erode":"IN","karachi":"PK",
 "lahore":"PK","islamabad":"PK","dhaka":"BD","kathmandu":"NP","colombo":"LK","manila":"PH",
 "jakarta":"ID","kuala lumpur":"MY","istanbul":"TR","riyadh":"SA","doha":"QA","cairo":"EG",
 "nairobi":"KE","accra":"GH","lagos":"NG","toronto":"CA","sydney":"AU","melbourne":"AU",
 "berlin":"DE","paris":"FR","rome":"IT","madrid":"ES","lisbon":"PT"}
SCAM = ["b-love","blove","forsage","sheyi","paypal loader","bitfinex","counterfeit","crypto doubling","carding","double your money","double money","money doubling","airdrop","free bitcoin","free usdt"]
ADULT = ["🔞","🥵","sexy","hookup","escort","porn","xxx","nude","naked","sex video","sex chat","adult","hot girl","hot girls","hot bhabhi","desi sex","call girl","call girls","onlyfans","erotic","horny","lust","fuck","💋","🫦","crot"]

def norm_name(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def clean_desc(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def has_phone(s):
    return bool(re.search(r"\+?\d[\d\s\-]{8,}\d", s or ""))

to_verify = json.load(open(f"{W}/team04_to_verify.json"))
ver = {}
for line in open(f"{W}/team04_verify_ckpt.jsonl"):
    r = json.loads(line); ver[r["code"]] = r
print("verify records:", len(ver), "of", len(to_verify))
status = collections.Counter(r["status"] for r in ver.values())
print("status:", dict(status))

prescreen = json.load(open(f"{W}/team04_prescreen_dropped.json"))
exclusions = list(prescreen)
verified, pending, dead = [], [], 0
post_drop = []
for code, meta in to_verify.items():
    r = ver.get(code)
    if r is None:
        pending.append({"code": code, "reason": "not checked - verifier did not reach it", "invite": f"https://chat.whatsapp.com/{code}"})
        continue
    st = r["status"]
    if st == "transport-fail":
        pending.append({"code": code, "reason": "transport failure (curl error/timeout, no HTTP status)", "invite": f"https://chat.whatsapp.com/{code}"})
        continue
    if st != "live":
        dead += 1
        continue
    title = norm_name(r.get("title",""))
    ogdesc = clean_desc(r.get("desc",""))
    # listing-level NSFW flags (groupjoin): never bank an NSFW/18+ rated group
    if meta.get("nsfw"):
        post_drop.append({"code": code, "reason": f"listing nsfw flag set (nsfw={meta.get('nsfw')}, contentRating={meta.get('contentRating')})"}); dead += 1; continue
    cr = meta.get("contentRating")
    if isinstance(cr, (int, float)) and cr >= 18:
        post_drop.append({"code": code, "reason": f"listing contentRating {cr} (18+)"}); dead += 1; continue
    text = f"{title} {ogdesc} {meta.get('title','')} {meta.get('desc','')}".lower()
    s = [w for w in SCAM if w in text]
    a = [w for w in ADULT if w in text]
    if s:
        post_drop.append({"code": code, "reason": f"post-verify scam keyword(s): {s} in og:title/desc"}); dead += 1; continue
    if a:
        post_drop.append({"code": code, "reason": f"post-verify adult signal(s): {a} in og:title/desc"}); dead += 1; continue
    if not title or title.isdigit() or len(re.sub(r"[^A-Za-z0-9]","",title)) < 2:
        post_drop.append({"code": code, "reason": f"unusable group name after cleaning: {title!r}"}); dead += 1; continue
    if has_phone(title) or has_phone(ogdesc):
        post_drop.append({"code": code, "reason": "personal info (phone-like digits) in og:title/desc"}); dead += 1; continue
    # category
    cat = ""
    rawcat = (meta.get("category") or "").strip()
    if rawcat:
        cat = CATMAP.get(rawcat.lower(), "")
        if not cat:
            # try substring match
            for k, v in CATMAP.items():
                if k in rawcat.lower():
                    cat = v; break
    if not cat:
        pt = (meta.get("page_title","") + " " + meta.get("context","")).lower()
        if "job" in pt: cat = "Jobs"
        elif "news" in pt: cat = "News"
        elif any(k in pt for k in ("cricket","football","sport","fifa","ipl")): cat = "Sports"
        elif any(k in pt for k in ("study","exam","education","school","university","ssc","bpsc","cat ","neet","jee")): cat = "Education"
        elif any(k in pt for k in ("islam","quran","muslim","naat","ramadan")): cat = "Islamic"
        elif any(k in pt for k in ("movie","song","music","drama","film","shayari","poetry","funny","meme","comedy")): cat = "Entertainment"
        elif any(k in pt for k in ("buy","sell","shopping","sale","market")): cat = "Buy Sell"
        elif any(k in pt for k in ("health","doctor","fitness","yoga","medical")): cat = "Health"
        elif any(k in pt for k in ("game","gaming","free fire","pubg","fortnite")): cat = "Gaming"
        elif any(k in pt for k in ("tech","software","crypto","forex","trading","earning","money","finance","business","stock")): cat = "Finance" if any(k in pt for k in ("forex","trading","earning","money","finance","stock")) else "Technology"
        else: cat = "Community & Social"
    # country
    country = (meta.get("country") or "").strip().upper()
    if len(country) != 2:
        country = ""
        pt = (meta.get("page_title","") + " " + title).lower()
        for w, cc in COUNTRY_WORDS.items():
            if w in pt:
                country = cc; break
    if not country:
        country = "International"
    # description
    ldesc = clean_desc(meta.get("desc",""))
    boiler = ldesc.lower().startswith("welcome to my whatsapp group")
    if ldesc and not boiler and len(ldesc) > 40 and not has_phone(ldesc):
        desc = ldesc
        if len(desc) > 220:
            desc = desc[:217].rsplit(" ", 1)[0] + "..."
    else:
        desc = f"A WhatsApp group for {title} members to chat, share updates and connect with each other."
    verified.append({"name": title, "category": cat, "country": country,
                     "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
exclusions.extend(post_drop)

# leads: discovered listing-page URLs, deduped, exclude input URLs and groupjoin API pages already covered
leads_in = set(x["url"] for x in json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_04.json")))
raw_leads = json.load(open(f"{W}/team04_leads_raw.json"))
leads = sorted(u for u in set(raw_leads) if u not in leads_in)
# keep only plausible listing pages on the slice domains
DOMS = ("whtspgrouplink.com","appgrouplink.com","linkado.app","igrupos.com","groupizo.com","groupjoin.link")
leads = [u for u in leads if any(d in u for d in DOMS)]

json.dump(verified, open(f"{W}/team04-leads-slice4.json","w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{W}/team04-leads-slice4-pending.json","w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{W}/team04-leads-slice4-leads.json","w"), ensure_ascii=False, indent=1)

# sources for summary
recs = [json.loads(l) for l in open(f"{W}/team04_fetch_ckpt.jsonl")]
sources = sorted(set(r["source"] for r in recs))
summary = {
 "team": 4,
 "slice": "leads slice 4",
 "sources": sources,
 "verified": len(verified),
 "pending": len(pending),
 "leads": len(leads),
 "dead": dead,
 "exclusions": exclusions,
 "resume": "team04-leads-slice4-pending.json holds transport-only pending codes for a retry pass; team04-leads-slice4-leads.json holds newly discovered listing-page URLs for future waves.",
 "notes": (
  f"Fetched all 184 listing pages; {sum(1 for r in recs if r.get('dead'))} pages dead/codeless. "
  f"2855 unique invite codes extracted; 905 fresh vs the 108,365-code union; 373 dropped in prescreen "
  f"(344 groupjoin Adult category dropped wholesale without verification, 22 adult-sexual signals, 7 scam keywords); "
  f"532 sent to verification. Verify: {dict(status)}. {len(post_drop)} live groups dropped post-verify on og:title/desc screen. "
  f"Verification ran through the egress proxy with keep-alive sessions; the proxy stalled repeatedly (whole-network timeouts, "
  f"incl. a full outage) so transport-fail batches were discarded as unreliable and re-checked until every code reached a verdict "
  f"(0 transport-fails remain). Control check: two Nov-9-verified-live codes still return non-empty og:titles, so the empty-title=dead "
  f"signal is sound. Post-verify drops: 8 adult-sexual og:titles (3 xxx, 2 sexy, 1 'FUCK CONNECTION', 1 sexual-suggestive emoji title, "
  f"1 Indonesian sexual-slang 'CROT' title), 1 pure-digit name ('2023'), 1 NSFW-flagged earning-scheme group "
  f"(Orionmaal AddWatch: nsfw=1/contentRating 18 + phone number in listing desc + '$10-$50 daily' earning pitch), 1 sexual-suggestive "
  f"emoji title, 1 Indonesian sexual-slang title. "
  f"Names are WhatsApp og:titles NFKC-normalized; categories mapped to the allowed list; country from groupjoin ISO2 or page-title inference else International. "
  f"No source names/links or personal info in any banked field."
 )
}
json.dump(summary, open(f"{W}/team04-leads-slice4-summary.json","w"), ensure_ascii=False, indent=1)
print("verified:", len(verified), "pending:", len(pending), "leads:", len(leads), "dead:", dead, "exclusions:", len(exclusions))
print(json.dumps(collections.Counter(v["category"] for v in verified), indent=1))
print(json.dumps(collections.Counter(v["country"] for v in verified).most_common(10)))
